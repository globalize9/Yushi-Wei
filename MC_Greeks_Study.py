# -*- coding: utf-8 -*-
"""
Created on Sat Apr  18 15:20:12 2020
Project #3
@author: yushi
"""
# %reset -f # clears variable space
import random
import pandas as pd
import numpy as np
import scipy.stats as si
from scipy.stats import stats
import matplotlib.pyplot as plt


def MonteCarloOptions(S0, r, sigma, T, X, option_type = 'call', n = 1000000):
    Z = np.random.normal(size = n)
    S_T_p = S0 * np.exp((r - sigma**2/2)*T + sigma*Z*np.sqrt(T))
    S_T_n = S0 * np.exp((r - sigma**2/2)*T + sigma*(-Z)*np.sqrt(T))
    S_T = np.concatenate((S_T_n,S_T_p), axis = 0)
    if option_type == 'call':
        option_price = np.exp(-r*T) * np.mean(np.maximum(0,S_T - X))
    if option_type == 'put':
        option_price = np.exp(-r*T) * np.mean(np.maximum(0,X - S_T))
    if option_type != 'call' and option_type != 'put':
        option_price = 'invalid selection'
    return(option_price)

# approximation of the normal distribution
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

# BSM formula
def BSMOptionsN_Approx(S0, r, sigma, T, X, option_type = 'call'):
    d1 = (np.log(S0 / X) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S0 / X) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        option_price = (S0 * N_d(d1) - X * np.exp(-r * T) * N_d(d2))
    if option_type == 'put':
        option_price = -(S0 * N_d(-d1) + X * np.exp(-r * T) * N_d(-d2))
    if option_type != 'call' and option_type != 'put':
        option_price = 'invalid selection'
    return(option_price)

def BSMOptions(S0, r, sigma, T, X, option_type = 'call'):
    d1 = (np.log(S0 / X) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S0 / X) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        option_price = (S0 * si.norm.cdf(d1) - X * np.exp(-r * T) * si.norm.cdf(d2))
    if option_type == 'put':
        option_price = -(S0 * si.norm.cdf(-d1) + X * np.exp(-r * T) * si.norm.cdf(-d2))
    if option_type != 'call' and option_type != 'put':
        option_price = 'invalid selection'
    return(option_price)

BSM_Option_N_Approx = BSMOptionsN_Approx(S0 = 15, r = 0.04, sigma = 0.25, T = 0.5, X = 20, option_type = 'call')
BSM_Option = BSMOptions(S0 = 15, r = 0.04, sigma = 0.25, T = 0.5, X = 20, option_type = 'call')
option_price = MonteCarloOptions(S0 = 15, r = 0.04, sigma = 0.25, T = 0.5, X = 20, option_type = 'call')
print('Monte-Carlo simulated option price is: ${:.5f}'.format(option_price))
print('BSM option price with normal approximation is: ${:.5f}'.format(BSM_Option_N_Approx))
print('BSM option price without normal approximation is: ${:.5f}'.format(BSM_Option))

def GreekStudyEuroCall(S_0, r, sigma, T, X, dt):
    def Greeks(S0, r, sigma, T, X):
        d1 = (np.log(S0 / X) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        N_d1 = si.norm.cdf(d1)
        N_d2 = N_d1 - 1
        n_d1 = 1 / np.sqrt(2 * np.pi) * np.exp(- d1**2 /2)
        Delta = N_d1
        Gamma = 1 / (S0 * sigma * np.sqrt(T)) * n_d1
        Theta = -S0 * sigma * n_d1 / (2*np.sqrt(T)) - r * X * np.exp(-r*T) * N_d2
        Vega = S0 * np.sqrt(T) * n_d1
        Rho = X * T * np.exp(-r*T) * N_d2
        return(Delta, Gamma, Theta, Vega, Rho)


    time_t = np.arange(0, T, dt)
    time_t = T - time_t # reversing order

    D = pd.DataFrame(np.zeros((len(time_t),len(S_0))), columns = np.arange(S_0[0],S_0[len(S_0)-1]+1))
    D.index = time_t
    G = D.copy()
    T = D.copy()
    V = D.copy()

    for i in np.arange(len(S_0)):
        D_temp, G_temp, T_temp, V_temp, R_temp = Greeks(S0 = S_0[i], r = r, sigma = sigma, T = time_t, X = X)
        D.iloc[:,i] = D_temp
        G.iloc[:,i] = G_temp
        T.iloc[:,i] = T_temp
        V.iloc[:,i] = V_temp

    D.T.plot(kind = 'line', title = "Euro-Call Delta over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)
    G.T.plot(kind = 'line', title = "Euro-Call Gamma over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)
    T.T.plot(kind = 'line', title = "Euro-Call Theta over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)
    V.T.plot(kind = 'line', title = "Euro-Call Vega over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)

    return(D,G,T,V)

D,G,T,V = GreekStudyEuroCall(S_0 = np.arange(15,26,1), r = 0.04, sigma = 0.25, T = 0.5, X = 20, dt = 0.04)



