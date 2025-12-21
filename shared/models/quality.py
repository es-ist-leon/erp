"""
Quality Control Models - Qualitätssicherung, Mängelmanagement
Enterprise-Level für Holzbau
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class DefectSeverity(enum.Enum):
    """Mangel-Schweregrad"""
    COSMETIC = "cosmetic"  # Kosmetisch
    MINOR = "minor"  # Geringfügig
    MAJOR = "major"  # Erheblich
    CRITICAL = "critical"  # Kritisch/Sicherheitsrelevant


class DefectStatus(enum.Enum):
    """Mangel-Status"""
    OPEN = "open"  # Offen
    ACKNOWLEDGED = "acknowledged"  # Anerkannt
    IN_PROGRESS = "in_progress"  # In Bearbeitung
    FIXED = "fixed"  # Behoben
    VERIFIED = "verified"  # Verifiziert/Abgenommen
    REJECTED = "rejected"  # Abgelehnt
    CLOSED = "closed"  # Geschlossen


class QualityCheckType(enum.Enum):
    """Prüfungstypen"""
    INCOMING_INSPECTION = "incoming_inspection"  # Wareneingangsprüfung
    IN_PROCESS = "in_process"  # Fertigungsbegleitend
    FINAL_INSPECTION = "final_inspection"  # Endkontrolle
    INSTALLATION = "installation"  # Montageprüfung
    ACCEPTANCE = "acceptance"  # Abnahmeprüfung
    WARRANTY = "warranty"  # Gewährleistung


class Defect(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Mangel/Reklamation"""
    __tablename__ = "defects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    defect_number = Column(String(50), nullable=False, index=True)
    
    # === BEZUG ===
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    
    # === KLASSIFIZIERUNG ===
    severity = Column(Enum(DefectSeverity), default=DefectSeverity.MINOR)
    status = Column(Enum(DefectStatus), default=DefectStatus.OPEN)
    
    defect_type = Column(String(100), nullable=True)
    # Maßabweichung, Oberflächenmangel, Feuchtigkeitsschaden, Montagedefekt, etc.
    
    category = Column(String(100), nullable=True)  # Kategorie
    subcategory = Column(String(100), nullable=True)
    
    # === BESCHREIBUNG ===
    title = Column(String(255), nullable=False)  # Kurzbezeichnung
    description = Column(Text, nullable=False)  # Ausführliche Beschreibung
    
    # === ORT ===
    location = Column(String(255), nullable=True)  # Wo genau
    location_detail = Column(Text, nullable=True)  # Detaillierte Ortsangabe
    building_part = Column(String(100), nullable=True)  # Bauteil
    floor = Column(String(50), nullable=True)  # Geschoss
    room = Column(String(100), nullable=True)  # Raum
    
    # Koordinaten auf Plan
    plan_reference = Column(String(255), nullable=True)  # Planreferenz
    plan_coordinates = Column(JSONB, default=dict)  # {"x": 100, "y": 200}
    
    # === FESTSTELLUNG ===
    detected_date = Column(Date, nullable=False)  # Feststellungsdatum
    detected_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    detected_by_external = Column(String(255), nullable=True)  # Externer Melder
    
    detection_phase = Column(String(100), nullable=True)
    # Produktion, Montage, Abnahme, Gewährleistung
    
    # === URSACHE ===
    root_cause = Column(Text, nullable=True)  # Ursache
    root_cause_category = Column(String(100), nullable=True)
    # Material, Verarbeitung, Planung, Transport, Witterung, Fremdverschulden
    
    responsible_party = Column(String(100), nullable=True)  # Verantwortlicher
    # Eigenverschulden, Lieferant, Subunternehmer, Kunde
    
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id'), nullable=True)
    subcontractor = Column(String(255), nullable=True)
    
    # === BEHEBUNG ===
    remediation_description = Column(Text, nullable=True)  # Maßnahme
    remediation_deadline = Column(Date, nullable=True)  # Frist
    remediation_priority = Column(Integer, default=5)  # 1-10
    
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Durchführung
    remediation_started = Column(Date, nullable=True)
    remediation_completed = Column(Date, nullable=True)
    remediation_hours = Column(String(10), nullable=True)  # Aufwand
    remediation_notes = Column(Text, nullable=True)
    
    # Verifizierung
    verified_date = Column(Date, nullable=True)
    verified_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # === KOSTEN ===
    estimated_cost = Column(String(20), nullable=True)  # Geschätzte Kosten
    actual_cost = Column(String(20), nullable=True)  # Tatsächliche Kosten
    cost_recovery = Column(String(20), nullable=True)  # Rückforderung
    cost_recovered = Column(Boolean, default=False)
    
    # === DOKUMENTATION ===
    photos_before = Column(JSONB, default=list)  # Fotos vorher
    photos_after = Column(JSONB, default=list)  # Fotos nachher
    documents = Column(JSONB, default=list)  # Dokumente
    
    # === KOMMUNIKATION ===
    customer_notified = Column(Boolean, default=False)
    customer_notified_date = Column(Date, nullable=True)
    customer_response = Column(Text, nullable=True)
    
    # === ABSCHLUSS ===
    closed_date = Column(Date, nullable=True)
    closed_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    closure_notes = Column(Text, nullable=True)
    
    # === PRÄVENTION ===
    preventive_action = Column(Text, nullable=True)  # Präventivmaßnahme
    lessons_learned = Column(Text, nullable=True)  # Erkenntnisse
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    project = relationship("Project")
    customer = relationship("Customer")
    detected_by = relationship("Employee", foreign_keys=[detected_by_id])
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])
    verified_by = relationship("Employee", foreign_keys=[verified_by_id])
    closed_by = relationship("Employee", foreign_keys=[closed_by_id])


