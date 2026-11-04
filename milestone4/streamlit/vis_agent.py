'''
Visualization agent that uses Gemini through the OpenAI Python library.

The model answers a user's question by calling TOOLS. A tool is just a Python
function that we write; the model decides when to call it and with which
arguments, and we send the function's result back to the model.

The tools are:
    1. select_dataset     - returns the details of all datasets so the model can pick one.
    2. design_chart       - returns the rules for designing a chart on the chosen dataset.
    3. test_chart         - runs the Altair code the model wrote, renders it, and checks that it
                            has data rows (our enhancement), then reports success or the error.
    4. review_chart       - asks a second "reviewer" model whether the chart answers the question.

The model calls tools in a loop. When it has nothing more to do it replies with
plain text instead of a tool call, and the loop stops.

Install:
    pip install openai pydantic pandas altair logfire

API keys:
    Gemini API (Google AI Studio):  set GOOGLE_API_KEY
    Pydantic Logfire API (optional): set LOGFIRE_TOKEN

Direct links:
    Google AI Studio: https://aistudio.google.com/api-keys?project=PROJECT (replace PROJECT with your GCP project id)
    Logfire: https://logfire-us.pydantic.dev
'''

import os
import json
import traceback

import pandas as pd
import altair as alt
import logfire
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from data import load_prepare_datasets, DATASET_DESCRIPTIONS

# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #

GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'
MODEL_NAME = os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash-lite')   # 3.1-flash-lite was overloaded (503) on 2026-11-04
TEMPERATURE = 0.1
MAX_STEPS = 12     # how many times we let the model call tools before we stop
MAX_REVIEWS = 2    # how many times the reviewer may be asked for one question
MAX_DISTINCT_VALUES = 50   # list a text column's distinct values only if it has at most this many
MAX_CHART_ROWS = 5000     # Altair refuses to embed more rows than this

# --------------------------------------------------------------------------- #
# Connect to Gemini
# --------------------------------------------------------------------------- #

api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise RuntimeError('Missing environment variable GOOGLE_API_KEY')

# The OpenAI library talks to Gemini because we point it at Google's base_url.
client = OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL, max_retries=6)   # Gemini often returns 503 when busy; the library waits and retries

# Send a trace of every call to Logfire (only if LOGFIRE_TOKEN is set).
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_openai(client)


# --------------------------------------------------------------------------- #
# The arguments of each tool
# Each class describes the arguments the model must give when it calls a tool.
# The descriptions are sent to the model (Gemini) so it knows what to put in
# each field.
# --------------------------------------------------------------------------- #

class Select_Dataset_Args(BaseModel):
    '''This tool needs no arguments: it returns the details of every dataset.'''
    pass


class Design_Chart_Args(BaseModel):
    dataset_name: str = Field(description='The json key of the dataset you have chosen to answer the question.')
    reason: str = Field(description='A 1-3 sentence rationale for choosing this dataset.')


class Test_Chart_Args(BaseModel):
    chart_code: str = Field(description='Python executable Altair code of your chart. The data is in a DataFrame named `df`. Assign the final chart to a variable named `final_chart`.')


class Review_Chart_Args(BaseModel):
    chart_desc: str = Field(description='A 1-3 sentence description of your chart and what it represents without giving away the answer.')


# The shape of the reviewer's answer (the reviewer is a separate model call
# that returns JSON, like in the earlier version of this program).
class Review_Out(BaseModel):
    relevant: bool = Field(description="Does the chart help answer the user's question?")
    feedback: str = Field(description='1-3 sentences: what is good about the chart and what should change.')


# --------------------------------------------------------------------------- #
# Describe the tools to the model
# This is the list we send with every request. The model reads the names,
# descriptions and argument schemas to decide which tool to call.
# --------------------------------------------------------------------------- #

def tool_definition(name, description, args_class):
    '''Describe one tool in the format the OpenAI library expects.'''
    return {
        'type': 'function',
        'function': {
            'name': name,
            'description': description,
            'parameters': args_class.model_json_schema(),
        },
    }


