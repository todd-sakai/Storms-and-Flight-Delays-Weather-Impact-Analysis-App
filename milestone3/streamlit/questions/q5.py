import altair as alt
import streamlit as st

from data import footnote, load_flights, weather_order

st.title('Hail Days vs Lightning Days')
st.markdown('#### Question 5: Do hail days and lightning days produce different operational responses (cancellations versus delays)?')
st.write('This page works with single flights. Each flight gets the weather label of its origin airport on that day: '
         'clear, lightning only, hail only, or both.')

flights = load_flights()
flights['weather_cancel'] = flights['cancellation_code'] == 'B'   # B = cancelled for weather
q5 = flights.groupby('weather').agg(
    flights=('cancelled', 'size'),
    cancel_rate=('cancelled', 'mean'),
    weather_cancel_rate=('weather_cancel', 'mean'),
    mean_dep_delay=('dep_delay', 'mean')
).reset_index()

points = alt.Chart(q5).mark_circle(size=400).encode(
    alt.X('mean_dep_delay:Q', title='Mean departure delay (min)', scale=alt.Scale(domain=[10, 40])),
    alt.Y('cancel_rate:Q', title='Share of flights cancelled', axis=alt.Axis(format='%'), scale=alt.Scale(domain=[0, 0.07])),
    alt.Color('weather:N', sort=weather_order, scale=alt.Scale(scheme='tableau10'), legend=None),
    tooltip=['weather', 'flights', alt.Tooltip('cancel_rate:Q', format='.1%'),
             alt.Tooltip('weather_cancel_rate:Q', format='.1%'), alt.Tooltip('mean_dep_delay:Q', format='.1f')]
)
names = alt.Chart(q5[q5['weather'] != 'lightning only']).mark_text(align='left', dx=14, fontSize=12).encode(
    alt.X('mean_dep_delay:Q'), alt.Y('cancel_rate:Q'), text='weather')
lightning_name = alt.Chart(q5[q5['weather'] == 'lightning only']).mark_text(align='left', dx=10, dy=18, fontSize=12).encode(
    alt.X('mean_dep_delay:Q'), alt.Y('cancel_rate:Q'), text='weather')

scatter = (points + names + lightning_name).properties(
    title='Hail Alone and Lightning Alone Look Alike; Together They Cancel 6% of Flights',
    width=450,
    height=320,
    autosize='pad'
)

st.altair_chart(scatter, width='content')
st.caption('Each circle is one type of weather at the origin airport. It sits at the mean departure delay and the '
           'share of cancelled flights for all flights that left airports with that weather. Hover over a circle to '
           'see the number of flights and the share cancelled because of weather.')

with st.expander('View the data for the scatter plot'):
    st.dataframe(q5, hide_index=True, width='stretch')

footnote()
