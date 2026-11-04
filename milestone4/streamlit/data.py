import pandas as pd
import streamlit as st

BUCKET = 'gs://cs329e-fusion-datasets'
weather_order = ['clear', 'lightning only', 'hail only', 'both']


def weather_type(row):
    if row['lightning_count'] > 0 and row['hail_count'] > 0:
        return 'both'
    if row['lightning_count'] > 0:
        return 'lightning only'
    if row['hail_count'] > 0:
        return 'hail only'
    return 'clear'


@st.cache_data
def load_fused():
    fused = pd.read_parquet(f'{BUCKET}/processed/fused.parquet').reset_index()
    fused['weather'] = fused.apply(weather_type, axis=1)
    fused['storm'] = fused['weather'] != 'clear'
    fused['origin'] = fused['origin'].astype(str)
    return fused


@st.cache_data
def load_flights():
    # only load the columns the pages and the agent use
    flights = pd.read_parquet(f'{BUCKET}/processed/flights_clean.parquet',
                              columns=['airline', 'dest', 'dep_time_blk', 'dep_delay', 'arr_delay', 'cancelled',
                                       'cancellation_code', 'diverted', 'distance', 'carrier_delay', 'weather_delay',
                                       'nas_delay', 'security_delay', 'late_aircraft_delay']).reset_index()
    flights['origin'] = flights['origin'].astype(str)
    fused = load_fused()
    flights = flights.merge(fused[['flight_date', 'origin', 'weather']], on=['flight_date', 'origin'], how='inner')
    flights['storm'] = flights['weather'] != 'clear'
    return flights


# Read by the agent's select_dataset tool to choose a dataset.
DATASET_DESCRIPTIONS = {
    'airport_days': (
        'One row is one origin airport on one day in June 2026 (2026-06-01 to 2026-06-30), 9,416 rows, 320 US origin airports. '
        'Joins BTS on-time flight data with NOAA lightning and hail counts in the 0.1-degree tile around the airport. '
        'Key columns: flight_date, origin (airport code), origin_state, lat, lon, n_flights (departures that day), '
        'mean_dep_delay and mean_arr_delay (minutes), cancel_rate and divert_rate (shares 0-1), '
        'carrier_delay, weather_delay, nas_delay, security_delay, late_aircraft_delay (total minutes that day by cause), '
        'lightning_count and hail_count (storm detections near the airport), '
        'weather (clear, lightning only, hail only, both) and storm (True if not clear). '
        'Use it for questions about airports, states, days, maps, and how storms relate to delays.'),
    'flights': (
        'One row is one domestic flight in June 2026 (2026-06-01 to 2026-06-30), about 589,000 rows, 12 airlines. '
        'From the BTS Reporting Carrier On-Time Performance data. '
        'Key columns: flight_date, origin and dest (airport codes), airline (two-letter carrier code), '
        'dep_time_blk (scheduled departure hour block), dep_delay and arr_delay (minutes, negative = early), '
        'cancelled, cancellation_code (A carrier, B weather, C national air system, D security), diverted, '
        'distance (miles), the five delay-cause columns in minutes, and weather / storm at the origin airport that day. '
        'Use it for questions about airlines, routes, time of day, distance, cancellations, or single flights. '
        'It is too large to plot row by row: aggregate it with pandas first.'),
}


@st.cache_data
def load_prepare_datasets():
    return {'airport_days': load_fused(), 'flights': load_flights()}


def footnote():
    st.divider()
    st.caption('Sources: U.S. Bureau of Transportation Statistics, Reporting Carrier On-Time Performance, June 2026. '
               'NOAA National Centers for Environmental Information, Severe Weather Data Inventory '
               '(NLDN lightning tiles and NEXRAD hail tiles), June 2026. OurAirports, airport locations.')
