import numpy as np
import pandas as pd
import pdb

def var_climatology( ser ) :
    """
    Take multiyear series and return a climatology dataset in which
    each year is separated into a column, and annual mean, std dev, std err,
    cv and other descriptive stats are calculated.
    
    Args:
        ser (obj)   : a pandas series object with a timeseries index
        
    Return:
        clim (obj)  : a pandas dataframe with year and descriptive columns 
    """

    # Create dataframes to hold raw year data and climatology calculations
    raw_years = pd.DataFrame( index = range( 1, 367 ))
    clim = raw_years.copy()
    # Put 1 day values for each year in a column
    for i in np.unique(ser.index.year):
        year_vals = ser[ ser.index.year==i ].values
        raw_years[ str(i) ] = np.nan
        pdb.set_trace()
        raw_years[ str(i) ][ 0:len(year_vals)] = year_vals
        clim[ str(i) ] = raw_years[ str(i) ]
    # Get summary stats each day of the year
    clim[ 'allyr_mean' ] = raw_years.mean(axis=1)
    clim[ 'allyr_stdev' ] = raw_years.std(axis=1)
    clim[ 'allyr_stderr' ] = clim.allyr_stdev / math.sqrt( 
            len(np.unique(ser.index.year))-1 )
    clim[ 'allyr_cv' ] = clim.allyr_stdev / clim.allyr_mean
    clim[ 'allyr_cv2' ] = clim.allyr_stdev / ser.mean()

    return clim


def climate_anomaly( ser, norm=False ) :
    """
    Take multiyear series and return an anomaly series of the distance
    from the multiyear mean for each observation.
    
    Args:
        ser (obj)   : a pandas series object with a timeseries index
        norm (bool) : if True, divide anomaly by mean to normalize
        
    Return:
        anom (obj)  : a pandas dataframe with year and descriptive columns 
    """

    # Calculate the anomaly of the original series
    # (subtract multiyear mean)
    anom = ser.copy()
    serclim = var_climatology( ser )
    for i in np.unique(ser.index.year):
        if norm:
            anom[ anom.index.year==i ] = ((ser[ ser.index.year==i ] -
                serclim.allyr_mean[0:len(ser[ ser.index.year==i ])].values) / 
                serclim.allyr_mean[0:len(ser[ ser.index.year==i ])].values)
        else:
            anom[ anom.index.year==i ] = (ser[ ser.index.year==i ] -
                    serclim.allyr_mean[0:len(ser[ ser.index.year==i ])].values)
            
    return anom

def ts_anomaly( ser, window='full', norm=False ) :
    """
    Take multiyear series and return an anomaly series of the distance
    from the multiyear mean for each observation.
    
    Args:
        ser (obj)   : a pandas series object with a timeseries index
        norm (bool) : if True, divide anomaly by mean to normalize
        
    Return:
        anom (obj)  : a pandas dataframe with year and descriptive columns 
    """

    # Calculate the anomaly of the original series
    # (subtract multiyear mean)
    if window is 'full':
        mov_avg = ser.mean()
    else:
        mov_avg = ser.rolling(window=window, center=True,
                min_periods=round(0.9*window)).mean() 
    anom = ser - mov_avg
    pdb.set_trace()
    if norm:
        anom_n = anom/mov_avg
        return anom_n
    else:
        return anom

def ts_z( ser, window='full', norm=False ) :
    """
    Take multiyear series and return an anomaly series of the distance
    from the multiyear mean for each observation.
    
    Args:
        ser (obj)   : a pandas series object with a timeseries index
        norm (bool) : if True, divide anomaly by mean to normalize
        
    Return:
        anom (obj)  : a pandas dataframe with year and descriptive columns 
    """

    # Calculate the anomaly of the original series
    # (subtract multiyear mean)
    if window is 'full':
        mov_avg = ser.mean()
    else:
        mov_avg = ser.rolling(window=window, center=True,
                min_periods=round(0.9*window)).mean() 
    anom = ser - mov_avg
    pdb.set_trace()
    if norm:
        anom_n = anom/mov_avg
        return anom_n
    else:
        return anom
