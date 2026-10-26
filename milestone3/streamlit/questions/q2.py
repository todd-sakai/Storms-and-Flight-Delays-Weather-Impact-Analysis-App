import altair as alt
import streamlit as st

from data import footnote, load_fused

st.title('Storm-Sensitive Airports')
st.markdown('#### Question 2: Which of the 351 airports show the strongest weather-delay sensitivity, and does that track their geography?')

fused = load_fused()

lightning_days = fused[fused['lightning_count'] > 0].groupby('origin').agg(
    storm_delay=('mean_dep_delay', 'mean'),
    lightning_days=('mean_dep_delay', 'size'))
other_days = fused[fused['lightning_count'] == 0].groupby('origin').agg(
    calm_delay=('mean_dep_delay', 'mean'),
    flights_per_day=('n_flights', 'mean'))
location = fused.groupby('origin').agg(state=('origin_state', 'first'), lat=('lat', 'first'), lon=('lon', 'first'))

q2 = lightning_days.join(other_days).join(location).reset_index()
q2 = q2[(q2['lightning_days'] >= 4) & (q2['flights_per_day'] >= 30)]
q2['sensitivity'] = q2['storm_delay'] - q2['calm_delay']

st.write("An airport's storm sensitivity is its mean departure delay on days with lightning in its 0.1° tile, minus its "
         'mean delay on days without lightning. We keep the airports with at least 4 lightning days and at least 30 '
         f'departures on an average day without lightning. This leaves {len(q2)} airports.')

state_select = alt.selection_point(fields=['state'])

points = alt.Chart(q2).mark_circle(stroke='gray').encode(
    alt.X('lon:Q', title='Longitude', scale=alt.Scale(domain=[-125, -66])),
    alt.Y('lat:Q', title='Latitude', scale=alt.Scale(domain=[24, 50])),
    alt.Size('flights_per_day:Q', title='Departures per day'),
    alt.Color('sensitivity:Q', title='Extra delay (min)', scale=alt.Scale(scheme='orangered')),
    opacity=alt.condition(state_select, alt.value(0.9), alt.value(0.15)),
    tooltip=['origin', 'state', alt.Tooltip('sensitivity:Q', format='.1f'), 'lightning_days',
             alt.Tooltip('flights_per_day:Q', format='.0f')]
).add_params(state_select)

top5 = q2.sort_values('sensitivity', ascending=False).head(5)
label_above = alt.Chart(top5[top5['origin'] != 'DAL']).mark_text(dy=-14, fontWeight='bold').encode(
    alt.X('lon:Q'), alt.Y('lat:Q'), text='origin')
label_right = alt.Chart(top5[top5['origin'] == 'DAL']).mark_text(align='left', dx=10, fontWeight='bold').encode(
    alt.X('lon:Q'), alt.Y('lat:Q'), text='origin')

map_chart = (points + label_above + label_right).properties(
    title='Texas Hubs Lose the Most Time to Lightning; Florida, with the Most Storm Days, Loses the Least',
    width=700,
    height=400,
    autosize='pad'
)

st.altair_chart(map_chart, width='content')
st.caption('Each circle is one airport, placed by its longitude and latitude. Circle size shows departures per day, '
           'and color shows storm sensitivity. Hover over a circle to see its numbers. Click a circle to highlight '
           'every airport in the same state, and double-click an empty spot in the chart to clear the highlight.')

with st.expander('View the data for the map'):
    st.dataframe(q2.sort_values('sensitivity', ascending=False), hide_index=True, width='stretch')

footnote()
