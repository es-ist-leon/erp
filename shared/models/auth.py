"""
User and Authentication Models
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin


# User-Role Association Table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

# Role-Permission Association Table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Tenant (for multi-company support)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True)
    
    # User's personal database name (created on first login)
    database_name = Column(String(100), nullable=True, unique=True)
    
    # Auth tracking
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(String(10), default="0")
    locked_until = Column(DateTime, nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    tenant = relationship("Tenant", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class Role(Base, TimestampMixin):
    """Role model for authorization"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System roles can't be deleted
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base, TimestampMixin):
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "projects:read"
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    resource = Column(String(100), nullable=False)  # e.g., "projects"
    action = Column(String(50), nullable=False)  # e.g., "read", "write", "delete"
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class RefreshToken(Base, TimestampMixin):
    """Refresh token for JWT authentication"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(500), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class Tenant(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant model for multi-company support - Enterprise Holzbau"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # === UNTERNEHMENSDATEN ===
    company_name = Column(String(255), nullable=True)
    legal_form = Column(String(50), nullable=True)
    founding_date = Column(DateTime, nullable=True)
    tax_id = Column(String(50), nullable=True)
    tax_number = Column(String(50), nullable=True)
    trade_register = Column(String(100), nullable=True)
    trade_register_court = Column(String(100), nullable=True)
    chamber_of_crafts = Column(String(100), nullable=True)
    chamber_membership_number = Column(String(50), nullable=True)
    ceo_name = Column(String(100), nullable=True)
    authorized_signatories = Column(Text, nullable=True)
    
    # === KONTAKT ===
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    phone_secondary = Column(String(30), nullable=True)
    fax = Column(String(30), nullable=True)
    mobile = Column(String(30), nullable=True)
    website = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    facebook_url = Column(String(255), nullable=True)
    instagram_url = Column(String(255), nullable=True)
    xing_url = Column(String(255), nullable=True)
    
    # === ADRESSE ===
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    address_addition = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Deutschland")
    country_code = Column(String(3), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    altitude = Column(String(20), nullable=True)
    
    # === BANKVERBINDUNGEN ===
    bank_name = Column(String(100), nullable=True)
    iban = Column(String(34), nullable=True)
    bic = Column(String(11), nullable=True)
    bank_account_holder = Column(String(100), nullable=True)
    secondary_bank_name = Column(String(100), nullable=True)
    secondary_iban = Column(String(34), nullable=True)
    secondary_bic = Column(String(11), nullable=True)
    paypal_email = Column(String(255), nullable=True)
    stripe_account_id = Column(String(100), nullable=True)
    
    # === ZERTIFIZIERUNGEN ===
    certifications = Column(Text, nullable=True)
    quality_management = Column(String(100), nullable=True)
    environmental_certification = Column(String(100), nullable=True)
    safety_certification = Column(String(100), nullable=True)
    master_craftsman_certificate = Column(String(100), nullable=True)
    master_craftsman_name = Column(String(100), nullable=True)
    guild_membership = Column(String(100), nullable=True)
    trade_association = Column(String(100), nullable=True)
    
    # === VERSICHERUNGEN ===
    liability_insurance = Column(String(100), nullable=True)
    liability_coverage = Column(String(50), nullable=True)
    building_insurance = Column(String(100), nullable=True)
    professional_indemnity = Column(String(100), nullable=True)
    insurance_policy_number = Column(String(50), nullable=True)
    insurance_valid_until = Column(DateTime, nullable=True)
    
    # === BETRIEBSDATEN ===
    employee_count = Column(String(10), nullable=True)
    apprentice_count = Column(String(10), nullable=True)
    annual_revenue = Column(String(50), nullable=True)
    production_facility_address = Column(Text, nullable=True)
    storage_facility_address = Column(Text, nullable=True)
    wood_types_offered = Column(Text, nullable=True)
    specializations = Column(Text, nullable=True)
    service_radius_km = Column(String(10), nullable=True)
    
    # === RECHNUNGSWESEN ===
    invoice_prefix = Column(String(20), nullable=True)
    invoice_number_format = Column(String(50), nullable=True)
    next_invoice_number = Column(String(10), nullable=True)
    offer_prefix = Column(String(20), nullable=True)
    offer_validity_days = Column(String(10), nullable=True)
    default_payment_terms = Column(String(10), nullable=True)
    default_vat_rate = Column(String(10), nullable=True)
    default_currency = Column(String(3), default="EUR")
    invoice_footer_text = Column(Text, nullable=True)
    
    # === E-MAIL ===
    email_signature = Column(Text, nullable=True)
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(String(10), nullable=True)
    smtp_user = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True)
    smtp_use_tls = Column(Boolean, nullable=True)
    
    # === ARBEITSZEITEN ===
    working_hours_start = Column(String(10), nullable=True)
    working_hours_end = Column(String(10), nullable=True)
    working_days = Column(String(20), nullable=True)
    
    # === SYSTEM ===
    fiscal_year_start_month = Column(String(10), nullable=True)
    data_retention_years = Column(String(10), nullable=True)
    gdpr_contact_email = Column(String(255), nullable=True)
    
    # === BRANDING ===
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#2563eb")
    
    # === SUBSCRIPTION ===
    subscription_plan = Column(String(50), default="starter")
    subscription_expires = Column(DateTime, nullable=True)
    max_users = Column(String(10), default="5")
    
    is_active = Column(Boolean, default=True)
    
    # Custom Fields
    custom_fields = Column(Text, nullable=True)
    extra_data = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
