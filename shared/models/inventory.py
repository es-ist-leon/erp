"""
Inventory Models - Materialverwaltung für Holzbau
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class MaterialCategory(enum.Enum):
    """Materialkategorien für Holzbau"""
    SCHNITTHOLZ = "schnittholz"  # Konstruktionsvollholz, Balkenschichtholz, etc.
    BRETTSCHICHTHOLZ = "brettschichtholz"  # BSH
    BRETTSPERRHOLZ = "brettsperrholz"  # CLT / Massivholzplatten
    PLATTEN = "platten"  # OSB, Sperrholz, MDF, etc.
    DAEMMUNG = "daemmung"  # Holzfaserdämmung, Zellulose, etc.
    DACH = "dach"  # Dachlatten, Konterlattung, etc.
    FASSADE = "fassade"  # Fassadenbekleidung
    VERBINDUNGSMITTEL = "verbindungsmittel"  # Schrauben, Nägel, Winkel, etc.
    BESCHLAEGE = "beschlaege"  # Balkenschuhe, Winkelverbinder, etc.
    FOLIEN = "folien"  # Dampfbremse, Unterspannbahn, etc.
    FENSTER_TUEREN = "fenster_tueren"  # Fenster, Türen
    SONSTIGES = "sonstiges"


class StockMovementType(enum.Enum):
    """Lagerbewegungstypen"""
    EINGANG = "eingang"  # Wareneingang
    AUSGANG = "ausgang"  # Warenausgang
    INVENTUR = "inventur"  # Inventurbuchung
    UMLAGERUNG = "umlagerung"  # Umlagerung
    RUECKGABE = "rueckgabe"  # Rückgabe
    VERSCHNITT = "verschnitt"  # Verschnitt/Verlust
    KORREKTUR = "korrektur"  # Korrektur


class Material(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Material/Artikel - Enterprise Holzbau mit allen technischen Details"""
    __tablename__ = "materials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_number = Column(String(50), nullable=False, index=True)  # Artikelnummer
    ean = Column(String(20), nullable=True)  # EAN/Barcode
    gtin = Column(String(20), nullable=True)  # GTIN
    manufacturer_number = Column(String(100), nullable=True)  # Herstellernummer
    
    name = Column(String(255), nullable=False)
    name_short = Column(String(100), nullable=True)  # Kurzbezeichnung
    description = Column(Text, nullable=True)
    description_long = Column(Text, nullable=True)  # Ausführliche Beschreibung
    
    # === KATEGORIE & KLASSIFIZIERUNG ===
    category = Column(Enum(MaterialCategory), nullable=False)
    subcategory = Column(String(100), nullable=True)
    product_group = Column(String(100), nullable=True)  # Warengruppe
    product_line = Column(String(100), nullable=True)  # Produktlinie
    
    # === HERSTELLER ===
    manufacturer = Column(String(255), nullable=True)  # Hersteller
    brand = Column(String(100), nullable=True)  # Marke
    manufacturer_url = Column(String(500), nullable=True)  # Herstellerseite
    
    # === ABMESSUNGEN ===
    length_mm = Column(Integer, nullable=True)  # Länge in mm
    width_mm = Column(Integer, nullable=True)  # Breite in mm
    height_mm = Column(Integer, nullable=True)  # Höhe/Dicke in mm
    
    # Toleranzen
    length_tolerance_mm = Column(String(20), nullable=True)  # Längentoleranz ±
    width_tolerance_mm = Column(String(20), nullable=True)
    height_tolerance_mm = Column(String(20), nullable=True)
    
    # Weitere Maße
    diameter_mm = Column(Integer, nullable=True)  # Durchmesser
    thread_size = Column(String(20), nullable=True)  # Gewindegröße
    
    # Gewicht & Volumen
    weight_kg = Column(String(20), nullable=True)  # Gewicht pro Einheit
    weight_per_meter = Column(String(20), nullable=True)  # kg/m
    weight_per_sqm = Column(String(20), nullable=True)  # kg/m²
    volume_m3 = Column(String(20), nullable=True)  # Volumen m³
    
    # === EINHEITEN ===
    unit = Column(String(20), default="STK")  # STK, m, m², m³, kg, PAK, etc.
    base_unit = Column(String(20), nullable=True)  # Basismengeneinheit
    sales_unit = Column(String(20), nullable=True)  # Verkaufseinheit
    purchase_unit = Column(String(20), nullable=True)  # Einkaufseinheit
    unit_conversion = Column(JSONB, default=dict)  # Umrechnungsfaktoren
    
    # Verpackung
    packaging_unit = Column(String(50), nullable=True)  # Verpackungseinheit
    pieces_per_package = Column(Integer, nullable=True)  # Stück pro Paket
    packages_per_pallet = Column(Integer, nullable=True)  # Pakete pro Palette
    pallet_quantity = Column(Integer, nullable=True)  # Menge pro Palette
    
    # === HOLZSPEZIFISCHE DATEN ===
    wood_type = Column(String(100), nullable=True)  # Fichte, Tanne, Lärche, Douglasie
    wood_type_latin = Column(String(100), nullable=True)  # Lateinischer Name
    wood_origin = Column(String(100), nullable=True)  # Herkunftsland
    
    quality_grade = Column(String(50), nullable=True)  # S10, C24, GL24h, etc.
    strength_class = Column(String(20), nullable=True)  # Festigkeitsklasse
    appearance_class = Column(String(20), nullable=True)  # Sichtqualität (A, B, AB)
    
    moisture_content = Column(String(10), nullable=True)  # Holzfeuchte %
    moisture_content_min = Column(String(10), nullable=True)  # Min Feuchte
    moisture_content_max = Column(String(10), nullable=True)  # Max Feuchte
    
    # Behandlung
    treatment = Column(String(100), nullable=True)  # KVH, NSi, technisch getrocknet
    surface_treatment = Column(String(100), nullable=True)  # Gehobelt, sägerau, gebürstet
    impregnation = Column(String(100), nullable=True)  # Imprägnierung
    fire_protection_class = Column(String(20), nullable=True)  # Brandschutzklasse
    
    # Zertifizierung
    certification = Column(String(50), nullable=True)  # PEFC, FSC
    certification_number = Column(String(100), nullable=True)
    ce_marking = Column(Boolean, default=False)  # CE-Kennzeichnung
    declaration_of_performance = Column(String(100), nullable=True)  # Leistungserklärung
    
    # === TECHNISCHE WERTE ===
    density_kg_m3 = Column(String(20), nullable=True)  # Rohdichte kg/m³
    bending_strength_mpa = Column(String(20), nullable=True)  # Biegefestigkeit MPa
    tensile_strength_mpa = Column(String(20), nullable=True)  # Zugfestigkeit
    compression_strength_mpa = Column(String(20), nullable=True)  # Druckfestigkeit
    shear_strength_mpa = Column(String(20), nullable=True)  # Scherfestigkeit
    e_modulus_mpa = Column(String(20), nullable=True)  # E-Modul
    
    # Bauphysik
    thermal_conductivity = Column(String(20), nullable=True)  # Wärmeleitfähigkeit λ
    vapor_diffusion_resistance = Column(String(20), nullable=True)  # Wasserdampfdiffusionswiderstand μ
    fire_reaction_class = Column(String(20), nullable=True)  # Brandverhaltensklasse
    sound_insulation_rw = Column(String(20), nullable=True)  # Schalldämmmaß Rw
    
    # Verbindungsmittel-spezifisch
    head_type = Column(String(50), nullable=True)  # Kopfform (Senkkopf, etc.)
    drive_type = Column(String(50), nullable=True)  # Antrieb (TX, PZ, etc.)
    tip_type = Column(String(50), nullable=True)  # Spitzenform
    thread_type = Column(String(50), nullable=True)  # Gewindeart
    material_type = Column(String(100), nullable=True)  # Material (Stahl, Edelstahl)
    coating = Column(String(100), nullable=True)  # Beschichtung
    corrosion_class = Column(String(20), nullable=True)  # Korrosionsschutzklasse
    
    # Zulassungen
    eta_number = Column(String(100), nullable=True)  # ETA-Zulassungsnummer
    approval_document = Column(String(255), nullable=True)  # Zulassungsdokument
    characteristic_load_capacity = Column(String(100), nullable=True)  # Charakt. Tragfähigkeit
    
    # === PREISE ===
    purchase_price = Column(String(20), nullable=True)  # Einkaufspreis
    purchase_price_date = Column(Date, nullable=True)  # Stand EK-Preis
    list_price = Column(String(20), nullable=True)  # Listenpreis
    selling_price = Column(String(20), nullable=True)  # Verkaufspreis
    minimum_price = Column(String(20), nullable=True)  # Mindestpreis
    
    margin_percent = Column(String(10), nullable=True)  # Marge %
    markup_percent = Column(String(10), nullable=True)  # Aufschlag %
    tax_rate = Column(String(10), default="19")  # MwSt.
    
    # Staffelpreise
    price_scales = Column(JSONB, default=list)  # [{qty: 100, price: 5.50}, ...]
    
    # === BESTAND ===
    min_stock = Column(String(20), default="0")  # Mindestbestand
    max_stock = Column(String(20), nullable=True)  # Maximalbestand
    safety_stock = Column(String(20), nullable=True)  # Sicherheitsbestand
    reorder_point = Column(String(20), nullable=True)  # Bestellpunkt
    reorder_quantity = Column(String(20), nullable=True)  # Bestellmenge
    lot_size = Column(String(20), nullable=True)  # Losgröße
    
    # Aktueller Bestand (Summe über alle Lager)
    current_stock = Column(String(20), default="0")
    reserved_stock = Column(String(20), default="0")
    available_stock = Column(String(20), default="0")
    ordered_stock = Column(String(20), default="0")  # Bestellte Menge
    
    # Statistiken
    average_consumption = Column(String(20), nullable=True)  # Durchschnittlicher Verbrauch
    last_purchase_date = Column(Date, nullable=True)
    last_sale_date = Column(Date, nullable=True)
    turnover_rate = Column(String(10), nullable=True)  # Umschlagshäufigkeit
    
    # === LIEFERANT ===
    primary_supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id'), nullable=True)
    supplier_article_number = Column(String(100), nullable=True)
    lead_time_days = Column(Integer, nullable=True)  # Lieferzeit in Tagen
    minimum_order_quantity = Column(String(20), nullable=True)  # Mindestbestellmenge
    
    # Alternative Lieferanten in supplier_articles Tabelle
    
    # === LAGER ===
    default_location_id = Column(UUID(as_uuid=True), ForeignKey('warehouse_locations.id'), nullable=True)
    storage_conditions = Column(Text, nullable=True)  # Lagerbedingungen
    shelf_life_days = Column(Integer, nullable=True)  # Haltbarkeit
    
    # === STATUS & FLAGS ===
    is_active = Column(Boolean, default=True)
    is_producible = Column(Boolean, default=False)  # Kann gefertigt werden
    is_purchasable = Column(Boolean, default=True)  # Kann eingekauft werden
    is_sellable = Column(Boolean, default=True)  # Kann verkauft werden
    is_stockable = Column(Boolean, default=True)  # Lagerfähig
    is_serial_tracked = Column(Boolean, default=False)  # Seriennummernpflichtig
    is_batch_tracked = Column(Boolean, default=False)  # Chargenpflichtig
    is_hazardous = Column(Boolean, default=False)  # Gefahrgut
    
    # Lifecycle
    status = Column(String(50), default="active")  # active, discontinued, obsolete
    discontinued_date = Column(Date, nullable=True)
    replacement_article_id = Column(UUID(as_uuid=True), nullable=True)  # Nachfolgeartikel
    
    # === DOKUMENTE & MEDIEN ===
    image_url = Column(String(500), nullable=True)
    image_urls = Column(JSONB, default=list)  # Weitere Bilder
    datasheet_url = Column(String(500), nullable=True)  # Datenblatt
    safety_datasheet_url = Column(String(500), nullable=True)  # Sicherheitsdatenblatt
    installation_guide_url = Column(String(500), nullable=True)  # Montageanleitung
    video_url = Column(String(500), nullable=True)  # Produktvideo
    
    # === NOTIZEN ===
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    purchase_notes = Column(Text, nullable=True)  # Hinweise für Einkauf
    production_notes = Column(Text, nullable=True)  # Hinweise für Produktion
    
    # === FLEXIBLE ERWEITERUNG ===
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    technical_data = Column(JSONB, default=dict)  # Zusätzliche technische Daten
    
    # === RELATIONSHIPS ===
    primary_supplier = relationship("Supplier", foreign_keys=[primary_supplier_id])
    default_location = relationship("WarehouseLocation", foreign_keys=[default_location_id])
    stock_levels = relationship("StockLevel", back_populates="material")
    supplier_articles = relationship("SupplierArticle", back_populates="material")


