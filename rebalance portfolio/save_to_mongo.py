from bs4 import BeautifulSoup
import requests
import pymongo

# Initialize PyMongo to work with MongoDB
conn = 'mongodb://localhost:27107'
client = pymongo.MongoClient(conn)

# Define database & collection
db = client.transaction_db
transactions = db.transaction_db.find()

db.transaction_db.insert_one(
    {
        'transaction_id': 1,
        'rebalance_id': 1,
        'date': '1/1/2018',
        'side': 'buy',
        'ticker1': 'BTC',
        'ticker2': 'USD',
        'quantity': 1.000,
        'dollar_value': 5,000,
        'fees': 12.50
    }
)
