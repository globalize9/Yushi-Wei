## Monto-Carlo simulation to study the effect of jumps on Delta-Hedged call ##

library(data.table)
library(ggplot2)
library(gridExtra)

Black_Scholes = function (t, S, r, sigma, K, T, type = c("call", "put")) 
{
  d1 <- (log(S/K) + (r + sigma^2/2) * (T - t))/(sigma * sqrt(T - t))
  d2 <- d1 - sigma * sqrt(T - t)
  type <- match.arg(type)
  switch(type, call = {
    S * pnorm(d1) - K * exp(-r * (T - t)) * pnorm(d2)}, 
    put = {
    -S * pnorm(-d1) + K * exp(-r * (T - t)) * pnorm(-d2)}, 
    stop("Wrong type"))
} # end BS fn

Delta = function(t, S, r, sigma, K, T){
  d1 = (log(S/K) + (r + sigma^2/2) * (T - t))/(sigma * sqrt(T - t))
  Delta = pnorm(d1)
} # end Delta fn


# initial parameters 
Tm = 60/365 # time to maturity in years
S0 = 100 # initial stock price
K = 100 # strike price
r = 0.05 # risk free interest
sigma = 0.3 # volatility of the underlying
div = 0 # dividend of the underlying
h = 5/(60*8*365) # interval of hedging

# run Monte-Carlo simulation with the above parameters 
SP_5 <- data.table(matrix(0, ncol= 1, nrow = 96*30+1)) 
SP_5[1,"time"] = 0
SP_5[1,"stock"] = S0
SP_5[1,"callprice"] = Black_Scholes(0,as.numeric(SP_5[1,"stock"]),r,sigma,K,Tm, type = "call")
SP_5[1,"Delta"] = Delta(0,as.numeric(SP_5[1,"stock"]),r,sigma,K,Tm)
SP_5[1,"Bond"] = SP_5[1,"callprice"] - SP_5[1,"Delta"] * SP_5[1,"stock"]
SP_5[1,"hedgeP"] = SP_5[1,"callprice"]
for(i in 2:(96*30+1)){
  # SP_5[i,as.character(j)] = (SP_5[(i-1),j])*exp(r*h + sigma*sqrt(h)*rnorm(1,0,1))
  SP_5[i,"stock"] = (SP_5[(i-1),"stock"])*exp(r*h + sigma*sqrt(h)*rnorm(1,0,1))
  SP_5[i,"time"] = SP_5[(i-1),"time"] + h
  SP_5[i,"callprice"] = Black_Scholes(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm, type = "call")
  SP_5[i,"Delta"] = Delta(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm)
  SP_5[i,"hedgeP"] = (SP_5[(i-1),"Delta"]) * SP_5[i,"stock"] + (SP_5[(i-1),"Bond"]) * exp(r*h)
  SP_5[i,"Bond"] = SP_5[i,"hedgeP"] - SP_5[i,"Delta"] * SP_5[i,"stock"]
}

SP_5$hedge_ratio = SP_5$hedgeP / SP_5$callprice

p1 <- ggplot(SP_5, aes(y = stock, x = time)) + geom_line() + ggtitle("Simulated Stock Price")
p2 <- ggplot(SP_5, aes(y = callprice, x = time, colour = "call price" )) + geom_line() + 
  geom_line(aes(y = hedgeP, color = "replicating portfolio")) + ggtitle("Simulated under risk-neutral")
p3 <- ggplot(SP_5, aes(y = hedge_ratio, x = time, color = "hedge_ratio")) + geom_line() + ggtitle("hedge ratio")
grid.arrange(p1,p2,p3)

# downward jump 10%
for(i in 2:(96*30+1)){
  SP_5[i,"stock"] = (SP_5[(i-1),"stock"])*exp(r*h + sigma*sqrt(h)*rnorm(1,0,1))
  if (i == 1441) {SP_5[i,"stock"] = SP_5[i,"stock"] * 0.9} # specify downward 10% movement in the middle
  SP_5[i,"time"] = SP_5[(i-1),"time"] + h
  SP_5[i,"callprice"] = Black_Scholes(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm, type = "call")
  SP_5[i,"Delta"] = Delta(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm)
  SP_5[i,"hedgeP"] = (SP_5[(i-1),"Delta"]) * SP_5[i,"stock"] + (SP_5[(i-1),"Bond"]) * exp(r*h)
  SP_5[i,"Bond"] = SP_5[i,"hedgeP"] - SP_5[i,"Delta"] * SP_5[i,"stock"]
}

