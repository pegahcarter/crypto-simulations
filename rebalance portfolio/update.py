def Update():

	if side == 'buy':

	else:

	session.add(Transactions(
		trade_num = trade_id,
		rebalance_num = rebalance_id,
		date = str(datetime.now()),
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