class Supplier(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Lieferant"""
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_number = Column(String(50), nullable=False, index=True)
    
    company_name = Column(String(255), nullable=False)
    tax_id = Column(String(50), nullable=True)
    
    # Contact
    contact_person = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    fax = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Deutschland")
    
    # Payment
    payment_terms = Column(String(10), default="30")
    iban = Column(String(50), nullable=True)
    bic = Column(String(20), nullable=True)
    
    # Rating
    rating = Column(Integer, nullable=True)  # 1-5 Sterne
    
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    supplier_articles = relationship("SupplierArticle", back_populates="supplier")


class SupplierArticle(Base, TimestampMixin):
    """Lieferanten-Artikel-Zuordnung (Einkaufspreise pro Lieferant)"""
    __tablename__ = "supplier_articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id'), nullable=False)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=False)
    
    supplier_article_number = Column(String(100), nullable=True)
    supplier_article_name = Column(String(255), nullable=True)
    
    purchase_price = Column(String(20), nullable=True)
    min_order_quantity = Column(String(20), nullable=True)
    price_unit = Column(String(20), default="STK")  # Preiseinheit
    
    lead_time_days = Column(Integer, nullable=True)
    is_preferred = Column(Boolean, default=False)
    
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="supplier_articles")
    material = relationship("Material", back_populates="supplier_articles")


class Warehouse(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Lager"""
    __tablename__ = "warehouses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Address
    street = Column(String(255), nullable=True)
    street_number = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    locations = relationship("WarehouseLocation", back_populates="warehouse")


class WarehouseLocation(Base, TimestampMixin):
    """Lagerplatz"""
    __tablename__ = "warehouse_locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=False)
    
    code = Column(String(50), nullable=False)  # z.B. "A-01-03" (Regal-Ebene-Fach)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Dimensions
    max_weight_kg = Column(Integer, nullable=True)
    length_mm = Column(Integer, nullable=True)
    width_mm = Column(Integer, nullable=True)
    height_mm = Column(Integer, nullable=True)
    
    location_type = Column(String(50), nullable=True)  # shelf, floor, outdoor, etc.
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="locations")
    stock_levels = relationship("StockLevel", back_populates="location")


