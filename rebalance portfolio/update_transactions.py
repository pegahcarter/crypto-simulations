import pandas as pd
import sqlite3

class Update_Transactions:

	def __init__(self, name):
        self.name = name

	def update_csv_transactions():
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


	def update_sql_transactions():
		session.add(Transactions(
			trade_id = trade_id,
			rebalance_id = rebalance_id,
			date = str(datetime.now()),
			coin = coin,
			side = side,
			ratio = ratio,
			quantity = quantity,
			dollar_value = dollar_value,
			fees = dollar_value * .0075
		))
		session.commit()
	# End of function


	def update_mongo_transactions(self):





	# End of function
