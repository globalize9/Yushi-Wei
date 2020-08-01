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

option_price = MonteCarloOptions(S0 = 15, r = 0.04, sigma = 0.25, T = 0.5, X = 20, option_type = 'call')
print('Monte-Carlo simulated option price is: ${:.5f}'.format(option_price))

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
def BSMOptions(S0, r, sigma, T, X, option_type = 'call'):
    d1 = (np.log(S0 / X) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S0 / X) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        option_price = (S0 * N_d(d1) - X * np.exp(-r * T) * N_d(d2))
    if option_type == 'put':
        option_price = -(S0 * N_d(-d1) + X * np.exp(-r * T) * N_d(-d2))
    if option_type != 'call' and option_type != 'put': 
        option_price = 'invalid selection'
    return(option_price)
    
BSM_Option = BSMOptions(S0 = 15, r = 0.04, sigma = 0.25, T = 0.5, X = 20, option_type = 'call')
print('BSM option price with normal approximation is: ${:.5f}'.format(BSM_Option))


def GreekStudy(S_0, r, sigma, T, X, dt):
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
        
    D.T.plot(kind = 'line', title = 'Delta over time with varying initial stock price dt = 0.04')
    plt.legend(fontsize = 7)
    
    G.T.plot(kind = 'line', title = "Gamma over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)
    T.T.plot(kind = 'line', title = "Theta over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)
    V.T.plot(kind = 'line', title = "Vega over time with varying initial stock price dt = 0.04")
    plt.legend(fontsize = 7)
    
    return(D,G,T,V)

D,G,T,V = GreekStudy(S_0 = np.arange(15,26,1), r = 0.04, sigma = 0.25, T = 0.5, X = 20, dt = 0.04)


# =============================================================================
# 
# ## Question 4
# def Q4(rho = -0.6, r = 0.03, S0 = 48, V0 = 0.05, sigma = 0.42, alpha = 5.8, beta = 0.0625, T = 1, K = 50):
#     n = 1000
#     dt = 0.01 # dynamic, can adjust n and dt to fine tune 
#     
#     # switch 
#     # 0: reflection 1: partial truncation 2: full truncation
#     def F1(x, method):
#         if method == 0:
#             return abs(x)
#         elif method == 1:
#             return x
#         elif method == 2:
#             return x
#         else:
#             return -10
#     
#     def F2(x, method):
#         if method == 0:
#             return abs(x)
#         elif method == 1:
#             return x
#         elif method == 2:
#             return np.maximum(x,0)
#         else:
#             return -10
#     
#     def F3(x, method):
#         if method == 0:
#             return abs(x)
#         elif method == 1:
#             return np.maximum(x,0)
#         elif method == 2:
#             return np.maximum(x,0)
#         else:
#             return -10
#         
#     C = np.zeros(3)
#     for M in np.arange(3):
#         level1hold = np.zeros(n)
#         for sim in np.arange(n):
#             # bivariate normals
#             mu_bm = 0
#             sig_bm = 1
#             Z1 = np.random.normal(0,1,int(T/dt)) 
#             Z2 = np.random.normal(0,1,int(T/dt)) 
#             W1 = mu_bm + sig_bm*Z1
#             W2 = mu_bm + sig_bm*rho*Z1 + sig_bm*np.sqrt(1-rho**2)*Z2
#             
#             S_t = np.zeros(int(T/dt))
#             V_t = np.zeros(int(T/dt))
#             S_t[0] = S0
#             V_t[0] = V0
#             for i in np.arange(1,int(T/dt)):
#                 S_t[i] = S_t[i-1] + r*S_t[i-1]*dt + np.sqrt(F3(V_t[i-1],M))*S_t[i-1]*W1[i] * np.sqrt(dt)
#                 V_t[i] = F1(V_t[i-1],M) + alpha*(beta-F2(V_t[i-1],M))*dt + sigma*np.sqrt(F3(V_t[i-1],M))*W2[i] * np.sqrt(dt)
#                 
#             level1hold[sim] = np.maximum(S_t[-1]-K,0) * np.exp(-r*T) # using the last stock price to calc call price
#         
#         C[M] = np.mean(level1hold)
#     
#     return(C)
# 
# C3, C2, C1 = Q4()
# 
# ## Question 5
# def LGM(n):
#     x = np.zeros(n)
#     x[0] = random.random()
#     a = 7**5
#     m = 2**31 - 1
#     for i in range(1,n):
#         x[i] = ((a * x[i-1]) % m) 
#     uniform_dist = x / m
#     return(uniform_dist)
# 
# # Q5a = np.concatenate([LGM(100),LGM(100)])
# Q5a = np.array([LGM(100),LGM(100)])
# colors = np.random.rand(100)
# plt.title("Scatter plot of Uniform Vectors")
# plt.scatter(Q5a[0,:],Q5a[1,:], c = colors)
# 
# 
# def GetHalton(n, base):
#     Seq = np.zeros(n)
#     NumBits = int(1 + np.ceil(np.log(n)/np.log(base)))
#     Vetbase = [base ** -x for x in range(1, NumBits+1)]
#     #base**(-np.arange(1,numbit+1)) #won't do -'ve int in **
#     WorkVet = np.zeros(NumBits)
#     for i in range(n):
#         j=0
#         ok = 0
#         # breakpoint()
#         while ok == 0:
#             WorkVet[j] = WorkVet[j]+1
#             if WorkVet[j] < base:
#                 ok = 1
#             else:
#                 WorkVet[j] = 0
#                 j = j+1          
#         Seq[i] = np.dot(WorkVet,Vetbase)
#     return(Seq)
# 
# halton2 = GetHalton(100,2)
# halton7 = GetHalton(100,7)
# halton4 = GetHalton(100,4)
# 
# plt.title("Halton Base 2 (Y) and Base 7 (X)")
# plt.scatter(x = halton7, y = halton2, c = colors)
# 
# plt.title("Halton Base 2 (Y) and Base 4 (X)")
# plt.scatter(x = halton4, y = halton2, c = colors)
# 
# def integralHalton(basei, baseii, n = 10000):
#     halton1 = GetHalton(n, basei)
#     halton2 = GetHalton(n, baseii)
#     result = np.zeros(n)
#     for i in np.arange(n):
#         result[i] = np.exp(-halton1[i]*halton2[i]) * (np.sin(6*np.pi*halton1[i]) + 
#                         np.sign(np.cos(2*np.pi*halton2[i])) * np.abs(np.cos(2*np.pi*halton2[i]))**(1.0/3))
#         # to compensate for imaginary number
#     return(np.mean(result))
# 
# q5e1 = integralHalton(basei = 2, baseii = 4)
# q5e2 = integralHalton(basei = 2, baseii = 7)
# q5e3 = integralHalton(basei = 5, baseii = 7)
# 
# =============================================================================