SP_5$hedge_ratio = SP_5$hedgeP / SP_5$callprice

p11 <- ggplot(SP_5, aes(y = stock, x = time)) + geom_line() + ggtitle("Simulated Stock Price")
p22 <- ggplot(SP_5, aes(y = callprice, x = time, colour = "call price" )) + geom_line() + 
  geom_line(aes(y = hedgeP, color = "replicating portfolio")) + ggtitle("downward jump of 10%")
p33 <- ggplot(SP_5, aes(y = hedge_ratio, x = time, color = "hedge_ratio")) + geom_line() + ggtitle("hedge ratio")
grid.arrange(p11, p22, p33)


# upward jump 10%
for(i in 2:(96*30+1)){
  SP_5[i,"stock"] = (SP_5[(i-1),"stock"])*exp(r*h + sigma*sqrt(h)*rnorm(1,0,1))
  if (i == 1441) {SP_5[i,"stock"] = SP_5[i,"stock"] * 1.1} # specify upward 10% move in the middle
  SP_5[i,"time"] = SP_5[(i-1),"time"] + h
  SP_5[i,"callprice"] = Black_Scholes(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm, type = "call")
  SP_5[i,"Delta"] = Delta(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm)
  SP_5[i,"hedgeP"] = (SP_5[(i-1),"Delta"]) * SP_5[i,"stock"] + (SP_5[(i-1),"Bond"]) * exp(r*h)
  SP_5[i,"Bond"] = SP_5[i,"hedgeP"] - SP_5[i,"Delta"] * SP_5[i,"stock"]
}

SP_5$hedge_ratio = SP_5$hedgeP / SP_5$callprice

p111 <- ggplot(SP_5, aes(y = stock, x = time)) + geom_line() + ggtitle("Simulated Stock Price")
p222 <- ggplot(SP_5, aes(y = callprice, x = time, colour = "call price" )) + geom_line() + 
  geom_line(aes(y = hedgeP, color = "replicating portfolio")) + ggtitle("upward jump of 10%")
p333 <- ggplot(SP_5, aes(y = hedge_ratio, x = time, color = "hedge_ratio")) + geom_line() + ggtitle("hedge ratio")
grid.arrange(p111, p222, p333)

# impact of transaction fee
for(i in 2:(96*30+1)){
  SP_5[i,"stock"] = (SP_5[(i-1),"stock"])*exp(r*h + sigma*sqrt(h)*rnorm(1,0,1))
  SP_5[i,"time"] = SP_5[(i-1),"time"] + h
  SP_5[i,"callprice"] = Black_Scholes(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm, type = "call")
  SP_5[i,"Delta"] = Delta(as.numeric(SP_5[i,"time"]),as.numeric(SP_5[i,"stock"]),r,sigma,K,Tm)
  SP_5[i,"hedgeP"] = (SP_5[(i-1),"Delta"]) * SP_5[i,"stock"] + (SP_5[(i-1),"Bond"]) * exp(r*h) - 
    abs(SP_5[i,"Delta"] - SP_5[(i-1),"Delta"]) * SP_5[i,"stock"] * 0.002
  SP_5[i,"Bond"] = SP_5[i,"hedgeP"] - SP_5[i,"Delta"] * SP_5[i,"stock"]
}

SP_5$hedge_ratio = SP_5$hedgeP / SP_5$callprice

p1111 <- ggplot(SP_5, aes(y = stock, x = time)) + geom_line() + ggtitle("Simulated Stock Price")
p2222 <- ggplot(SP_5, aes(y = callprice, x = time, colour = "call price" )) + geom_line() + 
  geom_line(aes(y = hedgeP, color = "replicating portfolio")) + ggtitle("with transaction fee")
p3333 <- ggplot(SP_5, aes(y = hedge_ratio, x = time, color = "hedge_ratio")) + geom_line() + ggtitle("hedge ratio")

grid.arrange(p1111,p2222,p3333)



