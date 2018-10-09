import pandas as pd
def update_csv_transactions(folder_path):
	file_path = folder_path + 'transactions.csv'
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
