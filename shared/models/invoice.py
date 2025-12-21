"""
Invoice Models - Rechnungsverwaltung
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class InvoiceType(enum.Enum):
    """Rechnungstyp"""
    INVOICE = "invoice"  # Rechnung
    PARTIAL_INVOICE = "partial_invoice"  # Teilrechnung
    FINAL_INVOICE = "final_invoice"  # Schlussrechnung
    CREDIT_NOTE = "credit_note"  # Gutschrift
    CANCELLATION = "cancellation"  # Stornorechnung
    PROFORMA = "proforma"  # Proforma-Rechnung
    ADVANCE = "advance"  # Anzahlungsrechnung


class InvoiceStatus(enum.Enum):
    """Rechnungsstatus"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL_PAID = "partial_paid"  # Teilweise bezahlt
    PAID = "paid"  # Bezahlt
    OVERDUE = "overdue"  # Überfällig
    CANCELLED = "cancelled"  # Storniert
    REMINDED = "reminded"  # Gemahnt


class PaymentMethod(enum.Enum):
    """Zahlungsart"""
    BANK_TRANSFER = "bank_transfer"  # Überweisung
    CASH = "cash"  # Bar
    CHECK = "check"  # Scheck
    CREDIT_CARD = "credit_card"
    DIRECT_DEBIT = "direct_debit"  # Lastschrift
    PAYPAL = "paypal"
    OTHER = "other"


class Invoice(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Rechnung"""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Relations
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    
    # Type & Status
    invoice_type = Column(Enum(InvoiceType), default=InvoiceType.INVOICE)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Dates
    invoice_date = Column(Date, default=date.today)
    due_date = Column(Date, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Reference to partial/final invoicing
    parent_invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=True)
    
    # Reference
    reference = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=True)
    
    # Billing Address (snapshot at invoice time)
    billing_company = Column(String(255), nullable=True)
    billing_name = Column(String(255), nullable=True)
    billing_street = Column(String(255), nullable=True)
    billing_street_number = Column(String(20), nullable=True)
    billing_postal_code = Column(String(20), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_country = Column(String(100), default="Deutschland")
    
    # Content
    intro_text = Column(Text, nullable=True)
    closing_text = Column(Text, nullable=True)
    
    # Financial
    subtotal = Column(String(20), default="0")  # Netto
    discount_percent = Column(String(10), default="0")
    discount_amount = Column(String(20), default="0")
    
    # Tax Details
    tax_rate_1 = Column(String(10), default="19")
    tax_base_1 = Column(String(20), default="0")
    tax_amount_1 = Column(String(20), default="0")
    tax_rate_2 = Column(String(10), nullable=True)  # For reduced rate items
    tax_base_2 = Column(String(20), nullable=True)
    tax_amount_2 = Column(String(20), nullable=True)
    
    total_tax = Column(String(20), default="0")
    total = Column(String(20), default="0")  # Brutto
    
    # Payment
    paid_amount = Column(String(20), default="0")
    remaining_amount = Column(String(20), default="0")
    
    # Payment Terms (in days)
    payment_terms_days = Column(Integer, default=30)
    early_payment_discount_days = Column(Integer, nullable=True)  # Skonto Tage
    early_payment_discount_percent = Column(String(10), nullable=True)  # Skonto %
    
    # Bank Details (for invoice)
    bank_name = Column(String(255), nullable=True)
    iban = Column(String(50), nullable=True)
    bic = Column(String(20), nullable=True)
    
    # Dunning
    dunning_level = Column(Integer, default=0)  # 0=keine, 1=1.Mahnung, 2=2.Mahnung, etc.
    last_dunning_date = Column(Date, nullable=True)
    
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # PDF Storage
    pdf_path = Column(String(500), nullable=True)
    
    # Custom Fields
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    order = relationship("Order", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base, TimestampMixin):
    """Rechnungsposition"""
    __tablename__ = "invoice_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    
    position = Column(Integer, nullable=False)
    item_type = Column(String(50), default="product")  # product, service, text, subtotal
    
    # Reference
    order_item_id = Column(UUID(as_uuid=True), ForeignKey('order_items.id'), nullable=True)
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Quantities
    quantity = Column(String(20), default="1")
    unit = Column(String(20), default="STK")
    
    # Pricing
    unit_price = Column(String(20), default="0")
    discount_percent = Column(String(10), default="0")
    tax_rate = Column(String(10), default="19")
    
    # Calculated
    subtotal = Column(String(20), default="0")  # Netto
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")  # Brutto
    
    # Grouping
    group_name = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")


class RecurringInvoice(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Wiederkehrende Rechnung (z.B. für Wartungsverträge)"""
    __tablename__ = "recurring_invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    
    name = Column(String(255), nullable=False)
    
    # Schedule
    frequency = Column(String(50), nullable=False)  # monthly, quarterly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    next_invoice_date = Column(Date, nullable=True)
    
    # Template
    subject = Column(String(255), nullable=True)
    intro_text = Column(Text, nullable=True)
    closing_text = Column(Text, nullable=True)
    
    subtotal = Column(String(20), default="0")
    tax_rate = Column(String(10), default="19")
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")
    
    payment_terms_days = Column(Integer, default=30)
    
    is_active = Column(Boolean, default=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    items = relationship("RecurringInvoiceItem", back_populates="recurring_invoice", cascade="all, delete-orphan")


class RecurringInvoiceItem(Base, TimestampMixin):
    """Position einer wiederkehrenden Rechnung"""
    __tablename__ = "recurring_invoice_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recurring_invoice_id = Column(UUID(as_uuid=True), ForeignKey('recurring_invoices.id'), nullable=False)
    
    position = Column(Integer, nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    quantity = Column(String(20), default="1")
    unit = Column(String(20), default="STK")
    unit_price = Column(String(20), default="0")
    tax_rate = Column(String(10), default="19")
    
    subtotal = Column(String(20), default="0")
    
    # Relationships
    recurring_invoice = relationship("RecurringInvoice", back_populates="items")
