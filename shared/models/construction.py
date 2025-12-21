"""
Construction Models - Bautagebuch, Baustellendokumentation, Wetter
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


class WeatherCondition(enum.Enum):
    """Wetterbedingungen"""
    SUNNY = "sunny"  # Sonnig
    PARTLY_CLOUDY = "partly_cloudy"  # Teilweise bewölkt
    CLOUDY = "cloudy"  # Bewölkt
    OVERCAST = "overcast"  # Bedeckt
    LIGHT_RAIN = "light_rain"  # Leichter Regen
    RAIN = "rain"  # Regen
    HEAVY_RAIN = "heavy_rain"  # Starker Regen
    THUNDERSTORM = "thunderstorm"  # Gewitter
    SNOW = "snow"  # Schnee
    SLEET = "sleet"  # Schneeregen
    FOG = "fog"  # Nebel
    FROST = "frost"  # Frost
    HAIL = "hail"  # Hagel
    WINDY = "windy"  # Windig


class DiaryEntryType(enum.Enum):
    """Bautagebuch-Eintragstypen"""
    WORK_PROGRESS = "work_progress"  # Arbeitsfortschritt
    DELIVERY = "delivery"  # Lieferung
    INSPECTION = "inspection"  # Prüfung/Abnahme
    MEETING = "meeting"  # Besprechung
    INCIDENT = "incident"  # Vorfall/Unfall
    DELAY = "delay"  # Verzögerung
    WEATHER = "weather"  # Wetterbedingte Unterbrechung
    VISITOR = "visitor"  # Besucher
    CHANGE_ORDER = "change_order"  # Nachtragsleistung
    INSTRUCTION = "instruction"  # Anweisung
    COMPLAINT = "complaint"  # Mängelrüge
    OTHER = "other"


class ConstructionDiary(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Bautagebuch - Tägliche Dokumentation"""
    __tablename__ = "construction_diaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diary_number = Column(String(50), nullable=False, index=True)
    
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    
    # === DATUM & ZEIT ===
    diary_date = Column(Date, nullable=False)  # Tagesdatum
    calendar_week = Column(Integer, nullable=True)  # KW
    
    work_start_time = Column(Time, nullable=True)  # Arbeitsbeginn
    work_end_time = Column(Time, nullable=True)  # Arbeitsende
    break_duration_minutes = Column(Integer, default=0)  # Pausendauer
    effective_work_hours = Column(String(10), nullable=True)  # Effektive Arbeitszeit
    
    # === WETTER ===
    weather_morning = Column(Enum(WeatherCondition), nullable=True)  # Wetter morgens
    weather_afternoon = Column(Enum(WeatherCondition), nullable=True)  # Wetter nachmittags
    weather_evening = Column(Enum(WeatherCondition), nullable=True)  # Wetter abends
    
    temperature_morning = Column(String(10), nullable=True)  # Temperatur morgens °C
    temperature_afternoon = Column(String(10), nullable=True)  # Temperatur nachmittags
    temperature_min = Column(String(10), nullable=True)  # Tiefsttemperatur
    temperature_max = Column(String(10), nullable=True)  # Höchsttemperatur
    
    humidity_percent = Column(String(10), nullable=True)  # Luftfeuchtigkeit %
    wind_speed_kmh = Column(String(10), nullable=True)  # Windgeschwindigkeit km/h
    wind_direction = Column(String(20), nullable=True)  # Windrichtung
    precipitation_mm = Column(String(10), nullable=True)  # Niederschlag mm
    
    weather_notes = Column(Text, nullable=True)  # Wetternotizen
    work_possible = Column(Boolean, default=True)  # Arbeit möglich
    weather_delay_hours = Column(String(10), nullable=True)  # Verzögerung durch Wetter
    
    # === PERSONAL ===
    own_workers_count = Column(Integer, default=0)  # Eigene Mitarbeiter
    subcontractor_workers_count = Column(Integer, default=0)  # Subunternehmer
    total_workers = Column(Integer, default=0)  # Gesamt
    
    # Detaillierte Personalaufstellung
    personnel_details = Column(JSONB, default=list)
    # [{"name": "Max Mustermann", "role": "Zimmerer", "hours": 8, "tasks": ["Wandmontage"]}]
    
    # Subunternehmer
    subcontractors_present = Column(JSONB, default=list)
    # [{"company": "Firma XY", "workers": 3, "tasks": ["Dachdeckung"]}]
    
    # === MASCHINEN & GERÄTE ===
    equipment_used = Column(JSONB, default=list)
    # [{"equipment": "Autokran 50t", "hours": 4, "operator": "Mustermann"}]
    
    crane_hours = Column(String(10), nullable=True)  # Kranstunden
    equipment_notes = Column(Text, nullable=True)
    
    # === ARBEITSFORTSCHRITT ===
    work_performed = Column(Text, nullable=True)  # Durchgeführte Arbeiten (ausführlich)
    work_location = Column(String(255), nullable=True)  # Arbeitsbereich
    
    # Gewerke
    trades_active = Column(ARRAY(String), default=list)  # Aktive Gewerke
    
    # Fortschritt
    progress_description = Column(Text, nullable=True)  # Fortschrittsbeschreibung
    progress_percent = Column(Integer, nullable=True)  # Tagesfortschritt %
    milestones_reached = Column(JSONB, default=list)  # Erreichte Meilensteine
    
    # === LIEFERUNGEN ===
    deliveries = Column(JSONB, default=list)
    # [{"supplier": "Lieferant", "material": "BSH", "quantity": "10 m³", "time": "08:30", "delivery_note": "LS-123"}]
    
    materials_used = Column(JSONB, default=list)
    # [{"material": "KVH 60x120", "quantity": "50 lfm", "project_area": "EG Wände"}]
    
    # === BESUCHER & BESPRECHUNGEN ===
    visitors = Column(JSONB, default=list)
    # [{"name": "Herr Müller", "company": "Bauamt", "purpose": "Rohbauabnahme", "time": "10:00"}]
    
    meetings_held = Column(JSONB, default=list)
    # [{"type": "Baubesprechung", "participants": ["Bauleiter", "Architekt"], "topics": ["..."]}]
    
    # === BESONDERE VORKOMMNISSE ===
    incidents = Column(JSONB, default=list)
    # [{"type": "accident", "description": "...", "persons_involved": [], "measures_taken": "..."}]
    
    delays = Column(JSONB, default=list)
    # [{"reason": "Materialverzögerung", "duration_hours": 2, "impact": "..."}]
    
    problems_encountered = Column(Text, nullable=True)  # Aufgetretene Probleme
    solutions_applied = Column(Text, nullable=True)  # Angewandte Lösungen
    
    # === ANWEISUNGEN & ÄNDERUNGEN ===
    instructions_received = Column(JSONB, default=list)
    # [{"from": "Architekt", "instruction": "...", "documented": true}]
    
    change_orders = Column(JSONB, default=list)
    # [{"description": "...", "requested_by": "...", "estimated_cost": "..."}]
    
    # === QUALITÄT & PRÜFUNGEN ===
    quality_checks = Column(JSONB, default=list)
    # [{"check_type": "Maßkontrolle", "result": "OK", "notes": "..."}]
    
    inspections = Column(JSONB, default=list)
    # [{"type": "Rohbauabnahme", "inspector": "Bauamt", "result": "bestanden"}]
    
    # === SICHERHEIT ===
    safety_briefing_done = Column(Boolean, default=False)  # Sicherheitsunterweisung
    safety_issues = Column(Text, nullable=True)  # Sicherheitsprobleme
    safety_measures = Column(Text, nullable=True)  # Ergriffene Maßnahmen
    
    # === FOTOS ===
    photos = Column(JSONB, default=list)
    # [{"url": "...", "caption": "...", "timestamp": "...", "category": "progress"}]
    
    photo_count = Column(Integer, default=0)
    
    # === PLANUNG FÜR MORGEN ===
    planned_work_tomorrow = Column(Text, nullable=True)  # Geplante Arbeiten
    planned_personnel_tomorrow = Column(Integer, nullable=True)  # Geplantes Personal
    required_materials_tomorrow = Column(Text, nullable=True)  # Benötigte Materialien
    required_equipment_tomorrow = Column(Text, nullable=True)  # Benötigte Geräte
    
    # === UNTERSCHRIFTEN ===
    site_manager_signature = Column(String(255), nullable=True)  # Bauleiter Unterschrift
    site_manager_signed_at = Column(DateTime, nullable=True)
    client_signature = Column(String(255), nullable=True)  # Bauherr Unterschrift
    client_signed_at = Column(DateTime, nullable=True)
    
    # === SYSTEM ===
    status = Column(String(50), default="draft")  # draft, submitted, approved
    submitted_at = Column(DateTime, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)  # Allgemeine Notizen
    internal_notes = Column(Text, nullable=True)  # Interne Notizen
    
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    project = relationship("Project")


