import json

import streamlit as st

from data import footnote

st.title('Ask Your Own Question')
st.markdown('The Vis Agent answers a question about our data with a chart that it writes itself. It can use two datasets, '
            'both for June 2026:')
st.markdown('- **airport_days**: one row per airport per day, with delays, cancellations, delay causes, and the '
            'lightning and hail counts near the airport.\n'
            '- **flights**: one row per domestic flight, with airline, destination, departure hour, delays, '
            'cancellations, and the weather at the origin airport that day.')
st.markdown('Ask one question at a time and name what you want to compare. For example:\n'
            '- *Which states had the highest mean departure delay on days with lightning?*\n'
            '- *How does the cancellation rate on storm days compare across airlines?*\n\n'
            'The agent cannot answer questions about other months, other countries, or topics outside flights and storms.')

try:
    from vis_agent import VisAgent, MODEL_NAME
except RuntimeError as e:   # GOOGLE_API_KEY is not set
    st.error(f'The agent is not available: {e}')
    st.stop()


def show_message(message):
    '''
    Show one message of the agent's conversation in the page.
    VisAgent calls this function every time a message is added to the
    conversation, instead of printing it to the terminal.
    '''
    role = message['role']

    if role == 'system':
        st.markdown('**System prompt**')
        st.code(message['content'], language=None, wrap_lines=True, height=150)

    elif role == 'user':
        st.markdown(f"**User:** {message['content']}")

    elif role == 'assistant':
        if message.get('content'):
            st.markdown(f"**Model:** {message['content']}")
        for call in message.get('tool_calls', []):
            name = call['function']['name']
            arguments = json.loads(call['function']['arguments'] or '{}')
            st.markdown(f'🔧 **Model calls** `{name}`')
            if 'chart_code' in arguments:
                st.code(arguments['chart_code'], language='python')   # code is easier to read than JSON
            elif arguments:
                st.json(arguments)

    elif role == 'tool':
        st.markdown('↩️ **Tool result**')
        st.json(message['content'], expanded=1)   # show the top level only: some results are long


user_question = st.chat_input('Ask a question about storms and flight delays in June 2026')

if user_question:
    st.markdown(f'#### **Question:** {user_question}')

    # Everything the agent logs while it works goes inside this status box.
    with st.status('Working on your question...', expanded=True) as status:
        va = VisAgent(log=show_message)
        resp = va.run(user_question)
        status.update(label='Done. Expand to see how the model used its tools.', state='complete', expanded=False)

    st.space()

    if resp['status'] == 'success':
        st.markdown(f"**Dataset used:** `{resp['dataset']}`")

        st.altair_chart(resp['chart_obj'])
        st.space()

        st.markdown(resp['chart_desc'])
        st.space()

        st.markdown('**Code behind this visualization**')
        st.code(resp['chart_code'], language='python')

        st.caption(f'Source: This visualization, description, and code were AI generated with {MODEL_NAME}.')

    else:
        # The agent could not answer: show its explanation in place of the chart.
        st.warning(resp['message'])

footnote()
