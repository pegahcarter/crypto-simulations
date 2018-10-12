def Update(db1, db2, db3):

	def update_csv():
		if not db1:
			return

		file_path = folder + '/csv/transactions.csv'
		transaction_db = pd.read_csv(file_path)

		transaction_db.append({
			'trade_id':trade_id,
			'rebalance_id':rebalance_id,
			'date': str(datetime.now()),
			'coin': coin,
			'side': side,
			'ratio': ratio,
			'quantity': quantity,
			'dollar_value': dollar_value,
			'fees': dollar_value * .0075,
		}, ignore_index=True)
		transaction_db.to_csv(file_path)
	# End of Function


	def update_sql():
		if not db2:
			return

		session.add(Transactions(
			trade_id = trade_id,
			rebalance_id = rebalance_id,
			date = str(datetime.now()),
			coin = coin,
			side = side,
			ratio = ratio,
			price = dollar_value/quantity
			quantity = quantity,
			dollar_value = dollar_value,
			fees = dollar_value * .0075
		))
		session.commit()
	# End of function


	def update_mongo():
		if not db3:
			return

		conn = 'mongodb://localhost:27017'
		client = MongoClient(conn)
		db = client.transactions

		db.insert_one({
			'trade_id': trade_id,
			'rebalance_id': rebalance_id,
			'date': str(datetime.now()),
			'side': side,
			'ratio': ratio,
			'price': dollar_value/quantity,
			'quantity': quantity,
			'dollar_value': dollar_value,
			'fees': dollar_value * 0.0075
		})
	# End of function

	update_csv()
	update_sql()
	update_mongo()

if __name__ == '__main__':
	sys.exit('Error: do not run this program outside of rebalance.py')
