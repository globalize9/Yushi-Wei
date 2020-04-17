# rm(list = ls())
library(data.table)

# Obtain data from CRSP
crsp = data.table(read.csv("CRSP_Stocks.csv"))
crsp[,date := as.Date(as.character(crsp$date), format = "%Y/%m/%d")]
# crsp$date = anydate(crsp$date) # same effect as above
crsp = crsp[,c("PERMNO","date","SHRCD","EXCHCD","RET","DLRET","PRC","SHROUT")]
# if full data, run the above line to subset to desired

clean_data = function(crsp) {
  setkey(crsp, PERMNO, EXCHCD)
  # subsetting the crsp data common shares
  dt = crsp[SHRCD == 10 | SHRCD == 11]
  # subsetting to exchange codes
  dt = dt[EXCHCD == 1| EXCHCD == 2| EXCHCD == 3] 
  
  dt[,HRET := as.numeric(as.character(RET))]
  dt[,DRET := as.numeric(as.character(DLRET))]
  dt[,c('DLRET','RET')] = NULL
  
  # calculating the cumulative dividend total returns
  # by replacing the NAs with 1 in holding and delisting returns
  dt[, RET := ifelse(is.na(DRET), HRET, ifelse(!is.na(HRET), (HRET+1) * (DRET+1) - 1, NA))]
  dt = dt[!is.na(RET)]
  # below is the long hand way to take care of the 3 conditions for cum div return 
  # dt[, HRET := HRET + 1]
  # dt[, DRET := DRET + 1]
  # dt[,c("HRET", "DRET")][is.na(dt[,c("HRET", "DRET")])] = 1
  # dt[, RET := HRET * DRET - 1]
  # HRET and DRET both NA's -> remove
  dt = dt[!is.na(dt$HRET) | !is.na(dt$DRET)]
  
  summary(dt$RET) # check for how the data looks 
  head(sort(dt$PRC)) # we see that there is negative price per share
  
  # testing the statistics in negative price per share
  tt = dt[which((dt$PRC < 0))]
  summary(tt$RET*100)
  
  dt[, MKTCAP := abs(PRC)*SHROUT/1000]
  # Filtering out for NA PRC, this implicitly filters out NAs in MKTCAP as well
  dt = dt[!is.na(PRC)]
  
  ### Those actually makes the correlation worse
  #dt = dt[RET != 0 ] & SHROUT > 0 & MKTCAP > 0]
  summary(dt)
  setkey(dt, PERMNO, date)
  
  dt[, totalCAP := sum(MKTCAP), by = date]
  ## dt[, Stock_lag_MV := shift(totalCAP), by = date] # HMMM THIS DOESN'T WORK....
  dt[, lagMKTCAP := shift(MKTCAP), by = PERMNO]
  
  # lagging the securities' market cap and total market cap by t-1
  temp = dt[, sum(MKTCAP), by = date]
  setkey(temp, date)
  temp[, Stock_lag_MV := shift(V1)]
  temp$V1 = NULL
  dt = merge(dt, temp)
  setkey(dt, PERMNO, date)
  
  # check those values for lagged
  dt[date %between% c("2002-10-30", "2010-01-01")]
  
  dt[, mkt_wt := lagMKTCAP/Stock_lag_MV, by = date]
  # dt[, lengthday := .N, by = date] # this is same as length() 
  dt[, Stock_Ew_Ret := mean(RET), by = date]
  dt[, Stock_Vw_Ret := sum(na.omit(mkt_wt * RET)), by = date]
  
  dt[, Year := as.integer(format(date,"%Y"))]
  dt[, Month := as.integer(format(date, "%m"))]
  
  clean_dt = unique(dt, by = "date")
  clean_dt = clean_dt[,c("Year", "Month", "Stock_lag_MV","Stock_Ew_Ret","Stock_Vw_Ret")]
  setorder(clean_dt)
  return(clean_dt)
}
Monthly_CRSP_Stocks = clean_data(crsp)


# Obtaining Fama-French's Rf and vwretd
# Fama-French's data are monthly (i.e. not annualized, same as crsp from Question 1)
# pre-cleaning the data set to comply with requirements
FF_mkt = data.table(read.csv("F-F_Research_Data_Factors.CSV", skip = 3, header = TRUE, stringsAsFactors = FALSE))
colnames(FF_mkt) = c("date","Market_minus_Rf","SMB","HML","Rf")
date_position = which(grepl("201912", FF_mkt$date))
FF_mkt = FF_mkt[1:date_position]
FF_mkt[, Year := as.integer(substring(date,1,4))]
FF_mkt[, Month := as.integer(substring(date,5,6))]
FF_mkt[, names(FF_mkt) := lapply(.SD,as.numeric)] # converts the entire dataset to numeric
FF_mkt[, Year := as.integer(Year)]
FF_mkt[, Month := as.integer(Month)]
FF_mkt$date = NULL

