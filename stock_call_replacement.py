# -*- coding: utf-8 -*-
"""
Replacing stocks with 2 calls if IV is low or a number of calls
"""
import pandas as pd
import numpy as np
from sympy import symbols, solve

def N_d(x):
    d = [0, 0.0498673470, 0.0211410061, 0.0032776263, 
         0.00000380036, 0.0000488906, 0.0000053830]
    
    def result(x):
        result = 1 - 1/2 * (1 + d[1]*x + d[2]*x**2 + d[3]*x**3
                            + d[4]*x**4 + d[5]*x**5 + d[6]*x**6) ** -16
        return result
    
    if (x>=0):
        approx = result(x)
    if (x<0):
        approx = 1 - result(-x)
    
    return(approx)

def BS_Form(S0, r, div, sigma, T, X, opt):
    "specify opt as 'call' or 'put', return opt price, Delta, prob ITM"
    d1 = (np.log(S0 / X) + (r - div + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    # d2 = d1 - sigma * np.sqrt(T)
    d2 = (np.log(S0 / X) + (r - div - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if opt == 'call': opt_price = S0 * N_d(d1) - X * np.exp(-r * T) * N_d(d2)
    if opt == 'put': opt_price = -S0 * N_d(-d1) + X * np.exp(-r * T) * N_d(-d2)
    return(opt_price, N_d(d1), N_d(d2))

S0 = 100
r = 0
div = 0 
sigma = 0.2
T = 0.5
strike = 100
call_qty = 2 # optional parameter, otherwise calculate equivalent to 100 shares
opt_type = 'call'

call_cost = BS_Form(S0, r, div, sigma, T, strike, 'call')
put_cost = BS_Form(S0, r, div, sigma, T, strike, 'put')

# strategy is to replace long stock position with 2x 50D calls
# analysis conducted at T

# need to redefine vars
def UpperBreak(S0, r, div, sigma, T, strike, opt_type, call_qty = None):
    "obtain payoff where long stock == long calls"
    call_cost, delta, prob_itm = BS_Form(S0, r, div, sigma, T, strike, opt_type)
    if call_qty == None: call_qty = round(1 / delta)
    unknown_price = symbols('unknown_price')
    # Solve this eq 
    expr = (unknown_price - S0) - (unknown_price - strike - call_cost[0]) * call_qty
    return solve(expr)[0]

UpperBreak(2)

# lower breakpoint is equivalent to call premium
lower_break = S0 - call_qty * call_cost[0]

atm_by_maturity = pd.DataFrame(None, index = [1/12, 3/12, 6/12, 12/12], columns = ['Strike','Delta','Prob_ITM','Upper_Break','Lower_Break', 'Opt_Cost',
                                                                                   'Opt_Qty'])


