from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, UUID
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from .database import Base
import uuid

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(PostgresUUID, unique=True, index=True, default=uuid.uuid4)
    company_id = Column(Integer, ForeignKey("companies.id"))
    repository_id = Column(String, nullable=True)  # Para tokens específicos de repositório
    is_active = Column(Boolean, default=True)
    payment_status = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    payment_id = Column(String, unique=True, index=True)  # ID do PayPal
    amount = Column(String)
    currency = Column(String)
    status = Column(String)
    payment_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class ValidationLog(Base):
    __tablename__ = "validation_logs"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"))
    payload = Column(JSON)
    result = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now()) 