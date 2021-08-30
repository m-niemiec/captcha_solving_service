from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()


class CreditsTransaction(Base):
    __tablename__ = 'credits_transaction'
    id = Column(Integer, primary_key=True, index=True)
    credit_amount = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User')


class CaptchaSolveQuery(Base):
    __tablename__ = 'captcha_solve_query'
    id = Column(Integer, primary_key=True, index=True)
    captcha_metadata = Column(String)
    captcha_type = Column(String)
    captcha_solution = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    credit_balance = Column(Integer)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
