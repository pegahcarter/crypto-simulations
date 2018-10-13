def Initialize():

	if Path(os.getcwd() + '/sql/transactions.db') and Path(os.getcwd() + '/sql/portfolio.db'):
		return

	import sql.setup
	engine = create_engine('sqlite:///dbs/sql/rebalance.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	for trade_id, coin in enumerate(coins):
		price, quantity, dollar_value = pull_coin_info(coin)

		session.add(Transactions(
			trade_id = trade_id,
			rebalance_id = 0,
			date = str(datetime.now()),
# 				coin = coin,
			side = 'buy',
			ratio = coin + '/USD',
			price = price,
			quantity = quantity,
			dollar_value = dollar_value
			fees = dollar_value * 0.0075
		))
		session.commit()

'''
		session.add(Portfolio(
			coin = coin,
			current_price = price,
			quantity = quantity,
			dollar_value = dollar_value
			))
		session.commit()
'''


if __name__ = '__main__':
	sys.exit('Error: do not run this program separately from rebalace.py.')
