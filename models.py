from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Users(Base) :
    __tablename__ = 'users'

    i_key = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(50), unique=True, nullable=False)
    disabled = Column(Boolean, server_default='0', nullable=False)
    description = Column(String(50))

class Subscriber(Base) :
    __tablename__ = 'subscriber'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False)
    domain = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    email_address = Column(String(64), nullable=False)
    ha1 = Column(String(64), nullable=False)
    ha1_sha256 = Column(String(64), nullable=False)
    ha1_sha512t256 = Column(String(64), nullable=False)
    rpid = Column(String(64))

class Groups(Base) :
    __tablename__ = 'grp'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False)
    domain = Column(String(64), nullable=False)
    grp = Column(String(64), nullable=False)
    last_modified = Column(String(64), nullable=False)