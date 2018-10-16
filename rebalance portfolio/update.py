def Update():

	session.add(Transactions(
		trade_id = trade_id,
		rebalance_id = rebalance_id,
		date = str(datetime.now()),
		coin = coin,
		side = side,
		ratio = ratio,
		price = dollar_value/quantity,
		quantity = quantity,
		dollar_value = dollar_value,
		fees = dollar_value * .0075
	))
	session.commit()

if __name__ == '__main__':
	sys.exit('Error: do not run this program outside of rebalance.py')
