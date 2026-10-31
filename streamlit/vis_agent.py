'''
Visualization agent that uses Gemini through the OpenAI Python library.

It answers a user's question in two steps:
    1. Ask model which dataset (if any) can answer the question.
    2. Ask model to write Altair code for a chart. We run the code, and if it
       fails we send the error back to Gemini so it can fix its code.

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
from dataclasses import dataclass

import pandas as pd
import altair as alt
import logfire
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from data_commons import load_prepare_datasets

# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #

GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'
MODEL_NAME = 'gemini-3.1-flash-lite'
TEMPERATURE = 0.1
CODEGEN_RETRIES = 2   # how many extra tries Gemini gets to fix broken chart code

# --------------------------------------------------------------------------- #
# Connect to Gemini
# --------------------------------------------------------------------------- #

api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise RuntimeError('Missing environment variable GOOGLE_API_KEY')

# The OpenAI library talks to Gemini because we point it at Google's base_url.
client = OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)

# Send a trace of every call to Logfire (only if LOGFIRE_TOKEN is set).
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_openai(client)


# --------------------------------------------------------------------------- #
# The inputs to each step in the workflow
# Each dataclass groups the inputs for one step, so we can pass them around
# as a single object instead of a long list of arguments.
# --------------------------------------------------------------------------- #
@dataclass
class Dataset_Selector_In:
    schemas: dict   # column names and types of every dataset
    stats: dict     # summary statistics of every dataset
    samples: dict   # a few example rows from every dataset


@dataclass
class Vis_Designer_In:
    dataset_name: str
    schema: dict
    stats: dict
    sample: dict
    df: pd.DataFrame   # the data the chart code will use


# --------------------------------------------------------------------------- #
# The shape of the model's answers
# Each class describes the JSON we want back. The descriptions are sent to
# the model (Gemini) so it knows what to put in each field.
# --------------------------------------------------------------------------- #

class Dataset_Selector_Out(BaseModel):
    feasible: bool = Field(description="Is the user's question related to the available datasets and can it be answered by one of them?")
    reason: str = Field(description="A 1-3 sentence rationale for your decision.")
    selected_dataset: str | None = Field(description='The json key identifying the dataset you have chosen to answer the question. Return None if no dataset was chosen.')


class Vis_Designer_Out(BaseModel):
    chart_code: str | None = Field(description='Python executable code of your final Altair chart to be returned to the user. None if no code produced.')
    chart_desc: str = Field(description='A 1-3 sentence description of your final chart and what it represents without giving away the answer.')

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def ask_model(messages, answer_class):
    '''
    Send the conversation to model and return its reply as a JSON string.
    answer_class (one of the classes above) tells the model what JSON to return.
    '''
    
    print('*** calling completions.create ***')
    for message in messages:
        print(f"--- {message['role']} ---")
        print(message['content'])
        print()
    
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


def remove_code_fences(code):
    '''Remove the ```python ... ``` markers that models sometimes add around code.'''
    if code is None:
        return None
    return code.replace('```python', '').replace('```', '').strip()


def run_chart_code(code, df):
    '''
    Run the chart code that model wrote.
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

    return chart, ''


# --------------------------------------------------------------------------- #
# Step 1: decide whether the question can be answered, and with which dataset
# --------------------------------------------------------------------------- #

def dataset_selector_instructions(inputs):
    return (
        "You are an analyst who helps public health experts extract insights from public flu data. "
        "Given the user's question and available datasets, determine the feasibility "
        "of their question. To do so, first review the schema information, summary stats, "
        "and sample rows provided and then decide if at least one of the datasets can answer the user's question.\n"
        "If the user's question can be answered by visualizing at least one of the "
        "datasets in the collection, return the json key of the most relevant dataset.\n"
        "If the user's question is not related to any of the datasets or if no one dataset " 
        "can answer the user's question, return None instead.\n"
        f"The available datasets to choose from are: {json.dumps(inputs.schemas)}.\n"
        f"The summary stats for each dataset are: {json.dumps(inputs.stats)}. \n"
        f"Some sample records for each dataset are: {json.dumps(inputs.samples)}."
    )


def select_dataset(user_question, inputs):
    '''Ask model which dataset fits the question. Returns a Dataset_Selector_Out.'''
    messages = [
        {'role': 'system', 'content': dataset_selector_instructions(inputs)},
        {'role': 'user', 'content': user_question},
    ]
    reply = ask_model(messages, Dataset_Selector_Out)
    return Dataset_Selector_Out.model_validate_json(reply)


