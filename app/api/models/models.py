from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, MetaData

from app.config.config import Base, engine

metadata = MetaData()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True, default=None)
    registered_at = Column(DateTime, nullable=True, default=None)
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


# Base.metadata.drop_all(engine) # use only in dev environment
Base.metadata.create_all(engine, checkfirst=True)
