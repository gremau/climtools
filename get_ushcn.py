import os
import numpy as np
import pandas as pd
#import pdb

"""
Code for getting USHCN version 2.5 data and returning as pandas dataframes.
For more information on USHCN see here:
    https://www.ncdc.noaa.gov/ushcn/introduction
There are 2 available datasets on drive. The latest data come from the NCEI
(formerly NCDC) ftp site. Those data are labeled "latest" in the function 
parameters. I also have a 2014 dataset from the ORNL CDIAC archive (now 
transitioning to storage at ESS Dive). Those are labeled 2014.
"""

default_basepath = '/home/greg/data/rawdata/NCDC/ushcn_v2.5/'
valid_vars = ['prcp', 'tavg', 'tmax', 'tmin']

def get_filename(dataset, varname, stationids='all',
        basepath = default_basepath):
    """
    Function to get the correct filename for a variable/version/path
    Possible versions = 'latest' and '2014'
    Possible varnames = 'prcp', 'tavg', 'tmax', and 'tmin'
    """
    # Create a list if needed and check for invalid variable names
    if not isinstance(stationids, list):
        stationids = [stationids]
    if varname not in valid_vars:
        raise ValueError('Not a valid variable type (select prcp, tavg, tmax, '
                + 'or tmin.)')
    # Fetch filenames from the dataset
    if dataset == 'latest':
        fdir = os.path.join(basepath,'ushcn.v2.5.5.20220609')
        files = os.listdir(fdir)
        varfiles = [f for f in files if varname in f]
        if 'all' not in stationids:
            varfiles = [f for f in varfiles if any(s in f for s in stationids)]
        fpath = [os.path.join(fdir, f) for f in varfiles]

    elif dataset == '2014':
        fname = 'ushcn2014_FLs_52i_' + varname + '.txt'
        fpath = os.path.join(basepath, fname, fname)
    else:
        raise ValueError('Only "latest" and "2014" are accepted datasets.')
    
    return(fpath)


def get_stationsfile(basepath = default_basepath):
    """
    Get the station ID list. Note that the 2014 and latest versions of this
    file are basically the same, so using latest.
    """
    fname = os.path.join(basepath, 'ushcn-v2.5-stations.txt')
    staid = pd.read_fwf(fname, header=None, 
            names=['id','lat','lon','elev','state','name','comp1','comp2',
                'comp3','utcoffset'])
    return(staid)

def station_subset(df, stationids):
    """
    Drop all rows except for given staion
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
    Load file from 2014 dataset
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


def get_monthly_var(varname, stationids='all', dataset='latest',
        basepath=default_basepath, prep=True):
    """
    Get USHCN variable
    """
    fnames = get_filename(dataset, varname, stationids) 
    if dataset=='latest':
        df = load_latest(fnames)

    elif dataset=='2014':
        df = load_2014(fnames)
        df = station_subset(df, stationids)
        # Get rid of annual columns
        df = df.iloc[:,:-4]

    # Drop flags and convert to long format
    if prep:
        df = dropflags(df)
        df = reshape_ts(df, varname)
        # Convert units
        if dataset=='2014':
            if varname in valid_vars[1:4]:
                # Convert F temps to degrees C
                df.value = ((df.value/10)-32)*(5/9)
            elif varname in valid_vars[0:1]:
                # Convert in precip to mm
                df.value = (df.value/100)*25.4
        elif dataset=='latest':
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
