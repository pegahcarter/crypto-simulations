import os
import sys
import ccxt
import numpy as np
import pandas as pd

df = pd.read_csv(os.getcwd() + '/backtests/historical market cap.csv')
df.head()

df = np.array(df)

start_dates = df[:len(df)-365]
end_dates = df[365:]

market_cap_diffs = end_dates[:, 3] - start_dates[:, 3]

largest_diff_startdate = df[market_cap_diffs.argmax(), 0]
smallest_diff_startdate = df[market_cap_diffs.argmin(), 0]

middle_diff = (max(market_cap_diffs) - min(market_cap_diffs)) / 2
temp = list(market_cap_diffs)
middle_diff_startdate = df[temp.index(min(market_cap_diffs, key=lambda x: abs(x - middle_diff))), 0]
