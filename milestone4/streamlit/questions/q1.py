import altair as alt
import streamlit as st

from data import footnote, load_fused

st.title('Lightning and Departure Delay')
st.markdown("#### Question 1: How does the daily volume of lightning near an airport relate to that airport's mean departure delay?")
st.write('An airport-day is one airport on one day in June 2026. For each airport-day, we count the lightning strikes '
         'in the 0.1° tile around the airport (about 11 x 9 km) and put the count into one of five levels.')

fused = load_fused()


def lightning_level(n):
    if n == 0:
        return '0'
    if n <= 10:
        return '1-10'
    if n <= 50:
        return '11-50'
    if n <= 200:
        return '51-200'
    return '200+'


level_order = ['0', '1-10', '11-50', '51-200', '200+']
fused['lightning_level'] = fused['lightning_count'].apply(lightning_level)

q1 = fused.groupby('lightning_level').agg(
    airport_days=('mean_dep_delay', 'size'),
    mean_dep_delay=('mean_dep_delay', 'mean'),
    cancel_rate=('cancel_rate', 'mean')
).reset_index()
q1['delay_label'] = q1['mean_dep_delay'].round(1).astype(str)

# click a bar to filter the scatter plot
level_select = alt.selection_point(fields=['lightning_level'])
level_colors = alt.Scale(domain=level_order, scheme='orangered')

bars = alt.Chart(q1).mark_bar().encode(
    alt.X('lightning_level:O', title='Lightning strikes in the airport tile that day', sort=level_order, axis=alt.Axis(labelAngle=0)),
    alt.Y('mean_dep_delay:Q', title='Mean departure delay (min)'),
    alt.Color('lightning_level:O', scale=level_colors, legend=None),
    opacity=alt.condition(level_select, alt.value(1.0), alt.value(0.3)),
    tooltip=['lightning_level', 'airport_days',
             alt.Tooltip('mean_dep_delay:Q', format='.1f'), alt.Tooltip('cancel_rate:Q', format='.1%')]
).add_params(level_select)
labels = alt.Chart(q1).mark_text(dy=-8).encode(
    alt.X('lightning_level:O', sort=level_order),
    alt.Y('mean_dep_delay:Q'),
    text='delay_label'
)
bar_chart = (bars + labels).properties(
    title='Departure Delays Quadruple as Lightning at the Airport Increases',
    width=400,
    height=300
)

days = alt.Chart(fused).mark_circle(size=30, opacity=0.5).encode(
    alt.X('lightning_count:Q', title='Lightning strikes in airport tile'),
    alt.Y('mean_dep_delay:Q', title='Mean departure delay (min)'),
    alt.Color('lightning_level:O', scale=level_colors, legend=None),
    tooltip=['origin', 'flight_date', 'lightning_count', alt.Tooltip('mean_dep_delay:Q', format='.1f')]
).transform_filter(level_select).properties(
    title='Every Airport-Day in the Selected Level',
    width=400,
    height=300
)

st.altair_chart(bar_chart | days, width='content')
st.caption('The bar chart shows the mean delay at each lightning level, and the scatter plot shows every airport-day. '
           'Hover over a bar to see how many airport-days it averages. Click a bar to show only that level in the '
           'scatter plot, and double-click an empty spot in a chart to show all levels again.')

with st.expander('View the data for the bar chart'):
    st.dataframe(q1.drop(columns='delay_label'), hide_index=True, width='stretch')
with st.expander('View the data for the scatter plot'):
    st.dataframe(fused[['flight_date', 'origin', 'lightning_count', 'lightning_level', 'mean_dep_delay']],
                 hide_index=True, width='stretch')

footnote()
