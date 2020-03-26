## Return Forecasting Regressions in R ##

library(anytime)
library(xts)
library(ggplot2)
library(DataAnalytics)
library(sandwich)

# data cleaning
mkt = read.csv("MonthlyMktCumandExDiv.csv") # skip = 2, header = TRUE
tbill = read.csv("MonthlyTbillAnnualizedYield.csv") 
ffm = read.csv("T10YFFM.csv")
aaaffm = read.csv("AAAFFM.csv")
baaffm = read.csv("BAAFFM.csv")

names(mkt)[1] = "date"
names(tbill)[2] = "date"
names(ffm)[1] = "date"
names(aaaffm)[1] = "date"
names(baaffm)[1] = "date"

mkt$date = anydate(mkt$date)
tbill$date = anydate(tbill$date)

mktxts = xts(mkt[,2:4], order.by = mkt$date) # x is excl div and t incl div
mktxts$divP = (mktxts$vwretd - mktxts$vwretx) * mktxts$spindx # in abs amount
tbillxts = xts(log(tbill$TMYTM/100+1), order.by = tbill$date)

mktxts$dp = NA
for (i in 13:length(mktxts$divP)){
  mktxts$dp[i] = sum(mktxts$divP[i:(i-12)])/mktxts$spindx[i]
}

mktxts$ex = (log(1+mktxts$vwretd) - tbillxts/12)  # monthly excess
# Cum dividend = including div
# Construct excess re-turns by subtracting the log of the 1-month gross t-bill rate 
# from the 1-month gross cum-dividends returns
mktxts$ts = xts(ffm$T10YFFM/100, order.by = mkt$date) # term spread
mktxts$ds = xts((baaffm$BAAFFM - aaaffm$AAAFFM)/100, order.by = mkt$date)# default spread

plot(mktxts$ex, main = "Market Excess over 1 month T-Bill" )
lines(mktxts$ts, col = "red")
lines(mktxts$ds, col = "blue")
legend(x = "bottomright", y = -0.1, legend = c("Excess", "Term Spread", "Default Spread"),
       col = c("black","red","blue"), lty = 1, cex = 1)
plot(mktxts$ts, main = "Term Spread")
plot(mktxts$ds, main = "Default Spread")


# regression analysis
pie = na.omit(mktxts)
lmSumm(lm(ex ~ dp + ts + ds, pie))

pie1 = lm(ex[-1] ~ na.omit(lag(pie$dp,1)) + na.omit(lag(pie$ts,1)) + na.omit(lag(pie$ds,1)), pie)
# NeweyWest SE for k month (k-1)*1.5
out1SE = sqrt(diag(NeweyWest(pie1, lag = (1-1)*1.5)))

piesum = pie
piesum$ex3mt = NA
for (i in 4:dim(piesum)[1]){
  piesum$ex3mt[i] = sum(piesum$ex[(i-1):(i-3)])
}
piesum$ex12mt = NA
for (i in 13:dim(piesum)[1]){
  piesum$ex12mt[i] = sum(piesum$ex[(i-1):(i-12)])
}
piesum$ex24mt = NA
for (i in 25:dim(piesum)[1]){
  piesum$ex24mt[i] = sum(piesum$ex[(i-1):(i-24)])
}
piesum$ex60mt = NA
for (i in 61:dim(piesum)[1]){
  piesum$ex60mt[i] = sum(piesum$ex[(i-1):(i-60)])
}
out3 = lm(ex3mt[-seq(1,3)] ~ na.omit(lag(piesum$dp,3)) + na.omit(lag(piesum$ts,3)) + 
            na.omit(lag(piesum$ds,3)), piesum)
out3SE = sqrt(diag(NeweyWest(out3, lag = (3-1)*1.5)))

out12 = lm(ex12mt[-seq(1,12)] ~ na.omit(lag(piesum$dp,12)) + na.omit(lag(piesum$ts,12)) + 
             na.omit(lag(piesum$ds,12)), piesum)
out12SE = sqrt(diag(NeweyWest(out12, lag = (12-1)*1.5)))

out24 = lm(ex24mt[-seq(1,24)] ~ na.omit(lag(piesum$dp,24)) + na.omit(lag(piesum$ts,24)) + 
             na.omit(lag(piesum$ds,24)), piesum)
out24SE = sqrt(diag(NeweyWest(out24, lag = (24-1)*1.5)))

out60 = lm(ex60mt[-seq(1,60)] ~ na.omit(lag(piesum$dp,60)) + na.omit(lag(piesum$ts,60)) + 
             na.omit(lag(piesum$ds,60)), piesum)
out60SE = sqrt(diag(NeweyWest(out60, lag = (60-1)*1.5)))


# mean reverting for an AR(1) model and the graph is showing a stationary process
summary_stat = data.frame(matrix(nrow = 9, ncol = 5))
colnames(summary_stat) = c("1-month", "3-month", "12-month", "24-month", "60-month")
rownames(summary_stat) = c("dividend yield", "dividend yield SE", "term spread", "term spread SE",
                           "default spread", "default spread SE","intercept", "intercept SE", "R-Squared")

coef_matrix = t(rbind(t(lmSumm(pie1)$coef)[1,], t(lmSumm(out3)$coef)[1,], t(lmSumm(out12)$coef)[1,],
             t(lmSumm(out24)$coef)[1,],t(lmSumm(out60)$coef)[1,]))
se_matrix = t(rbind(out1SE, out3SE, out12SE,out24SE,out60SE))

colnames(coef_matrix) = c("1-month", "3-month", "12-month", "24-month", "60-month")
colnames(se_matrix) = c("1-month", "3-month", "12-month", "24-month", "60-month")
rownames(coef_matrix) = c("dividend yield", "term spread", "default spread","intercept")
rownames(se_matrix) = c("dividend yield SE", "term spread SE", "default spread SE", "intercept SE")

coef_matrix
se_matrix

p12ex = as.xts(out12$fitted.values, order.by = mkt$date[-seq(1,25)]) # = predict(lm)
plot(p12ex, main = "Estimated expected 12-month excess return")

# Behaves opposite of business cycles...i.e. the rates are going up in economic recessions
# and vice versa in the boom times
