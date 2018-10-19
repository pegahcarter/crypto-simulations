import os
import sys

def Initialize(session, exchange, *args):
	btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
	for i, coin in enumerate(args):
		quantity = balance[coin][total]
		price = coin_price(coin)
		dollar_value = quantity * price

		session.add(Transactions(
			trade_num = i,
			rebalance_id = 0,
			date = str(datetime.now()),
			coin = coin,
			side = 'buy',
			units = quantity,
			price_per_unit = price,
			fees = dollar_value * 0.0075,
			previous_units = 0,
			cumulative_units = quantity,
			transacted_value = dollar_value,
			previous_cost = 0,
			cost_of_transaction = 0,
			cost_per_unit = 0,
			cumulative_cost = dollar_value,
			gain_loss = 0,
			realised_pct = 0
		))
		session.commit()