class QualityCheck(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Qualitätsprüfung"""
    __tablename__ = "quality_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_number = Column(String(50), nullable=False, index=True)
    
    # === BEZUG ===
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=True)
    
    # === TYP ===
    check_type = Column(Enum(QualityCheckType), nullable=False)
    
    # === ZEITPUNKT ===
    check_date = Column(Date, nullable=False)
    check_time = Column(String(10), nullable=True)
    
    # === PRÜFER ===
    inspector_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    external_inspector = Column(String(255), nullable=True)
    
    # === GEGENSTAND ===
    subject = Column(String(255), nullable=False)  # Was wird geprüft
    description = Column(Text, nullable=True)
    
    # Menge
    quantity_checked = Column(String(20), nullable=True)  # Geprüfte Menge
    sample_size = Column(String(20), nullable=True)  # Stichprobengröße
    
    # === ERGEBNIS ===
    overall_result = Column(String(50), nullable=True)  # passed, failed, conditional
    
    # Checkliste
    checklist_items = Column(JSONB, default=list)
    # [{"item": "Maßhaltigkeit", "specification": "±3mm", "measured": "2mm", 
    #   "result": "OK", "notes": ""}]
    
    # Messwerte
    measurements = Column(JSONB, default=list)
    # [{"parameter": "Holzfeuchte", "target": "12%", "actual": "11.5%", 
    #   "tolerance": "±2%", "result": "OK"}]
    
    # === ABWEICHUNGEN ===
    deviations_found = Column(Integer, default=0)
    deviations_description = Column(Text, nullable=True)
    
    # Verknüpfte Mängel
    defect_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    
    # === ENTSCHEIDUNG ===
    decision = Column(String(100), nullable=True)
    # Freigabe, Nacharbeit erforderlich, Sperrung, Sonderfreigabe
    
    decision_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    decision_date = Column(Date, nullable=True)
    decision_notes = Column(Text, nullable=True)
    
    # === DOKUMENTATION ===
    photos = Column(JSONB, default=list)
    documents = Column(JSONB, default=list)
    
    # Protokoll
    protocol_text = Column(Text, nullable=True)
    protocol_signed = Column(Boolean, default=False)
    signature_url = Column(String(500), nullable=True)
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    
    # === FLEXIBLE ERWEITERUNG ===
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    project = relationship("Project")
    inspector = relationship("Employee", foreign_keys=[inspector_id])
    decision_by = relationship("Employee", foreign_keys=[decision_by_id])


class QualityCheckTemplate(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Prüfplan-Vorlage"""
    __tablename__ = "quality_check_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    check_type = Column(Enum(QualityCheckType), nullable=True)
    
    # Für welche Materialien/Produkte
    applicable_to = Column(JSONB, default=list)
    # ["material_category:schnittholz", "product_group:wandelemente"]
    
    # Checkliste
    checklist_items = Column(JSONB, default=list)
    # [{"item": "...", "specification": "...", "is_mandatory": true, 
    #   "measurement_type": "numeric", "unit": "mm", "min": 0, "max": 100}]
    
    # Anweisungen
    instructions = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    custom_fields = Column(JSONB, default=dict)


class Warranty(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Gewährleistung"""
    __tablename__ = "warranties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warranty_number = Column(String(50), nullable=False, index=True)
    
    # === BEZUG ===
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    
    # === ZEITRAUM ===
    acceptance_date = Column(Date, nullable=False)  # Abnahmedatum
    warranty_start = Column(Date, nullable=False)  # Gewährleistungsbeginn
    warranty_end = Column(Date, nullable=False)  # Gewährleistungsende
    warranty_months = Column(Integer, default=60)  # Dauer in Monaten
    
    # === STATUS ===
    status = Column(String(50), default="active")  # active, expired, extended
    
    # === SICHERHEITEN ===
    retention_amount = Column(String(20), nullable=True)  # Einbehalt
    retention_percent = Column(String(10), nullable=True)
    retention_due_date = Column(Date, nullable=True)  # Auszahlungstermin
    retention_paid = Column(Boolean, default=False)
    retention_paid_date = Column(Date, nullable=True)
    
    bank_guarantee = Column(Boolean, default=False)  # Bankbürgschaft
    guarantee_amount = Column(String(20), nullable=True)
    guarantee_valid_until = Column(Date, nullable=True)
    guarantee_document = Column(String(500), nullable=True)
    
    # === BEGEHUNGEN ===
    inspections_planned = Column(JSONB, default=list)
    # [{"date": "2025-06-15", "type": "1-Jahr-Begehung", "status": "planned"}]
    
    # === MÄNGEL WÄHREND GEWÄHRLEISTUNG ===
    defect_count = Column(Integer, default=0)
    defect_cost_total = Column(String(20), default="0")
    
    # === VERLÄNGERUNG ===
    extended = Column(Boolean, default=False)
    extension_reason = Column(Text, nullable=True)
    extended_until = Column(Date, nullable=True)
    
    # === ABSCHLUSS ===
    final_inspection_date = Column(Date, nullable=True)
    final_inspection_passed = Column(Boolean, nullable=True)
    
    closed_date = Column(Date, nullable=True)
    closed_notes = Column(Text, nullable=True)
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    
    # === FLEXIBLE ERWEITERUNG ===
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    project = relationship("Project")
    customer = relationship("Customer")


class Certificate(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Zertifikate und Bescheinigungen (für Projekte/Produkte)"""
    __tablename__ = "certificates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    certificate_number = Column(String(100), nullable=False, index=True)
    
    # === BEZUG ===
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=True)
    
    # === TYP ===
    certificate_type = Column(String(100), nullable=False)
    # CE-Kennzeichnung, Leistungserklärung, Holzzertifikat (FSC/PEFC), 
    # Brandschutznachweis, Statikprüfung, EnEV-Nachweis, etc.
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # === AUSSTELLER ===
    issuer = Column(String(255), nullable=True)  # Ausstellende Stelle
    issuer_accreditation = Column(String(255), nullable=True)  # Akkreditierung
    
    # === GÜLTIGKEIT ===
    issue_date = Column(Date, nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    is_valid = Column(Boolean, default=True)
    
    # === DOKUMENT ===
    document_url = Column(String(500), nullable=True)
    document_pages = Column(Integer, nullable=True)
    
    # === VERKNÜPFTE NORMEN ===
    standards = Column(ARRAY(String), default=list)
    # ["DIN EN 14081-1", "EN 1995-1-1"]
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    
    # === FLEXIBLE ERWEITERUNG ===
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    project = relationship("Project")
    material = relationship("Material")
