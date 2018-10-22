import pandas as pd
import os
import sys
import ccxt
from datetime import datetime
from functions import coin_price
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup import Transactions, Base

# Function to update our sql database with the trade that was just made
def Update(dual_trade, coins, sides, quantities, t, session):

	# Add a transaction for each side of the trade ratio to keep cost and realised/unrealised
	# numbers in $.  This will help when we analyze overall performance.
	for coin, side, quantity in zip(trade_coins, trade_sides, trade_quantities):
		try:
			# Small temporary dataframe of all transactions for the coin.  If it's
			# the first trade that we have in our data for the coin, we need an
			# error handler.
			temp = t.loc[t['coin'] == coin]
			previous_units = temp['cumulative_units'].values[len(temp)-1]
			previous_cost = temp['cumulative_cost'].values[len(temp)-1]

			if side == 'buy':
				transacted_value = trade_dollars * (1 + .0075)
				cumulative_cost = previous_cost + transacted_value
				cumulative_units = previous_units + quantity

				cost_of_transaction = 0
				cost_per_unit = 0

				gain_loss = 0
				realised_pct = 0
			else:
				transacted_value = trade_dollars * (1 - .0075)
				cumulative_cost = previous_cost - transacted_value
				cumulative_units = previous_units - quantity

				cost_of_transaction = previous_cost * quantity/previous_units
				cost_per_unit = previous_cost / previous_units

				gain_loss = transacted_value - cost_of_transaction
				realised_pct = gain_loss / cost_of_transaction

				# push to SQL
				session.add(Transactions(
					rebalance_num = rebalance_num,
					date = datetime.now(),
					coin = coin,
					side = side,
					units = quantity,
					price_per_unit = trade_dollars / quantity,
					fees = dollar_value * .0075,
					previous_units = previous_units,
					cumulative_units = cumulative_units,
					transacted_value = transacted_value,
					previous_cost = previous_cost,
					cost_of_transaction = cost_of_transaction,
					cost_per_unit = cost_per_unit,
					cumulative_cost = cumulative_cost,
					gain_loss = gain_loss,
					realised_pct = realised_pct
				))
				session.commit()

				# Don't log the BTC transaction if it's a dual trade
				if dual_trade:
					break

		# It's our first documented trade with the coin, so we need to add it uniquely
		except:
			balance = exchange.fetchBalance()
			btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])
			price = coin_price(coin)
			quantity = balance[coin]['total']
			dollar_value = price * quantity

			# NOTE: this session.add is redundant -- it's the exact same in initialize.py.
			# How do I fix this?
			session.add(Transactions(
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

		# Refresh our dataframe with the updated SQL transactions
		engine = create_engine('sqlite:///../sql/transactions.db')
		Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)
		session = DBSession()
		t = pd.read_sql(sql=query, con=engine)

	return t
