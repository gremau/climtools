import os
import pandas as pd

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

def get_filename(dataset, varname, stationid = 'all',
        basepath = default_basepath):
    """
    Function to get the correct filename for a variable/version/path
    Possible versions = 'latest' and '2014'
    Possible varnames = 'prcp', 'tavg', 'tmax', and 'tmin'
    """
    if not isinstance(stationid, list):
        stationid = [stationid]
    if dataset == 'latest':
        fdir = os.path.join(basepath,'ushcn.v2.5.5.20210118')
        files = os.listdir(fdir)
        varfiles = [f for f in files if varname in f]
        if stationid[0] is not 'all':
            varfiles = [f for f in varfiles if any(s in f for s in stationid)]

        if stationid is None:
            raise ValueError('Missing parameter - Provide a valid USHCN ' +
                    'station ID.')
        #fname = stationid + '.FLs.52j.' + varname
        fpath = [os.path.join(fdir, f) for f in varfiles]

    elif dataset == '2014':
        fname = 'ushcn2014_FLs_52j_' + varname + '.txt'
        fpath = os.path.join(basepath, pathname, fname)
    
    #print(fpath)
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

def station_subset(ushcn_df, staid):
    """
    Drop all rows except for given staion
    """
    out = ushcn_df.loc[staid, :]
    return(out)


def dropflags(ushcn_df):
    """
    Drop the flag columns
    """
    out = ushcn_df.loc[:, ['1','2','3','4','5','6','7','8',
        '9','10','11','12','ann']]
    return(out)

def load_2014(fname):
    widths = [11,5,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3]
    ushcn2014 = pd.read_fwf(fname, na_values=['-9999'], header=None,
            widths=widths,
            names=['1','janflag','2','febflag','3','marflag','4',
                'aprflag','5','mayflag','6','junflag','7','julflag',
                '8','augflag','9','sepflag','10','octflag','11',
                'novflag','12','decflag','ann','annflag'])
    return(ushcn2014)

def load_latest(fnames):
    widths = [11,5,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3]
    for i, fname in enumerate(fnames):
        latest = pd.read_fwf(fname, na_values=['-9999'], header=None,
                widths=widths,
                names=['1','janflag','2','febflag','3','marflag','4',
                    'aprflag','5','mayflag','6','junflag','7','julflag',
                    '8','augflag','9','sepflag','10','octflag','11',
                    'novflag','12','decflag','ann','annflag'])
        #print(i)
        if i==0:
            latest_out = latest
        else:
            latest_out = pd.concat([latest_out, latest])
            
    return(latest_out)


def get_var(varname, staid='all', dataset='latest', basepath=default_basepath,
        drop_flags=True, to_mm=True):
    """
    Get USHCN variable
    """
    fname = get_filename(dataset, varname, staid)
    #print(fname)
    if dataset=='latest':
        df = load_latest(fname)
    elif dataset=='2014':
        df = load_2014(fname)

    #if staid is not 'all':
    #    df = station_subset(df, staid)
    #if drop_flags:
    #    df = dropflags(df)
    #if to_mm:
    #    df = (df/100)*25.4

    return(df)

def get_tavg(basepath=default_basepath, staid=None, drop_flags=True,
        to_cels=True):
    """
    Get USHCN average temp
    """
    fname = os.path.join(basepath,'ushcn2014_FLs_52i_tavg.txt',
            'ushcn2014_FLs_52i_tavg.txt')
    widths = [11,5,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3]
    ushcn_tavg = pd.read_fwf(fname, na_values=['-9999'], header=None,
            widths=widths,
            names=['1','janflag','2','febflag','3','marflag','4',
                'aprflag','5','mayflag','6','junflag','7','julflag',
                '8','augflag','9','sepflag','10','octflag','11',
                'novflag','12','decflag','ann','annflag'])
    if staid is not None:
        ushcn_tavg = station_subset(ushcn_tavg, staid)
    if dropflags:
        ushcn_tavg = dropflags(ushcn_tavg)
    if to_cels:
        ushcn_tavg = ((ushcn_tavg/10)-32)*(5/9)

    return(ushcn_tavg)

def reshape_ts(ushcn_ts, staid, varname):
    """
    Reshape a standard ushcn table with a year index and month columns. Returns
    a long-form timeseries table
    """
    ushcn_ts['year'] = ushcn_ts.index
    #slp2.melt(id_vars=['year'],value_vars=slp2.columns, ignore_index=False)
    df = ushcn_ts.melt(id_vars=['year'], value_vars=ushcn_ts.columns[:-2],
            var_name='month')
    df['day'] = 1
    df['station'] = staid
    df['variable'] = varname
    df.index = pd.to_datetime(df.year.map(str) + df.month.map(str) + 
            df.day.map(str), format='%Y%m%d')
    df.day = df.index.days_in_month
    df.index = pd.to_datetime(df.year.map(str) + df.month.map(str) +
            df.day.map(str), format='%Y%m%d')
    df = df.sort_index()
    return(df.iloc[:,[4,5,0,1,3,2]])



