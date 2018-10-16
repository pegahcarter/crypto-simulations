import os
import sys


def Initialize():

	if Path(os.getcwd() + '/sql/rebalance.db'):
		return

	import sql.setup
	db = create_engine(os.getcwd() + '/sql/rebalance.db')

"""
CREATE TABLE portfolio (
	coin TEXT PRIMARY KEY		NOT NULL,
	quantity integer
);
"""


	for trade_id, coin in enumerate(coins):
		price, quantity, dollar_value = pull_coin_info(coin)

		session.add(Portfolio(
		coin = coin,
		current_price = price,
		quantity = quantity,
		dollar_value = dollar_value
		))
		session.commit()

		session.add(Transactions(
			trade_id = trade_id,
			rebalance_id = 0,
			date = str(datetime.now()),
			coin = coin,
			side = 'buy',
			ratio = coin + '/USD',
			price = price,
			quantity = quantity,
			dollar_value = dollar_value,
			fees = dollar_value * 0.0075
		))
		session.commit()


if __name__ != '__main__':
	sys.exit('Error: do not run this program separately from rebalace.py.')
