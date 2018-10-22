# NOTE: using this as a template for rebalance.py.  It is outdated.  Once I know
# I can work with the SQL table correctly, I'll use this function again.

def Update(rebalance_num, session, order, transactions):

	trade_num = transactions['trade_num'].max() + 1
	ratio = order[???].split('/') # Since we are recording both coins
	sides = [???, ???]
	dollar_value = order[???]

	for coin, side in zip(ratio, sides):
		price = coin_price(coin)
		units = dollar_value / price
		try:
			temp = transactions.loc[transactions['coin'] == coin]
			previous_units = temp.at[len(temp)-1, 'cumulative_units']
			if side == 'buy':
				cumulative_units = previous_units + units
				gain_loss, realised_pct = 0, 0
			else:
				cumulative_units = previous_units - units


		# First transaction documented with coin
		except:
			previous_units, previous_cost, gain_loss, realised_pct = 0, 0, 0, 0
			cumulative_units = units
			cost_per_unit = price



		trade_data =
		session.add(Transactions(
			trade_num = trade_num,
			rebalance_num = rebalance_num,
			date = datetime.now(),
			coin = coin,
			side = side,
			units = quantity,
			price_per_unit = dollar_value/quantity,
			fees = dollar_value * .0075,
			previous_units = ??,
			cumulative_units = ??,
			transacted_value = dollar_value,
			previous_cost = ??,
			cost_of_transaction = ??,
			cost_per_unit = ??,
			cumulative_cost = ??,
			gain_loss = ??,
			realised_pct = ??
		))
		session.commit()
