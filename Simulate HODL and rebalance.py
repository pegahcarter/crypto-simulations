import ccxt
import pandas as pd
import numpy as np
from Portfolio import hist_prices, Portfolio
from functions import hodl, rebalance

# Set the threshold of weight difference to trigger a trade
thresh = 0.05
avg_weight = .2
weighted_thresh = np.float32(avg_weight * thresh)

coins = hist_prices.columns.tolist()[1:]

# TODO: update historical market cap
hist_mcap = np.array(pd.read_csv('data/historical/market_cap.csv'))

# note- there are 8760 hours in a year
start_dates = hist_mcap[:len(hist_mcap) - 8760]
end_date = hist_mcap[8760:]
cap_diffs = list(end_dates[:, 3] - start_dates[:, 3]) # TODO: fix this after we have the new market cap data

# Make sure there's an odd number of dates, so the median value can be indexed
if len(cap_diffs) % 2 == 0:
	cap_diffs.pop(len(cap_diffs)-1)

# Start date for sims
start_date = cap_diffs.index(np.median(cap_diffs))

# Limit dataframe dates to the date range
hist_prices = hist_prices[start_date:start_date + 8760]
sim_dates = hist_prices['date']

# Retrieve all current tickers on exchange
exchange = ccxt.bittrex()
tickers = set()
[tickers.add(ticker) for ticker in exchange.fetch_tickers()]

hodl_df = hodl(hist_prices)

rebalance_df = rebalance(hist_prices, hodl_df)

trade_intervals = [1, 24, 24*30]

test = {1:'hourly', 24:'daily', 24*30:'monthly'}
for a in test:
	print(a)

trade_intervals = {1:'hourly', 24:'daily', 24*30:'monthly'}

for interval in trade_intervals:

	hr_totals = []
	sims = pd.DataFrame()

	for col in hodl_df.columns:

		coin_list = col.split('-')

		simPortfolio = Portfolio(coin_list)

		for hr in range(1, len(hist_prices), interval):
			if num_day % trade_interval == 0:
				simPortfolio = rebalance(simPortfolio, hr)

			hr_totals.append(np.dot(simPortfolio.daily_prices[hr], simPortfolio.quantities))

		sims[col] = hr_totals

	sims.to_csv('data/simulations/' + trade_intervals[interval] + '.csv')
