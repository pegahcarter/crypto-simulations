import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ccxt
%matplotlib inline

folder = 'C:/Users/18047/Documents/Rebalance/backtests/2/2_'

sim1 = pd.read_csv(folder + 'HODL.csv')
sim2 = pd.read_csv(folder + 'rebalanced.csv')
