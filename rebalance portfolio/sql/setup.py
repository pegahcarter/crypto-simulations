from sqlalchemy import Column, Integer, DateTime, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine

Base = declarative_base()

class Porfolio(Base):
	__tablename__ = 'portfolio'

	coin			= Column(String(25), primary_key=True)
	current_price	= Column(Numeric(asdecimal=False))
	quantity		= Column(Numeric(asdecimal=False))
	dollar_value	= Column(Numeric(asdecimal=False))

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Transactions(Base):
	__tablename__ = 'transactions'

	trade_id		= Column(Integer, primary_key=True)
	rebalance_id	= Column(Integer)
	date			= Column(DateTime(timezone=True), server_default=func.now())
	# coin 			= Column(String(25), ForeignKey(portfolio.coin))
	side			= Column(String(25))
	ratio			= Column(String(50))
	price			= Column(Numeric(asdecimal=False))
	quantity		= Column(Numeric(asdecimal=False))
	dollar_value	= Column(Numeric(asdecimal=False))
	fees			= Column(Numeric(asdecimal=False))

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

engine = create_engine('sqlite:///rebalance.db')

Base.metadata.create_all(engine)
