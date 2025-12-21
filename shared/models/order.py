"""
Order Models - Auftrags- und Angebotsverwaltung
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class QuoteStatus(enum.Enum):
    """Angebotsstatus"""
    DRAFT = "draft"  # Entwurf
    SENT = "sent"  # Versendet
    VIEWED = "viewed"  # Angesehen
    ACCEPTED = "accepted"  # Angenommen
    REJECTED = "rejected"  # Abgelehnt
    EXPIRED = "expired"  # Abgelaufen
    REVISED = "revised"  # Überarbeitet


class OrderStatus(enum.Enum):
    """Auftragsstatus"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"  # Bestätigt
    IN_PROGRESS = "in_progress"  # In Bearbeitung
    PARTIAL_DELIVERED = "partial_delivered"  # Teilgeliefert
    DELIVERED = "delivered"  # Geliefert/Montiert
    COMPLETED = "completed"  # Abgeschlossen
    INVOICED = "invoiced"  # Abgerechnet
    CANCELLED = "cancelled"  # Storniert


class Quote(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Angebot"""
    __tablename__ = "quotes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_number = Column(String(50), nullable=False, index=True)
    
    # Relations
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    
    # Status
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)
    
    # Dates
    quote_date = Column(Date, default=date.today)
    valid_until = Column(Date, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    # Reference
    reference = Column(String(255), nullable=True)  # Kundenprojekt-Referenz
    subject = Column(String(255), nullable=True)  # Betreff
    
    # Content
    intro_text = Column(Text, nullable=True)  # Einleitungstext
    closing_text = Column(Text, nullable=True)  # Schlusstext
    
    # Terms
    payment_terms = Column(Text, nullable=True)
    delivery_terms = Column(Text, nullable=True)
    warranty_terms = Column(Text, nullable=True)
    
    # Financial
    subtotal = Column(String(20), default="0")  # Zwischensumme
    discount_percent = Column(String(10), default="0")
    discount_amount = Column(String(20), default="0")
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")  # Gesamtbetrag
    
    # Internal
    margin_percent = Column(String(10), nullable=True)
    cost_estimate = Column(String(20), nullable=True)
    
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Version Control
    version = Column(Integer, default=1)
    parent_quote_id = Column(UUID(as_uuid=True), ForeignKey('quotes.id'), nullable=True)
    
    # Custom Fields
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="quote")


class QuoteItem(Base, TimestampMixin):
    """Angebotsposition"""
    __tablename__ = "quote_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id = Column(UUID(as_uuid=True), ForeignKey('quotes.id'), nullable=False)
    
    position = Column(Integer, nullable=False)  # Positionsnummer
    item_type = Column(String(50), default="product")  # product, service, text, subtotal
    
    # Reference to material (optional)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=True)
    
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
    subtotal = Column(String(20), default="0")
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")
    
    # Internal
    cost_price = Column(String(20), nullable=True)
    margin_percent = Column(String(10), nullable=True)
    
    # Grouping
    group_name = Column(String(100), nullable=True)  # z.B. "Dachstuhl", "Material", "Montage"
    is_optional = Column(Boolean, default=False)  # Alternative Position
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    quote = relationship("Quote", back_populates="items")
    material = relationship("Material")


class Order(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Auftrag"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), nullable=False, index=True)
    
    # Relations
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    quote_id = Column(UUID(as_uuid=True), ForeignKey('quotes.id'), nullable=True)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Dates
    order_date = Column(Date, default=date.today)
    confirmed_date = Column(Date, nullable=True)
    planned_start = Column(Date, nullable=True)
    planned_end = Column(Date, nullable=True)
    actual_start = Column(Date, nullable=True)
    actual_end = Column(Date, nullable=True)
    
    # Reference
    reference = Column(String(255), nullable=True)
    customer_order_number = Column(String(100), nullable=True)
    subject = Column(String(255), nullable=True)
    
    # Delivery Address
    delivery_street = Column(String(255), nullable=True)
    delivery_street_number = Column(String(20), nullable=True)
    delivery_postal_code = Column(String(20), nullable=True)
    delivery_city = Column(String(100), nullable=True)
    delivery_country = Column(String(100), default="Deutschland")
    
    # Terms
    payment_terms = Column(Text, nullable=True)
    delivery_terms = Column(Text, nullable=True)
    
    # Financial
    subtotal = Column(String(20), default="0")
    discount_percent = Column(String(10), default="0")
    discount_amount = Column(String(20), default="0")
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")
    
    # Payment Tracking
    invoiced_amount = Column(String(20), default="0")
    paid_amount = Column(String(20), default="0")
    
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Custom Fields
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    quote = relationship("Quote", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="order")


class OrderItem(Base, TimestampMixin):
    """Auftragsposition"""
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    
    position = Column(Integer, nullable=False)
    item_type = Column(String(50), default="product")
    
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=True)
    quote_item_id = Column(UUID(as_uuid=True), ForeignKey('quote_items.id'), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    quantity = Column(String(20), default="1")
    delivered_quantity = Column(String(20), default="0")
    invoiced_quantity = Column(String(20), default="0")
    unit = Column(String(20), default="STK")
    
    unit_price = Column(String(20), default="0")
    discount_percent = Column(String(10), default="0")
    tax_rate = Column(String(10), default="19")
    
    subtotal = Column(String(20), default="0")
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")
    
    cost_price = Column(String(20), nullable=True)
    
    group_name = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    material = relationship("Material")


class PurchaseOrder(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Bestellung (Einkauf)"""
    __tablename__ = "purchase_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_number = Column(String(50), nullable=False, index=True)
    
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    
    status = Column(String(50), default="draft")  # draft, sent, confirmed, partial_received, received, cancelled
    
    order_date = Column(Date, default=date.today)
    expected_delivery = Column(Date, nullable=True)
    actual_delivery = Column(Date, nullable=True)
    
    delivery_address = Column(Text, nullable=True)
    
    subtotal = Column(String(20), default="0")
    tax_amount = Column(String(20), default="0")
    total = Column(String(20), default="0")
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier")
    project = relationship("Project")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base, TimestampMixin):
    """Bestellposition"""
    __tablename__ = "purchase_order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey('purchase_orders.id'), nullable=False)
    
    position = Column(Integer, nullable=False)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=True)
    
    title = Column(String(255), nullable=False)
    supplier_article_number = Column(String(100), nullable=True)
    
    quantity = Column(String(20), default="1")
    received_quantity = Column(String(20), default="0")
    unit = Column(String(20), default="STK")
    
    unit_price = Column(String(20), default="0")
    tax_rate = Column(String(10), default="19")
    
    subtotal = Column(String(20), default="0")
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    material = relationship("Material")
