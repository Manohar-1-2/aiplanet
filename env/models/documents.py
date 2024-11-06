from sqlalchemy import Boolean, Column, Integer, String,Date
from sqlalchemy.sql import func
from .database import Base


class IndexedData(Base):
    __tablename__ = "indexed_data"
    filename = Column(String, primary_key=True, index=True)
    indexed_text = Column(String)
