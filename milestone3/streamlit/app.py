import streamlit as st

st.set_page_config(page_title='Storms and Flight Delays', layout='wide')

q1 = st.Page('questions/q1.py', title='1. Lightning and delay')
q2 = st.Page('questions/q2.py', title='2. Storm-sensitive airports')
q3 = st.Page('questions/q3.py', title='3. BTS weather delay vs storms')
q4 = st.Page('questions/q4.py', title='4. Delay causes')
q5 = st.Page('questions/q5.py', title='5. Hail vs lightning')
q6 = st.Page('questions/q6.py', title='6. Delay that travels')
q7 = st.Page('questions/q7.py', title='7. Carriers in storms')

pg = st.navigation({'Storms and Flight Delays': [q1, q2, q3, q4, q5, q6, q7]})

pg.run()