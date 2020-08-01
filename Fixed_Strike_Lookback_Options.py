# -*- coding: utf-8 -*-
"""
Created on Sat May  2 14:30:48 2020

@author: yushi
"""
# %reset -f # clears variable space
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def Lookback(S_0, K, T, r, sigma, n = 10000):
# al the way up to 48%
    def stock_price(n, T = 1, S_0 = 98, sigma = 0.12, r = 0.03):
        dt = T/np.sqrt(n)
        column = int(T/dt+1)
        S_T = np.zeros(n*column).reshape(n,column)
        Z = np.random.normal(size = int(n/2 * column)).reshape(int(n/2), column)
        Z = np.insert(Z,0,np.repeat(0,int(n/2)), axis = 1)
        Z = np.concatenate([Z,-Z]) # antithetic variance reduction

        S_T[:,0] = S_0
        for j in range(1,column):
            S_T[:,j] = S_T[:,(j-1)] + S_T[:,(j-1)] * r *dt + S_T[:,(j-1)]*np.sqrt(dt)*sigma*Z[:,j]
        return(S_T)

    def fixed_lookback(stock, T = 1, S_0 = 98, sigma = 0.12, r = 0.03):
        S_max = stock.apply(np.max, axis = 1) # calculates the maximum along each path
        S_min = stock.apply(np.min, axis = 1) # calculates the maximum along each path

        Call_price = np.mean(np.exp(-r*T) * np.maximum(S_max - K, 0))
        Put_price = np.mean(np.exp(-r*T) * np.maximum(K - S_min, 0))

        return(Call_price, Put_price)

    results = pd.DataFrame(np.zeros((10,2)), columns = ["Call", "Put"])

    for i in range(sigma.size):
        stock = pd.DataFrame(stock_price(n = n, T = T, S_0 = S_0, sigma = sigma[i], r = r))
        results.iloc[i,0], results.iloc[i,1] = fixed_lookback(stock, T, S_0, sigma, r)

    results.index = sigma * 100
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(results.iloc[:,0], linestyle='--', marker='o', color='b', label='Call')
    ax1.plot(results.iloc[:,1], linestyle='--', marker='o', color='r', label='Put')
    plt.title('Look Back Options with Varying Volatility')
    plt.xlabel('Volatility')
    plt.ylabel('Option Prices')
    plt.legend(loc='upper left')
    plt.show()

    return results

Lookback(S_0 = 98, K = 100, T = 1, r = 0.03, sigma = np.arange(0.12, 0.48+0.04, 0.04), n = 10000)
