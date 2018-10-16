import os
import sqlite3
from sqlite3 import Error
from pathlib import Path



def create_connection(db_file):
	try:
		conn = sqlite3.connect(db_file)
		print(sqlite3.version)
	except Error as e:
		print(e)
	finally:
		conn.close()

if __name__ != '__main__':
	if not Path(os.getcwd() + '/sql/portfolio.db'):
		create_connection(os.getcwd() + '/sql/portfolio.db')




from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
 
