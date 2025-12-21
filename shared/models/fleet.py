"""
Fleet & Equipment Models - Fahrzeuge und Geräte/Maschinen
Enterprise-Level für Holzbau
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class VehicleType(enum.Enum):
    """Fahrzeugtypen"""
    PKW = "pkw"  # PKW
    TRANSPORTER = "transporter"  # Transporter
    LKW = "lkw"  # LKW
    LKW_ANHAENGER = "lkw_anhaenger"  # LKW mit Anhänger
    SATTELZUG = "sattelzug"  # Sattelzug
    PRITSCHE = "pritsche"  # Pritschenwagen
    KIPPER = "kipper"  # Kipper
    TIEFLADER = "tieflader"  # Tieflader
    KRAN_LKW = "kran_lkw"  # LKW mit Ladekran
    ANHAENGER = "anhaenger"  # Anhänger
    SONSTIGE = "sonstige"


class VehicleStatus(enum.Enum):
    """Fahrzeugstatus"""
    AVAILABLE = "available"  # Verfügbar
    IN_USE = "in_use"  # Im Einsatz
    MAINTENANCE = "maintenance"  # In Wartung
    REPAIR = "repair"  # In Reparatur
    RESERVED = "reserved"  # Reserviert
    OUT_OF_SERVICE = "out_of_service"  # Außer Betrieb


class EquipmentType(enum.Enum):
    """Geräte/Maschinentypen"""
    AUTOKRAN = "autokran"  # Autokran
    MOBILKRAN = "mobilkran"  # Mobilkran
    GABELSTAPLER = "gabelstapler"  # Gabelstapler
    TELESKOPLADER = "teleskoplader"  # Teleskoplader
    HUBSTEIGER = "hubsteiger"  # Hubarbeitsbühne
    BAGGER = "bagger"  # Bagger
    RADLADER = "radlader"  # Radlader
    KOMPRESSOR = "kompressor"  # Kompressor
    GENERATOR = "generator"  # Generator/Stromaggregat
    NAGLER = "nagler"  # Nagelgerät
    KETTENSAEGE = "kettensaege"  # Kettensäge
    KREISSAEGE = "kreissaege"  # Kreissäge
    BANDSAEGE = "bandsaege"  # Bandsäge
    HOBEL = "hobel"  # Hobelmaschine
    BOHRMASCHINE = "bohrmaschine"  # Bohrmaschine
    AKKUSCHRAUBER = "akkuschrauber"  # Akkuschrauber
    LASER = "laser"  # Laser/Nivelliergerät
    MESSGERAET = "messgeraet"  # Messgerät
    WERKZEUGKOFFER = "werkzeugkoffer"  # Werkzeugkoffer
    GERUEST = "geruest"  # Gerüst
    ABSTURZSICHERUNG = "absturzsicherung"  # Absturzsicherung
    SONSTIGES = "sonstiges"


class Vehicle(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Fahrzeug - Komplette Fuhrparkverwaltung"""
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_number = Column(String(50), nullable=False, index=True)  # Interne Nummer
    
    # === GRUNDDATEN ===
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)
    
    # Kennzeichen
    license_plate = Column(String(20), nullable=False, index=True)
    license_plate_secondary = Column(String(20), nullable=True)  # Bei Anhänger
    
    # Fahrzeugdaten
    manufacturer = Column(String(100), nullable=True)  # Hersteller
    model = Column(String(100), nullable=True)  # Modell
    variant = Column(String(100), nullable=True)  # Variante
    color = Column(String(50), nullable=True)  # Farbe
    
    vin = Column(String(50), nullable=True)  # Fahrgestellnummer (VIN)
    first_registration = Column(Date, nullable=True)  # Erstzulassung
    purchase_date = Column(Date, nullable=True)  # Kaufdatum
    warranty_until = Column(Date, nullable=True)  # Garantie bis
    
    # === TECHNISCHE DATEN ===
    engine_type = Column(String(50), nullable=True)  # Diesel, Benzin, Elektro, Hybrid
    engine_power_kw = Column(Integer, nullable=True)  # Leistung kW
    engine_power_hp = Column(Integer, nullable=True)  # Leistung PS
    engine_displacement_ccm = Column(Integer, nullable=True)  # Hubraum ccm
    
    transmission = Column(String(50), nullable=True)  # Schaltung, Automatik
    drive_type = Column(String(50), nullable=True)  # 4x2, 4x4, 6x4
    axle_count = Column(Integer, nullable=True)  # Achsanzahl
    
    # Maße & Gewichte
    length_mm = Column(Integer, nullable=True)  # Länge
    width_mm = Column(Integer, nullable=True)  # Breite
    height_mm = Column(Integer, nullable=True)  # Höhe
    
    curb_weight_kg = Column(Integer, nullable=True)  # Leergewicht
    gross_weight_kg = Column(Integer, nullable=True)  # Zulässiges Gesamtgewicht
    payload_kg = Column(Integer, nullable=True)  # Nutzlast
    trailer_load_kg = Column(Integer, nullable=True)  # Anhängelast
    
    # Ladefläche
    loading_length_mm = Column(Integer, nullable=True)
    loading_width_mm = Column(Integer, nullable=True)
    loading_height_mm = Column(Integer, nullable=True)
    loading_volume_m3 = Column(String(20), nullable=True)
    
    # Kran (falls vorhanden)
    has_crane = Column(Boolean, default=False)
    crane_manufacturer = Column(String(100), nullable=True)
    crane_model = Column(String(100), nullable=True)
    crane_max_reach_m = Column(String(20), nullable=True)  # Maximale Reichweite
    crane_max_capacity_kg = Column(Integer, nullable=True)  # Maximale Tragkraft
    crane_inspection_date = Column(Date, nullable=True)  # Kranprüfung
    crane_inspection_due = Column(Date, nullable=True)  # Nächste Prüfung fällig
    
    # === VERBRAUCH & KOSTEN ===
    fuel_type = Column(String(50), nullable=True)  # Kraftstoffart
    tank_capacity_l = Column(Integer, nullable=True)  # Tankinhalt Liter
    avg_consumption = Column(String(10), nullable=True)  # Durchschnittsverbrauch l/100km
    
    # Kostenerfassung
    purchase_price = Column(String(20), nullable=True)  # Kaufpreis
    current_value = Column(String(20), nullable=True)  # Aktueller Wert
    monthly_lease_rate = Column(String(20), nullable=True)  # Leasingrate
    insurance_cost_annual = Column(String(20), nullable=True)  # Jährliche Versicherung
    tax_annual = Column(String(20), nullable=True)  # Kfz-Steuer
    
    # === KILOMETERSTAND ===
    current_mileage_km = Column(Integer, default=0)  # Aktueller km-Stand
    mileage_at_purchase = Column(Integer, nullable=True)  # km bei Kauf
    annual_mileage_limit = Column(Integer, nullable=True)  # Jahresfahrleistung (bei Leasing)
    
    # === PRÜFUNGEN & TERMINE ===
    tuv_date = Column(Date, nullable=True)  # Letzte HU
    tuv_due = Column(Date, nullable=True)  # Nächste HU fällig
    au_date = Column(Date, nullable=True)  # Letzte AU
    au_due = Column(Date, nullable=True)  # Nächste AU fällig
    sp_date = Column(Date, nullable=True)  # Letzte SP (Sicherheitsprüfung)
    sp_due = Column(Date, nullable=True)  # Nächste SP fällig
    uvv_date = Column(Date, nullable=True)  # Letzte UVV-Prüfung
    uvv_due = Column(Date, nullable=True)  # Nächste UVV fällig
    
    # === VERSICHERUNG ===
    insurance_company = Column(String(255), nullable=True)
    insurance_number = Column(String(100), nullable=True)
    insurance_type = Column(String(50), nullable=True)  # Haftpflicht, Teilkasko, Vollkasko
    insurance_valid_until = Column(Date, nullable=True)
    
    # === FAHRZEUGDOKUMENTE ===
    registration_document_1 = Column(String(500), nullable=True)  # Zulassungsbescheinigung I
    registration_document_2 = Column(String(500), nullable=True)  # Zulassungsbescheinigung II
    
    # === AUSSTATTUNG ===
    equipment_list = Column(JSONB, default=list)  # Sonderausstattung
    accessories = Column(JSONB, default=list)  # Zubehör
    
    # GPS-Tracking
    gps_device_id = Column(String(100), nullable=True)
    gps_enabled = Column(Boolean, default=False)
    last_known_latitude = Column(String(20), nullable=True)
    last_known_longitude = Column(String(20), nullable=True)
    last_position_at = Column(DateTime, nullable=True)
    
    # === ZUWEISUNG ===
    assigned_driver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    assigned_project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    
    home_location = Column(String(255), nullable=True)  # Heimatstandort
    current_location = Column(String(255), nullable=True)  # Aktueller Standort
    
    # === WARTUNG ===
    last_service_date = Column(Date, nullable=True)  # Letzte Wartung
    last_service_mileage = Column(Integer, nullable=True)  # km bei letzter Wartung
    next_service_date = Column(Date, nullable=True)  # Nächste Wartung
    next_service_mileage = Column(Integer, nullable=True)  # km-Stand für nächste Wartung
    service_interval_km = Column(Integer, nullable=True)  # Wartungsintervall km
    service_interval_months = Column(Integer, nullable=True)  # Wartungsintervall Monate
    
    # === BILDER & DOKUMENTE ===
    image_url = Column(String(500), nullable=True)
    images = Column(JSONB, default=list)
    documents = Column(JSONB, default=list)
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    damage_notes = Column(Text, nullable=True)  # Schadenhinweise
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    assigned_driver = relationship("Employee", foreign_keys=[assigned_driver_id])
    assigned_project = relationship("Project", foreign_keys=[assigned_project_id])
    fuel_logs = relationship("FuelLog", back_populates="vehicle")
    mileage_logs = relationship("MileageLog", back_populates="vehicle")
    maintenance_records = relationship("VehicleMaintenance", back_populates="vehicle")


