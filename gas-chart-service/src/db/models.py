from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func
from src.db.database import Base

class ChartTemplate(Base):
    __tablename__ = "chart_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    layout = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FavoriteIndicator(Base):
    __tablename__ = "favorite_indicators"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    indicator = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
