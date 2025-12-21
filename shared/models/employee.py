"""
Employee Models - Mitarbeiterverwaltung
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class EmploymentType(enum.Enum):
    """Beschäftigungsart"""
    VOLLZEIT = "vollzeit"
    TEILZEIT = "teilzeit"
    MINIJOB = "minijob"
    PRAKTIKANT = "praktikant"
    AZUBI = "azubi"  # Auszubildender
    FREELANCER = "freelancer"


class EmployeeStatus(enum.Enum):
    """Mitarbeiterstatus"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"  # Urlaub/Elternzeit/etc.
    TERMINATED = "terminated"


class Employee(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Mitarbeiter - Enterprise-Level mit allen Details"""
    __tablename__ = "employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_number = Column(String(50), nullable=False, index=True)
    
    # Link to user account (optional)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, unique=True)
    
    # === PERSÖNLICHE DATEN ===
    salutation = Column(String(20), nullable=True)  # Herr, Frau, etc.
    title = Column(String(50), nullable=True)  # Dr., Ing., etc.
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    birth_name = Column(String(100), nullable=True)  # Geburtsname
    
    date_of_birth = Column(Date, nullable=True)
    place_of_birth = Column(String(100), nullable=True)
    country_of_birth = Column(String(100), nullable=True)
    nationality = Column(String(100), nullable=True)
    second_nationality = Column(String(100), nullable=True)
    
    gender = Column(String(20), nullable=True)  # male, female, diverse
    marital_status = Column(String(50), nullable=True)  # single, married, divorced, widowed
    number_of_children = Column(Integer, default=0)
    
    # Ausweisdaten
    id_card_number = Column(String(50), nullable=True)
    id_card_valid_until = Column(Date, nullable=True)
    passport_number = Column(String(50), nullable=True)
    passport_valid_until = Column(Date, nullable=True)
    
    # === KONTAKT ===
    email = Column(String(255), nullable=True)
    email_private = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)  # Diensttelefon
    phone_private = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)  # Diensthandy
    mobile_private = Column(String(50), nullable=True)
    
    # Notfallkontakt
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_relationship = Column(String(100), nullable=True)  # Beziehung
    emergency_contact_phone = Column(String(50), nullable=True)
    emergency_contact_phone_alt = Column(String(50), nullable=True)
    
    # === ADRESSE ===
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    address_addition = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Deutschland")
    
    # Geokoordinaten (für Routenplanung)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    distance_to_office_km = Column(String(10), nullable=True)
    
    # === BESCHÄFTIGUNGSVERHÄLTNIS ===
    employment_type = Column(Enum(EmploymentType), default=EmploymentType.VOLLZEIT)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    
    position = Column(String(100), nullable=True)  # Zimmerer, Meister, Bauleiter
    position_code = Column(String(20), nullable=True)  # Positionskürzel
    job_title = Column(String(100), nullable=True)  # Stellenbezeichnung
    job_description = Column(Text, nullable=True)  # Stellenbeschreibung
    
    department = Column(String(100), nullable=True)  # Produktion, Montage, Planung
    department_code = Column(String(20), nullable=True)
    team = Column(String(100), nullable=True)  # Team/Gruppe
    cost_center = Column(String(50), nullable=True)  # Kostenstelle
    
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Eintrittsdaten
    hire_date = Column(Date, nullable=True)  # Eintrittsdatum
    seniority_date = Column(Date, nullable=True)  # Dienstalter-Datum
    probation_end = Column(Date, nullable=True)  # Ende Probezeit
    contract_end_date = Column(Date, nullable=True)  # Befristungsende
    termination_date = Column(Date, nullable=True)  # Austrittsdatum
    termination_reason = Column(String(255), nullable=True)  # Kündigungsgrund
    
    # Vertragsdetails
    contract_type = Column(String(50), nullable=True)  # befristet, unbefristet
    notice_period = Column(String(50), nullable=True)  # Kündigungsfrist
    collective_agreement = Column(String(100), nullable=True)  # Tarifvertrag
    wage_group = Column(String(50), nullable=True)  # Lohngruppe
    
    # === ARBEITSZEIT ===
    weekly_hours = Column(String(10), default="40")
    daily_hours = Column(String(10), nullable=True)
    work_days_per_week = Column(Integer, default=5)
    
    # Arbeitszeitmodell
    work_time_model = Column(String(50), nullable=True)  # Gleitzeit, Schicht, Vertrauensarbeitszeit
    flexible_time_start = Column(Time, nullable=True)  # Gleitzeit Start
    flexible_time_end = Column(Time, nullable=True)  # Gleitzeit Ende
    core_time_start = Column(Time, nullable=True)  # Kernzeit Start
    core_time_end = Column(Time, nullable=True)  # Kernzeit Ende
    
    # Schichtarbeit
    shift_model = Column(String(50), nullable=True)  # Früh, Spät, Nacht
    
    # Zeitkonten
    overtime_balance = Column(String(20), default="0")  # Überstunden-Saldo
    time_account_balance = Column(String(20), default="0")  # Zeitkonto
    
    # === URLAUB & ABWESENHEIT ===
    vacation_days_annual = Column(Integer, default=30)  # Jahresurlaub
    vacation_days_remaining = Column(Integer, default=0)  # Resturlaub
    vacation_days_taken = Column(Integer, default=0)  # Genommener Urlaub
    vacation_days_planned = Column(Integer, default=0)  # Geplanter Urlaub
    vacation_days_carried = Column(Integer, default=0)  # Übertrag Vorjahr
    
    special_leave_days = Column(Integer, default=0)  # Sonderurlaub
    sick_days_current_year = Column(Integer, default=0)  # Krankheitstage aktuelles Jahr
    
    # === VERGÜTUNG ===
    # ACHTUNG: Sensible Daten - in Produktion verschlüsseln!
    payment_type = Column(String(20), nullable=True)  # hourly, monthly, annual
    hourly_rate = Column(String(20), nullable=True)  # Stundenlohn
    monthly_salary = Column(String(20), nullable=True)  # Monatsgehalt
    annual_salary = Column(String(20), nullable=True)  # Jahresgehalt
    
    # Zulagen
    travel_allowance = Column(String(20), nullable=True)  # Fahrtkostenzuschuss
    meal_allowance = Column(String(20), nullable=True)  # Verpflegungszuschuss
    housing_allowance = Column(String(20), nullable=True)  # Wohnungszuschuss
    other_allowances = Column(JSONB, default=dict)  # Sonstige Zulagen
    
    # Bonus
    bonus_eligible = Column(Boolean, default=False)
    bonus_target = Column(String(20), nullable=True)  # Zielbonus
    
    # Abrechnungszeitraum
    payroll_period = Column(String(20), default="monthly")  # weekly, bi-weekly, monthly
    
    # === SOZIALVERSICHERUNG ===
    social_security_number = Column(String(50), nullable=True)  # Sozialversicherungsnummer
    tax_id = Column(String(50), nullable=True)  # Steuer-ID
    tax_class = Column(String(10), nullable=True)  # Steuerklasse
    tax_factor = Column(String(10), nullable=True)  # Faktor
    church_tax = Column(Boolean, default=False)  # Kirchensteuer
    church_denomination = Column(String(50), nullable=True)  # Konfession
    
    # Krankenversicherung
    health_insurance = Column(String(100), nullable=True)  # Krankenkasse
    health_insurance_number = Column(String(50), nullable=True)  # Versichertennummer
    health_insurance_type = Column(String(20), nullable=True)  # gesetzlich, privat
    
    # Weitere Versicherungen
    pension_insurance_number = Column(String(50), nullable=True)  # Rentenversicherungsnummer
    unemployment_insurance = Column(Boolean, default=True)
    nursing_care_insurance = Column(Boolean, default=True)
    accident_insurance = Column(Boolean, default=True)
    
    # === BANKVERBINDUNG ===
    bank_name = Column(String(255), nullable=True)
    iban = Column(String(50), nullable=True)
    bic = Column(String(20), nullable=True)
    account_holder = Column(String(255), nullable=True)
    
    # === QUALIFIKATIONEN ===
    education_level = Column(String(100), nullable=True)  # Ausbildungsabschluss
    education_field = Column(String(100), nullable=True)  # Ausbildungsberuf
    education_institution = Column(String(255), nullable=True)  # Ausbildungsstätte
    education_completion_date = Column(Date, nullable=True)  # Abschlussdatum
    
    highest_degree = Column(String(100), nullable=True)  # Höchster Abschluss
    degree_field = Column(String(100), nullable=True)  # Studiengang
    degree_institution = Column(String(255), nullable=True)  # Hochschule
    
    qualifications = Column(ARRAY(String), default=list)  # Zimmerergeselle, Meister, etc.
    specializations = Column(ARRAY(String), default=list)  # Spezialisierungen
    skills = Column(JSONB, default=dict)  # Fähigkeiten mit Bewertung
    
    # Führerscheine
    drivers_license = Column(ARRAY(String), default=list)  # B, BE, C, CE, etc.
    drivers_license_expiry = Column(JSONB, default=dict)  # Ablaufdaten pro Klasse
    
    # Sprachkenntnisse
    languages = Column(JSONB, default=dict)  # {"de": "native", "en": "B2"}
    
    # === SICHERHEIT & SCHUTZ ===
    safety_training_date = Column(Date, nullable=True)  # Letzte Sicherheitsunterweisung
    safety_training_due = Column(Date, nullable=True)  # Nächste fällig
    first_aid_trained = Column(Boolean, default=False)  # Ersthelfer
    first_aid_training_date = Column(Date, nullable=True)
    fire_warden = Column(Boolean, default=False)  # Brandschutzhelfer
    
    # Schutzausrüstung
    clothing_size = Column(String(10), nullable=True)  # S, M, L, XL
    shoe_size = Column(String(10), nullable=True)
    glove_size = Column(String(10), nullable=True)
    hard_hat_issued = Column(Boolean, default=False)
    safety_shoes_issued = Column(Boolean, default=False)
    
    # Arbeitsmedizin
    medical_exam_date = Column(Date, nullable=True)  # Letzte arbeitsmedizinische Untersuchung
    medical_exam_due = Column(Date, nullable=True)  # Nächste fällig
    medical_restrictions = Column(Text, nullable=True)  # Medizinische Einschränkungen
    
    # === AUSSTATTUNG ===
    equipment = Column(JSONB, default=dict)  # Zugewiesene Werkzeuge, Geräte
    company_car = Column(String(100), nullable=True)  # Firmenwagen
    company_car_license = Column(String(20), nullable=True)  # Kennzeichen
    company_phone = Column(String(50), nullable=True)  # Firmenhandy
    access_card_number = Column(String(50), nullable=True)  # Zugangskarte
    locker_number = Column(String(20), nullable=True)  # Spindnummer
    
    # IT-Ausstattung
    computer_name = Column(String(100), nullable=True)
    software_licenses = Column(JSONB, default=list)
    
    # === DIGITALE PRÄSENZ ===
    photo_url = Column(String(500), nullable=True)
    signature_url = Column(String(500), nullable=True)  # Digitale Unterschrift
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    hr_notes = Column(Text, nullable=True)  # HR-Notizen (vertraulich)
    performance_notes = Column(Text, nullable=True)  # Leistungsnotizen
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    user = relationship("User")
    supervisor = relationship("Employee", remote_side=[id])
    time_entries = relationship("TimeEntry", back_populates="employee")
    absences = relationship("Absence", back_populates="employee")
    certifications = relationship("Certification", back_populates="employee")


class TimeEntry(Base, TimestampMixin, TenantMixin):
    """Zeiterfassung"""
    __tablename__ = "time_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    
    work_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    break_minutes = Column(Integer, default=0)
    
    hours = Column(String(10), nullable=False)  # Arbeitsstunden
    overtime_hours = Column(String(10), default="0")
    
    activity_type = Column(String(50), nullable=True)  # Produktion, Montage, Planung, Fahrt, etc.
    description = Column(Text, nullable=True)
    
    # Location
    location = Column(String(255), nullable=True)  # Werkstatt, Baustelle, Büro
    
    # Billing
    is_billable = Column(Boolean, default=True)
    hourly_rate = Column(String(20), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")


class Absence(Base, TimestampMixin, TenantMixin):
    """Abwesenheiten (Urlaub, Krankheit, etc.)"""
    __tablename__ = "absences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    absence_type = Column(String(50), nullable=False)  # vacation, sick, training, unpaid, etc.
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(String(10), nullable=True)  # Anzahl Tage
    
    reason = Column(Text, nullable=True)
    
    # Approval
    status = Column(String(50), default="pending")  # pending, approved, rejected
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Documents
    document_url = Column(String(500), nullable=True)  # Krankmeldung, etc.
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="absences")


class Certification(Base, TimestampMixin):
    """Zertifikate und Qualifikationen"""
    __tablename__ = "certifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    name = Column(String(255), nullable=False)  # Kranschein, Motorsägeschein, Ersthelfer, etc.
    issuer = Column(String(255), nullable=True)
    
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    certification_number = Column(String(100), nullable=True)
    document_url = Column(String(500), nullable=True)
    
    is_mandatory = Column(Boolean, default=False)  # Pflichtqualifikation
    reminder_days = Column(Integer, default=30)  # Erinnerung vor Ablauf
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="certifications")