fama_french = function(Monthly_CRSP_Stocks, FF_mkt){
  setkey(FF_mkt, Year, Month)
  setkey(Monthly_CRSP_Stocks, Year, Month)
  
  dt_monthly = merge(Monthly_CRSP_Stocks, FF_mkt)
  dt_monthly[, Rf := Rf/100]
  dt_monthly[, Market_minus_Rf := Market_minus_Rf/100]
  dt_monthly[, Ew_Rf := Stock_Ew_Ret - Rf]
  dt_monthly[, Vw_Rf := Stock_Vw_Ret - Rf]
  
  
  summaryM = matrix(data = 0, nrow = 5, ncol = 2)
  rownames(summaryM) = c("Annualized Mean", "Annualized Standard Deviation", "Annualized Sharpe Ratio",
                         "Excess Skewness", "Kurtosis")
  colnames(summaryM) = c("Replication", "French's")
  
  # Annualized statistics calculations
  summaryM["Annualized Mean",1] = mean(dt_monthly$Vw_Rf) * 12 
  summaryM["Annualized Mean",2] = mean(dt_monthly$Market_minus_Rf) * 12 
  
  summaryM["Annualized Standard Deviation",1] = sd(dt_monthly$Vw_Rf) * sqrt(12)
  summaryM["Annualized Standard Deviation",2] = sd(dt_monthly$Market_minus_Rf) * sqrt(12)
  
  summaryM["Annualized Sharpe Ratio",1] = sqrt(12) * mean(dt_monthly$Vw_Rf) / sd(dt_monthly$Vw_Rf) 
  summaryM["Annualized Sharpe Ratio",2] = sqrt(12) * mean(dt_monthly$Market_minus_Rf) / sd(dt_monthly$Market_minus_Rf)
  
  N = dim(dt_monthly)[1]
  summaryM["Excess Skewness",1] = sum((dt_monthly$Vw_Rf - mean(dt_monthly$Vw_Rf))^3) / N / sd(dt_monthly$Vw_Rf)^3 
  summaryM["Excess Skewness",2] = sum((dt_monthly$Market_minus_Rf - mean(dt_monthly$Market_minus_Rf))^3) / N / sd(dt_monthly$Market_minus_Rf)^3 
  
  summaryM["Kurtosis",1] = sum((dt_monthly$Vw_Rf - mean(dt_monthly$Vw_Rf))^4) / N / sd(dt_monthly$Vw_Rf)^4 - 3
  summaryM["Kurtosis",2] = sum((dt_monthly$Market_minus_Rf - mean(dt_monthly$Market_minus_Rf))^4) / N / sd(dt_monthly$Market_minus_Rf)^4 - 3
  
  summaryM = round(summaryM, digits = 4)
  return(summaryM)
}

summaryM = fama_french(Monthly_CRSP_Stocks, FF_mkt)



# Correlation and maximum difference calculation
corr_ff_rep = function(Monthly_CRSP_Stocks, FF_mkt){
  setkey(FF_mkt, Year, Month)
  setkey(Monthly_CRSP_Stocks, Year, Month)
  
  dt_monthly = merge(Monthly_CRSP_Stocks, FF_mkt)
  dt_monthly[, Rf := Rf/100]
  dt_monthly[, Market_minus_Rf := Market_minus_Rf/100]
  dt_monthly[, Ew_Rf := Stock_Ew_Ret - Rf]
  dt_monthly[, Vw_Rf := Stock_Vw_Ret - Rf]
  
  joint = dt_monthly[,c('Vw_Rf','Market_minus_Rf')]
  joint[, diff := Vw_Rf - Market_minus_Rf]
  corr_v = vector(length = 2)
  names(corr_v) = c("correlation", "max_abs_diff")
  corr_v[1] = cor(joint)[1,2]
  if (abs(max(joint$diff)) > abs(min(joint$diff)))
  {
    corr_v[2] = abs(max(joint$diff))
    } else
      {
        corr_v[2] = abs(min(joint$diff))
      }
  return(corr_v)
}

corr_ff_rep(Monthly_CRSP_Stocks, FF_mkt)


