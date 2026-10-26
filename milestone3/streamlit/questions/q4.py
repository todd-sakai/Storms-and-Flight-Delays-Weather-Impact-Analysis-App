import altair as alt
import pandas as pd
import streamlit as st

from data import footnote, load_fused, weather_order

st.title('Delay Causes on Storm Days')
st.markdown('#### Question 4: How do the five delay causes shift in composition on days with severe weather versus clear days?')
st.write('Airlines assign delay minutes to five causes: the carrier, weather, the national aviation system (NAS), '
         'security, and a late-arriving aircraft. We sum the minutes of each cause by the weather at the airport, '
         'then divide by the number of scheduled flights. This makes weather types with few days comparable to clear days.')

fused = load_fused()
causes = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']

q4_wide = fused.groupby('weather').agg(
    flights=('n_flights', 'sum'),
    carrier_delay=('carrier_delay', 'sum'),
    weather_delay=('weather_delay', 'sum'),
    nas_delay=('nas_delay', 'sum'),
    security_delay=('security_delay', 'sum'),
    late_aircraft_delay=('late_aircraft_delay', 'sum')
).reset_index()

# Altair needs one row per (weather, cause): make one small data frame per cause and stack them vertically
parts = []
for cause in causes:
    parts.append(pd.DataFrame({'weather': q4_wide['weather'],
                               'cause': cause.replace('_delay', '').replace('_', ' '),
                               'minutes_per_flight': q4_wide[cause] / q4_wide['flights']}))
q4 = pd.concat(parts)
q4_totals = q4.groupby('weather').agg(total=('minutes_per_flight', 'sum')).reset_index()
q4_totals['total_label'] = q4_totals['total'].round(1).astype(str)

# click a cause in the legend to highlight it
cause_select = alt.selection_point(fields=['cause'], bind='legend')
cause_colors = alt.Scale(domain=['weather', 'late aircraft', 'nas', 'carrier', 'security'],
                         range=['#c03d3e', '#1f4e79', '#9db4c8', '#c9c9c9', '#e8e8e8'])
bars = alt.Chart(q4).mark_bar().encode(
    alt.Y('weather:N', title=None, sort=weather_order),
    alt.X('minutes_per_flight:Q', title='Delay minutes per scheduled flight'),
    alt.Color('cause:N', title='Cause', scale=cause_colors),
    opacity=alt.condition(cause_select, alt.value(1.0), alt.value(0.2)),
    tooltip=['weather', 'cause', alt.Tooltip('minutes_per_flight:Q', format='.2f')]
).add_params(cause_select)
totals = alt.Chart(q4_totals).mark_text(dx=16).encode(
    alt.Y('weather:N', sort=weather_order),
    alt.X('total:Q'),
    text='total_label'
)
stacked = (bars + totals).properties(
    title='On Lightning-and-Hail Days, Late Aircraft Add More Delay than the Storm Itself',
    width=500,
    height=200,
    autosize='pad'
)

st.altair_chart(stacked, width='content')
st.caption('Each bar is one type of weather at the airport, split into the five delay causes, with its total at the end. '
           'Hover over a segment to see its minutes per flight. Click a cause in the legend to highlight it in every '
           'bar, and double-click an empty spot in the chart to show all causes again.')

with st.expander('View the data for the stacked bar chart'):
    st.dataframe(q4, hide_index=True, width='stretch')

footnote()
