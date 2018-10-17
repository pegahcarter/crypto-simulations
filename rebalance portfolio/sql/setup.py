import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

if Path(os.getcwd() + '/sql/portfolio.db'):
	return

Base = declarative_base()

class Portfolio(Base):
    __tablename__ = 'portfolio'

	coin = Column(String(10), primary_key=True))
	current_price = Column(Float(10, 2))
	units = Column(Float(10, 2))
	avg_cost = Column(Float(10, 2))
    unrealised_amt = Column(Float(10, 2))
	unrealised_pct =
	realised_amt = Column(Float(10, 2))
	realised_pct =
	gain_loss = Column(Float(10, 2))
	mkt_value = Column(Float(10, 2))

class Transactions(Base):
    __tablename__ = 'transactions'

	date =
	rebalance_num = Column(Integer)
	coin = Column(String(10), ForeignKey('portfolio.coin'))
	side =
	units =
	

	portfolio = relationship(Portfolio)



    id = Column(Integer, primary_key=True)
    street_name = Column(String(250))
    street_number = Column(String(250))
    post_code = Column(String(250), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship(Person)


engine = create_engine('sqlite:///sql/crypto.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