# --------------------------------------------------------------------------- #
# Step 2: write the chart code, run it, and let the model fix any errors
# --------------------------------------------------------------------------- #

def vis_designer_instructions(inputs):
    return (
        f"Analyze the user's question about the dataset {inputs.dataset_name} and create a visualization "
        "in Altair that would help answer the user's question. \n"
        "The data is available in a DataFrame named `df`.\n"
        f"The schema information is: {inputs.schema}. \n"
        f"Some summary stats for this dataset: {inputs.stats}. \n"
        f"A few sample rows: {inputs.sample}. \n"
        "Think carefully about your choice of marks and visual encodings. \n\n"
        "Here are a few more rules to follow:\n"
        "1. Don't label the x-axis when it encodes either states or dates. Otherwise, label it.\n"
        "2. Don't label the y-axis when it encodes either states or dates. Otherwise, label it.\n"
        "3. Prioritize blue and green colors over red, orange, and yellow colors.\n"
        "4. Include a tooltip, and format the numeric values shown in it to two decimal places.\n"
        "5. Only return executable Python code.\n"
        "6. Do NOT use plt.show().\n"
        "7. Do NOT save the json.\n"
        "8. Your code will be rendered by a downstream process in Streamlit.\n"
        "9. Assign the final chart to a variable named final_chart."
    )


def design_chart(user_question, inputs):
    '''
    Ask the model for the chart code and run it. If something goes wrong, show model
    the error and ask again, up to CODEGEN_RETRIES more times.
    Returns three values: (design, chart, error_message).
    On success error_message is ''. On failure design and chart are None.
    '''
    messages = [
        {'role': 'system', 'content': vis_designer_instructions(inputs)},
        {'role': 'user', 'content': user_question},
    ]
    error_message = ''

    for attempt in range(1 + CODEGEN_RETRIES):
        reply = ask_model(messages, Vis_Designer_Out)

        try:
            design = Vis_Designer_Out.model_validate_json(reply)
        except ValidationError as e:
            design = None
            error_message = 'Your reply did not match the required JSON format. Fix it:\n' + str(e)

        if design is not None:
            design.chart_code = remove_code_fences(design.chart_code)
            chart, error_message = run_chart_code(design.chart_code, inputs.df)
            if chart is not None:
                return design, chart, ''

        # Add model's reply and our error message to the conversation,
        # so on the next try, model can see what went wrong.
        messages.append({'role': 'assistant', 'content': reply or '(empty reply)'})
        messages.append({'role': 'user', 'content': error_message})

    return None, None, error_message


# --------------------------------------------------------------------------- #
# Run the end-to-end workflow
# --------------------------------------------------------------------------- #

class VisAgent:
    def __init__(self):
        self.datasets = load_prepare_datasets()

        # Short summaries of each dataset that we include in the prompts.
        self.schemas = {}
        self.stats = {}
        self.samples = {}
        for name, df in self.datasets.items():
            self.schemas[name] = df.dtypes.astype(str).to_dict()
            self.stats[name] = df.describe().astype(str).to_dict()
            self.samples[name] = df.sample(5).astype(str).to_dict()

    def run(self, user_question):
        # Step 1: pick a dataset
        selector_in = Dataset_Selector_In(schemas=self.schemas, stats=self.stats, samples=self.samples)
        try:
            selection = select_dataset(user_question, selector_in)
        except ValidationError as e:
            return {'status': 'error', 'message': f'Model returned an invalid dataset choice: {e}'}

        if not selection.feasible:
            return {'status': 'error', 'message': f'Request not feasible: {selection.reason}'}

        name = selection.selected_dataset
        if name not in self.datasets:
            return {'status': 'error', 'message': f'Model selected an unknown dataset: {name}'}

        # Step 2: make the chart
        designer_in = Vis_Designer_In(
            dataset_name=name,
            schema=self.schemas[name],
            stats=self.stats[name],
            sample=self.samples[name],
            df=self.datasets[name],
        )
        design, chart, error_message = design_chart(user_question, designer_in)
        if chart is None:
            return {
                'status': 'error',
                'message': 'Failed to generate valid code within retry limit.',
                'last_error': error_message,
            }

        return {
            'status': 'success',
            'dataset': name,
            'chart_obj': chart,
            'chart_code': design.chart_code,
            'chart_desc': design.chart_desc,
        }


if __name__ == '__main__':
    user_question = 'What is the relationship between the CDC data and the Google Trends data?'
    agent = VisAgent()
    response = agent.run(user_question)
    print('response:', response)