TOOLS = [
    tool_definition(
        'select_dataset',
        'Returns the schema, summary stats, sample rows and distinct text values of every available dataset, '
        'so you can select the one that best answers the question.',
        Select_Dataset_Args,
    ),
    tool_definition(
        'design_chart',
        'Records the dataset you chose and returns the rules you must follow when writing the chart code.',
        Design_Chart_Args,
    ),
    tool_definition(
        'test_chart',
        'Runs your Altair chart code on the chosen dataset. Returns ok if it produced a chart, '
        'or the error message so you can fix the code and test again.',
        Test_Chart_Args,
    ),
    tool_definition(
        'review_chart',
        "Asks a reviewer whether the chart that last passed test_chart answers the user's question. "
        "Returns the reviewer's verdict and feedback.",
        Review_Chart_Args,
    ),
]


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def print_message(message):
    '''
    Print one message of the conversation so we can follow what is going on.
    This is the default "log" function. The Streamlit app passes its own log
    function to VisAgent so the same messages show up in the page instead.
    '''
    print(f"--- {message['role']} ---")
    if message.get('content'):
        print(message['content'])
    for call in message.get('tool_calls', []):
        print(f"tool call: {call['function']['name']}({call['function']['arguments']})")
    print()


def ask_model(messages, answer_class, log=print_message):
    '''
    Send the conversation to the model and return its reply as a JSON string.
    answer_class (one of the classes above) tells the model what JSON to return.
    Used by the reviewer tool.
    '''
    for message in messages:
        log(message)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=TEMPERATURE,
        response_format={
            'type': 'json_schema',
            'json_schema': {
                'name': answer_class.__name__,
                'schema': answer_class.model_json_schema(),
            },
        },
    )
    return response.choices[0].message.content or ''


def ask_model_with_tools(messages):
    '''
    Send the conversation to the model together with the list of tools.
    Returns the model's reply as a plain dict. The reply either contains
    'tool_calls' (the model wants us to run a tool) or only 'content'
    (the model is done and is talking to the user).
    '''
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=TEMPERATURE,
        tools=TOOLS,
    )
    reply = response.choices[0].message

    # Convert the reply object into a plain dict so we can append it to messages.
    message = {'role': 'assistant', 'content': reply.content or ''}
    if reply.tool_calls:
        message['tool_calls'] = [call.model_dump() for call in reply.tool_calls]
    return message


def remove_code_fences(code):
    '''Remove the ```python ... ``` markers that models sometimes add around code.'''
    if code is None:
        return None
    return code.replace('```python', '').replace('```', '').strip()


def run_chart_code(code, df):
    '''
    Run the chart code that the model wrote.
    Returns two values: (chart, error_message).
      - If the code worked: chart is the Altair chart and error_message is ''.
      - If it failed: chart is None and error_message says what went wrong.
    '''
    if not code:
        return None, 'No code was returned. Return executable Altair code that assigns the chart to a variable named `final_chart`.'

    # The variables the code is allowed to use. Any variables the code creates
    # (such as final_chart) are added to this same dictionary.
    variables = {'df': df.copy(), 'pd': pd, 'alt': alt}

    try:
        exec(code, variables)
    except Exception:
        return None, 'Running your code raised an error. Fix it:\n' + traceback.format_exc()

    chart = variables.get('final_chart')
    if chart is None:
        return None, 'Your code ran but did not assign a chart to `final_chart`. Assign the final chart to it.'

    return chart, check_rendered_chart(chart)


def check_rendered_chart(chart):
    '''
    Our enhancement to test_chart. Code that runs is not always a chart that
    shows something: Altair only fails when the chart is rendered (for example
    with more than 5000 rows), and a filter with a misspelled value gives an
    empty chart without any error. Render the chart to its JSON spec and check
    that its data has rows. Returns '' if the chart is fine, else the problem.
    '''
    try:
        spec = chart.to_dict()
    except alt.MaxRowsError:
        return (f'The chart has more than {MAX_CHART_ROWS} rows, so it cannot be rendered. '
                'Aggregate the data with pandas (groupby) before you make the chart.')
    except Exception as e:
        return f'The chart could not be rendered: {e}'

    rows = [len(values) for values in spec.get('datasets', {}).values()]
    if rows and max(rows) == 0:
        return ('The chart data has 0 rows, so the chart is empty. Your filter probably matched nothing: '
                'check the filter values against the distinct values from select_dataset.')
    return ''


# --------------------------------------------------------------------------- #
# Instructions
# --------------------------------------------------------------------------- #

