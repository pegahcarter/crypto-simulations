# Note: Historical market cap downloaded from https://coin.dance/stats/marketcaphistorical
import pandas as pd
import os
import time

file = os.getcwd() + '/backtests/historical market cap.csv'
df = pd.read_csv(file)

# convert date column to epoch time
df.rename(columns={0: 'date'}, inplace=True)
date_epochs = [int(time.mktime(time.strptime(day, '%m/%d/%Y'))) for day in df['date']]
df['date'] = date_epochs

# Total market cap
df['Total Market Cap'] = df['Altcoin Market Cap'] + df['Bitcoin Market Cap']

# Save file
df.set_index('date', drop=True, inplace=True)
df.to_csv(os.getcwd() + '/backtests/historical market cap.csv')
