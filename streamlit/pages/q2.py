import streamlit as st
import pandas as pd
import altair as alt

st.title("Flu Activity Explorer")
st.markdown(
    "#### How does flu activity tend to vary across an average flu season?"
)

df = (
    pd.read_parquet('gs://data-vis-open-access/clean/cdc_flu_trends_monthly_mean.parquet')
    .reset_index()
)

df['year'] = df['weekend_date'].dt.year

# Create a container for our two different views
base = alt.Chart(df).properties(width=350, height=200)

selection = alt.selection_point(fields=['year'])

bar = base.mark_bar().encode(
    alt.X('weekend_date:T', title='Date'),
    alt.Y('activity_estimate:Q', title='Activity Estimate'),
    #color = alt.condition(selection, 'year:O', alt.value('lightgray')), # legend default to right-hand-side
    color = alt.condition(selection, alt.Color('year:O').legend(orient='bottom', direction='horizontal', title=None), alt.value('lightgray')),
    tooltip=[alt.Tooltip('weekend_date:T'),
             alt.Tooltip('activity_estimate:Q', format='.2f')]
).add_params(selection)

line = base.mark_line().encode(
    alt.X('month(weekend_date):T', title='Month'),
    alt.Y('mean(activity_estimate):Q', title='Activity Estimate'),
    tooltip=[alt.Tooltip('month(weekend_date):T', title='Month'),
             alt.Tooltip('mean(activity_estimate):Q', title='Activity Estimate', format='.2f')]
).transform_filter(selection)

final = bar | line

st.altair_chart(final, width='content')

with st.expander("View the underlying data"):
    st.dataframe(df, width='stretch')

st.caption("Source: U.S. CDC FluView surveillance — monthly mean activity estimate.")