class ConstructionDiaryEntry(Base, TimestampMixin):
    """Einzelne Einträge im Bautagebuch"""
    __tablename__ = "construction_diary_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diary_id = Column(UUID(as_uuid=True), ForeignKey('construction_diaries.id'), nullable=False)
    
    entry_type = Column(Enum(DiaryEntryType), nullable=False)
    entry_time = Column(Time, nullable=True)  # Uhrzeit des Eintrags
    
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    
    # Beteiligte
    persons_involved = Column(ARRAY(String), default=list)
    companies_involved = Column(ARRAY(String), default=list)
    
    # Auswirkungen
    impact_description = Column(Text, nullable=True)
    cost_impact = Column(String(20), nullable=True)  # Kostenauswirkung
    time_impact_hours = Column(String(10), nullable=True)  # Zeitliche Auswirkung
    
    # Dokumentation
    photos = Column(JSONB, default=list)
    documents = Column(JSONB, default=list)
    
    # Status
    requires_followup = Column(Boolean, default=False)
    followup_description = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    diary = relationship("ConstructionDiary")


class SiteInspection(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Baustellenbegehung / Abnahme"""
    __tablename__ = "site_inspections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_number = Column(String(50), nullable=False, index=True)
    
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    
    # === GRUNDDATEN ===
    inspection_type = Column(String(100), nullable=False)
    # Rohbauabnahme, Zwischenabnahme, Endabnahme, Mängelbegehung, Behördenprüfung
    
    inspection_date = Column(Date, nullable=False)
    inspection_time = Column(Time, nullable=True)
    
    # === BETEILIGTE ===
    inspector_name = Column(String(255), nullable=True)  # Prüfer
    inspector_company = Column(String(255), nullable=True)
    inspector_role = Column(String(100), nullable=True)  # Bauamt, TÜV, Sachverständiger
    
    our_representative_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    client_representative = Column(String(255), nullable=True)
    architect_present = Column(Boolean, default=False)
    
    participants = Column(JSONB, default=list)
    # [{"name": "...", "company": "...", "role": "..."}]
    
    # === PRÜFUNGSERGEBNIS ===
    overall_result = Column(String(50), nullable=True)  # passed, passed_with_conditions, failed
    
    # Geprüfte Bereiche
    areas_inspected = Column(JSONB, default=list)
    # [{"area": "Dachstuhl", "result": "OK", "notes": "..."}]
    
    # Checkliste
    checklist_items = Column(JSONB, default=list)
    # [{"item": "Maßhaltigkeit", "checked": true, "result": "OK", "notes": "..."}]
    
    # === MÄNGEL ===
    defects_found = Column(JSONB, default=list)
    # [{"id": 1, "description": "...", "severity": "minor", "location": "...", "photo": "...", 
    #   "deadline": "2024-01-15", "responsible": "...", "status": "open"}]
    
    defects_count_total = Column(Integer, default=0)
    defects_count_critical = Column(Integer, default=0)
    defects_count_major = Column(Integer, default=0)
    defects_count_minor = Column(Integer, default=0)
    
    # Nachbesserungen
    remediation_deadline = Column(Date, nullable=True)  # Frist für Nachbesserung
    follow_up_date = Column(Date, nullable=True)  # Nachprüfung geplant
    
    # === DOKUMENTATION ===
    findings_summary = Column(Text, nullable=True)  # Zusammenfassung
    recommendations = Column(Text, nullable=True)  # Empfehlungen
    conditions = Column(Text, nullable=True)  # Auflagen
    
    photos = Column(JSONB, default=list)
    documents = Column(JSONB, default=list)
    
    # === PROTOKOLL ===
    protocol_text = Column(Text, nullable=True)
    protocol_pdf_url = Column(String(500), nullable=True)
    
    # Unterschriften
    signatures = Column(JSONB, default=list)
    # [{"name": "...", "role": "...", "signed_at": "...", "signature_url": "..."}]
    
    # === SYSTEM ===
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed
    completed_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    project = relationship("Project")
    our_representative = relationship("Employee")


class WeatherLog(Base, TimestampMixin, TenantMixin):
    """Wetterdaten-Protokoll (kann automatisch erfasst werden)"""
    __tablename__ = "weather_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    
    recorded_at = Column(DateTime, nullable=False)
    
    # Wetterdaten
    condition = Column(Enum(WeatherCondition), nullable=True)
    temperature_celsius = Column(String(10), nullable=True)
    feels_like_celsius = Column(String(10), nullable=True)
    humidity_percent = Column(String(10), nullable=True)
    pressure_hpa = Column(String(10), nullable=True)
    
    wind_speed_kmh = Column(String(10), nullable=True)
    wind_gust_kmh = Column(String(10), nullable=True)
    wind_direction_degrees = Column(String(10), nullable=True)
    wind_direction_name = Column(String(20), nullable=True)
    
    precipitation_mm = Column(String(10), nullable=True)
    precipitation_probability = Column(String(10), nullable=True)
    
    cloud_coverage_percent = Column(String(10), nullable=True)
    visibility_km = Column(String(10), nullable=True)
    uv_index = Column(String(10), nullable=True)
    
    # Quelle
    data_source = Column(String(100), nullable=True)  # manual, openweathermap, etc.
    
    # Auswirkung auf Baustelle
    affects_work = Column(Boolean, default=False)
    work_restriction = Column(Text, nullable=True)  # z.B. "Kein Holztransport bei Nässe"
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project")
