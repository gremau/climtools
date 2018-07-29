import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

def ts_anomaly( ser, window=None, norm=False, plot=False ) :
    """
    Take multiyear series and return an anomaly series of the distance
    from the multiyear mean for each observation.
    
    Args:
        ser (obj)   : a pandas series object with a timeseries index
        window (int): number of observations for a rolling window calcuation
        norm (bool) : if true normalize the anomaly by the mean (anom/mean)
        plot (bool) : if True make a simple plot comparing the original and
                      transformed data
        
    Return:
        ser_z (obj)  : a pandas series of z-scored values 
    """

    if window is None:
        ser_m = ser.mean()
    else:
        ser_m = ser.rolling(window=window, center=True,
                min_periods=round(0.3*window)).mean()
    # Calculate anomaly by subtracting mean
    anom = ser - ser_m
    if norm:
        anom = anom/ser_m
    
    if plot:
        plt.figure()
        anom.plot(label='Anomaly (window={0},\nnorm={1})'.format(
            str(window), str(norm)))
        ser.plot(label='Original series')
        plt.axhline(y=0, ls=':', c='k')
        plt.legend()
        plt.show()

    return anom

def ts_zscore( ser, window=None, plot=False ) :
    """
    Take a data series and return a z-score series indicating the number of
    standard deviations away from the mean.
    
    Args:
        ser (obj)   : a pandas series object with a timeseries index
        window (int): number of observations for a rolling window calcuation
        plot (bool) : if True make a simple plot comparing the original and
                      transformed data
        
    Return:
        ser_z (obj)  : a pandas series of z-scored values 
    """
    
    if window is None:
        ser_m = ser.mean(skipna=True)
        ser_sd = ser.std(skipna=True)
    else:
        ser_m = ser.rolling(window=window, center=True,
                min_periods=round(0.3*window)).mean()
        ser_sd = ser.rolling(window=window, center=True,
                min_periods=round(0.3*window)).std()
    # Calculate z score
    ser_z = ((ser - ser_m)/ser_sd)

    if plot:
        plt.figure()
        ser_z.plot(label='z-score (window={0})'.format(
            str(window)))
        ser.plot(label='Original series')
        plt.axhline(y=0, ls=':', c='k')
        plt.legend()
        plt.show()

    return ser_z


# Group days meeting a particular condition according to a specified
# duration. Contiguous "true" days >= duration are marked true
def condition_duration_match( condition, obs_duration ):
    # Use shift-compare-cumsum algorithm to group contiguous periods of
    # meeting or not meeting the condition (True or False in column)
    cgroup = (condition != condition.shift()).cumsum()
    # Count the number of contiguous observations in "True" cgroups
    cgroup_counts = cgroup[condition==True].value_counts()
    # Get the egroups with given duration or greater and 
    # find in original condition array
    true_duration_cgroups = cgroup_counts.index[cgroup_counts.values >= 
            obs_duration]
    condition_duration = np.in1d(cgroup, true_duration_cgroups)
    
    return condition_duration

# Get the start and end dates of a conditional array by year. Useful for
# determining growing seasons or suchlike
def get_condition_season( df, condition_col ):
    # Subset array to true values only using condition column
    df_true_cond = df.loc[ df[condition_col], [condition_col,] ].copy()
    # Duplicate the index into a new column, then group by year
    # and get first/last occurrence of true values in each year
    df_true_cond['season_date'] = df_true_cond.index
    startdates = df_true_cond.groupby(df_true_cond.index.year).first()
    enddates = df_true_cond.groupby(df_true_cond.index.year).last()
    # Put start and end dates in a dataframe
    new_df = pd.DataFrame( index=startdates.index )
    new_df['start_seas'] = startdates.season_date
    new_df['end_seas'] = enddates.season_date
    new_df['numdays'] = enddates.season_date - startdates.season_date
    
    return new_df

def array_pattern_match(array, pattern):
    """
    This is a simple matching algorithm that finds a small to medium pattern
    within an array. Can be used to find the start or end of boolean conditions
    defined by condition_duration_match.

    See [this SE question](https://stackoverflow.com/a/42493033)
    """
    m,n = len(array), len(pattern)
    # Get a list of array slices to match against
    idx = [np.s_[i:m-n+1+i] for i in range(n)]
    # Get a boolean array with a row containing matches for each
    # element in the pattern
    rowmatch = [array[idx[i]] == pattern[i] for i in range(n)]
    # Return boolean where match begins 
    match = np.all(rowmatch, axis=0)
    return match