def agent_instructions():
    '''System prompt for the main model: who it is and in which order to use the tools.'''
    return (
        "You are an analyst who helps travelers and airline planners understand how storms relate to US flight "
        "delays in June 2026. "
        "You answer the user's question by making a chart. Use the tools in this order:\n"
        "1. select_dataset: get the details of all available datasets. Review the dataset descriptions "
        "schema information, summary stats, sample rows and distinct values, and decide if "
        "at least one dataset can answer the user's question. "
        "If the question is not related to any of the datasets, or if no single "
        "dataset can answer it, stop calling tools and reply with a 1-3 sentence explanation of why.\n"
        "2. design_chart: record the dataset you chose and get the rules for writing the chart code.\n"
        "3. test_chart: write Altair code that follows the rules and test it. "
        "If the tool returns an error, fix your code and test it again.\n"
        "4. review_chart: ask the reviewer whether your chart answers the question. "
        "If the reviewer says it does not, improve the code, test it again, and review it again.\n"
        "When the chart has been accepted, reply with a 1-2 sentence message for the user "
        "that describes the chart without giving away the answer."
    )


def chart_rules(dataset_name, schema, values):
    '''Returned by the design_chart tool: how to write the chart code.'''
    return (
        f"Create a visualization in Altair on the dataset {dataset_name} that would help answer the user's question. "
        f"Its schema is: {json.dumps(schema)}. "
        f"The distinct values of its text columns are: {json.dumps(values)}. "
        "Use these exact values when you filter or label the data.\n"
        "Think carefully about your choice of marks and visual encodings.\n\n"
        "Here are a few more rules to follow:\n"
        "1. The data is available in a DataFrame named `df`. pandas (`pd`) and Altair (`alt`) are already imported. "
        f"The chart may hold at most {MAX_CHART_ROWS} rows, so aggregate large data with pandas first.\n"
        "2. Don't label the x-axis when it encodes either states or dates. Otherwise, label it.\n"
        "3. Don't label the y-axis when it encodes either states or dates. Otherwise, label it.\n"
        "4. Prioritize blue and green colors over red, orange, and yellow colors.\n"
        "5. Include a tooltip, and format the numeric values shown in it to two decimal places.\n"
        "6. Only send executable Python code.\n"
        "7. Do NOT use plt.show().\n"
        "8. Do NOT save the json.\n"
        "9. Your code will be rendered by a downstream process in Streamlit.\n"
        "10. Assign the final chart to a variable named final_chart.\n"
        "Test your code with the test_chart tool."
    )


def reviewer_instructions(dataset_name, schema, chart_code, chart_desc):
    '''System prompt for the reviewer model: judge the chart by reading its code.'''
    return (
        "You are a strict reviewer of data visualizations. A colleague made a chart to answer "
        "the user's question. Decide whether the chart is relevant: does it show the right "
        "variables with sensible marks and encodings, so that a reader could answer the "
        "question by looking at it? Judge the chart by reading its code; do not run it.\n"
        f"The chart uses the dataset {dataset_name}, which has the schema: {json.dumps(schema)}.\n"
        f"The colleague describes the chart as: {chart_desc}\n"
        f"The chart code is:\n{chart_code}"
    )


# --------------------------------------------------------------------------- #
# The agent: the tools (as Python functions) and the loop that runs them
# --------------------------------------------------------------------------- #

