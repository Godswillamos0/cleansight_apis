from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    token_amount = Column(Float, default=0.0)
    email = Column(String, unique=True)
    profile_picture = Column(String, nullable=True)
    hashed_password = Column(String)
    
    
class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    type = Column(String)  # 'donation' or 'purchase'
    created_at = Column(DateTime)
    description = Column(String, nullable=True)
    
    
