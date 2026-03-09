from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer, DateTime
import datetime
import uuid

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: f"ord_{uuid.uuid4().hex[:10]}")
    user_id = Column(String, index=True)
    symbol = Column(String, index=True)
    action = Column(String)
    order_type = Column(String)
    volume = Column(Float)
    req_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    status = Column(String, default="pending") # pending, filled, canceled, rejected
    fill_price = Column(Float, nullable=True)
    fill_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
class Position(Base):
    __tablename__ = "positions"
    
    id = Column(String, primary_key=True, default=lambda: f"pos_{uuid.uuid4().hex[:10]}")
    user_id = Column(String, index=True)
    order_id = Column(String, unique=True)
    symbol = Column(String)
    action = Column(String)
    volume = Column(Float)
    open_price = Column(Float)
    current_price = Column(Float, nullable=True)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    profit = Column(Float, default=0.0)
    status = Column(String, default="open") # open, closed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
