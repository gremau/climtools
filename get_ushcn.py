import os
import pandas as pd

def get_stationsfile(basepath):
    """
    Get the station ID list
    """
    fname = os.path.join(basepath, 'ushcn-stations.txt')
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
    out = ushcn_df.loc[:, ['jan','feb','mar','apr','may','jun','jul','aug',
        'sep','oct','nov','dec','ann']]
    return(out)


def get_prcp(basepath, staid=None, drop_flags=True, to_mm=True):
    """
    Get USHCN precip
    """
    fname = os.path.join(basepath, 'ushcn2014_FLs_52i_prcp.txt',
            'ushcn2014_FLs_52i_prcp.txt')
    widths = [11,5,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3]
    ushcn_prcp = pd.read_fwf(fname, na_values=['-9999'], header=None,
            widths=widths,
            names=['jan','janflag','feb','febflag','mar','marflag','apr',
                'aprflag','may','mayflag','jun','junflag','jul','julflag',
                'aug','augflag','sep','sepflag','oct','octflag','nov',
                'novflag','dec','decflag','ann','annflag'])
    if staid is not None:
        ushcn_prcp = station_subset(ushcn_prcp, staid)
    if drop_flags:
        ushcn_prcp = dropflags(ushcn_prcp)
    if to_mm:
        ushcn_prcp = (ushcn_prcp/100)*25.4

    return(ushcn_prcp)

def get_tavg(basepath, staid=None, drop_flags=True, to_cels=True):
    """
    Get USHCN average temp
    """
    fname = os.path.join(basepath, 'ushcn2014_FLs_52i_tavg.txt')
    widths = [11,5,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3,6,3]
    ushcn_tavg = pd.read_fwf(fname, na_values=['-9999'], header=None,
            widths=widths,
            names=['jan','janflag','feb','febflag','mar','marflag','apr',
                'aprflag','may','mayflag','jun','junflag','jul','julflag',
                'aug','augflag','sep','sepflag','oct','octflag','nov',
                'novflag','dec','decflag','ann','annflag'])
    if staid is not None:
        ushcn_tavg = station_subset(ushcn_tavg, staid)
    if dropflags:
        ushcn_tavg = dropflags(ushcn_tavg)
    if to_cels:
        ushcn_tavg = ((ushcn_tavg/10)-32)*(5/9)

    return(ushcn_tavg)
