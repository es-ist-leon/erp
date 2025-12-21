"""
Customer Models - Kunden und Kontakte
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class CustomerType(enum.Enum):
    PRIVATE = "private"  # Privatkunde
    BUSINESS = "business"  # Geschäftskunde
    PUBLIC = "public"  # Öffentliche Hand


class CustomerStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"  # Interessent
    BLOCKED = "blocked"


class Customer(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Kunde - Enterprise-Level mit allen Details"""
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_number = Column(String(50), nullable=False, index=True)  # Kundennummer
    
    # === TYP & STATUS ===
    customer_type = Column(Enum(CustomerType), default=CustomerType.PRIVATE, nullable=False)
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE, nullable=False)
    
    # === FIRMENDATEN (für Geschäftskunden) ===
    company_name = Column(String(255), nullable=True)
    company_name_addition = Column(String(255), nullable=True)  # Firmenzusatz
    legal_form = Column(String(50), nullable=True)  # Rechtsform
    tax_id = Column(String(50), nullable=True)  # USt-IdNr.
    tax_number = Column(String(50), nullable=True)  # Steuernummer
    trade_register = Column(String(100), nullable=True)  # Handelsregisternummer
    trade_register_court = Column(String(100), nullable=True)  # Registergericht
    industry = Column(String(100), nullable=True)  # Branche
    company_size = Column(String(50), nullable=True)  # Unternehmensgröße
    founding_year = Column(String(4), nullable=True)  # Gründungsjahr
    
    # === PERSONENDATEN (für Privatkunden / Hauptkontakt) ===
    salutation = Column(String(20), nullable=True)  # Herr, Frau, etc.
    title = Column(String(50), nullable=True)  # Dr., Prof., etc.
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)  # Geburtsdatum
    nationality = Column(String(100), nullable=True)  # Nationalität
    language = Column(String(10), default="de")  # Kommunikationssprache
    
    # === KONTAKTDATEN ===
    email = Column(String(255), nullable=True, index=True)
    email_secondary = Column(String(255), nullable=True)  # Zweite E-Mail
    email_invoice = Column(String(255), nullable=True)  # Rechnungs-E-Mail
    
    phone = Column(String(50), nullable=True)
    phone_direct = Column(String(50), nullable=True)  # Durchwahl
    phone_secondary = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    fax = Column(String(50), nullable=True)
    
    website = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    xing_url = Column(String(255), nullable=True)
    
    # Kommunikationspräferenzen
    preferred_contact_method = Column(String(50), nullable=True)  # email, phone, mail
    preferred_contact_time = Column(String(100), nullable=True)  # Bevorzugte Kontaktzeit
    newsletter_subscribed = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    marketing_consent_date = Column(DateTime, nullable=True)
    
    # === HAUPTADRESSE ===
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    address_addition = Column(String(100), nullable=True)  # Adresszusatz
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)  # Ortsteil
    state = Column(String(100), nullable=True)  # Bundesland
    country = Column(String(100), default="Deutschland")
    country_code = Column(String(3), default="DE")
    
    # Geokoordinaten
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # === FINANZDATEN ===
    payment_terms = Column(String(10), default="30")  # Zahlungsziel in Tagen
    payment_method = Column(String(50), nullable=True)  # Standardzahlungsart
    credit_limit = Column(String(20), nullable=True)  # Kreditlimit
    discount_percent = Column(String(10), default="0")  # Standardrabatt
    early_payment_discount = Column(String(10), nullable=True)  # Skonto %
    early_payment_days = Column(String(10), nullable=True)  # Skontofrist
    
    # Bankverbindung
    bank_name = Column(String(255), nullable=True)
    iban = Column(String(50), nullable=True)
    bic = Column(String(20), nullable=True)
    account_holder = Column(String(255), nullable=True)
    sepa_mandate = Column(String(100), nullable=True)  # SEPA-Mandat
    sepa_mandate_date = Column(Date, nullable=True)
    
    # Buchhaltung
    debitor_number = Column(String(50), nullable=True)  # Debitorennummer
    cost_center = Column(String(50), nullable=True)  # Kostenstelle
    revenue_account = Column(String(50), nullable=True)  # Erlöskonto
    
    # === KLASSIFIZIERUNG ===
    category = Column(String(100), nullable=True)  # Bauherr, Architekt, GU, etc.
    subcategory = Column(String(100), nullable=True)
    customer_group = Column(String(100), nullable=True)  # Kundengruppe
    customer_class = Column(String(10), nullable=True)  # A, B, C Kunde
    price_group = Column(String(50), nullable=True)  # Preisgruppe
    
    # Bewertung
    rating = Column(Integer, nullable=True)  # 1-5 Sterne
    credit_rating = Column(String(50), nullable=True)  # Bonität
    credit_rating_date = Column(Date, nullable=True)
    
    # === AKQUISE & VERTRIEB ===
    source = Column(String(100), nullable=True)  # Empfehlung, Website, Messe, etc.
    source_detail = Column(String(255), nullable=True)  # Detaillierte Quelle
    referral_customer_id = Column(UUID(as_uuid=True), nullable=True)  # Empfehlungsgeber
    first_contact_date = Column(Date, nullable=True)  # Erstkontakt
    acquisition_date = Column(Date, nullable=True)  # Kundengewinnungsdatum
    
    # Vertriebsverantwortung
    sales_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    account_manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # === STATISTIKEN (automatisch berechnet) ===
    total_revenue = Column(String(20), default="0")  # Gesamtumsatz
    total_projects = Column(Integer, default=0)  # Anzahl Projekte
    last_project_date = Column(Date, nullable=True)  # Letztes Projekt
    last_contact_date = Column(Date, nullable=True)  # Letzter Kontakt
    last_invoice_date = Column(Date, nullable=True)  # Letzte Rechnung
    open_invoices_amount = Column(String(20), default="0")  # Offene Posten
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)  # Allgemeine Notizen
    internal_notes = Column(Text, nullable=True)  # Interne Notizen
    payment_notes = Column(Text, nullable=True)  # Zahlungshinweise
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)  # Tags
    custom_fields = Column(JSONB, default=dict)  # Benutzerdefinierte Felder
    
    # === SYSTEM ===
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)  # Gesperrt
    blocked_reason = Column(Text, nullable=True)  # Sperrgrund
    blocked_date = Column(DateTime, nullable=True)
    
    # DSGVO
    data_processing_consent = Column(Boolean, default=False)  # Einwilligung Datenverarbeitung
    data_processing_consent_date = Column(DateTime, nullable=True)
    
    # === RELATIONSHIPS ===
    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="customer")
    sales_person = relationship("Employee", foreign_keys=[sales_person_id])
    account_manager = relationship("Employee", foreign_keys=[account_manager_id])


class Contact(Base, TimestampMixin, SoftDeleteMixin):
    """Ansprechpartner bei einem Kunden"""
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    
    # Personal
    salutation = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=True)  # Position im Unternehmen
    department = Column(String(100), nullable=True)  # Abteilung
    
    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    
    # Flags
    is_primary = Column(Boolean, default=False)  # Hauptansprechpartner
    is_invoice_contact = Column(Boolean, default=False)  # Rechnungskontakt
    is_project_contact = Column(Boolean, default=False)  # Projektkontakt
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="contacts")


class CustomerAddress(Base, TimestampMixin):
    """Zusätzliche Adressen eines Kunden (Lieferadresse, Rechnungsadresse, etc.)"""
    __tablename__ = "customer_addresses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    
    address_type = Column(String(50), nullable=False)  # billing, delivery, construction_site
    label = Column(String(100), nullable=True)  # Bezeichnung
    
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Deutschland")
    
    # For construction sites
    gps_latitude = Column(String(20), nullable=True)
    gps_longitude = Column(String(20), nullable=True)
    
    notes = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="addresses")
