import os
import pandas as pd
import requests
from io import StringIO

# See here for possible API calls:
# https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation
#'https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-summary-of-the-year&dataTypes=TMAX,TMIN,TAVG,PRCP&stations=USC00267369&startDate=2017-01-01&endDate=2020-01-31&includeAttributes=true&format=csv'
# Other possible services here: https://www.ncei.noaa.gov/access
base_url = 'https://www.ncei.noaa.gov/access/services/data/v1'

# Get the version number of the newest revision on EDI
def get_dailysummary(stationlist, startdt, enddt,
        varnames='TMAX,TMIN,TAVG,PRCP'):
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
    return(df)

def get_annualsummary(stationlist, startdt, enddt,
        varnames='TMAX,TMIN,TAVG,PRCP'):
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

def get_stationsfile(basepath):
    """
    Get the station ID list
    """
    fname = os.path.join(basepath, 'ushcn-stations.txt')
    staid = pd.read_fwf(fname, header=None, 
            names=['id','lat','lon','elev','state','name','comp1','comp2',
                'comp3','utcoffset'])
    return(staid)

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


