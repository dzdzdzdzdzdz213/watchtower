import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Enum as SAEnum, Uuid
from sqlalchemy.orm import relationship
import enum

from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Severity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"

class AlertStatus(str, enum.Enum):
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Uuid(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    api_key = Column(Uuid(), unique=True, default=uuid.uuid4, index=True)
    plan = Column(String(20), default="free")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    logs = relationship("LogEntry", back_populates="organization", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="organization", cascade="all, delete-orphan")

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Uuid(), primary_key=True, default=uuid.uuid4)
    org_id = Column(Uuid(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    source_ip = Column(String(45), nullable=True)
    event_type = Column(String(100), nullable=True)
    severity = Column(SAEnum(Severity), nullable=False, default=Severity.info)
    raw_message = Column(Text, nullable=False)
    parsed_fields = Column(JSON, default=dict)
    hostname = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    organization = relationship("Organization", back_populates="logs")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Uuid(), primary_key=True, default=uuid.uuid4)
    org_id = Column(Uuid(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)
    severity = Column(SAEnum(Severity), nullable=False)
    description = Column(Text, nullable=False)
    source_ip = Column(String(45), nullable=True)
    affected_user = Column(String(255), nullable=True)
    log_count = Column(Integer, default=1)
    status = Column(SAEnum(AlertStatus), default=AlertStatus.open)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    organization = relationship("Organization", back_populates="alerts")
