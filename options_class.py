from datetime import datetime, date
import scipy.stats as si
import pandas as pd
import numpy as np
import yfinance as yf

class Options:
    def __init__(self, ticker, option_type):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.expiry_dates = self.stock.options
        self.strike_width = 5 # specify how many strikes around ATM to obtain
        self.option_type = option_type # specify whether we want to see the call or put options chain

    def getdata(self, expiry):
        call_chain = self.stock.option_chain(date=expiry).calls
        put_chain = self.stock.option_chain(date=expiry).puts
        stock_chain = self.stock.history(period="max")
        return([call_chain,put_chain,stock_chain])
    
    def intrinsic(self, optiondf, underlyingdf, option_type):
        # todaystock = underlyingdf.loc[date.today().strftime('%Y-%m-%d'),'Close']
        todaystock = underlyingdf.iloc[-1]['Close'] # grab the most recent closing price
        if option_type == 'call':
            optiondf['intrinsic'] = [max(todaystock - strikeprice,0) for strikeprice in optiondf['strike']]
        else:
            optiondf['intrinsic'] = [max(strikeprice - todaystock,0) for strikeprice in optiondf['strike']]
        optiondf['mid'] = (optiondf['bid'] + optiondf['ask'])/2
        optiondf['timevalue'] = np.maximum(optiondf['mid'] - optiondf['intrinsic'],0)
        return(optiondf)
    
    @staticmethod
    def BSMOptions(self, S0, r, sigma, T, X, option_type = 'call'):
        d1 = (np.log(S0 / X) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = (np.log(S0 / X) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if option_type == 'call':
            option_price = (S0 * si.norm.cdf(d1) - X * np.exp(-r * T) * si.norm.cdf(d2))
        if option_type == 'put':
            option_price = -S0 * si.norm.cdf(-d1) + X * np.exp(-r * T) * si.norm.cdf(-d2)
        if option_type != 'call' and option_type != 'put':
            option_price = 'invalid selection'
        return(option_price)

    @staticmethod
    def ProbITM(self, S0, r, sigma, T, X, option_type = 'call'):
        d2 = (np.log(S0 / X) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if option_type == 'call': return(si.norm.cdf(d2))
        else: return(si.norm.cdf(-d2))

    def ImpliedMove(self, S0, calldf, putdf):
        put_idx = np.abs(putdf['strike'] - S0).argmin() # find nearest strike
        call_idx = np.abs(S0 - calldf['strike']).argmin()
        return round(putdf.loc[put_idx, 'mid'] + calldf.loc[call_idx, 'mid'],2)

    # still need to think about how to define the Expected Payout
    def ExpPayout(self, S0, df, option_type):
        return df['timevalue'] * (1-df['ProbITM'])
        # if option_type == 'call':
        #     if S0 > df['strike']:
        #         return df['mid']
        #     else:            
        #         return (df['strike'] - S0) * df['ProbITM']

    def CleanDF(self, df, input_df, time_to_expiry, opt_type, bs_filter = True): 
        todaystock = round(input_df.iloc[-1]['Close'],2) # take the px_last of the underlying
        bs_filter_cutoff = 0.5 # if BS estimate is off by 0.5, drop the contracts
        temp_df = df.copy()
        # converting to datetime format
        temp_df['lastTradeDate'] = pd.to_datetime(temp_df['lastTradeDate']).dt.date
        
        # filter to drop trades that are more than 2 days old
        # temp_df = temp_df[temp_df['lastTradeDate'] > input_df.index[-2].date()].reset_index(drop=True)

        # check listed IV against BS calculated option price
        # no need to calc IV again, its already calculated with BS using MID price
        temp_df['Calc_OptP'] = None
        for i in range(len(temp_df)):
            temp_line = temp_df.iloc[i,:]
            temp_df.loc[i,'Calc_OptP'] = self.BSMOptions(self, todaystock, 0, temp_line['impliedVolatility'], time_to_expiry/252, temp_line['strike'], opt_type) 
        temp_df['Diff'] = abs(temp_df['Calc_OptP'] - temp_df['mid'])
        
        if bs_filter:
            temp_df = temp_df[temp_df['Diff'] < bs_filter_cutoff].reset_index(drop=True)
        return temp_df
    
    def MainDF(self):
        opt_exp_date = self.expiry_dates[0] # temp use of the first exp date
        
        implied_move_df = pd.DataFrame(None, index = self.expiry_dates, columns = ['Implied_Move'])
        
        calldf, putdf, stockdf = self.getdata(opt_exp_date)
        initial_price = round(stockdf.iloc[-1]['Close'],2) # obtain the relevant strikes around this value
        strike_mid = 1 * round(initial_price/1)
        strike_width = 5
        strike_col = range((strike_mid - strike_width)*10, (strike_mid + strike_width)*10, 5)
        strike_col = [x/10 for x in strike_col]
        
        puts_df = pd.DataFrame(None, index = self.expiry_dates, columns = strike_col)
        puts_tv_df = pd.DataFrame(None, index = self.expiry_dates, columns = strike_col)
        
        
        for opt_exp_date in self.expiry_dates:
            print(opt_exp_date)
            calldf, putdf, stockdf = self.getdata(opt_exp_date)
            
            # focusing on put df for now, works equally for call
            # assuming sell short call or put
            putdf = self.intrinsic(putdf, stockdf, 'put')
            calldf = self.intrinsic(calldf, stockdf, 'call')
            todaystock = round(stockdf.iloc[-1]['Close'],2)
            time_to_expiry = np.busday_count(date.today(), datetime.strptime(opt_exp_date,'%Y-%m-%d').date())
            cleaned_df = self.CleanDF(putdf, stockdf, time_to_expiry, self.option_type)
            
            cleaned_df['ProbITM'] = None
            # cleaned_df['Exp_Payout'] = None # assuming no price movement until maturity (very unlikely)
            
            for i in range(len(cleaned_df)):
                temp_line = cleaned_df.iloc[i,:]
                cleaned_df.loc[i,'ProbITM'] = self.ProbITM(self, todaystock, 0, temp_line['impliedVolatility'], time_to_expiry/252, temp_line['strike'], self.option_type)
                if temp_line['strike'] in strike_col:
                    puts_df.loc[opt_exp_date, temp_line['strike']] = cleaned_df.loc[i,'ProbITM']
                    puts_tv_df.loc[opt_exp_date, temp_line['strike']] = cleaned_df.loc[i,'timevalue']
                    
            implied_move_df.loc[opt_exp_date, 'Implied_Move'] = self.ImpliedMove(todaystock, calldf, putdf)
        
        implied_move_df['Percentage'] = implied_move_df['Implied_Move'] / initial_price
        implied_move_df['Lower'] = initial_price - implied_move_df['Implied_Move']
        implied_move_df['Upper'] = initial_price + implied_move_df['Implied_Move']

        print(f'{self.ticker} options implied moves generated')
        return puts_df, puts_tv_df, implied_move_df

if __name__ == '__main__': 
    ## inputs
    ticker = input('Enter a ticker: ')
    option_type = 'put'
    kweb_opt = Options(ticker, option_type)
    out_dfs = kweb_opt.MainDF()

    with pd.ExcelWriter('{}_{}.xlsx'.format(ticker,date.today().strftime('%Y-%m-%d'))) as writer:
        out_dfs[0].to_excel(writer, sheet_name = 'ProbITM')
        out_dfs[1].to_excel(writer, sheet_name = 'TimeValue')
        out_dfs[2].to_excel(writer, sheet_name = 'ImpliedMove')
