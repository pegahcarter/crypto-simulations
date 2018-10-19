import os
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Portfolio(Base):
	__tablename__ = 'portfolio'

	coin = Column(String(10), primary_key=True)
	current_price = Column(Float(10, 2))
	units = Column(Float(10, 2))
	avg_cost = Column(Float(10, 2))
	unrealised_amt = Column(Float(10, 2))
	unrealised_pct = Column(Float(10, 2))
	realised_amt = Column(Float(10, 2))
	realised_pct = Column(Float(10, 2))
	gain_loss = Column(Float(10, 2))
	mkt_value = Column(Float(10, 2))

class Transactions(Base):
	__tablename__ = 'transactions'

	trade_num = Column(Integer, primary_key=True)
	rebalance_num = Column(Integer)
	date = Column(DateTime, default=datetime.utcnow)
	coin = Column(String(10), ForeignKey('portfolio.coin'))
	side = Column(String(10))
	units = Column(Float(10,2))
	price_per_unit = Column(Float(10,2))
	fees = Column(Float(10,2))
	previous_units = Column(Float(10,2))
	cumulative_units = Column(Float(10,2))
	transacted_value = Column(Float(10,2))
	previous_cost = Column(Float(10,2))
	cost_of_transaction = Column(Float(10,2))
	cost_per_unit = Column(Float(10,2))
	cumulative_cost = Column(Float(10,2))
	gain_loss = Column(Float(10,2))
	realised_pct = Column(Float(10,2))
	portfolio = relationship(Portfolio)

# Create an engine that stores data in our local directory file
engine = create_engine('sqlite:///crypto.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
