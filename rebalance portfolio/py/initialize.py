import os
import sys
import ccxt
from setup import Transactions, Base
from functions import coin_price

def Initialize(session, exchange, coins):
	# NOTE: had issues with coin_price function since it's in rebalance.py
	balance = exchange.fetchBalance()
	btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
	for i, coin in enumerate(coins):
		quantity = balance[coin]['total']
		price = coin_price(coin)
		dollar_value = quantity * price

		session.add(Transactions(
			trade_num = i + 1,
			rebalance_num = 0,
			date = datetime.now(),
			coin = coin,
			side = 'buy',
			units = quantity,
			price_per_unit = price,
			fees = dollar_value * 0.0075,
			previous_units = 0,
			cumulative_units = quantity,
			transacted_value = dollar_value,
			previous_cost = 0,
			cumulative_cost = dollar_value,
			realised_pct = 0
		))
		session.commit()
