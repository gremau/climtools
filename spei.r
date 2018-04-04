

library('SPEI')
library('xts')

get_cwdiff <- function(precip, pet){
    # Get climatic water difference from precip and pet data
    # precip: (xts object) monthly precipitation sums
    # pet   : (xts object) monthly potential ET sums
    cwdiff <- precip - pet
    return(cwdiff)
}

get_spei <- function(cwdiff, freq=12, int_per=6, plot=TRUE){
    # Get SPEI values from climatic water differential at given frequency and
    # integration period. Optionally make a plot of the data
    #
    # Default frequency is monthly (freq=12) but there may be ways to make
    # weekly frequency work (freq=52) if weekly PET is available.
    #
    # ---In---
    # cwdiff    : (xts obj) monthly climatic water differential time series
    # freq      : (int) frequency of cwdiff estimates (12=monthly, 52=weekly)
    # int_per   : (int) number of periods (weeks, months) used to calculate SPEI
    # plot      : (bool) Flag for making diagnostic plot of SPEI
    # ---Out---
    # spei_int  : (xts obj) spei time series at given integration period
    # spei_int_interp: (xts obj) spei_int with NA values interpolated over


    # Get start date
    startmon <- as.yearmon(index(cwdiff[1]))
    startyr <- floor(as.numeric(startmon))
    startmon <- as.numeric( format( startmon, '%m'))

    # Get spei for that integration period
    spei_int <- spei(ts(cwdiff, frequency=freq, start=c(startyr, startmon)),
                     int_per, na.rm=TRUE)

    # Check for invalid values
    values <- spei_int$fitted
    values[!is.finite(values)] <- NA
    if (sum(is.na(values)) > (int_per - 1)){
        print('WARNING!!! - there are invalid values in the SPEI series')
    }


    if (plot){
        plot(spei_int)
    }
    # Extract the spei values from the returned object and make xts
    #spei_xts <- xts(as.vector(spei_int$fitted),  order.by=index(cwdiff))
    
    
    # There may be both infinite and NA values in the output
    # Convert -Inf to NA
    #print(sum(is.na(spei_xts)))
    #spei_xts[!is.finite(spei_xts)] <- NA
    #print(sum(is.na(spei_xts)))
    
    # Interpolate over NA values
    #spei_xts_interp <- na.approx(spei_xts)

    return(spei_int)
}
