import altair as alt
import numpy as np
import streamlit as st

from data import footnote, load_fused

st.title('BTS Weather Delay vs Observed Storms')
st.markdown("#### Question 3: Does BTS's own WeatherDelay attribution agree with independently observed lightning and hail activity on the same date and location?")
st.write('Airlines report the cause of each delay to the Bureau of Transportation Statistics (BTS), and weather is one '
         'of five causes. For each airport-day, we compare two yes-or-no flags: did BTS record any weather-delay '
         "minutes, and did the airport's 0.1° tile have any lightning or hail.")

fused = load_fused()
fused['bts'] = np.where(fused['weather_delay'] > 0, 'BTS weather delay', 'No BTS weather delay')
fused['observed'] = np.where(fused['storm'], 'Lightning or hail in tile', 'No lightning or hail')

q3 = fused.groupby(['bts', 'observed']).agg(
    airport_days=('weather_delay', 'size'),
    minutes=('weather_delay', 'sum')
).reset_index()
row_totals = q3.groupby('bts').agg(row_total=('airport_days', 'sum')).reset_index()
q3 = q3.merge(row_totals, on='bts')
q3['row_share'] = q3['airport_days'] / q3['row_total']
q3['label'] = q3.apply(lambda row: f"{row['airport_days']:,} ({row['row_share']:.0%})", axis=1)

heat = alt.Chart(q3).mark_rect().encode(
    alt.X('observed:N', title='Observed in the airport tile', axis=alt.Axis(labelAngle=0, labelLimit=200)),
    alt.Y('bts:N', title='BTS attribution', axis=alt.Axis(labelLimit=200)),
    alt.Color('row_share:Q', title='Share of row', scale=alt.Scale(scheme='lighttealblue', domain=[0, 1])),
    tooltip=['bts', 'observed', 'airport_days', 'minutes']
)
text = alt.Chart(q3).mark_text(fontSize=14).encode(
    alt.X('observed:N'),
    alt.Y('bts:N'),
    text='label',
    color=alt.condition(alt.datum.row_share > 0.5, alt.value('white'), alt.value('black'))
)
matrix = (heat + text).properties(
    title='73% of Airport-Days with a BTS Weather Delay Had No Storm in the Airport Tile',
    width=420,
    height=220,
    autosize='pad'
)

st.altair_chart(matrix, width='content')
st.caption('Each row is what BTS recorded, and each column is what we observed in the airport tile on the same day. '
           'Each cell shows its number of airport-days and its share of the row, and a darker cell holds a larger '
           'share. Hover over a cell to see its weather-delay minutes.')

with st.expander('View the data for the matrix'):
    st.dataframe(q3.drop(columns='label'), hide_index=True, width='stretch')

footnote()
