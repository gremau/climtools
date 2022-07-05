import os
import pandas as pd
import requests
from io import StringIO
import pdb

# See here for possible API calls:
# https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation
#'https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-summary-of-the-year&dataTypes=TMAX,TMIN,TAVG,PRCP&stations=USC00267369&startDate=2017-01-01&endDate=2020-01-31&includeAttributes=true&format=csv'
# Other possible services here: https://www.ncei.noaa.gov/access
base_url = 'https://www.ncei.noaa.gov/access/services/data/v1'

def get_dailysummary(stationlist, startdt, enddt,
        varnames='TMAX,TMIN,TAVG,PRCP'):
    """
    Get GHCN-Daily data.

    https://doi.org/10.7289/V5D21VHZ
    """
    params = (
            ('dataset', 'daily-summaries'),
            ('dataTypes', varnames), 
            ('stations', stationlist),
            ('startDate', startdt),
            ('endDate', enddt),
            ('format', 'csv'),
            ('units', 'metric'),
            ('includeAttributes', False)
            )
    response = requests.get(base_url, params=params)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    return(df)


def get_monthlysummary(stationlist, startdt, enddt,
        varnames='TMAX,TMIN,TAVG,PRCP'):
    """
    Get Global Summary of the Month data. These are derived, in general
    from GHCN Daily data.

    https://doi.org/10.7289/V5QV3JJ5
    """
    params = (
            ('dataset', 'global-summary-of-the-month'),
            ('dataTypes', varnames), 
            ('stations', stationlist),
            ('startDate', startdt),
            ('endDate', enddt),
            ('format', 'csv'),
            ('units', 'metric'),
            ('includeAttributes', False)
            )
    response = requests.get(base_url, params=params)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    # Convert the year-month column to a monthly datetime (last day of month)
    # Create a day column set to 1, then create datetime column
    df['day'] = 1
    df['dt'] = pd.to_datetime(df.DATE + '-' + df.day.map(str), 
            format='%Y-%m-%d')
    # Get last day of month and create a new datetime column
    df.day = df.dt.dt.days_in_month
    df.dt = pd.to_datetime(df.DATE +
            '-' + df.day.map(str), format='%Y-%m-%d')
    df.DATE = df.dt
    df = df.loc[:,['STATION', 'DATE', 'PRCP', 'TAVG', 'TMAX', 'TMIN']]
    return(df)

def get_annualsummary(stationlist, startdt, enddt,
        varnames='TMAX,TMIN,TAVG,PRCP'):
    """
    Get Global Summary of the Year data. These data are derived, in general,
    from GHCN Daily data.

    https://doi.org/10.7289/JWPF-Y430
    """
    params = (
            ('dataset', 'global-summary-of-the-year'),
            ('dataTypes', varnames), 
            ('stations', stationlist),
            ('startDate', startdt),
            ('endDate', enddt),
            ('format', 'csv'),
            ('units', 'metric'),
            ('includeAttributes', False)
            )
    response = requests.get(base_url, params=params)
    data = StringIO(response.text)
    df = pd.read_csv(data)
    return(df)

def get_stationsfile(
        loc='https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt'
        ):
    """
    Get the station ID list for GHCN
    """
    inv = pd.read_fwf(loc, header=None, infer_nrows=1000,
            names=['id','lat','lon','elev','state','name', 'gsn_flag',
                'hcn_crn_flag','wmo_id'])

    return(inv)

def station_subset(ghcn_df, staid):
    """
    Drop all rows except for given station
    """
    out = ushcn_df.loc[staid, :]
    return(out)

def dropflags(ghcn_df):
    """
    Drop the flag columns
    """
    out = ushcn_df.loc[:, ['jan','feb','mar','apr','may','jun','jul','aug',
        'sep','oct','nov','dec','ann']]
    return(out)


