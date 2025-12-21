"""
CRM Models - Aktivitäten, Kommunikation, Leads
Enterprise-Level für Holzbau
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class ActivityType(enum.Enum):
    """Aktivitätstypen"""
    CALL = "call"  # Telefonat
    EMAIL = "email"  # E-Mail
    MEETING = "meeting"  # Besprechung
    VISIT = "visit"  # Besuch
    NOTE = "note"  # Notiz
    TASK = "task"  # Aufgabe
    FOLLOW_UP = "follow_up"  # Nachfassen
    QUOTE_SENT = "quote_sent"  # Angebot versendet
    CONTRACT_SIGNED = "contract_signed"  # Vertrag unterschrieben
    COMPLAINT = "complaint"  # Reklamation
    SUPPORT = "support"  # Support


class ActivityPriority(enum.Enum):
    """Priorität"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class LeadStatus(enum.Enum):
    """Lead-Status"""
    NEW = "new"  # Neu
    CONTACTED = "contacted"  # Kontaktiert
    QUALIFIED = "qualified"  # Qualifiziert
    PROPOSAL = "proposal"  # Angebot erstellt
    NEGOTIATION = "negotiation"  # In Verhandlung
    WON = "won"  # Gewonnen
    LOST = "lost"  # Verloren
    ON_HOLD = "on_hold"  # Pausiert


class LeadSource(enum.Enum):
    """Lead-Quelle"""
    WEBSITE = "website"
    REFERRAL = "referral"  # Empfehlung
    TRADE_SHOW = "trade_show"  # Messe
    COLD_CALL = "cold_call"  # Kaltakquise
    ADVERTISING = "advertising"  # Werbung
    SOCIAL_MEDIA = "social_media"
    DIRECTORY = "directory"  # Branchenverzeichnis
    PARTNER = "partner"
    REPEAT_CUSTOMER = "repeat_customer"  # Bestandskunde
    OTHER = "other"


class Activity(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """CRM-Aktivität - Alle Interaktionen mit Kunden"""
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_number = Column(String(50), nullable=False, index=True)
    
    # === TYP & STATUS ===
    activity_type = Column(String(50), nullable=False)
    priority = Column(String(50), default="normal")
    status = Column(String(50), default="planned")  # planned, in_progress, completed, cancelled
    
    # === BEZUG ===
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    contact_id = Column(UUID(as_uuid=True), nullable=True)  # Optional - table may not exist
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'), nullable=True)
    quote_id = Column(UUID(as_uuid=True), nullable=True)  # Optional - table may not exist
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    
    # === INHALT ===
    subject = Column(String(255), nullable=False)  # Betreff
    description = Column(Text, nullable=True)  # Beschreibung
    result = Column(Text, nullable=True)  # Ergebnis
    
    # === TERMIN ===
    scheduled_date = Column(Date, nullable=True)  # Geplantes Datum
    scheduled_time = Column(Time, nullable=True)  # Geplante Uhrzeit
    duration_minutes = Column(Integer, nullable=True)  # Dauer in Minuten
    
    completed_date = Column(Date, nullable=True)  # Abgeschlossen am
    completed_time = Column(Time, nullable=True)
    
    # Erinnerung
    reminder_date = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    
    # === ORT ===
    location = Column(String(255), nullable=True)  # Ort
    is_onsite = Column(Boolean, default=False)  # Vor-Ort-Termin
    
    # === KOMMUNIKATION (für Telefon/E-Mail) ===
    direction = Column(String(20), nullable=True)  # incoming, outgoing
    phone_number = Column(String(50), nullable=True)
    email_address = Column(String(255), nullable=True)
    
    # === TEILNEHMER ===
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    participants = Column(JSONB, default=list)
    # [{"name": "...", "email": "...", "role": "..."}]
    
    # === FOLLOW-UP ===
    requires_followup = Column(Boolean, default=False)
    followup_date = Column(Date, nullable=True)
    followup_description = Column(Text, nullable=True)
    followup_activity_id = Column(UUID(as_uuid=True), nullable=True)  # Verknüpfte Folge-Aktivität
    
    # === DOKUMENTE ===
    attachments = Column(JSONB, default=list)
    # [{"name": "...", "url": "...", "size": 1234}]
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    customer = relationship("Customer", foreign_keys=[customer_id])
    project = relationship("Project", foreign_keys=[project_id])
    lead = relationship("Lead", back_populates="activities", foreign_keys=[lead_id])
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])


