from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    color = Column(String, index=True)
    size = Column(String, index=True)
    price = Column(Integer, index=True, default=0)
    quantity = Column(Integer, default=0)


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    discount_percent = Column(Numeric(5, 2), nullable=False)
    active = Column(Boolean, default=True)
    start_date = Column(String, index=True)
    end_date = Column(String, index=True)
    products = Column(Integer, ForeignKey("products.id"))
