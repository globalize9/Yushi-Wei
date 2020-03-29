rm(list = ls())
library(data.table)
# library(anytime) # did not use it

# The data used is obtained from the CRSP library, monthly stock returns 
# with parameters selected from the Data_Cleaning....pdf
crsp = data.table(read.csv("CRSP_Stocks.csv"))
crsp[,date := as.Date(as.character(crsp$date), format = "%Y/%m/%d")]
# crsp$date = anydate(crsp$date) # same effect as above

PS1Q1 = function(crsp) {
  setkey(crsp, PERMNO, EXCHCD)
  # subsetting the crsp data common shares
  dt = crsp[SHRCD == 10 | SHRCD == 11]
  # subsetting to exchange codes
  dt = dt[EXCHCD == 1| EXCHCD == 2| EXCHCD == 3] 
  
  dt[,HRET := as.numeric(as.character(RET))]
  dt[,DRET := as.numeric(as.character(DLRET))]
  dt[,c('DLRET','RET')] = NULL
  
  # HRET and DRET both NA's -> remove
  dt = dt[!is.na(dt$HRET) | !is.na(dt$DRET)]
  
  # calculating the cumulative dividend total returns
  # by replacing the NAs with 1 in holding and delisting returns
  dt[, HRET := HRET + 1]
  dt[, DRET := DRET + 1]
  dt[,c("HRET", "DRET")][is.na(dt[,c("HRET", "DRET")])] = 1
  dt[, RET := HRET * DRET - 1]
  summary(dt$RET) # check for how the data looks 
  head(sort(dt$PRC)) # we see that there is negative price per share
  
  # testing the statistics in negative price per share
  tt = dt[which((dt$PRC < 0))]
  summary(tt$RET*100)
  
  dt[, MKTCAP := abs(PRC)*SHROUT/1000]
  # Filtering out for NA PRC, this implicitly filters out NAs in MKTCAP as well
  dt = dt[!is.na(PRC)]
  dt = dt[RET != 0 & SHROUT > 0 & MKTCAP > 0]
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
  dt[date %between% c("2019-10-31", "2020-01-01")]
  
  dt[, mkt_wt := lagMKTCAP/Stock_lag_MV, by = date]
  # dt[, lengthday := .N, by = date] # this is same as length() 
  dt[, Stock_Ew_Ret := mean(RET), by = date]
  dt[, Stock_Vw_Ret := sum(na.omit(mkt_wt * RET)), by = date]
  
  dt[, Year := as.integer(format(date,"%Y"))]
  dt[, Month := as.integer(format(date, "%m"))]
  
  clean_dt = dt[,c("Year", "Month", "Stock_lag_MV","Stock_Ew_Ret","Stock_Vw_Ret")]
  return(clean_dt)
}

clean_dt = PS1Q1(crsp)
