import altair as alt
import streamlit as st

from data import footnote, load_fused

st.title('Delay That Travels')
st.markdown('#### Question 6: How far does weather disruption propagate through LateAircraftDelay to airports with no local severe weather?')
st.write('A late-aircraft delay happens when the plane for a flight arrives late from its previous flight. For each '
         'day, we measure the total lightning strikes across all airport tiles. We also measure the late-aircraft '
         'delay per flight at the airports that had no lightning or hail that day.')

fused = load_fused()

national = fused.groupby('flight_date').agg(
    lightning_total=('lightning_count', 'sum'),
    storm_airports=('storm', 'sum')
).reset_index()
dry = fused[fused['storm'] == False].groupby('flight_date').agg(
    late_aircraft=('late_aircraft_delay', 'sum'),
    dry_flights=('n_flights', 'sum')
).reset_index()

q6 = national.merge(dry, on='flight_date')
q6['late_aircraft_per_flight'] = q6['late_aircraft'] / q6['dry_flights']


def national_level(total):
    if total < 300:
        return 'Low (under 300 strikes)'
    if total < 600:
        return 'Medium (300-600)'
    return 'High (over 600)'


national_order = ['Low (under 300 strikes)', 'Medium (300-600)', 'High (over 600)']
q6['national_level'] = q6['lightning_total'].apply(national_level)
q6_levels = q6.groupby('national_level').agg(
    days=('flight_date', 'size'),
    late_aircraft_per_flight=('late_aircraft_per_flight', 'mean')
).reset_index()
q6_levels['label'] = q6_levels['late_aircraft_per_flight'].round(1).astype(str)

bars = alt.Chart(q6_levels).mark_bar().encode(
    alt.X('national_level:O', title='Lightning across all airport tiles that day', sort=national_order, axis=alt.Axis(labelAngle=0, labelLimit=200)),
    alt.Y('late_aircraft_per_flight:Q', title='Late-aircraft delay per flight (min)'),
    alt.Color('national_level:O', sort=national_order, scale=alt.Scale(scheme='blues'), legend=None),
    tooltip=['national_level', 'days', alt.Tooltip('late_aircraft_per_flight:Q', format='.2f')]
)
labels = alt.Chart(q6_levels).mark_text(dy=-8).encode(
    alt.X('national_level:O', sort=national_order),
    alt.Y('late_aircraft_per_flight:Q'),
    text='label'
)
level_chart = (bars + labels).properties(
    title='Storms Elsewhere Delay Airports That Stay Dry',
    width=450,
    height=300,
    autosize='pad'
)

st.altair_chart(level_chart, width='content')
st.caption('Each bar groups the days of June 2026 by the total lightning across all airport tiles. It shows the mean '
           'late-aircraft delay per flight at the airports with no storm that day. Hover over a bar to see how many '
           'days it averages.')

with st.expander('View the data for the bar chart'):
    st.dataframe(q6_levels.drop(columns='label'), hide_index=True, width='stretch')

footnote()
