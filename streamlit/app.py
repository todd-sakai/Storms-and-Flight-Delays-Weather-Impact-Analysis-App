import streamlit as st

q1 = st.Page("pages/q1.py", title="What did flu activity look like?")
q2 = st.Page("pages/q2.py", title="How does flu activity tend to vary?")

pg = st.navigation({"Single time series": [q1, q2]})

pg.run()