class Lead(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Lead/Interessent - Potenzielle Kunden"""
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_number = Column(String(50), nullable=False, index=True)
    
    # === STATUS ===
    status = Column(String(50), default="new")
    
    # === QUELLE ===
    source = Column(String(50), nullable=True)
    source_detail = Column(String(255), nullable=True)  # z.B. "Messe XY 2024"
    campaign = Column(String(255), nullable=True)  # Marketing-Kampagne
    
    # === FIRMENDATEN ===
    company_name = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # === ANSPRECHPARTNER ===
    salutation = Column(String(20), nullable=True)
    title = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    
    # === KONTAKT ===
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    
    # === ADRESSE ===
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Deutschland")
    
    # === PROJEKT-INTERESSE ===
    project_type_interest = Column(String(100), nullable=True)  # Neubau, Anbau, etc.
    construction_type_interest = Column(String(100), nullable=True)  # Holzrahmenbau, etc.
    estimated_project_size = Column(String(100), nullable=True)  # z.B. "ca. 150m² Wohnfläche"
    estimated_budget = Column(String(100), nullable=True)  # Budget-Rahmen
    planned_start = Column(String(100), nullable=True)  # Geplanter Baubeginn
    building_site_available = Column(Boolean, nullable=True)  # Grundstück vorhanden
    building_site_location = Column(String(255), nullable=True)  # Grundstücksstandort
    
    # === QUALIFIZIERUNG ===
    score = Column(Integer, nullable=True)  # Lead-Score (0-100)
    qualification_notes = Column(Text, nullable=True)
    
    decision_maker = Column(Boolean, nullable=True)  # Ist Entscheider
    decision_timeframe = Column(String(100), nullable=True)  # Entscheidungszeitraum
    competitor_consideration = Column(Text, nullable=True)  # Welche Mitbewerber
    
    # === ZUWEISUNG ===
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # === KONVERTIERUNG ===
    converted_to_customer = Column(Boolean, default=False)
    converted_customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    converted_at = Column(DateTime, nullable=True)
    
    conversion_value = Column(String(20), nullable=True)  # Auftragswert bei Konvertierung
    lost_reason = Column(Text, nullable=True)  # Grund bei Verlust
    lost_to_competitor = Column(String(255), nullable=True)  # An welchen Mitbewerber verloren
    
    # === TERMINE ===
    first_contact_date = Column(Date, nullable=True)
    last_contact_date = Column(Date, nullable=True)
    next_contact_date = Column(Date, nullable=True)
    
    # === NOTIZEN ===
    description = Column(Text, nullable=True)  # Anfrage-Beschreibung
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # === DOKUMENTE ===
    attachments = Column(JSONB, default=list)
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])
    converted_customer = relationship("Customer", foreign_keys=[converted_customer_id])
    activities = relationship("Activity", back_populates="lead", foreign_keys="Activity.lead_id")


class CommunicationTemplate(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """E-Mail und Dokumentenvorlagen"""
    __tablename__ = "communication_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    template_type = Column(String(50), nullable=False)  # email, letter, sms
    category = Column(String(100), nullable=True)  # Angebot, Rechnung, Mahnung, etc.
    
    subject = Column(String(255), nullable=True)  # Betreff (für E-Mail)
    body = Column(Text, nullable=False)  # Inhalt mit Platzhaltern
    
    # Platzhalter-Info
    available_placeholders = Column(JSONB, default=list)
    # [{"placeholder": "{{kunde_name}}", "description": "Name des Kunden"}]
    
    # Design
    html_template = Column(Text, nullable=True)  # HTML-Version
    header_image_url = Column(String(500), nullable=True)
    footer_text = Column(Text, nullable=True)
    
    language = Column(String(10), default="de")
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    custom_fields = Column(JSONB, default=dict)


class Campaign(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Marketing-Kampagne"""
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    campaign_type = Column(String(100), nullable=True)  # Mailing, Messe, Social Media
    
    # Zeitraum
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Budget
    budget = Column(String(20), nullable=True)
    actual_cost = Column(String(20), nullable=True)
    
    # Ziele
    target_leads = Column(Integer, nullable=True)  # Ziel-Anzahl Leads
    target_conversions = Column(Integer, nullable=True)  # Ziel-Konversionen
    target_revenue = Column(String(20), nullable=True)  # Ziel-Umsatz
    
    # Ergebnisse
    actual_leads = Column(Integer, default=0)
    actual_conversions = Column(Integer, default=0)
    actual_revenue = Column(String(20), default="0")
    
    # Status
    status = Column(String(50), default="planned")  # planned, active, completed, cancelled
    
    # Zuweisung
    responsible_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    responsible = relationship("Employee")


class CustomerInteraction(Base, TimestampMixin, TenantMixin):
    """Automatisch protokollierte Kundeninteraktionen"""
    __tablename__ = "customer_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    contact_id = Column(UUID(as_uuid=True), nullable=True)  # Optional - table may not exist
    
    interaction_type = Column(String(50), nullable=False)
    # email_sent, email_received, email_opened, email_clicked
    # document_viewed, quote_viewed, invoice_viewed
    # website_visit, form_submission
    
    interaction_date = Column(DateTime, nullable=False)
    
    # Details
    subject = Column(String(255), nullable=True)
    details = Column(JSONB, default=dict)
    # z.B. {"email_id": "...", "opened_at": "...", "clicked_links": [...]}
    
    # Bezug
    related_entity_type = Column(String(50), nullable=True)  # quote, invoice, document
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Tracking
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Relationships
    customer = relationship("Customer")


class Task(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Allgemeine Aufgaben (nicht projektbezogen)"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_number = Column(String(50), nullable=False, index=True)
    
    # === GRUNDDATEN ===
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    priority = Column(String(50), default="normal")
    status = Column(String(50), default="open")  # open, in_progress, completed, cancelled
    
    # === TERMIN ===
    due_date = Column(Date, nullable=True)
    due_time = Column(Time, nullable=True)
    
    start_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    
    # Erinnerung
    reminder_date = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    
    # === AUFWAND ===
    estimated_hours = Column(String(10), nullable=True)
    actual_hours = Column(String(10), nullable=True)
    
    # === ZUWEISUNG ===
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    assigned_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # === BEZÜGE ===
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    
    # Wiederkehrend
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # daily, weekly, monthly
    recurrence_end_date = Column(Date, nullable=True)
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    
    # === CHECKLISTE ===
    checklist = Column(JSONB, default=list)
    # [{"item": "...", "completed": false}]
    
    # === DOKUMENTE ===
    attachments = Column(JSONB, default=list)
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])
    assigned_by = relationship("Employee", foreign_keys=[assigned_by_id])
    customer = relationship("Customer")
    project = relationship("Project")
