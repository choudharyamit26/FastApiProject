from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    func,
    MetaData,
)
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.config.config import Base, engine

metadata = MetaData()

# Association Table for Many-to-Many Relationship between Order and Product
order_product_association = Table(
    "order_products",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("quantity", Integer, nullable=False),  # Store quantity per product
)


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
    # One-to-many relationship with orders
    orders = relationship("Order", back_populates="user")


# Order Model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="orders")
    products = relationship(
        "Product", secondary=order_product_association, back_populates="orders"
    )


# Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=False)

    orders = relationship(
        "Order", secondary=order_product_association, back_populates="products"
    )


# Base.metadata.drop_all(engine) # use only in dev environment
Base.metadata.create_all(engine, checkfirst=True)
