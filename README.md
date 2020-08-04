# Welcome! 
Hi, welcome to Yushi's repository! You will find sample projects that I've worked on here in Python and R. Feel free to reach out if you have any suggestion/comment. Enjoy! 

## Monte-Carlo Delta-Hedged Option in R
The purpose of this study is to examine the effect of large price movement on the Delta-hedged call option. The stock price was simulated under the risk-neutral measure using geometric Brownian motion. Jump in stock price resulted in imperfect Delta-hedging. For small change in the underlying, the hedge ratio (defined as the ratio of Delta-hedged portfolio to the call option from Black-Scholes) is approximately one. Once the stock price jumps up or down, the hedge ratio deviated significantly from one. 

![Sample Simulation](https://github.com/globalize9/Yushi-Wei/blob/master/Images/Delta_Hedge_Upward_Jump10.png)

## Pricing of Fixed Strike Lookback Call and Put Options with Monte-Carlo Simulation in Python
Monte-Carlo simulation along with antithetic variance reduction were used to simulate the stock price. Initial stock price of $98, strike of $100, interest rate of 3%, 12-month, with varying volatilties from 12% to 48% in increments of 4%.

![Sample Simulation](https://github.com/globalize9/Yushi-Wei/blob/master/Images/Lookback_Options_Varying_Vol.png)

## How Greeks change over time with varying initial stock price for an European call
Time step size of dt = 0.004, initial stock price ranges from $15 to $25 in $1 increment, strike of $20, 6 months. Colored lines represent time to maturity in years. Gamma and Theta at the kink (ATM) approach infinity as time to expiration approaches zero. 

![Sample Simulation](https://github.com/globalize9/Yushi-Wei/blob/master/Images/Euro_Call_Greeks.png)

## Estimation of European Call option with Monte-Carlo via discretization of SDE  
The 2-factor model  for stock prices with stochastic volatility is discretized via Reflection, Partial Truncation and Full Truncation to estimate the European Call option via Monte-Carlo simulation. With 10,000 simulations, the following results were observed: Reflection: $4.33288, Partial Truncation: $4.28788, and Full Truncation: $4.39205

<img src ="https://github.com/globalize9/Yushi-Wei/blob/master/Images/Discretization_SDE.png" width="70" height ="70">

## Fama French Market Portfolio Replication
CRSP data was cleaned according to the Ken-French procedure before calculating the value-weighted and equal-weighted market excess returns. I report a correlation of 0.99998 with the Fama-French value-weighted market portfolio. Summary statistics of the two series are shown below. The full procedure is located here: [README_Fama_French_Mkt_Replication](https://github.com/globalize9/Yushi-Wei/blob/master/README_Fama_French_Mkt_Replication.pdf)

![Fama-French VWRETD Replication Summary Statistics](https://github.com/globalize9/Yushi-Wei/blob/master/Images/Fama_French_Mkt_Replication_Summary_Table.jpg)
 
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
