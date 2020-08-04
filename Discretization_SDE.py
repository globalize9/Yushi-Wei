# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 20:23:58 2020

@author: yushi
"""
import pandas as pd
import numpy as np

def Discretization_SDE(rho, r, S0, V0, sigma, alpha, beta, T, K):
    n = 1000
    dt = 0.01 # dynamic, can adjust n and dt to fine tune

    # switch
    # 0: reflection 1: partial truncation 2: full truncation
    def F1(x, method):
        if method == 0:
            return abs(x)
        elif method == 1:
            return x
        elif method == 2:
            return x
        else:
            return -10

    def F2(x, method):
        if method == 0:
            return abs(x)
        elif method == 1:
            return x
        elif method == 2:
            return np.maximum(x,0)
        else:
            return -10

    def F3(x, method):
        if method == 0:
            return abs(x)
        elif method == 1:
            return np.maximum(x,0)
        elif method == 2:
            return np.maximum(x,0)
        else:
            return -10

    C = np.zeros(3)
    for M in np.arange(3):
        level1hold = np.zeros(n)
        for sim in np.arange(n):
            # bivariate normals
            mu_bm = 0
            sig_bm = 1
            Z1 = np.random.normal(0,1,int(T/dt))
            Z2 = np.random.normal(0,1,int(T/dt))
            W1 = mu_bm + sig_bm*Z1
            W2 = mu_bm + sig_bm*rho*Z1 + sig_bm*np.sqrt(1-rho**2)*Z2

            S_t = np.zeros(int(T/dt))
            V_t = np.zeros(int(T/dt))
            S_t[0] = S0
            V_t[0] = V0
            for i in np.arange(1,int(T/dt)):
                S_t[i] = S_t[i-1] + r*S_t[i-1]*dt + np.sqrt(F3(V_t[i-1],M))*S_t[i-1]*W1[i] * np.sqrt(dt)
                V_t[i] = F1(V_t[i-1],M) + alpha*(beta-F2(V_t[i-1],M))*dt + sigma*np.sqrt(F3(V_t[i-1],M))*W2[i] * np.sqrt(dt)

            level1hold[sim] = np.maximum(S_t[-1]-K,0) * np.exp(-r*T) # using the last stock price to calc call price

        C[M] = np.mean(level1hold)

    return(C)

reflection, partial_truncation, full_truncation = Discretization_SDE(rho = -0.6, r = 0.03, S0 = 48, V0 = 0.05, sigma = 0.42, alpha = 5.8, beta = 0.0625, T = 1, K = 50)

print('Reflection: {:.5f}, Partial Truncation: {:.5f}, and Full Truncation: {:.5f}'.format(reflection, partial_truncation, full_truncation))

