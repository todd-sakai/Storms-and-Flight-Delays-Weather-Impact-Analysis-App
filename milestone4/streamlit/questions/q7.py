import altair as alt
import streamlit as st

from data import footnote, load_flights

st.title('Carriers in Storms')
st.markdown('#### Question 7: Which carriers absorb weather disruption best, controlling for their route geography?')
st.write('Carriers fly to different airports, so a raw comparison mixes the airline with its network. To control for '
         'geography, we compare each carrier with itself at the same airport. For every carrier-airport pair with at '
         'least 20 departures on storm days and 20 on clear days, we take the storm-day mean delay minus the clear-day '
         'mean delay. Then we average those differences for each carrier, weighted by the number of storm-day departures.')

flights = load_flights()
names = {'AA': 'American', 'AS': 'Alaska', 'B6': 'JetBlue', 'DL': 'Delta', 'F9': 'Frontier', 'G4': 'Allegiant',
         'MQ': 'Envoy', 'OH': 'PSA', 'OO': 'SkyWest', 'UA': 'United', 'WN': 'Southwest', 'YX': 'Republic'}
flights['airline'] = flights['airline'].astype(str)
flights['carrier'] = flights['airline'].map(names) + ' (' + flights['airline'] + ')'

storm_pairs = flights[flights['storm']].groupby(['carrier', 'origin']).agg(
    storm_delay=('dep_delay', 'mean'), storm_flights=('dep_delay', 'size')).reset_index()
clear_pairs = flights[flights['storm'] == False].groupby(['carrier', 'origin']).agg(
    clear_delay=('dep_delay', 'mean'), clear_flights=('dep_delay', 'size')).reset_index()

pairs = storm_pairs.merge(clear_pairs, on=['carrier', 'origin'])
pairs = pairs[(pairs['storm_flights'] >= 20) & (pairs['clear_flights'] >= 20)]
pairs['weighted_diff'] = (pairs['storm_delay'] - pairs['clear_delay']) * pairs['storm_flights']

q7 = pairs.groupby('carrier').agg(
    weighted_diff=('weighted_diff', 'sum'),
    storm_flights=('storm_flights', 'sum'),
    airports=('origin', 'size')
).reset_index()
q7['within_airport'] = q7['weighted_diff'] / q7['storm_flights']

# raw version: storm vs clear delay over all of a carrier's flights
raw = flights.groupby(['carrier', 'storm']).agg(delay=('dep_delay', 'mean')).reset_index()
raw_increase = raw[raw['storm']].merge(raw[raw['storm'] == False], on='carrier', suffixes=('_storm', '_clear'))
raw_increase['raw'] = raw_increase['delay_storm'] - raw_increase['delay_clear']
q7 = q7.merge(raw_increase[['carrier', 'raw']], on='carrier')

measure = st.radio('Compare each carrier', ['at the same airports', 'across all its airports (raw)'], horizontal=True)
if measure == 'at the same airports':
    column = 'within_airport'
    x_title = 'Extra departure delay on storm days at the same airports (min)'
    average = float(q7['weighted_diff'].sum() / q7['storm_flights'].sum())   # plain float, so Altair can write it into the chart
    title = f'SkyWest and JetBlue Absorb Storms Best; American and PSA Worst (Average {average:.1f} min)'
else:
    column = 'raw'
    x_title = 'Extra departure delay on storm days, all airports (min)'
    average = float(flights[flights['storm']]['dep_delay'].mean() - flights[flights['storm'] == False]['dep_delay'].mean())
    title = f'Raw Comparison, Which Mixes Each Carrier with Its Airports (Average {average:.1f} min)'

carrier_chart = alt.Chart(q7).mark_bar().encode(
    alt.Y('carrier:N', title=None, sort='x'),
    alt.X(f'{column}:Q', title=x_title),
    color=alt.condition(alt.datum[column] > average, alt.value('#c03d3e'), alt.value('#3b75af')),
    tooltip=['carrier', alt.Tooltip('within_airport:Q', format='.1f'), alt.Tooltip('raw:Q', format='.1f'),
             'airports', 'storm_flights']
).properties(
    title=title,
    width=500,
    height=320,
    autosize='pad'
)

st.altair_chart(carrier_chart, width='content')
st.caption('Each bar is one carrier. A red bar is above the all-carrier average, and a blue bar is below it. Use the '
           'buttons above the chart to switch between the same-airport comparison and the raw comparison. Hover over '
           'a bar to see both numbers and how many airports the same-airport number uses.')

with st.expander('View the data for the bar chart'):
    st.dataframe(q7.sort_values('within_airport'), hide_index=True, width='stretch')

footnote()
