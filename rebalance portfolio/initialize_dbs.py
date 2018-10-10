class InitalizeDB:

	def initialize_csv():

		portfolio = []
		transactions = []
		trade_id = 1
		for coin in coins:
			price, quantity, dollar_value = pull_coin_info(coin)
			portfolio.append([
				coin,					# coin
				price,					# current_price
				quantity,				# quantity
				dollar_value			# dollar_value
			])
			transactions.append([
				trade_id,				# trade_id
				0, 						# rebalance_id
				str(datetime.now()),	# date
				coin,					# coin
				'buy', 					# side
				coin + '/USD',			# ratio
				price, 					# price
				quantity, 				# quantity
				dollar_value, 			# dollar_value
				dollar_value * 0.0075	# fees
			])
			trade_id += 1

		portfolio_pd = pd.DataFrame(
			portfolio,
			columns = [
				'coin',
				'current_price',
				'quantity',
				'dollar_value'
			]
		)

		transactions_pd = pd.DataFrame(
			transactions,
			columns = [
				'trade_id',
				'rebalance_id',
				'date',
				'coin',
				'side',
				'ratio',
				'price',
				'quantity'
				'dollar_value',
				'fees'
			]
		)

		portfolio_pd.to_csv('/dbs/csv/portfolio.csv')
		transactions_pd.to_csv('/dbs/csv/transactions.csv')
		# End of function

	def initialize_sql():
		engine = create_engine('sqlite:///dbs/sql/rebalance.db')
		Base.metadata.bind = engine
		DBSession = sessionmaker(bind=engine)
		session = DBSession()

		for coin in coins:
			price, quantity, dollar_value = pull_coin_info(coin)
			session.add(Portfolio(
				coin = coin,
				current_price = price,
				quantity = quantity,
				dollar_value = dollar_value
			))
			session.commit()
			session.add(Transactions(
				rebalance_id = 0,
				date = str(datetime.now()),
				coin = coin,
				side = 'buy',
				ratio = coin + '/USD',
				price = price,
				quantity = quantity,
				dollar_value = dollar_value
				fees = dollar_value * 0.0075
			))
			session.commit()
	# End of function

	def initialize_mongo():
		client = MongoClient()
		mongo_db = client['rebalance']
		for coin in coins:
			price, quantity, dollar_value = pull_coin_info(coins)
			mongo_db.insert_one({
				coin: {
					'quantity': quantity,
					'current_price': price,
					'dollar_value': dollar_value,
					'transactions': {
						'trade_id': 0,
						'rebalance_id': 0,
						'date': date,
						'side': 'buy',
						'coin_used_to_buy': 'USD',
						'price': price,
						'quantity': quantity,
						'dollar_value': dollar_value,
						'fees': dollar_value * 0.0075
					}
				}
			})
	# End of function
