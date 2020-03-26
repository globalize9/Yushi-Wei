# Yushi Wei
 Assortment of Projects
 
## Return Forecasting Regressions in R
This is a series of regressions investigating the predictable power of three variables (lagged dividend yield, term spread, and default spread) on the excess equity returns at the 1-month, 3-month, 12-month, 24-month and 60-month horizons. The data used were:
 - MonthlyMktCumandExDiv.csv: CRPS monthly market returns ex and cum dividends
 - MonthlyTbillAnnualizedYield: CRPS monthly t-bill rate
 - T10YFFM.csv: Term Spreads defined as 10-year CMT minus Fed Funds Rate 
 - AAAFFM.csv: Moody's Seasoned Aaa Corporate Bond Minus Fed Funds Rate
 - BAAFFM.csv: Moody's Seasoned Baa Corporate Bond Minus Fed Funds Rate

Default Spreads was calculated by subtracting AAAFFM from BAAFFM.
Dividend Yield was calculated by taking the sum of the dividends over the last 12 months and dividing by the current price.
Newey-West SEs were used to correct for heteroskedasticity in the error terms 

