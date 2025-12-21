"""
Base Models - Common fields for all entities
"""
from sqlalchemy import Column, DateTime, Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from shared.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)


class TenantMixin:
    """Mixin for multi-tenancy support"""
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)


class AuditMixin:
    """Mixin for audit trail"""
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
