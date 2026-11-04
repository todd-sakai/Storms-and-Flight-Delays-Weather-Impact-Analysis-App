import streamlit as st

st.set_page_config(page_title='Storms and Flight Delays', layout='wide')

q1 = st.Page('questions/q1.py', title='1. Lightning and delay', icon='⚡️')
q2 = st.Page('questions/q2.py', title='2. Storm-sensitive airports', icon='🛫')
q3 = st.Page('questions/q3.py', title='3. BTS weather delay vs storms', icon='⚖️')
q4 = st.Page('questions/q4.py', title='4. Delay causes', icon='📊')
q5 = st.Page('questions/q5.py', title='5. Hail vs lightning', icon='🧊')
q6 = st.Page('questions/q6.py', title='6. Delay that travels', icon='🔁')
q7 = st.Page('questions/q7.py', title='7. Carriers in storms', icon='✈️')
ask = st.Page('questions/ask.py', title='Ask your own question', icon='🤖')

pg = st.navigation({'Storms and Flight Delays': [q1, q2, q3, q4, q5, q6, q7], 'Vis Agent': [ask]})

pg.run()