class Equipment(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Gerät/Maschine - Werkzeug- und Maschinenverwaltung"""
    __tablename__ = "equipment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_number = Column(String(50), nullable=False, index=True)  # Inventarnummer
    
    # === GRUNDDATEN ===
    equipment_type = Column(Enum(EquipmentType), nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hersteller & Modell
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    
    # === TECHNISCHE DATEN ===
    power_kw = Column(String(20), nullable=True)  # Leistung
    power_source = Column(String(50), nullable=True)  # Strom, Akku, Diesel, Benzin, Druckluft
    voltage = Column(String(20), nullable=True)  # Spannung (bei Elektro)
    
    weight_kg = Column(String(20), nullable=True)
    dimensions = Column(String(100), nullable=True)  # L x B x H
    
    # Spezifische Daten (je nach Typ)
    technical_data = Column(JSONB, default=dict)
    # z.B. {"lift_height_m": "20", "max_load_kg": "500", "reach_m": "15"}
    
    # === ANSCHAFFUNG ===
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(String(20), nullable=True)
    current_value = Column(String(20), nullable=True)
    warranty_until = Column(Date, nullable=True)
    supplier = Column(String(255), nullable=True)
    
    # Leasing/Miete
    is_owned = Column(Boolean, default=True)  # Eigentum oder Miete
    rental_company = Column(String(255), nullable=True)
    rental_start = Column(Date, nullable=True)
    rental_end = Column(Date, nullable=True)
    rental_cost_daily = Column(String(20), nullable=True)
    
    # === PRÜFUNGEN ===
    uvv_inspection_date = Column(Date, nullable=True)  # Letzte UVV-Prüfung
    uvv_inspection_due = Column(Date, nullable=True)  # Nächste fällig
    uvv_inspection_interval_months = Column(Integer, nullable=True)
    
    calibration_date = Column(Date, nullable=True)  # Kalibrierung (für Messgeräte)
    calibration_due = Column(Date, nullable=True)
    
    electrical_test_date = Column(Date, nullable=True)  # E-Check
    electrical_test_due = Column(Date, nullable=True)
    
    # === BETRIEBSSTUNDEN ===
    operating_hours = Column(String(20), default="0")  # Aktuelle Betriebsstunden
    operating_hours_at_purchase = Column(String(20), nullable=True)
    service_interval_hours = Column(Integer, nullable=True)  # Wartungsintervall
    
    # === STANDORT & ZUWEISUNG ===
    home_location = Column(String(255), nullable=True)  # Stammplatz
    current_location = Column(String(255), nullable=True)  # Aktueller Standort
    
    assigned_employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    assigned_project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    assigned_vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=True)
    
    # === ZERTIFIKATE & ZULASSUNGEN ===
    ce_marking = Column(Boolean, default=False)
    type_approval = Column(String(100), nullable=True)  # Typzulassung
    operating_permit = Column(String(100), nullable=True)  # Betriebserlaubnis
    
    # Erforderliche Qualifikation
    required_qualification = Column(String(255), nullable=True)  # z.B. "Kranschein"
    
    # === WARTUNG ===
    last_maintenance_date = Column(Date, nullable=True)
    last_maintenance_hours = Column(String(20), nullable=True)
    next_maintenance_date = Column(Date, nullable=True)
    next_maintenance_hours = Column(String(20), nullable=True)
    
    maintenance_notes = Column(Text, nullable=True)
    
    # === ZUBEHÖR & VERBRAUCHSMATERIAL ===
    accessories = Column(JSONB, default=list)
    # [{"item": "Sägeblatt 300mm", "quantity": 2}]
    
    consumables = Column(JSONB, default=list)
    # [{"item": "Kettensägenöl", "consumption_rate": "0.5l/h"}]
    
    # === BILDER & DOKUMENTE ===
    image_url = Column(String(500), nullable=True)
    images = Column(JSONB, default=list)
    documents = Column(JSONB, default=list)
    manual_url = Column(String(500), nullable=True)  # Bedienungsanleitung
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    condition_notes = Column(Text, nullable=True)  # Zustandshinweise
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # === RELATIONSHIPS ===
    assigned_employee = relationship("Employee", foreign_keys=[assigned_employee_id])
    assigned_project = relationship("Project", foreign_keys=[assigned_project_id])
    assigned_vehicle = relationship("Vehicle", foreign_keys=[assigned_vehicle_id])
    maintenance_records = relationship("EquipmentMaintenance", back_populates="equipment")


class FuelLog(Base, TimestampMixin, TenantMixin):
    """Tankprotokoll"""
    __tablename__ = "fuel_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    
    refuel_date = Column(Date, nullable=False)
    refuel_time = Column(String(10), nullable=True)
    
    mileage_km = Column(Integer, nullable=False)  # km-Stand beim Tanken
    
    fuel_type = Column(String(50), nullable=True)  # Diesel, Super, AdBlue
    quantity_liters = Column(String(20), nullable=False)  # Menge Liter
    price_per_liter = Column(String(10), nullable=True)  # Preis pro Liter
    total_price = Column(String(20), nullable=True)  # Gesamtpreis
    
    full_tank = Column(Boolean, default=True)  # Vollgetankt
    
    gas_station = Column(String(255), nullable=True)  # Tankstelle
    gas_station_location = Column(String(255), nullable=True)  # Ort
    
    payment_method = Column(String(50), nullable=True)  # Tankkarte, Bar, EC
    card_number = Column(String(50), nullable=True)  # Tankkartennummer
    receipt_number = Column(String(100), nullable=True)
    
    driver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    driver = relationship("Employee")


class MileageLog(Base, TimestampMixin, TenantMixin):
    """Fahrtenbuch"""
    __tablename__ = "mileage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    
    trip_date = Column(Date, nullable=False)
    
    # Start
    start_time = Column(String(10), nullable=True)
    start_mileage = Column(Integer, nullable=False)
    start_location = Column(String(255), nullable=True)
    
    # Ende
    end_time = Column(String(10), nullable=True)
    end_mileage = Column(Integer, nullable=False)
    end_location = Column(String(255), nullable=True)
    
    # Berechnet
    distance_km = Column(Integer, nullable=True)
    
    # Fahrt
    trip_type = Column(String(50), nullable=True)  # business, private, commute
    purpose = Column(String(255), nullable=True)  # Zweck der Fahrt
    route_description = Column(Text, nullable=True)  # Fahrtstrecke
    
    # Zuordnung
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    
    driver_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Abrechnung
    is_billable = Column(Boolean, default=False)
    km_rate = Column(String(10), nullable=True)  # €/km
    total_cost = Column(String(20), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="mileage_logs")
    project = relationship("Project")
    customer = relationship("Customer")
    driver = relationship("Employee")


class VehicleMaintenance(Base, TimestampMixin, TenantMixin):
    """Fahrzeugwartung/-reparatur"""
    __tablename__ = "vehicle_maintenance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    
    maintenance_type = Column(String(100), nullable=False)
    # Inspektion, Ölwechsel, Reifenwechsel, TÜV, Reparatur, Unfall, etc.
    
    maintenance_date = Column(Date, nullable=False)
    mileage_at_maintenance = Column(Integer, nullable=True)
    
    description = Column(Text, nullable=True)  # Beschreibung der Arbeiten
    
    # Werkstatt
    workshop_name = Column(String(255), nullable=True)
    workshop_address = Column(String(255), nullable=True)
    
    # Kosten
    parts_cost = Column(String(20), nullable=True)  # Materialkosten
    labor_cost = Column(String(20), nullable=True)  # Arbeitskosten
    total_cost = Column(String(20), nullable=True)  # Gesamtkosten
    
    invoice_number = Column(String(100), nullable=True)
    invoice_date = Column(Date, nullable=True)
    
    # Dokumentation
    documents = Column(JSONB, default=list)
    
    # Nächste Wartung
    next_maintenance_date = Column(Date, nullable=True)
    next_maintenance_mileage = Column(Integer, nullable=True)
    
    performed_by = Column(String(255), nullable=True)  # Durchgeführt von
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")


class EquipmentMaintenance(Base, TimestampMixin, TenantMixin):
    """Gerätewartung/-reparatur"""
    __tablename__ = "equipment_maintenance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id'), nullable=False)
    
    maintenance_type = Column(String(100), nullable=False)
    # Wartung, Reparatur, UVV-Prüfung, Kalibrierung, E-Check
    
    maintenance_date = Column(Date, nullable=False)
    operating_hours_at_maintenance = Column(String(20), nullable=True)
    
    description = Column(Text, nullable=True)
    
    # Kosten
    parts_cost = Column(String(20), nullable=True)
    labor_cost = Column(String(20), nullable=True)
    total_cost = Column(String(20), nullable=True)
    
    performed_by = Column(String(255), nullable=True)
    service_provider = Column(String(255), nullable=True)
    
    # Prüfergebnis (für UVV etc.)
    inspection_result = Column(String(50), nullable=True)  # passed, failed, conditional
    inspection_certificate = Column(String(500), nullable=True)  # Prüfbescheinigung
    
    # Nächste Wartung/Prüfung
    next_maintenance_date = Column(Date, nullable=True)
    next_maintenance_hours = Column(String(20), nullable=True)
    
    documents = Column(JSONB, default=list)
    notes = Column(Text, nullable=True)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")


class EquipmentReservation(Base, TimestampMixin, TenantMixin):
    """Geräte-/Fahrzeugreservierung"""
    __tablename__ = "equipment_reservations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Was wird reserviert
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=True)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id'), nullable=True)
    
    # Zeitraum
    start_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=True)
    end_date = Column(Date, nullable=False)
    end_time = Column(String(10), nullable=True)
    
    # Wofür
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=True)
    purpose = Column(String(255), nullable=True)
    
    # Wer
    reserved_by_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    reserved_for_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled, completed
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle")
    equipment = relationship("Equipment")
    project = relationship("Project")
    reserved_by = relationship("Employee", foreign_keys=[reserved_by_id])
    reserved_for = relationship("Employee", foreign_keys=[reserved_for_id])