class VisAgent:
    def __init__(self, log=print_message):
        # log is the function we hand every message of the conversation to.
        # By default it prints to the terminal; the Streamlit app passes a
        # function that shows the message in the page instead.
        self.log = log
        self.datasets = load_prepare_datasets()

        # Short summaries of each dataset that the select_dataset tool returns.
        self.schemas = {}
        self.stats = {}
        self.samples = {}
        self.values = {}    # the distinct values of each text column (e.g. metric names, state codes)
        for name, df in self.datasets.items():
            self.schemas[name] = df.dtypes.astype(str).to_dict()
            # include='all' adds unique/top/freq for text columns, not just numeric stats.
            # Stats that don't apply to a column are NaN; replace them with '' so they are valid JSON.
            self.stats[name] = df.describe(include='all').fillna('').astype(str).to_dict()
            self.samples[name] = df.sample(5).astype(str).to_dict()

            self.values[name] = {}
            for column in df.columns:
                if pd.api.types.is_string_dtype(df[column]) or isinstance(df[column].dtype, pd.CategoricalDtype):
                    distinct = df[column].dropna().unique()
                    if len(distinct) <= MAX_DISTINCT_VALUES:
                        self.values[name][column] = sorted(distinct.astype(str).tolist())

        # Map each tool name (as the model knows it) to the Python function that runs it.
        self.tools = {
            'select_dataset': self.select_dataset,
            'design_chart': self.design_chart,
            'test_chart': self.test_chart,
            'review_chart': self.review_chart,
        }

    # ---- Tool 1: describe all datasets so the model can pick one ------- #
    def select_dataset(self):
        return {
            'datasets': list(self.datasets),
            'descriptions': DATASET_DESCRIPTIONS,
            'schemas': self.schemas,
            'stats': self.stats,
            'samples': self.samples,
            'distinct_values': self.values,
        }

    # ---- Tool 2: record the chosen dataset and return the design rules - #
    def design_chart(self, dataset_name, reason):
        if dataset_name not in self.datasets:
            return {'error': f'Unknown dataset {dataset_name}. Choose one of: {list(self.datasets)}'}
        self.dataset_name = dataset_name
        return {'ok': True, 'rules': chart_rules(dataset_name, self.schemas[dataset_name], self.values[dataset_name])}

    # ---- Tool 3: run the chart code ------------------------------------ #
    def test_chart(self, chart_code):
        if self.dataset_name is None:
            return {'error': 'No dataset chosen yet. Call design_chart first.'}

        chart_code = remove_code_fences(chart_code)
        chart, error_message = run_chart_code(chart_code, self.datasets[self.dataset_name])
        if error_message:
            return {'error': error_message}

        # Remember the chart so review_chart and run() can use it.
        self.chart = chart
        self.chart_code = chart_code
        return {'ok': True, 'message': 'The code ran and produced a chart. Call review_chart next.'}

    # ---- Tool 4: ask a reviewer whether the chart is relevant ---------- #
    def review_chart(self, chart_desc):
        if self.chart is None:
            return {'error': 'There is no chart to review. Call test_chart first.'}
        if self.reviews >= MAX_REVIEWS:
            return {'error': 'Review limit reached. Finish with the current chart.'}
        self.reviews += 1
        self.chart_desc = chart_desc

        messages = [
            {'role': 'system', 'content': reviewer_instructions(
                self.dataset_name, self.schemas[self.dataset_name], self.chart_code, chart_desc)},
            {'role': 'user', 'content': self.user_question},
        ]
        reply = ask_model(messages, Review_Out, self.log)
        try:
            self.review = Review_Out.model_validate_json(reply)
        except ValidationError as e:
            return {'error': f'The reviewer returned invalid JSON: {e}'}
        return self.review.model_dump()

    # ---- Run one tool call that the model asked for -------------------- #
    def call_tool(self, call):
        name = call['function']['name']
        arguments = json.loads(call['function']['arguments'] or '{}')

        function = self.tools.get(name)
        if function is None:
            return {'error': f'Unknown tool {name}. Available tools: {list(self.tools)}'}
        try:
            return function(**arguments)
        except TypeError as e:
            return {'error': f'Bad arguments for {name}: {e}'}

    # ---- The agent loop ------------------------------------------------ #
    def run(self, user_question):
        # Start from a clean state for this question.
        self.user_question = user_question
        self.dataset_name = None
        self.chart = None
        self.chart_code = None
        self.chart_desc = None
        self.review = None
        self.reviews = 0

        messages = [
            {'role': 'system', 'content': agent_instructions()},
            {'role': 'user', 'content': user_question},
        ]
        for message in messages:
            self.log(message)

        for step in range(MAX_STEPS):
            reply = ask_model_with_tools(messages)
            messages.append(reply)
            self.log(reply)

            # No tool calls means the model is done and is talking to the user.
            if 'tool_calls' not in reply:
                break

            # Run every tool the model asked for and send the results back.
            for call in reply['tool_calls']:
                result = self.call_tool(call)
                tool_message = {'role': 'tool', 'tool_call_id': call['id'], 'content': json.dumps(result)}
                messages.append(tool_message)
                self.log(tool_message)

        if self.chart is None:
            return {'status': 'error', 'message': reply['content'] or 'No chart was produced.'}

        return {
            'status': 'success',
            'dataset': self.dataset_name,
            'chart_obj': self.chart,
            'chart_code': self.chart_code,
            'chart_desc': self.chart_desc or reply['content'],
            'review': self.review.feedback if self.review else None,
        }


if __name__ == '__main__':
    import sys
    # python vis_agent.py "your question"  (with no question, runs one sample per dataset and one off-topic question)
    questions = sys.argv[1:] or [
        'Which states had the highest mean departure delay on days with lightning?',   # airport_days
        'Which airline has the highest cancellation rate on storm days?',             # flights
        'How did flu activity change in Texas in 2025?',                              # cannot be answered
    ]
    agent = VisAgent()
    for user_question in questions:
        response = agent.run(user_question)
        print('QUESTION:', user_question)
        print('RESULT:', response['status'], response.get('dataset') or response.get('message'))
        print()