class StockLevel(Base, TimestampMixin):
    """Aktueller Lagerbestand"""
    __tablename__ = "stock_levels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey('warehouse_locations.id'), nullable=False)
    
    quantity = Column(String(20), default="0")
    reserved_quantity = Column(String(20), default="0")  # Reserviert für Aufträge
    available_quantity = Column(String(20), default="0")  # Verfügbar
    
    batch_number = Column(String(100), nullable=True)  # Chargennummer
    serial_number = Column(String(100), nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    last_counted_at = Column(DateTime, nullable=True)
    last_counted_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    material = relationship("Material", back_populates="stock_levels")
    location = relationship("WarehouseLocation", back_populates="stock_levels")


class StockMovement(Base, TimestampMixin, TenantMixin):
    """Lagerbewegung"""
    __tablename__ = "stock_movements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    movement_number = Column(String(50), nullable=False, index=True)
    
    material_id = Column(UUID(as_uuid=True), ForeignKey('materials.id'), nullable=False)
    movement_type = Column(Enum(StockMovementType), nullable=False)
    
    quantity = Column(String(20), nullable=False)
    unit = Column(String(20), nullable=False)
    
    from_location_id = Column(UUID(as_uuid=True), ForeignKey('warehouse_locations.id'), nullable=True)
    to_location_id = Column(UUID(as_uuid=True), ForeignKey('warehouse_locations.id'), nullable=True)
    
    # Reference
    reference_type = Column(String(50), nullable=True)  # order, project, purchase_order, etc.
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    batch_number = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    performed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    performed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    material = relationship("Material")
    from_location = relationship("WarehouseLocation", foreign_keys=[from_location_id])
    to_location = relationship("WarehouseLocation", foreign_keys=[to_location_id])
