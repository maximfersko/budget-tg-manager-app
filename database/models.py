from sqlalchemy import Column, Integer, String, BigInteger, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from database.engine import Base


class User(Base):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True)
    username = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    operations = relationship("Operation", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(tg_id={self.tg_id}, username={self.username})>"


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    is_income = Column(Boolean, default=False)
    emoji = Column(String(10), nullable=True)
    
    user = relationship("User", back_populates="categories")
    operations = relationship("Operation", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, is_income={self.is_income})>"


class Operation(Base):
    __tablename__ = "operations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    raw_category = Column(String(100), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="RUB")
    description = Column(String, nullable=True)
    mcc = Column(String(10), nullable=True)
    is_income = Column(Boolean, nullable=False)
    bank_name = Column(String(50), nullable=False)
    
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="operations")
    category = relationship("Category", back_populates="operations")

    def __repr__(self):
        return (f"Operation(id={self.id}, user_id={self.user_id}, category_id={self.category_id}, "
                f"amount={self.amount}, is_income={self.is_income}, bank_name={self.bank_name}, "
                f"date={self.date}, description={self.description})")
