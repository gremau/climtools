import os
import numpy as np
import pandas as pd
#import pdb

"""_summary_

Code for getting USHCN version 2.5 data and returning as pandas dataframes.

For more information on USHCN see here:

https://www.ncei.noaa.gov/products/land-based-station/us-historical-climatology-network

The USHCN version 2.5 data are available for download here:

https://www.ncei.noaa.gov/pub/data/ushcn/v2.5/

and should be downloaded to the local filesystem and then unzipped into one
directory. The `default_ushcn_path` is currently set to the development
machine (Greg's).

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
"""

default_ushcn_path = '/home/greg/data/rawdata/NCDC/ushcn_v2.5/ushcn.v2.5.5.20220705'
valid_vars = ['prcp', 'tavg', 'tmax', 'tmin']

def get_filename(varname, stationids='all',
                ushcn_path = default_ushcn_path):
    """
        Function to get the correct filename for a variable/version/path
    Possible versions = 'latest' and '2014'
    Possible varnames = 'prcp', 'tavg', 'tmax', and 'tmin'

    Parameters
    ----------
    varname : _type_
        _description_
    stationids : str, optional
        _description_, by default 'all'
    ushcn_path : _type_, optional
        _description_, by default default_ushcn_path

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    """
    # Create a list if needed and check for invalid variable names
    if not isinstance(stationids, list):
        stationids = [stationids]

    if varname not in valid_vars:
        raise ValueError('Not a valid variable type (select prcp, tavg, tmax, '
                + 'or tmin.)')

    # Fetch filenames from the dataset
    files = os.listdir(ushcn_path)
    varfiles = [f for f in files if varname in f]
    if 'all' not in stationids:
        varfiles = [f for f in varfiles if any(s in f for s in stationids)]
    
    fpath = [os.path.join(ushcn_path, f) for f in varfiles]
    
    return(fpath)


def get_stationsfile(ushcn_path = default_ushcn_path):
    """
    Get the station ID list. Note that the 2014 and latest versions of this
    file are basically the same, so using latest.
    """
    fname = os.path.join(os.path.dirname(ushcn_path), 'ushcn-v2.5-stations.txt')
    staid = pd.read_fwf(fname, header=None, 
            names=['id','lat','lon','elev','state','name','comp1','comp2',
                'comp3','utcoffset'])
    return(staid)

def station_subset(df, stationids):
    """
    Drop all rows except for given station
    """
    # Add to list if needed
    if not isinstance(stationids, list):
        stationids = [stationids]
    # Copy dataframe
    out = df.copy()
    if 'all' not in stationids:
        out = df.loc[df.stationid.isin(stationids), :]
    return(out)


def dropflags(df):
    """
    Drop the flag columns
    """
    out = df.loc[:,[c for c in df.columns if 'flag' not in c]]
    return(out)

def load_2014(fname):
    """
    Load file from 2014 dataset downloaded from CDIAC

    This is deprecated

    """
    cwidths = [11, 5] + ([6, 1, 1, 1] * 12)
    cnames = ['stationid','year',
            'jan', 'dmflag1', 'qcflag1', 'dsflag1',
            'feb', 'dmflag2', 'qcflag2', 'dsflag2',
            'mar', 'dmflag3', 'qcflag3', 'dsflag3',
            'apr', 'dmflag4', 'qcflag4', 'dsflag4',
            'may', 'dmflag5', 'qcflag5', 'dsflag5',
            'jun', 'dmflag6', 'qcflag6', 'dsflag6',
            'jul', 'dmflag7', 'qcflag7', 'dsflag7',
            'aug', 'dmflag8', 'qcflag8', 'dsflag8',
            'sep', 'dmflag9', 'qcflag9', 'dsflag9',
            'oct', 'dmflag10', 'qcflag10', 'dsflag10',
            'nov', 'dmflag11', 'qcflag11', 'dsflag11',
            'dec', 'dmflag12', 'qcflag12', 'dsflag12',
            'ann', 'dmflagann', 'qcflagann', 'dsflagann']
    print('Opening ' + fname)
    ushcn2014 = pd.read_fwf(fname, na_values=['-9999'], header=None,
            widths=cwidths, names=cnames)

    return(ushcn2014)

def load_latest(fnames):
    cwidths = [11, 1, 4] + ([6, 1, 1, 1] * 12)
    cnames = ['stationid', 'discard','year',
            'jan', 'dmflag1', 'qcflag1', 'dsflag1',
            'feb', 'dmflag2', 'qcflag2', 'dsflag2',
            'mar', 'dmflag3', 'qcflag3', 'dsflag3',
            'apr', 'dmflag4', 'qcflag4', 'dsflag4',
            'may', 'dmflag5', 'qcflag5', 'dsflag5',
            'jun', 'dmflag6', 'qcflag6', 'dsflag6',
            'jul', 'dmflag7', 'qcflag7', 'dsflag7',
            'aug', 'dmflag8', 'qcflag8', 'dsflag8',
            'sep', 'dmflag9', 'qcflag9', 'dsflag9',
            'oct', 'dmflag10', 'qcflag10', 'dsflag10',
            'nov', 'dmflag11', 'qcflag11', 'dsflag11',
            'dec', 'dmflag12', 'qcflag12', 'dsflag12']
    for i, fname in enumerate(fnames):
        print('Opening ' + fname)
        latest = pd.read_fwf(fname, na_values=["", "NA","-9999"], header=None,
                widths=cwidths, names=cnames)
        if i==0:
            latest_out = latest
        else:
            latest_out = pd.concat([latest_out, latest])
    # Drop the discard column
    latest_out = latest_out.drop(['discard'], axis=1)
    return(latest_out)


def get_monthly_var(varname, stationids='all',
        ushcn_path=default_ushcn_path, prep=True):
    """
    Get USHCN variable
    """
    fnames = get_filename(dataset, varname, stationids) 

    df = load_latest(fnames)

    # Drop flags and convert to long format
    if prep:
        df = dropflags(df)
        df = reshape_ts(df, varname)
        # Convert units
        if varname in valid_vars[1:4]:
            # Convert temps to degrees C (from hundredths)
            df.value = df.value/100
        elif varname in valid_vars[0:1]:
            # Convert precip to mm (from tenths)
            df.value = df.value/10

    return(df)


def reshape_ts(df, varname='variable'):
    """
    Reshape a standard ushcn table with a year index and month columns. Returns
    a long-form timeseries table
    """
    # Melt on staitionid and year
    df_out = df.melt(id_vars=['stationid', 'year'],
            value_vars=df.columns[2::],
            var_name='month')
    # Add a column naming the variable
    df_out['variable'] = varname
    # Create a day column set to 1, then create datetime column
    df_out['day'] = 1
    df_out['date'] = pd.to_datetime(df_out.year.map(str) + '-' + df_out.month + 
            '-' + df_out.day.map(str), format='%Y-%b-%d')
    # Get last day of month and create a new datetime column
    df_out.day = df_out.date.dt.days_in_month
    df_out.date = pd.to_datetime(df_out.year.map(str) + '-' + df_out.month +
            '-' + df_out.day.map(str), format='%Y-%b-%d')
    # Sort
    df_out = df_out.sort_values(by=['stationid', 'date'])
    # Out with sensible column order
    return(df_out.loc[:,['stationid', 'date', 'year', 'month', 'day',
        'variable', 'value']])
