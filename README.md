# Welcome! 
Hi, welcome to Yushi's repository! You will find sample projects that I've worked on here. Feel free to reach out if you have any suggestion/comment. Enjoy! 

 
## Return Forecasting Regressions in R
This is a series of regressions investigating the predictable power of three variables (lagged dividend yield, term spread, and default spread) on the excess equity returns at the 1-month, 3-month, 12-month, 24-month and 60-month horizons. The data used were:
 - MonthlyMktCumandExDiv.csv: CRPS monthly market returns ex and cum dividends
 - MonthlyTbillAnnualizedYield: CRPS monthly t-bill rate
 - T10YFFM.csv: Term Spreads defined as 10-year CMT minus Fed Funds Rate 
 - AAAFFM.csv: Moody's Seasoned Aaa Corporate Bond Minus Fed Funds Rate
 - BAAFFM.csv: Moody's Seasoned Baa Corporate Bond Minus Fed Funds Rate

Default Spreads was calculated by subtracting AAAFFM from BAAFFM.
Dividend Yield was calculated by taking the sum of the dividends over the last 12 months and dividing by the current price.
Newey-West SEs were used to correct for heteroskedasticity in the error terms.
It was observed that the excess return is higher in bad times and lower in good times. 

## Monto-Carlo Delta-Hedged Option in R
The purpose of this study is to examine the effect of large price movement on the Delta-hedged call option. The stock price was simulated under the risk-neutral measure using geometric Brownian motion. Jump in stock price resulted in imperfect Delta-hedging. For small change in the underlying, the hedge ratio (defined as the ratio of Delta-hedged portfolio to the call option from Black-Scholes) is approximately one. Once the stock price jumps up or down, the hedge ratio deviated significantly from one. 

![Sample Simulation](https://github.com/globalize9/Yushi-Wei/blob/master/Delta_Hedge_Upward_Jump10.png)
