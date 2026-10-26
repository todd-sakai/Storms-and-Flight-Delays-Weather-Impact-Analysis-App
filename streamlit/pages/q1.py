import streamlit as st
import pandas as pd
import altair as alt

st.title("Flu Activity Explorer")

st.write()

df = (
    pd.read_parquet('gs://data-vis-open-access/clean/cdc_flu_trends_monthly_mean.parquet')
    .reset_index()
)

highlight_condition = (alt.datum.weekend_date >= alt.expr.toDate('2008-07-01')) & \
                      (alt.datum.weekend_date < alt.expr.toDate('2010-07-01'))

chart = alt.Chart(df).mark_bar().encode(
    alt.X('weekend_date:T', title='Date'),
    alt.Y('activity_estimate:Q', title='Activity estimate', scale=alt.Scale(domain=(0, 5.2))),
    color = alt.condition(
        highlight_condition,
        alt.value('steelblue'),
        alt.value('lightgray')
    ),
    tooltip=[alt.Tooltip('weekend_date:T'),
             alt.Tooltip('activity_estimate:Q', format='.2f')]
).properties(
  title='Monthly mean CDC activity estimates'
)

peak_label_df = pd.DataFrame({
    'weekend_date': ['2009-03-01', '2009-10-01'],
    'activity_estimate': [4.26, 4.77],
    'label': ['March peak', 'October peak']
})

base = alt.Chart(peak_label_df).encode(
    alt.X('weekend_date:T'),
    alt.Y('activity_estimate:Q'),
    text='label:N'
)

# Positive dx moves text right, and positive dy moves it down,
march_label = base.transform_filter(
    alt.datum.label == 'March peak'
).mark_text(dy=-8, dx=-7, fontSize=9)  # left by 7 pixels

october_label = base.transform_filter(
    alt.datum.label == 'October peak'
).mark_text(dy=-8, fontSize=9)

final = (chart + march_label + october_label).properties(
    title='Flu activity peaks once every winter except in 2009',
    height=400 # hardcode the height because the default looks too short
)

st.altair_chart(final, width='stretch')

st.write()

with st.expander("View the underlying data"):
    st.dataframe(df, width="stretch")

st.caption("Source: U.S. CDC FluView surveillance — monthly mean activity estimate.")