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
    # only load the columns we use
    flights = pd.read_parquet(f'{BUCKET}/processed/flights_clean.parquet',
                              columns=['airline', 'dep_delay', 'cancelled', 'cancellation_code']).reset_index()
    flights['origin'] = flights['origin'].astype(str)
    fused = load_fused()
    flights = flights.merge(fused[['flight_date', 'origin', 'weather']], on=['flight_date', 'origin'], how='inner')
    flights['storm'] = flights['weather'] != 'clear'
    return flights


def footnote():
    st.divider()
    st.caption('Sources: U.S. Bureau of Transportation Statistics, Reporting Carrier On-Time Performance, June 2026. '
               'NOAA National Centers for Environmental Information, Severe Weather Data Inventory '
               '(NLDN lightning tiles and NEXRAD hail tiles), June 2026. OurAirports, airport locations.')
