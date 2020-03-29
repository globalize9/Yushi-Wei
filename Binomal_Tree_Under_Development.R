library(data.table)

#Create a Function that takes the ncessary arguments and creates the following trees:
  #Stock Tree
  #Payoff Tree
  #Delta Tree
  #Bond Portfolio Tree

# Specify the Payoff function at the very end
Binomial_Tree = function(S0, Payoff, K, r, h, T_Periods){
  #Creating Stock Tree
  # Stock_Matrix = data.table(matrix(0, ncol = T_Periods+1, nrow = T_Periods+1))
  # setnames(Stock_Matrix, old = colnames(Stock_Matrix), new = as.character(0:T_Periods)) 
  Stock_Matrix = matrix(ncol = T_Periods+1, nrow = T_Periods+1)
  colnames(Stock_Matrix) = 0:T_Periods # including initial stock price for column names
  rownames(Stock_Matrix) = 1:(T_Periods+1)
  u = exp((r*h) + 0.2*sqrt(h))
  d = exp((r*h) - 0.2*sqrt(h))
  
  for(i in 1:(T_Periods+1)){
    for(j in 1:(T_Periods+1)){
      ifelse(j >= i,(Stock_Matrix[i,j] = S0 * (u^(j-i)) * (d^(i-1))), 0) # going across the rows
    }
  }
  
  
  #Creating Payoff Tree - European
  # Payoff_Matrix = data.table(matrix(0, ncol = T_Periods+1, nrow = T_Periods+1))
  # setnames(Payoff_Matrix, old = colnames(Payoff_Matrix), new = as.character(0:T_Periods))
  Payoff_Matrix = matrix(ncol = T_Periods+1, nrow = T_Periods+1)
  colnames(Payoff_Matrix) = 0:T_Periods
  row.names(Payoff_Matrix) = 1:(T_Periods+1)
  p_u = (exp(r*h) - d)/(u-d)
  p_d = (1-p_u)
  
  # Calculating payoff using the function that is specified in the initial parameters
  for(i in 1:(T_Periods+1)){
    Payoff_Matrix[i,(T_Periods+1)] = Payoff(Stock_Matrix[i,(T_Periods+1)], K)
  }

  
  for(i in (T_Periods+1):1){
    for(j in (T_Periods):1){
      ifelse(j>=i,(Payoff_Matrix[i,j] = (exp(-r*h) * (p_u*Payoff_Matrix[i,j+1] + p_d*Payoff_Matrix[i+1,j+1]))), 0)
    }
  }
  
  # Creating Delta Tree
  Delta_Matrix = matrix(0, ncol = T_Periods, nrow = T_Periods+1) 
  colnames(Delta_Matrix) = 0:(T_Periods-1)
  rownames(Delta_Matrix) = 1:(T_Periods+1)
  
  
  # Creating Bond Portfolio Tree
  Bond_Matrix = matrix(0, ncol = T_Periods, nrow = T_Periods+1) 
  colnames(Bond_Matrix) = 0:(T_Periods-1)
  rownames(Bond_Matrix) = 1:(T_Periods+1)
  
  for(i in (T_Periods+1):1){
    for(j in (T_Periods):1){
      ifelse(j>=i,(Delta_Matrix[i,j] = (Payoff_Matrix[i,j+1] - Payoff_Matrix[i+1,j+1])/
                     (Stock_Matrix[i,j+1]-Stock_Matrix[i+1,j+1])),0)
    }
  }
  for(i in (T_Periods+1):1){
    for(j in (T_Periods):1){
      ifelse(j>=i,(Bond_Matrix[i,j] = exp(-r*h)*(Payoff_Matrix[i+1,j+1]*u - Payoff_Matrix[i,j+1]*d)/
                     (u-d)),0)
    }
  }

  #Return the required trees
  return(list(payoff = Payoff_Matrix, 
              stock = Stock_Matrix, 
              delta = Delta_Matrix,
              bond = Bond_Matrix
              ))
} # end function a

# Function to calculate Straddle Payoff
Payoff_Straddle = function(S,K){
  payoff_put = max(K-S,0)
  payoff_call = max(S-K,0)
  return(payoff_put+payoff_call)
}

# Function to calculate Binary Payoff
Payoff_Binary = function(S,K){
  payoff_binary = ifelse((S-K>0),1,0)
  return(payoff_binary)
}

S0 = 100
Payoff = Payoff_Straddle
K = 90
r = 0.02
h = 0.25 # length of each period
T_Periods = 4

#Parta
Value_Straddle1 = Binomial_Tree(100,Payoff_Straddle,90,0.02,0.25,4)$payoff[[1,1]]

#Partb
Value_Straddle2 = Binomial_Tree(100,Payoff_Straddle,90,0.02,0.025,40)$payoff[[1,1]]

#Partc
Value_Binary_Call = Binomial_Tree(100,Payoff_Binary,90,0.02,0.25,4)$payoff[[1,1]]


