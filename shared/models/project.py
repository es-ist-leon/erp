"""
Project Models - Projektverwaltung für Holzbau
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class ProjectType(enum.Enum):
    """Holzbau Projekttypen"""
    NEUBAU = "neubau"  # Neubau
    ANBAU = "anbau"  # Anbau
    UMBAU = "umbau"  # Umbau
    SANIERUNG = "sanierung"  # Sanierung
    DACHSTUHL = "dachstuhl"  # Dachstuhl
    CARPORT = "carport"  # Carport
    GARAGE = "garage"  # Garage
    TERRASSE = "terrasse"  # Terrasse/Balkon
    FASSADE = "fassade"  # Holzfassade
    INNENAUSBAU = "innenausbau"  # Innenausbau
    GEWERBEBAU = "gewerbebau"  # Gewerbebau
    HALLE = "halle"  # Hallenbau
    SONSTIGES = "sonstiges"


class ProjectStatus(enum.Enum):
    """Projektstatus"""
    ANFRAGE = "anfrage"  # Anfrage eingegangen
    ANGEBOT = "angebot"  # Angebot erstellt
    VERHANDLUNG = "verhandlung"  # In Verhandlung
    BEAUFTRAGT = "beauftragt"  # Auftrag erteilt
    PLANUNG = "planung"  # In Planung
    PRODUKTION = "produktion"  # In Produktion
    MONTAGE = "montage"  # Montage
    ABNAHME = "abnahme"  # Abnahme
    FERTIG = "fertig"  # Abgeschlossen
    GEWAEHRLEISTUNG = "gewaehrleistung"  # Gewährleistung
    ABGELEHNT = "abgelehnt"  # Abgelehnt
    STORNIERT = "storniert"  # Storniert


class ConstructionType(enum.Enum):
    """Bauweise"""
    HOLZRAHMENBAU = "holzrahmenbau"
    HOLZMASSIVBAU = "holzmassivbau"
    HOLZSKELETTBAU = "holzskelettbau"
    BLOCKBAU = "blockbau"
    FACHWERKBAU = "fachwerkbau"
    HYBRID = "hybrid"  # Mischbauweise
    SONSTIGES = "sonstiges"


class Project(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Hauptprojekt-Entität - Enterprise Holzbau mit allen Details"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_number = Column(String(50), nullable=False, index=True)  # Projektnummer
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)  # Kurzbeschreibung
    
    # === TYP & STATUS ===
    project_type = Column(Enum(ProjectType), default=ProjectType.NEUBAU, nullable=False)
    construction_type = Column(Enum(ConstructionType), nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ANFRAGE, nullable=False)
    sub_status = Column(String(100), nullable=True)  # Detaillierter Substatus
    
    # === KUNDE & BETEILIGTE ===
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    project_manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    site_manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)  # Bauleiter
    sales_person_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)  # Vertrieb
    
    # Externe Beteiligte
    architect_name = Column(String(255), nullable=True)
    architect_company = Column(String(255), nullable=True)
    architect_email = Column(String(255), nullable=True)
    architect_phone = Column(String(50), nullable=True)
    
    structural_engineer_name = Column(String(255), nullable=True)  # Statiker
    structural_engineer_company = Column(String(255), nullable=True)
    structural_engineer_email = Column(String(255), nullable=True)
    structural_engineer_phone = Column(String(50), nullable=True)
    
    energy_consultant_name = Column(String(255), nullable=True)  # Energieberater
    energy_consultant_company = Column(String(255), nullable=True)
    
    general_contractor_name = Column(String(255), nullable=True)  # Generalunternehmer
    general_contractor_company = Column(String(255), nullable=True)
    
    # === TERMINE & MEILENSTEINE ===
    inquiry_date = Column(Date, nullable=True)  # Anfragedatum
    quote_date = Column(Date, nullable=True)  # Angebotsdatum
    quote_deadline = Column(Date, nullable=True)  # Angebotsfrist
    decision_date = Column(Date, nullable=True)  # Entscheidungstermin
    order_date = Column(Date, nullable=True)  # Auftragsdatum
    contract_signing_date = Column(Date, nullable=True)  # Vertragsunterzeichnung
    
    planning_start = Column(Date, nullable=True)  # Planungsbeginn
    planning_end = Column(Date, nullable=True)  # Planungsende
    production_start = Column(Date, nullable=True)  # Produktionsbeginn
    production_end = Column(Date, nullable=True)  # Produktionsende
    delivery_date = Column(Date, nullable=True)  # Lieferdatum
    
    planned_start = Column(Date, nullable=True)  # Geplanter Montagebeginn
    planned_end = Column(Date, nullable=True)  # Geplantes Montageende
    actual_start = Column(Date, nullable=True)  # Tatsächlicher Start
    actual_end = Column(Date, nullable=True)  # Tatsächliches Ende
    
    acceptance_date = Column(Date, nullable=True)  # Abnahmedatum
    warranty_end_date = Column(Date, nullable=True)  # Gewährleistungsende
    
    # === BAUSTELLE - ADRESSE ===
    site_name = Column(String(255), nullable=True)  # Baustellenbezeichnung
    site_street = Column(String(255), nullable=True)
    site_street_number = Column(String(20), nullable=True)
    site_address_addition = Column(String(100), nullable=True)
    site_postal_code = Column(String(20), nullable=True)
    site_city = Column(String(100), nullable=True)
    site_district = Column(String(100), nullable=True)  # Ortsteil
    site_state = Column(String(100), nullable=True)  # Bundesland
    site_country = Column(String(100), default="Deutschland")
    
    # === BAUSTELLE - GEOKOORDINATEN ===
    site_latitude = Column(String(20), nullable=True)  # Breitengrad
    site_longitude = Column(String(20), nullable=True)  # Längengrad
    site_altitude = Column(String(20), nullable=True)  # Höhe über NN in Metern
    site_geohash = Column(String(20), nullable=True)  # Geohash für Suche
    
    # Detaillierte Lageangaben
    site_parcel_number = Column(String(50), nullable=True)  # Flurstücknummer
    site_cadastral_district = Column(String(100), nullable=True)  # Gemarkung
    site_land_register = Column(String(100), nullable=True)  # Grundbuch
    site_what3words = Column(String(100), nullable=True)  # What3Words Adresse
    
    # === BAUSTELLE - UMGEBUNG & ZUGANG ===
    site_access_description = Column(Text, nullable=True)  # Zufahrtsbeschreibung
    site_access_restrictions = Column(Text, nullable=True)  # Zufahrtsbeschränkungen
    site_access_width_m = Column(String(10), nullable=True)  # Zufahrtsbreite
    site_access_height_m = Column(String(10), nullable=True)  # Durchfahrtshöhe
    site_access_weight_limit = Column(String(10), nullable=True)  # Gewichtsbeschränkung
    
    site_crane_setup_possible = Column(Boolean, default=True)  # Kranstellplatz möglich
    site_crane_setup_location = Column(Text, nullable=True)  # Kranstellplatz Beschreibung
    site_storage_area_available = Column(Boolean, default=True)  # Lagerfläche vorhanden
    site_storage_area_sqm = Column(String(20), nullable=True)  # Lagerfläche m²
    
    site_electricity_available = Column(Boolean, default=False)  # Baustrom vorhanden
    site_water_available = Column(Boolean, default=False)  # Bauwasser vorhanden
    site_toilet_available = Column(Boolean, default=False)  # WC vorhanden
    
    site_parking_description = Column(Text, nullable=True)  # Parkmöglichkeiten
    site_special_conditions = Column(Text, nullable=True)  # Besondere Bedingungen
    
    # === GEBÄUDEDATEN ===
    building_class = Column(String(50), nullable=True)  # Gebäudeklasse 1-5
    building_use = Column(String(100), nullable=True)  # Nutzungsart (Wohnen, Gewerbe, etc.)
    
    # Flächen
    gross_floor_area = Column(String(20), nullable=True)  # Bruttogrundfläche BGF m²
    net_floor_area = Column(String(20), nullable=True)  # Nettogrundfläche NGF m²
    living_space = Column(String(20), nullable=True)  # Wohnfläche m²
    usable_area = Column(String(20), nullable=True)  # Nutzfläche m²
    basement_area = Column(String(20), nullable=True)  # Kellerfläche m²
    roof_area = Column(String(20), nullable=True)  # Dachfläche m²
    facade_area = Column(String(20), nullable=True)  # Fassadenfläche m²
    
    # Geschosse
    floors_above_ground = Column(Integer, nullable=True)  # Vollgeschosse
    floors_below_ground = Column(Integer, nullable=True)  # Kellergeschosse
    attic_type = Column(String(50), nullable=True)  # Dachgeschossausbau
    
    # Abmessungen
    building_length_m = Column(String(20), nullable=True)  # Gebäudelänge
    building_width_m = Column(String(20), nullable=True)  # Gebäudebreite
    building_height_m = Column(String(20), nullable=True)  # Gebäudehöhe
    ridge_height_m = Column(String(20), nullable=True)  # Firsthöhe
    eaves_height_m = Column(String(20), nullable=True)  # Traufhöhe
    
    # === DACH ===
    roof_type = Column(String(50), nullable=True)  # Satteldach, Pultdach, Flachdach, etc.
    roof_pitch = Column(String(20), nullable=True)  # Dachneigung in Grad
    roof_pitch_secondary = Column(String(20), nullable=True)  # Zweite Dachneigung
    roof_overhang_eaves = Column(String(20), nullable=True)  # Dachüberstand Traufe cm
    roof_overhang_gable = Column(String(20), nullable=True)  # Dachüberstand Giebel cm
    roof_covering = Column(String(100), nullable=True)  # Dacheindeckung
    
    # === HOLZBAU TECHNISCHE DATEN ===
    wood_volume_m3 = Column(String(20), nullable=True)  # Holzvolumen m³
    wood_type_primary = Column(String(100), nullable=True)  # Hauptholzart
    wood_type_secondary = Column(String(100), nullable=True)  # Nebenholzart
    wood_quality = Column(String(50), nullable=True)  # Holzqualität (S10, C24, etc.)
    wood_moisture = Column(String(20), nullable=True)  # Holzfeuchte %
    wood_certification = Column(String(50), nullable=True)  # PEFC, FSC
    
    # Konstruktion
    wall_construction = Column(String(100), nullable=True)  # Wandaufbau
    wall_thickness_cm = Column(String(20), nullable=True)  # Wanddicke
    ceiling_construction = Column(String(100), nullable=True)  # Deckenaufbau
    roof_construction = Column(String(100), nullable=True)  # Dachaufbau
    
    prefabrication_degree = Column(String(50), nullable=True)  # Vorfertigungsgrad
    module_count = Column(Integer, nullable=True)  # Anzahl Module/Elemente
    
    # === ENERGETIK & BAUPHYSIK ===
    insulation_standard = Column(String(50), nullable=True)  # KfW-Standard, Passivhaus
    energy_efficiency_class = Column(String(10), nullable=True)  # Energieeffizienzklasse
    primary_energy_demand = Column(String(20), nullable=True)  # Primärenergiebedarf kWh/m²a
    heating_demand = Column(String(20), nullable=True)  # Heizwärmebedarf
    u_value_wall = Column(String(20), nullable=True)  # U-Wert Außenwand
    u_value_roof = Column(String(20), nullable=True)  # U-Wert Dach
    u_value_floor = Column(String(20), nullable=True)  # U-Wert Bodenplatte
    blower_door_value = Column(String(20), nullable=True)  # Luftdichtheit n50
    
    heating_system = Column(String(100), nullable=True)  # Heizungssystem
    ventilation_system = Column(String(100), nullable=True)  # Lüftungssystem
    solar_system = Column(String(100), nullable=True)  # Solaranlage
    
    # === BAUGENEHMIGUNG & NORMEN ===
    building_permit_required = Column(Boolean, default=True)
    building_permit_number = Column(String(100), nullable=True)  # Baugenehmigungsnummer
    building_permit_date = Column(Date, nullable=True)  # Genehmigungsdatum
    building_permit_authority = Column(String(255), nullable=True)  # Baubehörde
    building_permit_status = Column(String(50), nullable=True)  # Status der Genehmigung
    
    structural_approval = Column(String(100), nullable=True)  # Statik-Prüfnummer
    structural_approval_date = Column(Date, nullable=True)
    fire_safety_concept = Column(Boolean, default=False)  # Brandschutzkonzept vorhanden
    fire_resistance_class = Column(String(20), nullable=True)  # Feuerwiderstandsklasse
    
    noise_protection_class = Column(String(20), nullable=True)  # Schallschutzklasse
    earthquake_zone = Column(String(20), nullable=True)  # Erdbebenzone
    snow_load_zone = Column(String(20), nullable=True)  # Schneelastzone
    wind_load_zone = Column(String(20), nullable=True)  # Windlastzone
    
    # === FINANZEN ===
    estimated_value = Column(String(20), nullable=True)  # Geschätzter Auftragswert
    quoted_value = Column(String(20), nullable=True)  # Angebotswert
    contract_value = Column(String(20), nullable=True)  # Auftragswert
    final_value = Column(String(20), nullable=True)  # Endabrechnungswert
    
    budget_materials = Column(String(20), nullable=True)  # Budget Material
    budget_labor = Column(String(20), nullable=True)  # Budget Arbeitskosten
    budget_external = Column(String(20), nullable=True)  # Budget Fremdleistungen
    budget_other = Column(String(20), nullable=True)  # Budget Sonstiges
    
    actual_cost_materials = Column(String(20), nullable=True)  # Ist-Kosten Material
    actual_cost_labor = Column(String(20), nullable=True)  # Ist-Kosten Arbeit
    actual_cost_external = Column(String(20), nullable=True)  # Ist-Kosten Fremd
    
    margin_percent = Column(String(10), nullable=True)  # Marge %
    margin_amount = Column(String(20), nullable=True)  # Marge absolut
    
    # Förderungen
    subsidy_program = Column(String(255), nullable=True)  # Förderprogramm (KfW, BAFA)
    subsidy_amount = Column(String(20), nullable=True)  # Fördersumme
    subsidy_status = Column(String(50), nullable=True)  # Förderstatus
    
    # === ZEITEN & AUFWAND ===
    planned_hours_total = Column(String(20), nullable=True)  # Geplante Stunden gesamt
    planned_hours_planning = Column(String(20), nullable=True)  # Geplante Stunden Planung
    planned_hours_production = Column(String(20), nullable=True)  # Geplante Stunden Produktion
    planned_hours_assembly = Column(String(20), nullable=True)  # Geplante Stunden Montage
    
    actual_hours_total = Column(String(20), nullable=True)  # Ist-Stunden gesamt
    actual_hours_planning = Column(String(20), nullable=True)
    actual_hours_production = Column(String(20), nullable=True)
    actual_hours_assembly = Column(String(20), nullable=True)
    
    # === FORTSCHRITT ===
    progress_overall = Column(Integer, default=0)  # Gesamtfortschritt %
    progress_planning = Column(Integer, default=0)  # Planungsfortschritt %
    progress_production = Column(Integer, default=0)  # Produktionsfortschritt %
    progress_assembly = Column(Integer, default=0)  # Montagefortschritt %
    
    # === PRIORITÄT & KLASSIFIZIERUNG ===
    priority = Column(Integer, default=5)  # 1-10, 1=highest
    complexity = Column(String(20), nullable=True)  # low, medium, high
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    strategic_importance = Column(String(20), nullable=True)  # Strategische Bedeutung
    
    # === VERTRAGLICHES ===
    contract_type = Column(String(100), nullable=True)  # Vertragsart (Werkvertrag, etc.)
    warranty_months = Column(Integer, default=60)  # Gewährleistung in Monaten
    retention_percent = Column(String(10), nullable=True)  # Einbehalt %
    retention_amount = Column(String(20), nullable=True)  # Einbehalt Betrag
    performance_bond = Column(Boolean, default=False)  # Vertragserfüllungsbürgschaft
    
    # === QUALITÄTSSICHERUNG ===
    quality_requirements = Column(Text, nullable=True)  # Qualitätsanforderungen
    inspection_plan_required = Column(Boolean, default=False)  # Prüfplan erforderlich
    acceptance_criteria = Column(Text, nullable=True)  # Abnahmekriterien
    
    # === KOMMUNIKATION ===
    communication_channel = Column(String(50), nullable=True)  # Bevorzugter Kanal
    report_frequency = Column(String(50), nullable=True)  # Berichtsfrequenz
    next_meeting_date = Column(DateTime, nullable=True)  # Nächster Termin
    
    # === REFERENZ & MARKETING ===
    is_reference_project = Column(Boolean, default=False)  # Referenzprojekt
    reference_approved = Column(Boolean, default=False)  # Referenz genehmigt
    photo_permission = Column(Boolean, default=False)  # Fotogenehmigung
    publication_allowed = Column(Boolean, default=False)  # Veröffentlichung erlaubt
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)  # Allgemeine Notizen
    internal_notes = Column(Text, nullable=True)  # Interne Notizen
    risk_notes = Column(Text, nullable=True)  # Risiko-Notizen
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)  # Tags für Kategorisierung
    custom_fields = Column(JSONB, default=dict)  # Benutzerdefinierte Felder
    extra_metadata = Column(JSONB, default=dict)  # Zusätzliche Metadaten
    
    # === RELATIONSHIPS ===
    customer = relationship("Customer", back_populates="projects")
    project_manager = relationship("Employee", foreign_keys=[project_manager_id])
    site_manager = relationship("Employee", foreign_keys=[site_manager_id])
    sales_person = relationship("Employee", foreign_keys=[sales_person_id])
    phases = relationship("ProjectPhase", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan")
    team_members = relationship("ProjectTeamMember", back_populates="project", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="project")


class ProjectPhase(Base, TimestampMixin):
    """Projektphasen"""
    __tablename__ = "project_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    
    planned_start = Column(Date, nullable=True)
    planned_end = Column(Date, nullable=True)
    actual_start = Column(Date, nullable=True)
    actual_end = Column(Date, nullable=True)
    
    progress_percent = Column(Integer, default=0)  # 0-100
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    project = relationship("Project", back_populates="phases")


class ProjectTask(Base, TimestampMixin, SoftDeleteMixin):
    """Projektaufgaben"""
    __tablename__ = "project_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    phase_id = Column(UUID(as_uuid=True), ForeignKey('project_phases.id'), nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('project_tasks.id'), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    priority = Column(Integer, default=5)  # 1-10
    status = Column(String(50), default="open")  # open, in_progress, completed, blocked
    
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    estimated_hours = Column(String(10), nullable=True)
    actual_hours = Column(String(10), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("Employee", foreign_keys=[assigned_to])
    subtasks = relationship("ProjectTask", backref="parent_task", remote_side=[id])


class ProjectDocument(Base, TimestampMixin, SoftDeleteMixin):
    """Projektdokumente"""
    __tablename__ = "project_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(100), nullable=True)  # plan, contract, permit, photo, etc.
    
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    version = Column(String(20), default="1.0")
    
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="documents")


class ProjectTeamMember(Base, TimestampMixin):
    """Projektteam-Mitglieder"""
    __tablename__ = "project_team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    role = Column(String(100), nullable=True)  # Projektleiter, Zimmerer, etc.
    planned_hours = Column(String(10), nullable=True)
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="team_members")
    employee = relationship("Employee")
