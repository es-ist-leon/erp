"""
Project Dialog - Umfassende Projekterfassung für Holzbau
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QDateEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QScrollArea, QLabel,
    QGridLayout, QFrame, QTimeEdit
)
from PyQt6.QtCore import Qt, QDate, QTime
import uuid
from datetime import datetime

from shared.models import Project, ProjectType, ProjectStatus, Customer
from sqlalchemy import select


class ProjectDialog(QDialog):
    """Dialog for creating/editing projects - Vollumfängliche Erfassung"""
    
    def __init__(self, db_service, project_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.project_id = project_id
        self.user = user
        self.project = None
        self.setup_ui()
        self.load_customers()
        if project_id:
            self.load_project()
    
    def _create_section_header(self, text):
        """Erstellt einen Abschnitts-Header"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #374151;
                padding: 8px 0 4px 0;
                border-bottom: 2px solid #e5e7eb;
                margin-top: 10px;
            }
        """)
        return label
    
    def _create_scrollable_tab(self, content_widget):
        """Erstellt einen scrollbaren Tab"""
        scroll = QScrollArea()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        return scroll
    
    def setup_ui(self):
        self.setWindowTitle("Neues Projekt" if not self.project_id else "Projekt bearbeiten")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # ==================== TAB 1: GRUNDDATEN ====================
        basic_widget = QWidget()
        basic_layout = QVBoxLayout(basic_widget)
        basic_layout.setSpacing(15)
        
        # Projektinformationen
        basic_layout.addWidget(self._create_section_header("📋 Projektinformationen"))
        info_form = QFormLayout()
        info_form.setSpacing(10)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("z.B. Einfamilienhaus Müller")
        info_form.addRow("Projektname*:", self.name)
        
        self.project_number = QLineEdit()
        self.project_number.setPlaceholderText("Wird automatisch generiert")
        self.project_number.setEnabled(False)
        info_form.addRow("Projektnummer:", self.project_number)
        
        self.customer_combo = QComboBox()
        info_form.addRow("Kunde:", self.customer_combo)
        
        self.project_type = QComboBox()
        self.project_type.addItem("Neubau", "neubau")
        self.project_type.addItem("Anbau", "anbau")
        self.project_type.addItem("Aufstockung", "aufstockung")
        self.project_type.addItem("Dachstuhl", "dachstuhl")
        self.project_type.addItem("Carport", "carport")
        self.project_type.addItem("Garage", "garage")
        self.project_type.addItem("Fassade", "fassade")
        self.project_type.addItem("Sanierung", "sanierung")
        self.project_type.addItem("Holzrahmenbau", "holzrahmenbau")
        self.project_type.addItem("Blockhaus", "blockhaus")
        self.project_type.addItem("Hallenbau", "hallenbau")
        self.project_type.addItem("Balkon/Terrasse", "balkon")
        self.project_type.addItem("Wintergarten", "wintergarten")
        self.project_type.addItem("Sonstiges", "sonstiges")
        info_form.addRow("Projekttyp:", self.project_type)
        
        self.status = QComboBox()
        self.status.addItem("Anfrage", "anfrage")
        self.status.addItem("Angebot erstellt", "angebot")
        self.status.addItem("Beauftragt", "beauftragt")
        self.status.addItem("In Planung", "planung")
        self.status.addItem("Genehmigung", "genehmigung")
        self.status.addItem("Produktion", "produktion")
        self.status.addItem("Montage", "montage")
        self.status.addItem("Nacharbeiten", "nacharbeiten")
        self.status.addItem("Abnahme", "abnahme")
        self.status.addItem("Fertiggestellt", "fertig")
        self.status.addItem("Gewährleistung", "gewaehrleistung")
        self.status.addItem("Storniert", "storniert")
        info_form.addRow("Status:", self.status)
        
        self.priority = QComboBox()
        self.priority.addItem("Niedrig", 7)
        self.priority.addItem("Normal", 5)
        self.priority.addItem("Hoch", 3)
        self.priority.addItem("Kritisch", 1)
        self.priority.setCurrentIndex(1)
        info_form.addRow("Priorität:", self.priority)
        
        basic_layout.addLayout(info_form)
        
        # Beschreibung
        basic_layout.addWidget(self._create_section_header("📝 Beschreibung"))
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Allgemeine Projektbeschreibung...")
        basic_layout.addWidget(self.description)
        
        # Tags & Kategorien
        basic_layout.addWidget(self._create_section_header("🏷️ Kategorisierung"))
        cat_form = QFormLayout()
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("z.B. Premium, Öko, Großprojekt (kommagetrennt)")
        cat_form.addRow("Tags:", self.tags)
        
        self.reference_number = QLineEdit()
        self.reference_number.setPlaceholderText("Externe Referenz/Bauaktenzeichen")
        cat_form.addRow("Referenznummer:", self.reference_number)
        basic_layout.addLayout(cat_form)
        
        basic_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(basic_widget), "📋 Grunddaten")
        
        # ==================== TAB 2: BAUSTELLE & STANDORT ====================
        site_widget = QWidget()
        site_layout = QVBoxLayout(site_widget)
        site_layout.setSpacing(15)
        
        # Adresse
        site_layout.addWidget(self._create_section_header("📍 Baustellenadresse"))
        addr_form = QFormLayout()
        addr_form.setSpacing(10)
        
        self.site_street = QLineEdit()
        self.site_street.setPlaceholderText("Straßenname")
        addr_form.addRow("Straße:", self.site_street)
        
        self.site_street_number = QLineEdit()
        self.site_street_number.setMaximumWidth(100)
        addr_form.addRow("Hausnummer:", self.site_street_number)
        
        self.site_postal = QLineEdit()
        self.site_postal.setMaximumWidth(100)
        addr_form.addRow("PLZ:", self.site_postal)
        
        self.site_city = QLineEdit()
        addr_form.addRow("Stadt:", self.site_city)
        
        self.site_district = QLineEdit()
        self.site_district.setPlaceholderText("Stadtteil/Ortsteil")
        addr_form.addRow("Ortsteil:", self.site_district)
        
        self.site_state = QLineEdit()
        self.site_state.setPlaceholderText("z.B. Bayern, NRW")
        addr_form.addRow("Bundesland:", self.site_state)
        
        self.site_country = QLineEdit()
        self.site_country.setText("Deutschland")
        addr_form.addRow("Land:", self.site_country)
        site_layout.addLayout(addr_form)
        
        # Geokoordinaten
        site_layout.addWidget(self._create_section_header("🌍 Geokoordinaten"))
        geo_form = QFormLayout()
        
        self.geo_latitude = QDoubleSpinBox()
        self.geo_latitude.setRange(-90, 90)
        self.geo_latitude.setDecimals(8)
        self.geo_latitude.setSpecialValueText("Nicht gesetzt")
        geo_form.addRow("Breitengrad (Lat):", self.geo_latitude)
        
        self.geo_longitude = QDoubleSpinBox()
        self.geo_longitude.setRange(-180, 180)
        self.geo_longitude.setDecimals(8)
        self.geo_longitude.setSpecialValueText("Nicht gesetzt")
        geo_form.addRow("Längengrad (Lon):", self.geo_longitude)
        
        self.geo_altitude = QDoubleSpinBox()
        self.geo_altitude.setRange(-500, 9000)
        self.geo_altitude.setDecimals(2)
        self.geo_altitude.setSuffix(" m ü. NN")
        self.geo_altitude.setSpecialValueText("Nicht gesetzt")
        geo_form.addRow("Höhe:", self.geo_altitude)
        
        self.geo_accuracy = QLineEdit()
        self.geo_accuracy.setPlaceholderText("z.B. GPS, Karte, geschätzt")
        geo_form.addRow("Genauigkeit:", self.geo_accuracy)
        site_layout.addLayout(geo_form)
        
        # Grundstücksdaten
        site_layout.addWidget(self._create_section_header("🏞️ Grundstücksdaten"))
        plot_form = QFormLayout()
        
        self.plot_number = QLineEdit()
        self.plot_number.setPlaceholderText("Flurstück/Parzelle")
        plot_form.addRow("Flurstücknummer:", self.plot_number)
        
        self.plot_area = QDoubleSpinBox()
        self.plot_area.setRange(0, 999999)
        self.plot_area.setDecimals(2)
        self.plot_area.setSuffix(" m²")
        plot_form.addRow("Grundstücksfläche:", self.plot_area)
        
        self.cadastral_district = QLineEdit()
        self.cadastral_district.setPlaceholderText("Gemarkung")
        plot_form.addRow("Gemarkung:", self.cadastral_district)
        
        self.land_register = QLineEdit()
        self.land_register.setPlaceholderText("Grundbuchblatt/Eintrag")
        plot_form.addRow("Grundbuch:", self.land_register)
        site_layout.addLayout(plot_form)
        
        # Zufahrt & Erreichbarkeit
        site_layout.addWidget(self._create_section_header("🚛 Zufahrt & Logistik"))
        access_form = QFormLayout()
        
        self.access_width = QDoubleSpinBox()
        self.access_width.setRange(0, 100)
        self.access_width.setDecimals(2)
        self.access_width.setSuffix(" m")
        access_form.addRow("Zufahrtsbreite:", self.access_width)
        
        self.access_height = QDoubleSpinBox()
        self.access_height.setRange(0, 50)
        self.access_height.setDecimals(2)
        self.access_height.setSuffix(" m")
        access_form.addRow("Durchfahrtshöhe:", self.access_height)
        
        self.max_vehicle_weight = QDoubleSpinBox()
        self.max_vehicle_weight.setRange(0, 100)
        self.max_vehicle_weight.setDecimals(1)
        self.max_vehicle_weight.setSuffix(" t")
        access_form.addRow("Max. Fahrzeuggewicht:", self.max_vehicle_weight)
        
        self.crane_access = QCheckBox("Kranstellplatz vorhanden")
        access_form.addRow("", self.crane_access)
        
        self.parking_available = QCheckBox("Parkflächen vorhanden")
        access_form.addRow("", self.parking_available)
        
        self.site_access_notes = QTextEdit()
        self.site_access_notes.setMaximumHeight(60)
        self.site_access_notes.setPlaceholderText("Besondere Hinweise zur Anfahrt, Einschränkungen...")
        access_form.addRow("Zufahrtshinweise:", self.site_access_notes)
        site_layout.addLayout(access_form)
        
        site_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(site_widget), "📍 Baustelle")
        
        # ==================== TAB 3: GEBÄUDEDATEN ====================
        building_widget = QWidget()
        building_layout = QVBoxLayout(building_widget)
        building_layout.setSpacing(15)
        
        # Gebäudetyp
        building_layout.addWidget(self._create_section_header("🏠 Gebäudetyp"))
        building_type_form = QFormLayout()
        
        self.building_type = QComboBox()
        self.building_type.addItems([
            "Einfamilienhaus", "Doppelhaushälfte", "Reihenhaus", 
            "Mehrfamilienhaus", "Bungalow", "Villa", "Ferienhaus",
            "Bürogebäude", "Gewerbehalle", "Lagerhalle", "Werkstatt",
            "Landwirtschaftsgebäude", "Carport", "Garage", "Sonstiges"
        ])
        building_type_form.addRow("Gebäudetyp:", self.building_type)
        
        self.construction_method = QComboBox()
        self.construction_method.addItems([
            "Holzrahmenbau", "Holzmassivbau", "Blockbohlen", "Fachwerk",
            "Holzskelettbau", "Holz-Beton-Verbund", "Mischbauweise", "Sonstiges"
        ])
        building_type_form.addRow("Bauweise:", self.construction_method)
        building_layout.addLayout(building_type_form)
        
        # Maße
        building_layout.addWidget(self._create_section_header("📐 Gebäudemaße"))
        dims_form = QFormLayout()
        
        self.building_length = QDoubleSpinBox()
        self.building_length.setRange(0, 999)
        self.building_length.setDecimals(2)
        self.building_length.setSuffix(" m")
        dims_form.addRow("Länge:", self.building_length)
        
        self.building_width = QDoubleSpinBox()
        self.building_width.setRange(0, 999)
        self.building_width.setDecimals(2)
        self.building_width.setSuffix(" m")
        dims_form.addRow("Breite:", self.building_width)
        
        self.building_height = QDoubleSpinBox()
        self.building_height.setRange(0, 99)
        self.building_height.setDecimals(2)
        self.building_height.setSuffix(" m")
        dims_form.addRow("Höhe (Traufe):", self.building_height)
        
        self.ridge_height = QDoubleSpinBox()
        self.ridge_height.setRange(0, 99)
        self.ridge_height.setDecimals(2)
        self.ridge_height.setSuffix(" m")
        dims_form.addRow("Firsthöhe:", self.ridge_height)
        
        self.gross_floor_area = QDoubleSpinBox()
        self.gross_floor_area.setRange(0, 99999)
        self.gross_floor_area.setDecimals(2)
        self.gross_floor_area.setSuffix(" m²")
        dims_form.addRow("BGF (Bruttogrundfläche):", self.gross_floor_area)
        
        self.living_area = QDoubleSpinBox()
        self.living_area.setRange(0, 99999)
        self.living_area.setDecimals(2)
        self.living_area.setSuffix(" m²")
        dims_form.addRow("Wohnfläche:", self.living_area)
        
        self.usable_area = QDoubleSpinBox()
        self.usable_area.setRange(0, 99999)
        self.usable_area.setDecimals(2)
        self.usable_area.setSuffix(" m²")
        dims_form.addRow("Nutzfläche:", self.usable_area)
        
        self.building_volume = QDoubleSpinBox()
        self.building_volume.setRange(0, 999999)
        self.building_volume.setDecimals(2)
        self.building_volume.setSuffix(" m³")
        dims_form.addRow("Brutto-Rauminhalt:", self.building_volume)
        building_layout.addLayout(dims_form)
        
        # Geschosse
        building_layout.addWidget(self._create_section_header("🏢 Geschosse"))
        floors_form = QFormLayout()
        
        self.floors_above = QSpinBox()
        self.floors_above.setRange(0, 50)
        floors_form.addRow("Obergeschosse:", self.floors_above)
        
        self.floors_below = QSpinBox()
        self.floors_below.setRange(0, 10)
        floors_form.addRow("Untergeschosse:", self.floors_below)
        
        self.has_basement = QCheckBox("Keller vorhanden")
        floors_form.addRow("", self.has_basement)
        
        self.has_attic = QCheckBox("Dachgeschoss ausgebaut")
        floors_form.addRow("", self.has_attic)
        building_layout.addLayout(floors_form)
        
        # Dach
        building_layout.addWidget(self._create_section_header("🏠 Dachkonstruktion"))
        roof_form = QFormLayout()
        
        self.roof_type = QComboBox()
        self.roof_type.addItems([
            "Satteldach", "Walmdach", "Krüppelwalmdach", "Pultdach",
            "Flachdach", "Mansarddach", "Zeltdach", "Tonnendach",
            "Sheddach", "Bogendach", "Sonstiges"
        ])
        roof_form.addRow("Dachform:", self.roof_type)
        
        self.roof_pitch = QDoubleSpinBox()
        self.roof_pitch.setRange(0, 90)
        self.roof_pitch.setDecimals(1)
        self.roof_pitch.setSuffix("°")
        roof_form.addRow("Dachneigung:", self.roof_pitch)
        
        self.roof_area = QDoubleSpinBox()
        self.roof_area.setRange(0, 9999)
        self.roof_area.setDecimals(2)
        self.roof_area.setSuffix(" m²")
        roof_form.addRow("Dachfläche:", self.roof_area)
        
        self.roof_covering = QComboBox()
        self.roof_covering.addItems([
            "Dachziegel", "Betondachstein", "Schiefer", "Bitumen",
            "Blech/Metall", "Gründach", "Reet", "Holzschindeln", "Sonstiges"
        ])
        roof_form.addRow("Eindeckung:", self.roof_covering)
        
        self.overhang = QDoubleSpinBox()
        self.overhang.setRange(0, 500)
        self.overhang.setDecimals(0)
        self.overhang.setSuffix(" cm")
        roof_form.addRow("Dachüberstand:", self.overhang)
        building_layout.addLayout(roof_form)
        
        building_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(building_widget), "🏠 Gebäude")
        
        # ==================== TAB 4: TECHNIK & ENERGIE ====================
        tech_widget = QWidget()
        tech_layout = QVBoxLayout(tech_widget)
        tech_layout.setSpacing(15)
        
        # Statik
        tech_layout.addWidget(self._create_section_header("⚙️ Statik & Konstruktion"))
        static_form = QFormLayout()
        
        self.snow_load_zone = QComboBox()
        self.snow_load_zone.addItems(["Zone 1", "Zone 1a", "Zone 2", "Zone 2a", "Zone 3"])
        static_form.addRow("Schneelastzone:", self.snow_load_zone)
        
        self.wind_load_zone = QComboBox()
        self.wind_load_zone.addItems(["Zone 1", "Zone 2", "Zone 3", "Zone 4"])
        static_form.addRow("Windlastzone:", self.wind_load_zone)
        
        self.seismic_zone = QComboBox()
        self.seismic_zone.addItems(["Zone 0", "Zone 1", "Zone 2", "Zone 3"])
        static_form.addRow("Erdbebenzone:", self.seismic_zone)
        
        self.ground_conditions = QComboBox()
        self.ground_conditions.addItems([
            "Fels", "Kies", "Sand", "Schluff", "Ton", "Torf", "Unbekannt"
        ])
        static_form.addRow("Baugrund:", self.ground_conditions)
        
        self.foundation_type = QComboBox()
        self.foundation_type.addItems([
            "Streifenfundament", "Plattenfundament", "Einzelfundament",
            "Pfahlgründung", "Bodenplatte", "Punktfundament", "Sonstiges"
        ])
        static_form.addRow("Gründungsart:", self.foundation_type)
        tech_layout.addLayout(static_form)
        
        # Energie
        tech_layout.addWidget(self._create_section_header("🌱 Energiestandard"))
        energy_form = QFormLayout()
        
        self.energy_standard = QComboBox()
        self.energy_standard.addItems([
            "Keine Vorgabe", "GEG-Standard", "KfW 55", "KfW 40", "KfW 40 Plus",
            "Passivhaus", "Plusenergiehaus", "Nullenergiehaus"
        ])
        energy_form.addRow("Energiestandard:", self.energy_standard)
        
        self.heating_system = QComboBox()
        self.heating_system.addItems([
            "Wärmepumpe", "Pelletheizung", "Gasbrennwert", "Ölheizung",
            "Fernwärme", "BHKW", "Elektroheizung", "Kamin/Ofen", "Sonstiges"
        ])
        energy_form.addRow("Heizsystem:", self.heating_system)
        
        self.solar_system = QCheckBox("Photovoltaik geplant")
        energy_form.addRow("", self.solar_system)
        
        self.solar_thermal = QCheckBox("Solarthermie geplant")
        energy_form.addRow("", self.solar_thermal)
        
        self.ventilation_system = QComboBox()
        self.ventilation_system.addItems([
            "Natürliche Lüftung", "Abluftanlage", "Zu-/Abluft ohne WRG",
            "Zu-/Abluft mit WRG", "Dezentrale Lüftung"
        ])
        energy_form.addRow("Lüftung:", self.ventilation_system)
        
        self.u_value_wall = QDoubleSpinBox()
        self.u_value_wall.setRange(0, 5)
        self.u_value_wall.setDecimals(3)
        self.u_value_wall.setSuffix(" W/(m²K)")
        energy_form.addRow("U-Wert Wand:", self.u_value_wall)
        
        self.u_value_roof = QDoubleSpinBox()
        self.u_value_roof.setRange(0, 5)
        self.u_value_roof.setDecimals(3)
        self.u_value_roof.setSuffix(" W/(m²K)")
        energy_form.addRow("U-Wert Dach:", self.u_value_roof)
        tech_layout.addLayout(energy_form)
        
        # Installationen
        tech_layout.addWidget(self._create_section_header("🔌 Installationen"))
        install_form = QFormLayout()
        
        self.electrical_power = QSpinBox()
        self.electrical_power.setRange(0, 999)
        self.electrical_power.setSuffix(" kW")
        install_form.addRow("Anschlussleistung:", self.electrical_power)
        
        self.smart_home = QCheckBox("Smart Home System")
        install_form.addRow("", self.smart_home)
        
        self.ev_charging = QCheckBox("E-Ladestation")
        install_form.addRow("", self.ev_charging)
        tech_layout.addLayout(install_form)
        
        tech_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(tech_widget), "⚙️ Technik")
        
        # ==================== TAB 5: GENEHMIGUNGEN ====================
        permit_widget = QWidget()
        permit_layout = QVBoxLayout(permit_widget)
        permit_layout.setSpacing(15)
        
        # Baugenehmigung
        permit_layout.addWidget(self._create_section_header("📋 Baugenehmigung"))
        permit_form = QFormLayout()
        
        self.permit_required = QCheckBox("Baugenehmigung erforderlich")
        self.permit_required.setChecked(True)
        permit_form.addRow("", self.permit_required)
        
        self.permit_number = QLineEdit()
        self.permit_number.setPlaceholderText("Aktenzeichen der Baugenehmigung")
        permit_form.addRow("Aktenzeichen:", self.permit_number)
        
        self.permit_date = QDateEdit()
        self.permit_date.setCalendarPopup(True)
        self.permit_date.setSpecialValueText("Nicht erteilt")
        permit_form.addRow("Genehmigt am:", self.permit_date)
        
        self.permit_authority = QLineEdit()
        self.permit_authority.setPlaceholderText("z.B. Bauamt Stadt München")
        permit_form.addRow("Genehmigungsbehörde:", self.permit_authority)
        
        self.permit_expires = QDateEdit()
        self.permit_expires.setCalendarPopup(True)
        self.permit_expires.setDate(QDate.currentDate().addYears(3))
        permit_form.addRow("Gültig bis:", self.permit_expires)
        permit_layout.addLayout(permit_form)
        
        # Status
        permit_layout.addWidget(self._create_section_header("📊 Genehmigungsstatus"))
        status_form = QFormLayout()
        
        self.building_permit_status = QComboBox()
        self.building_permit_status.addItems([
            "Nicht eingereicht", "Eingereicht", "In Prüfung", 
            "Nachforderungen", "Genehmigt", "Abgelehnt"
        ])
        status_form.addRow("Baugenehmigung:", self.building_permit_status)
        
        self.static_approval_status = QComboBox()
        self.static_approval_status.addItems([
            "Nicht erforderlich", "Nicht eingereicht", "Eingereicht", 
            "In Prüfung", "Genehmigt"
        ])
        status_form.addRow("Statikprüfung:", self.static_approval_status)
        permit_layout.addLayout(status_form)
        
        # Beteiligte
        permit_layout.addWidget(self._create_section_header("👷 Beteiligte Planer"))
        planner_form = QFormLayout()
        
        self.architect = QLineEdit()
        self.architect.setPlaceholderText("Name des Architekten")
        planner_form.addRow("Architekt:", self.architect)
        
        self.structural_engineer = QLineEdit()
        self.structural_engineer.setPlaceholderText("Name des Tragwerksplaners")
        planner_form.addRow("Statiker:", self.structural_engineer)
        
        self.site_manager = QLineEdit()
        self.site_manager.setPlaceholderText("Name des Bauleiters")
        planner_form.addRow("Bauleiter:", self.site_manager)
        
        self.energy_consultant = QLineEdit()
        self.energy_consultant.setPlaceholderText("Name des Energieberaters")
        planner_form.addRow("Energieberater:", self.energy_consultant)
        permit_layout.addLayout(planner_form)
        
        permit_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(permit_widget), "📋 Genehmigungen")
        
        # ==================== TAB 6: PLANUNG & TERMINE ====================
        planning_widget = QWidget()
        planning_layout = QVBoxLayout(planning_widget)
        planning_layout.setSpacing(15)
        
        # Termine
        planning_layout.addWidget(self._create_section_header("📅 Projekttermine"))
        dates_form = QFormLayout()
        
        self.inquiry_date = QDateEdit()
        self.inquiry_date.setCalendarPopup(True)
        self.inquiry_date.setDate(QDate.currentDate())
        dates_form.addRow("Anfragedatum:", self.inquiry_date)
        
        self.quote_date = QDateEdit()
        self.quote_date.setCalendarPopup(True)
        self.quote_date.setSpecialValueText("Nicht erstellt")
        dates_form.addRow("Angebotsdatum:", self.quote_date)
        
        self.order_date = QDateEdit()
        self.order_date.setCalendarPopup(True)
        self.order_date.setSpecialValueText("Nicht erteilt")
        dates_form.addRow("Auftragsdatum:", self.order_date)
        
        self.planned_start = QDateEdit()
        self.planned_start.setCalendarPopup(True)
        self.planned_start.setDate(QDate.currentDate())
        dates_form.addRow("Geplanter Start:", self.planned_start)
        
        self.planned_end = QDateEdit()
        self.planned_end.setCalendarPopup(True)
        self.planned_end.setDate(QDate.currentDate().addMonths(3))
        dates_form.addRow("Geplantes Ende:", self.planned_end)
        
        self.actual_start = QDateEdit()
        self.actual_start.setCalendarPopup(True)
        self.actual_start.setSpecialValueText("Nicht gestartet")
        dates_form.addRow("Tatsächlicher Start:", self.actual_start)
        
        self.actual_end = QDateEdit()
        self.actual_end.setCalendarPopup(True)
        self.actual_end.setSpecialValueText("Nicht beendet")
        dates_form.addRow("Tatsächliches Ende:", self.actual_end)
        
        self.delivery_date = QDateEdit()
        self.delivery_date.setCalendarPopup(True)
        self.delivery_date.setSpecialValueText("Nicht festgelegt")
        dates_form.addRow("Liefertermin Elemente:", self.delivery_date)
        
        self.assembly_start = QDateEdit()
        self.assembly_start.setCalendarPopup(True)
        self.assembly_start.setSpecialValueText("Nicht festgelegt")
        dates_form.addRow("Montagebeginn:", self.assembly_start)
        planning_layout.addLayout(dates_form)
        
        # Arbeitszeiten
        planning_layout.addWidget(self._create_section_header("⏰ Arbeitszeiten Baustelle"))
        work_form = QFormLayout()
        
        self.work_start_time = QTimeEdit()
        self.work_start_time.setTime(QTime(7, 0))
        work_form.addRow("Arbeitsbeginn:", self.work_start_time)
        
        self.work_end_time = QTimeEdit()
        self.work_end_time.setTime(QTime(17, 0))
        work_form.addRow("Arbeitsende:", self.work_end_time)
        
        self.saturday_work = QCheckBox("Samstagsarbeit erlaubt")
        work_form.addRow("", self.saturday_work)
        
        self.estimated_hours = QSpinBox()
        self.estimated_hours.setRange(0, 99999)
        self.estimated_hours.setSuffix(" Std")
        work_form.addRow("Geschätzte Stunden:", self.estimated_hours)
        planning_layout.addLayout(work_form)
        
        planning_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(planning_widget), "📅 Planung")
        
        # ==================== TAB 7: FINANZEN ====================
        finance_widget = QWidget()
        finance_layout = QVBoxLayout(finance_widget)
        finance_layout.setSpacing(15)
        
        # Werte
        finance_layout.addWidget(self._create_section_header("💰 Auftragswerte"))
        values_form = QFormLayout()
        
        self.quoted_value = QDoubleSpinBox()
        self.quoted_value.setRange(0, 99999999)
        self.quoted_value.setDecimals(2)
        self.quoted_value.setSuffix(" €")
        self.quoted_value.setGroupSeparatorShown(True)
        values_form.addRow("Angebotssumme netto:", self.quoted_value)
        
        self.contract_value = QDoubleSpinBox()
        self.contract_value.setRange(0, 99999999)
        self.contract_value.setDecimals(2)
        self.contract_value.setSuffix(" €")
        self.contract_value.setGroupSeparatorShown(True)
        values_form.addRow("Auftragssumme netto:", self.contract_value)
        
        self.final_value = QDoubleSpinBox()
        self.final_value.setRange(0, 99999999)
        self.final_value.setDecimals(2)
        self.final_value.setSuffix(" €")
        self.final_value.setGroupSeparatorShown(True)
        values_form.addRow("Schlussrechnungssumme:", self.final_value)
        finance_layout.addLayout(values_form)
        
        # Kalkulation
        finance_layout.addWidget(self._create_section_header("📊 Kalkulation"))
        calc_form = QFormLayout()
        
        self.material_cost = QDoubleSpinBox()
        self.material_cost.setRange(0, 99999999)
        self.material_cost.setDecimals(2)
        self.material_cost.setSuffix(" €")
        calc_form.addRow("Materialkosten (geplant):", self.material_cost)
        
        self.labor_cost = QDoubleSpinBox()
        self.labor_cost.setRange(0, 99999999)
        self.labor_cost.setDecimals(2)
        self.labor_cost.setSuffix(" €")
        calc_form.addRow("Lohnkosten (geplant):", self.labor_cost)
        
        self.subcontractor_cost = QDoubleSpinBox()
        self.subcontractor_cost.setRange(0, 99999999)
        self.subcontractor_cost.setDecimals(2)
        self.subcontractor_cost.setSuffix(" €")
        calc_form.addRow("Subunternehmer:", self.subcontractor_cost)
        
        self.overhead_percent = QDoubleSpinBox()
        self.overhead_percent.setRange(0, 100)
        self.overhead_percent.setDecimals(1)
        self.overhead_percent.setSuffix(" %")
        calc_form.addRow("GGK-Zuschlag:", self.overhead_percent)
        
        self.profit_margin = QDoubleSpinBox()
        self.profit_margin.setRange(0, 100)
        self.profit_margin.setDecimals(1)
        self.profit_margin.setSuffix(" %")
        calc_form.addRow("Gewinnmarge:", self.profit_margin)
        finance_layout.addLayout(calc_form)
        
        # Zahlungen
        finance_layout.addWidget(self._create_section_header("💳 Zahlungsplan"))
        payment_form = QFormLayout()
        
        self.advance_payment = QDoubleSpinBox()
        self.advance_payment.setRange(0, 100)
        self.advance_payment.setDecimals(1)
        self.advance_payment.setSuffix(" %")
        payment_form.addRow("Anzahlung:", self.advance_payment)
        
        self.partial_invoicing = QCheckBox("Abschlagsrechnungen")
        payment_form.addRow("", self.partial_invoicing)
        
        self.retention = QDoubleSpinBox()
        self.retention.setRange(0, 20)
        self.retention.setDecimals(1)
        self.retention.setSuffix(" %")
        self.retention.setValue(5)
        payment_form.addRow("Sicherheitseinbehalt:", self.retention)
        finance_layout.addLayout(payment_form)
        
        finance_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(finance_widget), "💰 Finanzen")
        
        # ==================== TAB 8: NOTIZEN ====================
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setSpacing(15)
        
        notes_layout.addWidget(self._create_section_header("📝 Allgemeine Notizen"))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Allgemeine Projektnotizen...")
        notes_layout.addWidget(self.notes)
        
        notes_layout.addWidget(self._create_section_header("🔒 Interne Notizen"))
        self.internal_notes = QTextEdit()
        self.internal_notes.setPlaceholderText("Interne Notizen (nicht für Kunden sichtbar)...")
        notes_layout.addWidget(self.internal_notes)
        
        notes_layout.addWidget(self._create_section_header("⚠️ Besondere Hinweise"))
        self.special_notes = QTextEdit()
        self.special_notes.setPlaceholderText("Besondere Anforderungen, Risiken, Warnungen...")
        self.special_notes.setMaximumHeight(100)
        notes_layout.addWidget(self.special_notes)
        
        tabs.addTab(self._create_scrollable_tab(notes_widget), "📝 Notizen")
        
        layout.addWidget(tabs)
        
        # ==================== BUTTONS ====================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 40px;
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #15803d;
            }
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_customers(self):
        session = self.db.get_session()
        try:
            customers = session.execute(
                select(Customer).where(Customer.is_deleted == False).order_by(Customer.company_name, Customer.last_name)
            ).scalars().all()
            
            self.customer_combo.addItem("-- Kein Kunde --", None)
            for cust in customers:
                name = cust.company_name or f"{cust.first_name or ''} {cust.last_name or ''}".strip()
                self.customer_combo.addItem(f"{cust.customer_number} - {name}", str(cust.id))
        finally:
            session.close()
    
    def _set_combo_by_text(self, combo, text):
        """Setzt ComboBox auf einen Wert basierend auf Text"""
        if text:
            idx = combo.findText(text)
            if idx >= 0:
                combo.setCurrentIndex(idx)
    
    def _set_date(self, date_edit, date_val):
        """Setzt DateEdit sicher"""
        if date_val:
            date_edit.setDate(QDate(date_val.year, date_val.month, date_val.day))
    
    def load_project(self):
        session = self.db.get_session()
        try:
            self.project = session.get(Project, uuid.UUID(self.project_id))
            if not self.project:
                return
                
            p = self.project
            
            # Grunddaten
            self.name.setText(p.name or "")
            self.project_number.setText(p.project_number or "")
            
            if p.customer_id:
                idx = self.customer_combo.findData(str(p.customer_id))
                if idx >= 0:
                    self.customer_combo.setCurrentIndex(idx)
            
            if p.project_type:
                idx = self.project_type.findData(p.project_type.value)
                if idx >= 0:
                    self.project_type.setCurrentIndex(idx)
            
            if p.status:
                idx = self.status.findData(p.status.value)
                if idx >= 0:
                    self.status.setCurrentIndex(idx)
            
            self.description.setPlainText(p.description or "")
            self.tags.setText(p.tags or "") if hasattr(p, 'tags') else None
            self.reference_number.setText(p.reference_number or "") if hasattr(p, 'reference_number') else None
            
            # Baustelle
            self.site_street.setText(p.site_street or "")
            self.site_street_number.setText(getattr(p, 'site_street_number', "") or "")
            self.site_postal.setText(p.site_postal_code or "")
            self.site_city.setText(p.site_city or "")
            self.site_district.setText(getattr(p, 'site_district', "") or "")
            self.site_state.setText(getattr(p, 'site_state', "") or "")
            self.site_country.setText(getattr(p, 'site_country', "Deutschland") or "Deutschland")
            
            # Geokoordinaten
            if hasattr(p, 'geo_latitude') and p.geo_latitude:
                self.geo_latitude.setValue(float(p.geo_latitude))
            if hasattr(p, 'geo_longitude') and p.geo_longitude:
                self.geo_longitude.setValue(float(p.geo_longitude))
            if hasattr(p, 'geo_altitude') and p.geo_altitude:
                self.geo_altitude.setValue(float(p.geo_altitude))
            
            # Grundstück
            self.plot_number.setText(getattr(p, 'plot_number', "") or "")
            if hasattr(p, 'plot_area') and p.plot_area:
                self.plot_area.setValue(float(p.plot_area))
            
            # Gebäude
            self._set_combo_by_text(self.building_type, getattr(p, 'building_type', None))
            self._set_combo_by_text(self.construction_method, getattr(p, 'construction_method', None))
            
            if hasattr(p, 'building_length') and p.building_length:
                self.building_length.setValue(float(p.building_length))
            if hasattr(p, 'building_width') and p.building_width:
                self.building_width.setValue(float(p.building_width))
            if hasattr(p, 'building_height') and p.building_height:
                self.building_height.setValue(float(p.building_height))
            if hasattr(p, 'gross_floor_area') and p.gross_floor_area:
                self.gross_floor_area.setValue(float(p.gross_floor_area))
            if hasattr(p, 'living_area') and p.living_area:
                self.living_area.setValue(float(p.living_area))
            
            # Dach
            self._set_combo_by_text(self.roof_type, getattr(p, 'roof_type', None))
            if hasattr(p, 'roof_pitch') and p.roof_pitch:
                self.roof_pitch.setValue(float(p.roof_pitch))
            if hasattr(p, 'roof_area') and p.roof_area:
                self.roof_area.setValue(float(p.roof_area))
            
            # Termine
            self._set_date(self.planned_start, p.planned_start)
            self._set_date(self.planned_end, p.planned_end)
            self._set_date(self.actual_start, getattr(p, 'actual_start', None))
            self._set_date(self.actual_end, getattr(p, 'actual_end', None))
            
            # Finanzen
            if p.quoted_value:
                self.quoted_value.setValue(float(p.quoted_value))
            if p.contract_value:
                self.contract_value.setValue(float(p.contract_value))
            if hasattr(p, 'final_value') and p.final_value:
                self.final_value.setValue(float(p.final_value))
            
            # Notizen
            self.notes.setPlainText(p.notes or "")
            if hasattr(p, 'internal_notes'):
                self.internal_notes.setPlainText(p.internal_notes or "")
                
        finally:
            session.close()
    
    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Projektnamen eingeben.")
            return
        
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Fehler", "Bitte einen Kunden auswählen.")
            return
        
        session = self.db.get_session()
        try:
            if self.project_id:
                project = session.get(Project, uuid.UUID(self.project_id))
            else:
                project = Project()
                from sqlalchemy import func
                count = session.execute(select(func.count(Project.id))).scalar() or 0
                project.project_number = f"P{datetime.now().year}{count + 1:04d}"
                
                if self.user:
                    project.tenant_id = self.user.tenant_id
                    project.created_by = self.user.id
            
            # ===== GRUNDDATEN =====
            project.name = self.name.text().strip()
            
            project.customer_id = uuid.UUID(customer_id)
            
            project.project_type = ProjectType(self.project_type.currentData())
            project.status = ProjectStatus(self.status.currentData())
            project.description = self.description.toPlainText().strip() or None
            
            # Tags & Referenz (nur wenn Felder im Model existieren)
            if hasattr(project, 'tags'):
                project.tags = self.tags.text().strip() or None
            if hasattr(project, 'reference_number'):
                project.reference_number = self.reference_number.text().strip() or None
            if hasattr(project, 'priority'):
                project.priority = self.priority.currentData()
            
            # ===== BAUSTELLE =====
            project.site_street = self.site_street.text().strip() or None
            if hasattr(project, 'site_street_number'):
                project.site_street_number = self.site_street_number.text().strip() or None
            project.site_postal_code = self.site_postal.text().strip() or None
            project.site_city = self.site_city.text().strip() or None
            if hasattr(project, 'site_district'):
                project.site_district = self.site_district.text().strip() or None
            if hasattr(project, 'site_state'):
                project.site_state = self.site_state.text().strip() or None
            if hasattr(project, 'site_country'):
                project.site_country = self.site_country.text().strip() or None
            
            # Geokoordinaten
            if hasattr(project, 'geo_latitude'):
                lat = self.geo_latitude.value()
                project.geo_latitude = lat if lat != 0 else None
            if hasattr(project, 'geo_longitude'):
                lon = self.geo_longitude.value()
                project.geo_longitude = lon if lon != 0 else None
            if hasattr(project, 'geo_altitude'):
                alt = self.geo_altitude.value()
                project.geo_altitude = alt if alt != 0 else None
            
            # Grundstück
            if hasattr(project, 'plot_number'):
                project.plot_number = self.plot_number.text().strip() or None
            if hasattr(project, 'plot_area'):
                area = self.plot_area.value()
                project.plot_area = area if area > 0 else None
            if hasattr(project, 'cadastral_district'):
                project.cadastral_district = self.cadastral_district.text().strip() or None
            
            # Zufahrt
            if hasattr(project, 'access_width'):
                project.access_width = self.access_width.value() or None
            if hasattr(project, 'crane_access'):
                project.crane_access = self.crane_access.isChecked()
            if hasattr(project, 'site_access_notes'):
                project.site_access_notes = self.site_access_notes.toPlainText().strip() or None
            
            # ===== GEBÄUDE =====
            if hasattr(project, 'building_type'):
                project.building_type = self.building_type.currentText()
            if hasattr(project, 'construction_method'):
                project.construction_method = self.construction_method.currentText()
            
            # Maße
            if hasattr(project, 'building_length'):
                project.building_length = self.building_length.value() or None
            if hasattr(project, 'building_width'):
                project.building_width = self.building_width.value() or None
            if hasattr(project, 'building_height'):
                project.building_height = self.building_height.value() or None
            if hasattr(project, 'ridge_height'):
                project.ridge_height = self.ridge_height.value() or None
            if hasattr(project, 'gross_floor_area'):
                project.gross_floor_area = self.gross_floor_area.value() or None
            if hasattr(project, 'living_area'):
                project.living_area = self.living_area.value() or None
            if hasattr(project, 'usable_area'):
                project.usable_area = self.usable_area.value() or None
            if hasattr(project, 'building_volume'):
                project.building_volume = self.building_volume.value() or None
            
            # Geschosse
            if hasattr(project, 'floors_above'):
                project.floors_above = self.floors_above.value()
            if hasattr(project, 'floors_below'):
                project.floors_below = self.floors_below.value()
            if hasattr(project, 'has_basement'):
                project.has_basement = self.has_basement.isChecked()
            if hasattr(project, 'has_attic'):
                project.has_attic = self.has_attic.isChecked()
            
            # Dach
            if hasattr(project, 'roof_type'):
                project.roof_type = self.roof_type.currentText()
            if hasattr(project, 'roof_pitch'):
                project.roof_pitch = self.roof_pitch.value() or None
            if hasattr(project, 'roof_area'):
                project.roof_area = self.roof_area.value() or None
            if hasattr(project, 'roof_covering'):
                project.roof_covering = self.roof_covering.currentText()
            if hasattr(project, 'overhang'):
                project.overhang = self.overhang.value() or None
            
            # ===== TECHNIK =====
            if hasattr(project, 'snow_load_zone'):
                project.snow_load_zone = self.snow_load_zone.currentText()
            if hasattr(project, 'wind_load_zone'):
                project.wind_load_zone = self.wind_load_zone.currentText()
            if hasattr(project, 'energy_standard'):
                project.energy_standard = self.energy_standard.currentText()
            if hasattr(project, 'heating_system'):
                project.heating_system = self.heating_system.currentText()
            if hasattr(project, 'solar_system'):
                project.solar_system = self.solar_system.isChecked()
            
            # ===== GENEHMIGUNGEN =====
            if hasattr(project, 'permit_required'):
                project.permit_required = self.permit_required.isChecked()
            if hasattr(project, 'permit_number'):
                project.permit_number = self.permit_number.text().strip() or None
            if hasattr(project, 'permit_authority'):
                project.permit_authority = self.permit_authority.text().strip() or None
            if hasattr(project, 'architect'):
                project.architect = self.architect.text().strip() or None
            if hasattr(project, 'structural_engineer'):
                project.structural_engineer = self.structural_engineer.text().strip() or None
            
            # ===== PLANUNG & TERMINE =====
            project.planned_start = self.planned_start.date().toPyDate()
            project.planned_end = self.planned_end.date().toPyDate()
            
            if hasattr(project, 'actual_start'):
                d = self.actual_start.date()
                project.actual_start = d.toPyDate() if d.isValid() and d.year() > 2000 else None
            if hasattr(project, 'actual_end'):
                d = self.actual_end.date()
                project.actual_end = d.toPyDate() if d.isValid() and d.year() > 2000 else None
            
            if hasattr(project, 'estimated_hours'):
                project.estimated_hours = self.estimated_hours.value() or None
            
            # ===== FINANZEN =====
            quoted = self.quoted_value.value()
            project.quoted_value = quoted if quoted > 0 else None
            
            contract = self.contract_value.value()
            project.contract_value = contract if contract > 0 else None
            
            if hasattr(project, 'final_value'):
                final = self.final_value.value()
                project.final_value = final if final > 0 else None
            
            if hasattr(project, 'material_cost'):
                project.material_cost = self.material_cost.value() or None
            if hasattr(project, 'labor_cost'):
                project.labor_cost = self.labor_cost.value() or None
            if hasattr(project, 'profit_margin'):
                project.profit_margin = self.profit_margin.value() or None
            if hasattr(project, 'advance_payment_percent'):
                project.advance_payment_percent = self.advance_payment.value() or None
            if hasattr(project, 'retention_percent'):
                project.retention_percent = self.retention.value() or None
            
            # ===== NOTIZEN =====
            project.notes = self.notes.toPlainText().strip() or None
            if hasattr(project, 'internal_notes'):
                project.internal_notes = self.internal_notes.toPlainText().strip() or None
            if hasattr(project, 'special_notes'):
                project.special_notes = self.special_notes.toPlainText().strip() or None
            
            # Updated by
            if self.user:
                project.updated_by = self.user.id
            
            if not self.project_id:
                session.add(project)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
