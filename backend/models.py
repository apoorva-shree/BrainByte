from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    NGO = "ngo"
    DONOR = "donor"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    organization_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary (excluding password)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "organization_name": self.organization_name,
            "phone": self.phone,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class FoodItem(Base):
    __tablename__ = "food_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), default="units")
    expiry_date = Column(DateTime, nullable=False, index=True)
    location = Column(String(255), default="Not specified")
    added_date = Column(DateTime, default=func.now(), nullable=False)
    consumed = Column(Boolean, default=False, index=True)
    consumed_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, nullable=True)  # Links to donor/ngo who added item
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "unit": self.unit,
            "expiryDate": self.expiry_date.isoformat() if self.expiry_date else None,
            "location": self.location,
            "addedDate": self.added_date.isoformat() if self.added_date else None,
            "consumed": self.consumed,
            "consumedDate": self.consumed_date.isoformat() if self.consumed_date else None,
            "userId": str(self.user_id) if self.user_id else None
        }