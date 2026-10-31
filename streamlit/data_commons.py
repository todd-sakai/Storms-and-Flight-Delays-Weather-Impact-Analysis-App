import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def get_cdc_flu_trends_monthly_mean():    
    
    df = (
        pd.read_parquet('gs://data-vis-open-access/clean/cdc_flu_trends_monthly_mean.parquet')
        .reset_index()
    )
    
    df['year'] = df['weekend_date'].dt.year
    df['month_label'] = df['weekend_date'].dt.strftime('%b')
    df.name = 'cdc_flu_trends_monthly_mean'
    
    return df


def get_cdc_flu_trends_monthly_mappable():
    
    cdc_flu_trends = (
        pd.read_parquet('gs://data-vis-open-access/clean/cdc_flu_trends_clean_indexed.parquet')
        .reset_index()
    )

    cdc_flu_trends = cdc_flu_trends.rename(columns={'weekend_date': 'month'})

    state_info = pd.read_csv(
        'gs://data-vis-open-access/state_lat_long.tsv', 
        encoding='latin-1', 
        delimiter='\t',
        names=['state_code', 'latitude', 'longitude', 'state_name']
    )

    df = pd.merge(cdc_flu_trends, state_info, left_on='state', right_on='state_name')
    df = df[['month', 'state_code', 'latitude', 'longitude', 'activity_estimate']]
    df = df.rename(columns={'state_code': 'state', 'activity_estimate': 'cdc_activity_estimate'})
    df.name = 'cdc_flu_trends_monthly_mappable'
    
    return df


def get_cdc_google_trends():
    
    scaler = MinMaxScaler()
    
    df = pd.read_parquet('gs://data-vis-open-access/clean/cdc_google_trends.parquet')
    df[df.columns] = scaler.fit_transform(df[df.columns])
    df = df.reset_index()
    
    df = pd.melt(df, id_vars=['month'], var_name='metric', value_name='value')
    df['month'] = df['month'].dt.to_timestamp()
    df['year'] = df['month'].dt.year
    df.name = 'cdc_google_trends'
    
    return df


def load_prepare_datasets():
    
    datasets = {'cdc_flu_trends_monthly_mean': get_cdc_flu_trends_monthly_mean(),
                'cdc_flu_trends_monthly_mappable': get_cdc_flu_trends_monthly_mappable(),
                'cdc_google_trends': get_cdc_google_trends()}
    return datasets
