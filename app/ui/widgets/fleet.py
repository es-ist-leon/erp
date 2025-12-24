"""
Fahrzeuge & Geräte Widget - Fleet and Equipment Management
Komplette Verwaltung von Fahrzeugen, Maschinen und Geräten
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QFrame, QDialog, QFormLayout,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTimeEdit, QTabWidget, QScrollArea, QGroupBox, QCheckBox,
    QFileDialog, QListWidget, QListWidgetItem, QMessageBox,
    QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QCalendarWidget
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, date
from decimal import Decimal
import uuid

from sqlalchemy import select, func
from app.ui.styles import COLORS, get_button_style, CARD_STYLE
from shared.models import (
    Vehicle, Equipment, VehicleType, VehicleStatus, EquipmentType,
    FuelLog, MileageLog, VehicleMaintenance, EquipmentMaintenance, EquipmentReservation
)


class FleetWidget(QWidget):
    """Fahrzeug- und Geräteverwaltung"""
    
    def __init__(self, db_service, user):
        super().__init__()
        self.db_service = db_service
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self._tab_style())
        
        # Tabs
        self.tabs.addTab(self._create_vehicles_tab(), "🚗 Fahrzeuge")
        self.tabs.addTab(self._create_cranes_tab(), "🏗️ Krane")
        self.tabs.addTab(self._create_equipment_tab(), "🔧 Geräte & Maschinen")
        self.tabs.addTab(self._create_fuel_log_tab(), "⛽ Tankprotokoll")
        self.tabs.addTab(self._create_trip_log_tab(), "📖 Fahrtenbuch")
        self.tabs.addTab(self._create_maintenance_tab(), "🔧 Wartung")
        self.tabs.addTab(self._create_reservations_tab(), "📅 Reservierungen")
        self.tabs.addTab(self._create_gps_tab(), "📍 GPS-Tracking")
        
        layout.addWidget(self.tabs)
    
    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet(CARD_STYLE)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        title = QLabel("🚚 Fahrzeuge & Geräte")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick stats
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(24)
        
        for label, value, color in [
            ("Fahrzeuge", "12", COLORS['primary']),
            ("Im Einsatz", "8", COLORS['success']),
            ("In Wartung", "2", COLORS['warning']),
            ("TÜV fällig", "3", COLORS['danger'])
        ]:
            stat = QVBoxLayout()
            stat_value = QLabel(value)
            stat_value.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            stat_value.setStyleSheet(f"color: {color};")
            stat_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat.addWidget(stat_value)
            
            stat_label = QLabel(label)
            stat_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat.addWidget(stat_label)
            
            stats_layout.addLayout(stat)
        
        header_layout.addWidget(stats_frame)
        
        return header
    
    def _create_vehicles_tab(self) -> QWidget:
        """Fahrzeugverwaltung"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Fahrzeug suchen...")
        search.setMaximumWidth(300)
        toolbar.addWidget(search)
        
        filter_combo = QComboBox()
        filter_combo.addItems(["Alle Fahrzeuge", "PKW", "LKW", "Transporter", "Anhänger", "Sonderfahrzeuge"])
        toolbar.addWidget(filter_combo)
        
        status_combo = QComboBox()
        status_combo.addItems(["Alle Status", "Verfügbar", "Im Einsatz", "In Wartung", "Außer Betrieb"])
        toolbar.addWidget(status_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neues Fahrzeug")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_vehicle)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Vehicle table
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(12)
        self.vehicles_table.setHorizontalHeaderLabels([
            "Kennzeichen", "Typ", "Marke/Modell", "Fahrer", "Status",
            "TÜV bis", "AU bis", "UVV bis", "km-Stand", "Standort", "GPS", "Aktionen"
        ])
        self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vehicles_table.setStyleSheet(self._table_style())
        self.vehicles_table.setAlternatingRowColors(True)
        layout.addWidget(self.vehicles_table)
        
        return tab
    
    def _create_cranes_tab(self) -> QWidget:
        """Kranverwaltung"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Kran suchen...")
        search.setMaximumWidth(300)
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neuer Kran")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_crane)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Crane table
        self.cranes_table = QTableWidget()
        self.cranes_table.setColumnCount(14)
        self.cranes_table.setHorizontalHeaderLabels([
            "Bezeichnung", "Typ", "Hersteller", "Tragkraft max", "Ausladung max",
            "Hakenhöhe max", "Hubgeschwindigkeit", "Baujahr", "Status",
            "UVV bis", "Letzte Prüfung", "Nächste Prüfung", "Standort", "Aktionen"
        ])
        self.cranes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cranes_table.setStyleSheet(self._table_style())
        layout.addWidget(self.cranes_table)
        
        # Crane details section
        details_group = QGroupBox("📋 Kran-Details")
        details_group.setStyleSheet(self._group_style())
        details_layout = QHBoxLayout(details_group)
        
        # Left: Technical data
        tech_frame = QFrame()
        tech_layout = QFormLayout(tech_frame)
        tech_layout.addRow("Tragkraft:", QLabel("---"))
        tech_layout.addRow("Ausladung:", QLabel("---"))
        tech_layout.addRow("Hakenhöhe:", QLabel("---"))
        tech_layout.addRow("Hubgeschwindigkeit:", QLabel("---"))
        tech_layout.addRow("Drehgeschwindigkeit:", QLabel("---"))
        tech_layout.addRow("Katzfahrgeschwindigkeit:", QLabel("---"))
        details_layout.addWidget(tech_frame)
        
        # Middle: Certifications
        cert_frame = QFrame()
        cert_layout = QFormLayout(cert_frame)
        cert_layout.addRow("CE-Kennzeichnung:", QLabel("---"))
        cert_layout.addRow("UVV-Prüfung:", QLabel("---"))
        cert_layout.addRow("Sachverständigenprüfung:", QLabel("---"))
        cert_layout.addRow("Kranführerschein erforderlich:", QLabel("---"))
        details_layout.addWidget(cert_frame)
        
        # Right: Current assignment
        assign_frame = QFrame()
        assign_layout = QFormLayout(assign_frame)
        assign_layout.addRow("Aktuelles Projekt:", QLabel("---"))
        assign_layout.addRow("Standort:", QLabel("---"))
        assign_layout.addRow("Kranführer:", QLabel("---"))
        assign_layout.addRow("Betriebsstunden:", QLabel("---"))
        details_layout.addWidget(assign_frame)
        
        layout.addWidget(details_group)
        
        return tab
    
    def _create_equipment_tab(self) -> QWidget:
        """Geräte und Maschinen"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Gerät/Maschine suchen...")
        search.setMaximumWidth(300)
        toolbar.addWidget(search)
        
        category_combo = QComboBox()
        category_combo.addItems([
            "Alle Kategorien", "Elektrowerkzeuge", "Handwerkzeuge", "Messgeräte",
            "Baumaschinen", "Gerüste", "Arbeitsbühnen", "Kompressoren", "Sägen",
            "Bohrmaschinen", "Schleifmaschinen", "Sonstiges"
        ])
        toolbar.addWidget(category_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neues Gerät")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_equipment)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Equipment table
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(12)
        self.equipment_table.setHorizontalHeaderLabels([
            "Inventar-Nr.", "Bezeichnung", "Kategorie", "Hersteller", "Modell",
            "Status", "Betriebsstunden", "Letzte Wartung", "Nächste Wartung",
            "Standort", "Verantwortlich", "Aktionen"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.equipment_table.setStyleSheet(self._table_style())
        layout.addWidget(self.equipment_table)
        
        return tab
    
    def _create_fuel_log_tab(self) -> QWidget:
        """Tankprotokoll"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        vehicle_combo = QComboBox()
        vehicle_combo.addItems(["Alle Fahrzeuge", "--- Auswählen ---"])
        toolbar.addWidget(QLabel("Fahrzeug:"))
        toolbar.addWidget(vehicle_combo)
        
        toolbar.addWidget(QLabel("Zeitraum:"))
        date_from = QDateEdit()
        date_from.setCalendarPopup(True)
        date_from.setDate(QDate.currentDate().addMonths(-1))
        toolbar.addWidget(date_from)
        toolbar.addWidget(QLabel("bis"))
        date_to = QDateEdit()
        date_to.setCalendarPopup(True)
        date_to.setDate(QDate.currentDate())
        toolbar.addWidget(date_to)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("⛽ Tankvorgang erfassen")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_fuel_entry)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        for label, value, unit in [
            ("Gesamtverbrauch", "1.234,5", "Liter"),
            ("Gesamtkosten", "2.345,67", "€"),
            ("Ø Verbrauch", "8,5", "l/100km"),
            ("Ø Preis", "1,89", "€/l")
        ]:
            stat_widget = QVBoxLayout()
            stat_value = QLabel(f"{value} {unit}")
            stat_value.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            stat_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(stat_value)
            stat_label = QLabel(label)
            stat_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(stat_label)
            stats_layout.addLayout(stat_widget)
        
        layout.addWidget(stats_frame)
        
        # Fuel log table
        self.fuel_table = QTableWidget()
        self.fuel_table.setColumnCount(10)
        self.fuel_table.setHorizontalHeaderLabels([
            "Datum", "Fahrzeug", "Tankstelle", "Kraftstoff", "Menge (l)",
            "Preis/l", "Gesamtpreis", "km-Stand", "Fahrer", "Aktionen"
        ])
        self.fuel_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.fuel_table.setStyleSheet(self._table_style())
        layout.addWidget(self.fuel_table)
        
        return tab
    
    def _create_trip_log_tab(self) -> QWidget:
        """Fahrtenbuch"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        vehicle_combo = QComboBox()
        vehicle_combo.addItems(["Alle Fahrzeuge"])
        toolbar.addWidget(QLabel("Fahrzeug:"))
        toolbar.addWidget(vehicle_combo)
        
        driver_combo = QComboBox()
        driver_combo.addItems(["Alle Fahrer"])
        toolbar.addWidget(QLabel("Fahrer:"))
        toolbar.addWidget(driver_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("📝 Fahrt erfassen")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_trip)
        toolbar.addWidget(add_btn)
        
        export_btn = QPushButton("📄 Export")
        export_btn.setStyleSheet(get_button_style('secondary'))
        export_btn.clicked.connect(self._export_trip_log)
        toolbar.addWidget(export_btn)
        
        layout.addLayout(toolbar)
        
        # Trip log table
        self.trip_table = QTableWidget()
        self.trip_table.setColumnCount(12)
        self.trip_table.setHorizontalHeaderLabels([
            "Datum", "Fahrzeug", "Fahrer", "Start", "Ziel", "Abfahrt",
            "Ankunft", "km Start", "km Ende", "km Gesamt", "Zweck", "Aktionen"
        ])
        self.trip_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trip_table.setStyleSheet(self._table_style())
        layout.addWidget(self.trip_table)
        
        return tab
    
    def _create_maintenance_tab(self) -> QWidget:
        """Wartungsplanung"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Upcoming maintenance
        upcoming_group = QGroupBox("⏰ Anstehende Wartungen & Prüfungen")
        upcoming_group.setStyleSheet(self._group_style())
        upcoming_layout = QVBoxLayout(upcoming_group)
        
        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(8)
        self.upcoming_table.setHorizontalHeaderLabels([
            "Fällig am", "Fahrzeug/Gerät", "Art", "Beschreibung",
            "Werkstatt", "Geschätzte Kosten", "Status", "Aktionen"
        ])
        self.upcoming_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.upcoming_table.setStyleSheet(self._table_style())
        upcoming_layout.addWidget(self.upcoming_table)
        
        layout.addWidget(upcoming_group)
        
        # Maintenance types
        types_frame = QFrame()
        types_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px; padding: 12px;")
        types_layout = QHBoxLayout(types_frame)
        
        for icon, label, count, color in [
            ("🔧", "Inspektion", "3", COLORS['primary']),
            ("🛡️", "TÜV", "2", COLORS['warning']),
            ("💨", "AU", "1", COLORS['info']),
            ("⚠️", "UVV", "4", COLORS['danger']),
            ("🔩", "Ölwechsel", "2", COLORS['success'])
        ]:
            type_widget = QVBoxLayout()
            type_icon = QLabel(f"{icon} {count}")
            type_icon.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            type_icon.setStyleSheet(f"color: {color};")
            type_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_widget.addWidget(type_icon)
            type_label = QLabel(label)
            type_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_widget.addWidget(type_label)
            types_layout.addLayout(type_widget)
        
        layout.addWidget(types_frame)
        
        # Maintenance history
        history_group = QGroupBox("📜 Wartungshistorie")
        history_group.setStyleSheet(self._group_style())
        history_layout = QVBoxLayout(history_group)
        
        toolbar = QHBoxLayout()
        add_btn = QPushButton("➕ Wartung erfassen")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_maintenance)
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        history_layout.addLayout(toolbar)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "Datum", "Fahrzeug/Gerät", "Art", "Beschreibung",
            "Werkstatt", "Kosten", "km-Stand/Betriebsstunden", "Nächste Wartung", "Aktionen"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setStyleSheet(self._table_style())
        history_layout.addWidget(self.history_table)
        
        layout.addWidget(history_group)
        
        return tab
    
    def _create_reservations_tab(self) -> QWidget:
        """Reservierungssystem"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Left: Calendar view
        left_panel = QFrame()
        left_panel.setStyleSheet(CARD_STYLE)
        left_panel.setMinimumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("📅 Kalender"))
        
        calendar = QCalendarWidget()
        calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background: white;
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background: transparent;
                border: none;
                padding: 8px;
            }}
            QCalendarWidget QToolButton:hover {{
                background: {COLORS['gray_100']};
                border-radius: 4px;
            }}
        """)
        left_layout.addWidget(calendar)
        
        # New reservation button
        new_res_btn = QPushButton("➕ Neue Reservierung")
        new_res_btn.setStyleSheet(get_button_style('primary'))
        new_res_btn.clicked.connect(self._add_reservation)
        left_layout.addWidget(new_res_btn)
        
        layout.addWidget(left_panel)
        
        # Right: Reservations list
        right_panel = QFrame()
        right_panel.setStyleSheet(CARD_STYLE)
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("📋 Reservierungen"))
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_combo = QComboBox()
        filter_combo.addItems(["Alle", "Heute", "Diese Woche", "Diesen Monat"])
        filter_layout.addWidget(filter_combo)
        
        resource_combo = QComboBox()
        resource_combo.addItems(["Alle Ressourcen", "Fahrzeuge", "Krane", "Geräte"])
        filter_layout.addWidget(resource_combo)
        filter_layout.addStretch()
        right_layout.addLayout(filter_layout)
        
        # Reservations table
        self.reservations_table = QTableWidget()
        self.reservations_table.setColumnCount(9)
        self.reservations_table.setHorizontalHeaderLabels([
            "Ressource", "Projekt", "Von", "Bis", "Mitarbeiter",
            "Status", "Bemerkung", "Erstellt von", "Aktionen"
        ])
        self.reservations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.reservations_table.setStyleSheet(self._table_style())
        right_layout.addWidget(self.reservations_table)
        
        layout.addWidget(right_panel, 1)
        
        return tab
    
    def _create_gps_tab(self) -> QWidget:
        """GPS-Tracking"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Info banner
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['info']}20;
                border: 1px solid {COLORS['info']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        info_layout = QHBoxLayout(info_frame)
        info_label = QLabel("📍 GPS-Tracking zeigt die aktuellen Positionen aller Fahrzeuge mit GPS-Sender.")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.setStyleSheet(get_button_style('primary'))
        info_layout.addWidget(refresh_btn)
        
        layout.addWidget(info_frame)
        
        # Map placeholder
        map_frame = QFrame()
        map_frame.setMinimumHeight(400)
        map_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_100']};
                border: 2px dashed {COLORS['gray_300']};
                border-radius: 8px;
            }}
        """)
        map_layout = QVBoxLayout(map_frame)
        map_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        map_icon = QLabel("🗺️")
        map_icon.setFont(QFont("Segoe UI", 48))
        map_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_layout.addWidget(map_icon)
        
        map_text = QLabel("Kartenansicht\n(Integration mit OpenStreetMap/Google Maps)")
        map_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_text.setStyleSheet(f"color: {COLORS['text_secondary']};")
        map_layout.addWidget(map_text)
        
        layout.addWidget(map_frame)
        
        # Vehicle positions table
        positions_group = QGroupBox("📍 Aktuelle Positionen")
        positions_group.setStyleSheet(self._group_style())
        positions_layout = QVBoxLayout(positions_group)
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(8)
        self.positions_table.setHorizontalHeaderLabels([
            "Fahrzeug", "Fahrer", "Position", "Geschwindigkeit",
            "Letzte Aktualisierung", "Status", "Projekt/Ziel", "Aktionen"
        ])
        self.positions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.positions_table.setStyleSheet(self._table_style())
        positions_layout.addWidget(self.positions_table)
        
        layout.addWidget(positions_group)
        
        return tab
    
    def _tab_style(self) -> str:
        return f"""
            QTabWidget::pane {{
                border: none;
                background: white;
                border-radius: 8px;
            }}
            QTabBar::tab {{
                padding: 12px 20px;
                margin-right: 4px;
                background: {COLORS['gray_50']};
                border: none;
                border-bottom: 3px solid transparent;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background: white;
                border-bottom: 3px solid {COLORS['primary']};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background: {COLORS['gray_100']};
            }}
        """
    
    def _table_style(self) -> str:
        return f"""
            QTableWidget {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                gridline-color: {COLORS['gray_100']};
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:alternate {{
                background: {COLORS['gray_50']};
            }}
            QTableWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
            QHeaderView::section {{
                background: {COLORS['gray_50']};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['gray_200']};
                font-weight: bold;
            }}
        """
    
    def _group_style(self) -> str:
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                background: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background: white;
            }}
        """
    
    # Event handlers
    def _add_vehicle(self):
        """Neues Fahrzeug hinzufügen"""
        dialog = VehicleDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_crane(self):
        """Neuen Kran hinzufügen"""
        dialog = EquipmentDialog(self.db_service, equipment_type="crane", user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_equipment(self):
        """Neues Gerät hinzufügen"""
        dialog = EquipmentDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_fuel_entry(self):
        """Tankvorgang erfassen"""
        dialog = FuelLogDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_trip(self):
        """Fahrt erfassen"""
        dialog = TripLogDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_maintenance(self):
        """Wartung erfassen"""
        dialog = MaintenanceDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_reservation(self):
        """Reservierung erstellen"""
        dialog = ReservationDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _export_trip_log(self):
        """Exportiert Fahrtenbuch als PDF/Excel"""
        from PyQt6.QtWidgets import QFileDialog
        from shared.services.export_service import ExportService
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Fahrtenbuch exportieren",
            f"Fahrtenbuch_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Dateien (*.pdf);;Excel Dateien (*.xlsx)"
        )
        
        if not filename:
            return
        
        try:
            # Fahrten laden
            session = self.db_service.get_session()
            query = select(TripLog).where(TripLog.is_deleted == False).order_by(TripLog.departure_datetime.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(TripLog.tenant_id == self.user.tenant_id)
            trips = session.execute(query).scalars().all()
            session.close()
            
            columns = [
                {"key": "date", "label": "Datum", "width": 15},
                {"key": "vehicle", "label": "Fahrzeug", "width": 20},
                {"key": "driver", "label": "Fahrer", "width": 20},
                {"key": "start", "label": "Start", "width": 25},
                {"key": "destination", "label": "Ziel", "width": 25},
                {"key": "km_start", "label": "km Start", "width": 15},
                {"key": "km_end", "label": "km Ende", "width": 15},
                {"key": "km_total", "label": "km Gesamt", "width": 15},
                {"key": "purpose", "label": "Zweck", "width": 30},
            ]
            
            data = []
            for t in trips:
                data.append({
                    "date": t.departure_datetime.strftime('%d.%m.%Y') if t.departure_datetime else '',
                    "vehicle": t.vehicle.license_plate if t.vehicle else '',
                    "driver": t.driver_name or '',
                    "start": t.start_location or '',
                    "destination": t.end_location or '',
                    "km_start": str(t.start_mileage or ''),
                    "km_end": str(t.end_mileage or ''),
                    "km_total": str((t.end_mileage or 0) - (t.start_mileage or 0)),
                    "purpose": t.purpose or '',
                })
            
            if filename.endswith('.xlsx'):
                ExportService.export_to_excel(data=data, columns=columns, title="Fahrtenbuch", filename=filename)
            else:
                ExportService.export_to_pdf(data=data, columns=columns, title="Fahrtenbuch", filename=filename, landscape_mode=True)
            
            QMessageBox.information(self, "Erfolg", f"Export wurde erstellt:\n{filename}")
            import os
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Export fehlgeschlagen: {e}")
    
    def _export_vehicles(self):
        """Exportiert Fahrzeugliste als PDF"""
        from PyQt6.QtWidgets import QFileDialog
        from shared.services.export_service import ExportService
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Fahrzeugliste exportieren",
            f"Fuhrpark_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Dateien (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            session = self.db_service.get_session()
            query = select(Vehicle).where(Vehicle.is_deleted == False).order_by(Vehicle.license_plate)
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Vehicle.tenant_id == self.user.tenant_id)
            vehicles = session.execute(query).scalars().all()
            session.close()
            
            ExportService.export_fleet_pdf(vehicles=vehicles, filename=filename)
            
            QMessageBox.information(self, "Erfolg", f"Export wurde erstellt:\n{filename}")
            import os
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Export fehlgeschlagen: {e}")
    
    def refresh(self):
        """Refresh all data"""
        self._load_vehicles()
        self._load_equipment()
    
    def _load_vehicles(self):
        """Lädt alle Fahrzeuge"""
        session = self.db_service.get_session()
        try:
            query = select(Vehicle).where(Vehicle.is_deleted == False).order_by(Vehicle.license_plate)
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Vehicle.tenant_id == self.user.tenant_id)
            
            vehicles = session.execute(query).scalars().all()
            self.vehicles_table.setRowCount(len(vehicles))
            
            status_names = {
                VehicleStatus.AVAILABLE: "Verfügbar",
                VehicleStatus.IN_USE: "Im Einsatz",
                VehicleStatus.MAINTENANCE: "In Wartung",
                VehicleStatus.REPAIR: "In Reparatur",
                VehicleStatus.RESERVED: "Reserviert",
                VehicleStatus.OUT_OF_SERVICE: "Außer Betrieb",
            }
            
            type_names = {
                VehicleType.PKW: "PKW",
                VehicleType.TRANSPORTER: "Transporter",
                VehicleType.LKW: "LKW",
                VehicleType.ANHAENGER: "Anhänger",
            }
            
            for row, v in enumerate(vehicles):
                self.vehicles_table.setItem(row, 0, QTableWidgetItem(v.license_plate or ""))
                self.vehicles_table.setItem(row, 1, QTableWidgetItem(type_names.get(v.vehicle_type, str(v.vehicle_type.value) if v.vehicle_type else "")))
                self.vehicles_table.setItem(row, 2, QTableWidgetItem(f"{v.manufacturer or ''} {v.model or ''}".strip()))
                self.vehicles_table.setItem(row, 3, QTableWidgetItem(""))  # Fahrer
                self.vehicles_table.setItem(row, 4, QTableWidgetItem(status_names.get(v.status, "")))
                self.vehicles_table.setItem(row, 5, QTableWidgetItem(v.tuv_due.strftime("%d.%m.%Y") if v.tuv_due else ""))
                self.vehicles_table.setItem(row, 6, QTableWidgetItem(v.au_due.strftime("%d.%m.%Y") if v.au_due else ""))
                self.vehicles_table.setItem(row, 7, QTableWidgetItem(v.uvv_due.strftime("%d.%m.%Y") if v.uvv_due else ""))
                self.vehicles_table.setItem(row, 8, QTableWidgetItem(str(v.current_mileage_km or 0)))
                self.vehicles_table.setItem(row, 9, QTableWidgetItem(v.current_location or ""))
                self.vehicles_table.setItem(row, 10, QTableWidgetItem("✓" if v.gps_enabled else ""))
                
                self.vehicles_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(v.id))
        finally:
            session.close()
    
    def _load_equipment(self):
        """Lädt alle Geräte"""
        session = self.db_service.get_session()
        try:
            query = select(Equipment).where(Equipment.is_deleted == False).order_by(Equipment.equipment_number)
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Equipment.tenant_id == self.user.tenant_id)
            
            equipment_list = session.execute(query).scalars().all()
            self.equipment_table.setRowCount(len(equipment_list))
            
            status_names = {
                VehicleStatus.AVAILABLE: "Verfügbar",
                VehicleStatus.IN_USE: "Im Einsatz",
                VehicleStatus.MAINTENANCE: "In Wartung",
                VehicleStatus.REPAIR: "In Reparatur",
            }
            
            for row, e in enumerate(equipment_list):
                self.equipment_table.setItem(row, 0, QTableWidgetItem(e.equipment_number or ""))
                self.equipment_table.setItem(row, 1, QTableWidgetItem(e.name or ""))
                self.equipment_table.setItem(row, 2, QTableWidgetItem(str(e.equipment_type.value) if e.equipment_type else ""))
                self.equipment_table.setItem(row, 3, QTableWidgetItem(e.manufacturer or ""))
                self.equipment_table.setItem(row, 4, QTableWidgetItem(e.model or ""))
                self.equipment_table.setItem(row, 5, QTableWidgetItem(status_names.get(e.status, "")))
                self.equipment_table.setItem(row, 6, QTableWidgetItem(e.operating_hours or "0"))
                self.equipment_table.setItem(row, 7, QTableWidgetItem(e.last_maintenance_date.strftime("%d.%m.%Y") if e.last_maintenance_date else ""))
                self.equipment_table.setItem(row, 8, QTableWidgetItem(e.next_maintenance_date.strftime("%d.%m.%Y") if e.next_maintenance_date else ""))
                self.equipment_table.setItem(row, 9, QTableWidgetItem(e.current_location or ""))
                self.equipment_table.setItem(row, 10, QTableWidgetItem(""))
                
                self.equipment_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(e.id))
        finally:
            session.close()


class VehicleDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten von Fahrzeugen"""
    
    def __init__(self, db_service, vehicle_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.vehicle_id = vehicle_id
        self.user = user
        self.setup_ui()
        if vehicle_id:
            self.load_vehicle()
    
    def setup_ui(self):
        self.setWindowTitle("Neues Fahrzeug" if not self.vehicle_id else "Fahrzeug bearbeiten")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.license_plate = QLineEdit()
        self.license_plate.setPlaceholderText("z.B. M-AB 1234")
        form.addRow("Kennzeichen*:", self.license_plate)
        
        self.vehicle_type = QComboBox()
        self.vehicle_type.addItem("PKW", "pkw")
        self.vehicle_type.addItem("Transporter", "transporter")
        self.vehicle_type.addItem("LKW", "lkw")
        self.vehicle_type.addItem("LKW mit Anhänger", "lkw_anhaenger")
        self.vehicle_type.addItem("Sattelzug", "sattelzug")
        self.vehicle_type.addItem("Pritsche", "pritsche")
        self.vehicle_type.addItem("Kipper", "kipper")
        self.vehicle_type.addItem("Tieflader", "tieflader")
        self.vehicle_type.addItem("LKW mit Kran", "kran_lkw")
        self.vehicle_type.addItem("Anhänger", "anhaenger")
        self.vehicle_type.addItem("Sonstige", "sonstige")
        form.addRow("Fahrzeugtyp*:", self.vehicle_type)
        
        self.manufacturer = QLineEdit()
        self.manufacturer.setPlaceholderText("z.B. Mercedes-Benz")
        form.addRow("Hersteller:", self.manufacturer)
        
        self.model = QLineEdit()
        self.model.setPlaceholderText("z.B. Sprinter 316 CDI")
        form.addRow("Modell:", self.model)
        
        self.vin = QLineEdit()
        self.vin.setPlaceholderText("Fahrgestellnummer")
        form.addRow("FIN (VIN):", self.vin)
        
        self.first_registration = QDateEdit()
        self.first_registration.setCalendarPopup(True)
        self.first_registration.setSpecialValueText("Nicht angegeben")
        form.addRow("Erstzulassung:", self.first_registration)
        
        self.status = QComboBox()
        self.status.addItem("Verfügbar", "available")
        self.status.addItem("Im Einsatz", "in_use")
        self.status.addItem("In Wartung", "maintenance")
        self.status.addItem("In Reparatur", "repair")
        self.status.addItem("Reserviert", "reserved")
        self.status.addItem("Außer Betrieb", "out_of_service")
        form.addRow("Status:", self.status)
        
        self.current_mileage = QSpinBox()
        self.current_mileage.setRange(0, 9999999)
        self.current_mileage.setSuffix(" km")
        form.addRow("Km-Stand:", self.current_mileage)
        
        self.tuv_due = QDateEdit()
        self.tuv_due.setCalendarPopup(True)
        self.tuv_due.setSpecialValueText("Nicht angegeben")
        form.addRow("TÜV fällig:", self.tuv_due)
        
        self.current_location = QLineEdit()
        self.current_location.setPlaceholderText("Aktueller Standort")
        form.addRow("Standort:", self.current_location)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("Notizen...")
        form.addRow("Notizen:", self.notes)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_vehicle(self):
        session = self.db.get_session()
        try:
            vehicle = session.get(Vehicle, uuid.UUID(self.vehicle_id))
            if vehicle:
                self.license_plate.setText(vehicle.license_plate or "")
                if vehicle.vehicle_type:
                    idx = self.vehicle_type.findData(vehicle.vehicle_type.value)
                    if idx >= 0:
                        self.vehicle_type.setCurrentIndex(idx)
                self.manufacturer.setText(vehicle.manufacturer or "")
                self.model.setText(vehicle.model or "")
                self.vin.setText(vehicle.vin or "")
                if vehicle.status:
                    idx = self.status.findData(vehicle.status.value)
                    if idx >= 0:
                        self.status.setCurrentIndex(idx)
                self.current_mileage.setValue(vehicle.current_mileage_km or 0)
                self.current_location.setText(vehicle.current_location or "")
                self.notes.setPlainText(vehicle.notes or "")
        finally:
            session.close()
    
    def save(self):
        if not self.license_plate.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Kennzeichen eingeben.")
            return
        
        session = self.db.get_session()
        try:
            if self.vehicle_id:
                vehicle = session.get(Vehicle, uuid.UUID(self.vehicle_id))
            else:
                vehicle = Vehicle()
                count = session.execute(select(func.count(Vehicle.id))).scalar() or 0
                vehicle.vehicle_number = f"FZ{count + 1:04d}"
                if self.user and hasattr(self.user, 'tenant_id'):
                    vehicle.tenant_id = self.user.tenant_id
            
            vehicle.license_plate = self.license_plate.text().strip()
            vehicle.vehicle_type = VehicleType(self.vehicle_type.currentData())
            vehicle.manufacturer = self.manufacturer.text().strip() or None
            vehicle.model = self.model.text().strip() or None
            vehicle.vin = self.vin.text().strip() or None
            vehicle.status = VehicleStatus(self.status.currentData())
            vehicle.current_mileage_km = self.current_mileage.value()
            vehicle.current_location = self.current_location.text().strip() or None
            vehicle.notes = self.notes.toPlainText().strip() or None
            
            if not self.vehicle_id:
                session.add(vehicle)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class EquipmentDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten von Geräten"""
    
    def __init__(self, db_service, equipment_id=None, equipment_type=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.equipment_id = equipment_id
        self.preset_type = equipment_type  # "crane" für Kran-Preset
        self.user = user
        self.setup_ui()
        if equipment_id:
            self.load_equipment()
    
    def setup_ui(self):
        self.setWindowTitle("Neues Gerät" if not self.equipment_id else "Gerät bearbeiten")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("z.B. Autokran 50t")
        form.addRow("Bezeichnung*:", self.name)
        
        self.equipment_type = QComboBox()
        self.equipment_type.addItem("Autokran", "autokran")
        self.equipment_type.addItem("Mobilkran", "mobilkran")
        self.equipment_type.addItem("Gabelstapler", "gabelstapler")
        self.equipment_type.addItem("Teleskoplader", "teleskoplader")
        self.equipment_type.addItem("Hubarbeitsbühne", "hubsteiger")
        self.equipment_type.addItem("Kompressor", "kompressor")
        self.equipment_type.addItem("Generator", "generator")
        self.equipment_type.addItem("Kettensäge", "kettensaege")
        self.equipment_type.addItem("Kreissäge", "kreissaege")
        self.equipment_type.addItem("Bohrmaschine", "bohrmaschine")
        self.equipment_type.addItem("Akkuschrauber", "akkuschrauber")
        self.equipment_type.addItem("Laser/Nivelliergerät", "laser")
        self.equipment_type.addItem("Messgerät", "messgeraet")
        self.equipment_type.addItem("Gerüst", "geruest")
        self.equipment_type.addItem("Sonstiges", "sonstiges")
        
        if self.preset_type == "crane":
            self.equipment_type.setCurrentIndex(0)
        
        form.addRow("Gerätetyp*:", self.equipment_type)
        
        self.manufacturer = QLineEdit()
        self.manufacturer.setPlaceholderText("z.B. Liebherr")
        form.addRow("Hersteller:", self.manufacturer)
        
        self.model_field = QLineEdit()
        self.model_field.setPlaceholderText("z.B. LTM 1050-3.1")
        form.addRow("Modell:", self.model_field)
        
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("Seriennummer")
        form.addRow("Seriennummer:", self.serial_number)
        
        self.status = QComboBox()
        self.status.addItem("Verfügbar", "available")
        self.status.addItem("Im Einsatz", "in_use")
        self.status.addItem("In Wartung", "maintenance")
        self.status.addItem("In Reparatur", "repair")
        self.status.addItem("Außer Betrieb", "out_of_service")
        form.addRow("Status:", self.status)
        
        self.operating_hours = QSpinBox()
        self.operating_hours.setRange(0, 999999)
        self.operating_hours.setSuffix(" h")
        form.addRow("Betriebsstunden:", self.operating_hours)
        
        self.current_location = QLineEdit()
        self.current_location.setPlaceholderText("Aktueller Standort")
        form.addRow("Standort:", self.current_location)
        
        self.uvv_due = QDateEdit()
        self.uvv_due.setCalendarPopup(True)
        self.uvv_due.setSpecialValueText("Nicht angegeben")
        form.addRow("UVV fällig:", self.uvv_due)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("Notizen...")
        form.addRow("Notizen:", self.notes)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_equipment(self):
        session = self.db.get_session()
        try:
            equipment = session.get(Equipment, uuid.UUID(self.equipment_id))
            if equipment:
                self.name.setText(equipment.name or "")
                if equipment.equipment_type:
                    idx = self.equipment_type.findData(equipment.equipment_type.value)
                    if idx >= 0:
                        self.equipment_type.setCurrentIndex(idx)
                self.manufacturer.setText(equipment.manufacturer or "")
                self.model_field.setText(equipment.model or "")
                self.serial_number.setText(equipment.serial_number or "")
                if equipment.status:
                    idx = self.status.findData(equipment.status.value)
                    if idx >= 0:
                        self.status.setCurrentIndex(idx)
                self.operating_hours.setValue(int(equipment.operating_hours or 0))
                self.current_location.setText(equipment.current_location or "")
                self.notes.setPlainText(equipment.notes or "")
        finally:
            session.close()
    
    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Bezeichnung eingeben.")
            return
        
        session = self.db.get_session()
        try:
            if self.equipment_id:
                equipment = session.get(Equipment, uuid.UUID(self.equipment_id))
            else:
                equipment = Equipment()
                count = session.execute(select(func.count(Equipment.id))).scalar() or 0
                equipment.equipment_number = f"GE{count + 1:05d}"
                if self.user and hasattr(self.user, 'tenant_id'):
                    equipment.tenant_id = self.user.tenant_id
            
            equipment.name = self.name.text().strip()
            equipment.equipment_type = EquipmentType(self.equipment_type.currentData())
            equipment.manufacturer = self.manufacturer.text().strip() or None
            equipment.model = self.model_field.text().strip() or None
            equipment.serial_number = self.serial_number.text().strip() or None
            equipment.status = VehicleStatus(self.status.currentData())
            equipment.operating_hours = str(self.operating_hours.value())
            equipment.current_location = self.current_location.text().strip() or None
            equipment.notes = self.notes.toPlainText().strip() or None
            
            if not self.equipment_id:
                session.add(equipment)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class FuelLogDialog(QDialog):
    """Dialog zum Erfassen von Tankvorgängen"""
    
    def __init__(self, db_service, fuel_log_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.fuel_log_id = fuel_log_id
        self.user = user
        self.setup_ui()
        self._load_vehicles()
    
    def setup_ui(self):
        self.setWindowTitle("Tankvorgang erfassen")
        self.setMinimumSize(500, 450)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.vehicle_combo = QComboBox()
        form.addRow("Fahrzeug*:", self.vehicle_combo)
        
        self.refuel_date = QDateEdit()
        self.refuel_date.setCalendarPopup(True)
        self.refuel_date.setDate(QDate.currentDate())
        form.addRow("Datum*:", self.refuel_date)
        
        self.refuel_time = QTimeEdit()
        self.refuel_time.setTime(QTime.currentTime())
        form.addRow("Uhrzeit:", self.refuel_time)
        
        self.mileage = QSpinBox()
        self.mileage.setRange(0, 9999999)
        self.mileage.setSuffix(" km")
        form.addRow("Km-Stand*:", self.mileage)
        
        self.fuel_type = QComboBox()
        self.fuel_type.addItems(["Diesel", "Super E10", "Super E5", "Super Plus", "AdBlue", "LPG", "CNG", "Strom"])
        form.addRow("Kraftstoff:", self.fuel_type)
        
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(0, 9999)
        self.quantity.setDecimals(2)
        self.quantity.setSuffix(" Liter")
        form.addRow("Menge*:", self.quantity)
        
        self.price_per_liter = QDoubleSpinBox()
        self.price_per_liter.setRange(0, 10)
        self.price_per_liter.setDecimals(3)
        self.price_per_liter.setSuffix(" €/l")
        self.price_per_liter.valueChanged.connect(self._calc_total)
        form.addRow("Preis pro Liter:", self.price_per_liter)
        
        self.total_price = QDoubleSpinBox()
        self.total_price.setRange(0, 99999)
        self.total_price.setDecimals(2)
        self.total_price.setSuffix(" €")
        form.addRow("Gesamtpreis:", self.total_price)
        
        self.full_tank = QCheckBox("Vollgetankt")
        self.full_tank.setChecked(True)
        form.addRow("", self.full_tank)
        
        self.gas_station = QLineEdit()
        self.gas_station.setPlaceholderText("z.B. Aral, Shell, etc.")
        form.addRow("Tankstelle:", self.gas_station)
        
        self.gas_station_location = QLineEdit()
        self.gas_station_location.setPlaceholderText("Ort der Tankstelle")
        form.addRow("Ort:", self.gas_station_location)
        
        self.fuel_notes = QTextEdit()
        self.fuel_notes.setMaximumHeight(60)
        self.fuel_notes.setPlaceholderText("Bemerkungen...")
        form.addRow("Notizen:", self.fuel_notes)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_vehicles(self):
        session = self.db.get_session()
        try:
            query = select(Vehicle).where(Vehicle.is_deleted == False).order_by(Vehicle.license_plate)
            vehicles = session.execute(query).scalars().all()
            self.vehicle_combo.addItem("-- Fahrzeug wählen --", None)
            for v in vehicles:
                self.vehicle_combo.addItem(f"{v.license_plate} - {v.manufacturer or ''} {v.model or ''}", str(v.id))
        finally:
            session.close()
    
    def _calc_total(self):
        total = self.quantity.value() * self.price_per_liter.value()
        self.total_price.setValue(total)
    
    def save(self):
        vehicle_id = self.vehicle_combo.currentData()
        if not vehicle_id:
            QMessageBox.warning(self, "Fehler", "Bitte Fahrzeug auswählen.")
            return
        if self.quantity.value() <= 0:
            QMessageBox.warning(self, "Fehler", "Bitte Menge eingeben.")
            return
        
        session = self.db.get_session()
        try:
            fuel_log = FuelLog()
            fuel_log.vehicle_id = uuid.UUID(vehicle_id)
            fuel_log.refuel_date = self.refuel_date.date().toPyDate()
            fuel_log.refuel_time = self.refuel_time.time().toString("HH:mm")
            fuel_log.mileage_km = self.mileage.value()
            fuel_log.fuel_type = self.fuel_type.currentText()
            fuel_log.quantity_liters = str(self.quantity.value())
            fuel_log.price_per_liter = str(self.price_per_liter.value()) if self.price_per_liter.value() > 0 else None
            fuel_log.total_price = str(self.total_price.value()) if self.total_price.value() > 0 else None
            fuel_log.full_tank = self.full_tank.isChecked()
            fuel_log.gas_station = self.gas_station.text().strip() or None
            fuel_log.gas_station_location = self.gas_station_location.text().strip() or None
            fuel_log.notes = self.fuel_notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                fuel_log.tenant_id = self.user.tenant_id
            
            session.add(fuel_log)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class TripLogDialog(QDialog):
    """Dialog zum Erfassen von Fahrten (Fahrtenbuch)"""
    
    def __init__(self, db_service, trip_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.trip_id = trip_id
        self.user = user
        self.setup_ui()
        self._load_vehicles()
    
    def setup_ui(self):
        self.setWindowTitle("Fahrt erfassen")
        self.setMinimumSize(550, 550)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.trip_vehicle_combo = QComboBox()
        form.addRow("Fahrzeug*:", self.trip_vehicle_combo)
        
        self.trip_date = QDateEdit()
        self.trip_date.setCalendarPopup(True)
        self.trip_date.setDate(QDate.currentDate())
        form.addRow("Datum*:", self.trip_date)
        
        # Start
        start_label = QLabel("--- Abfahrt ---")
        start_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(start_label)
        
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(7, 0))
        form.addRow("Abfahrtszeit:", self.start_time)
        
        self.start_mileage = QSpinBox()
        self.start_mileage.setRange(0, 9999999)
        self.start_mileage.setSuffix(" km")
        form.addRow("Km-Stand Start*:", self.start_mileage)
        
        self.start_location = QLineEdit()
        self.start_location.setPlaceholderText("z.B. Betriebshof")
        form.addRow("Startort:", self.start_location)
        
        # Ende
        end_label = QLabel("--- Ankunft ---")
        end_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(end_label)
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(17, 0))
        form.addRow("Ankunftszeit:", self.end_time)
        
        self.end_mileage = QSpinBox()
        self.end_mileage.setRange(0, 9999999)
        self.end_mileage.setSuffix(" km")
        self.end_mileage.valueChanged.connect(self._calc_distance)
        form.addRow("Km-Stand Ende*:", self.end_mileage)
        
        self.end_location = QLineEdit()
        self.end_location.setPlaceholderText("z.B. Baustelle Müller")
        form.addRow("Zielort:", self.end_location)
        
        self.distance_label = QLabel("0 km")
        self.distance_label.setStyleSheet("font-weight: bold;")
        form.addRow("Strecke:", self.distance_label)
        
        # Zweck
        details_label = QLabel("--- Details ---")
        details_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(details_label)
        
        self.trip_type = QComboBox()
        self.trip_type.addItems(["Dienstfahrt", "Privatfahrt", "Arbeitsweg"])
        form.addRow("Fahrtart:", self.trip_type)
        
        self.purpose = QLineEdit()
        self.purpose.setPlaceholderText("z.B. Materialtransport, Baustellenbesuch")
        form.addRow("Zweck*:", self.purpose)
        
        self.trip_notes = QTextEdit()
        self.trip_notes.setMaximumHeight(60)
        self.trip_notes.setPlaceholderText("Route, Bemerkungen...")
        form.addRow("Notizen:", self.trip_notes)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_vehicles(self):
        session = self.db.get_session()
        try:
            query = select(Vehicle).where(Vehicle.is_deleted == False).order_by(Vehicle.license_plate)
            vehicles = session.execute(query).scalars().all()
            self.trip_vehicle_combo.addItem("-- Fahrzeug wählen --", None)
            for v in vehicles:
                self.trip_vehicle_combo.addItem(f"{v.license_plate} - {v.manufacturer or ''} {v.model or ''}", str(v.id))
        finally:
            session.close()
    
    def _calc_distance(self):
        dist = self.end_mileage.value() - self.start_mileage.value()
        self.distance_label.setText(f"{max(0, dist)} km")
    
    def save(self):
        vehicle_id = self.trip_vehicle_combo.currentData()
        if not vehicle_id:
            QMessageBox.warning(self, "Fehler", "Bitte Fahrzeug auswählen.")
            return
        if not self.purpose.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Zweck der Fahrt eingeben.")
            return
        
        session = self.db.get_session()
        try:
            trip = MileageLog()
            trip.vehicle_id = uuid.UUID(vehicle_id)
            trip.trip_date = self.trip_date.date().toPyDate()
            trip.start_time = self.start_time.time().toString("HH:mm")
            trip.start_mileage = self.start_mileage.value()
            trip.start_location = self.start_location.text().strip() or None
            trip.end_time = self.end_time.time().toString("HH:mm")
            trip.end_mileage = self.end_mileage.value()
            trip.end_location = self.end_location.text().strip() or None
            trip.distance_km = max(0, self.end_mileage.value() - self.start_mileage.value())
            
            type_map = {"Dienstfahrt": "business", "Privatfahrt": "private", "Arbeitsweg": "commute"}
            trip.trip_type = type_map.get(self.trip_type.currentText(), "business")
            trip.purpose = self.purpose.text().strip()
            trip.notes = self.trip_notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                trip.tenant_id = self.user.tenant_id
            
            session.add(trip)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class MaintenanceDialog(QDialog):
    """Dialog zum Erfassen von Wartungen"""
    
    def __init__(self, db_service, maintenance_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.maintenance_id = maintenance_id
        self.user = user
        self.setup_ui()
        self._load_resources()
    
    def setup_ui(self):
        self.setWindowTitle("Wartung/Reparatur erfassen")
        self.setMinimumSize(550, 550)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.resource_type = QComboBox()
        self.resource_type.addItems(["Fahrzeug", "Gerät/Maschine"])
        self.resource_type.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Typ:", self.resource_type)
        
        self.maint_vehicle_combo = QComboBox()
        form.addRow("Fahrzeug:", self.maint_vehicle_combo)
        
        self.maint_equipment_combo = QComboBox()
        self.maint_equipment_combo.setVisible(False)
        form.addRow("Gerät:", self.maint_equipment_combo)
        
        self.maintenance_date = QDateEdit()
        self.maintenance_date.setCalendarPopup(True)
        self.maintenance_date.setDate(QDate.currentDate())
        form.addRow("Datum*:", self.maintenance_date)
        
        self.maintenance_type = QComboBox()
        self.maintenance_type.addItems([
            "Inspektion", "Ölwechsel", "Reifenwechsel", "TÜV/HU", "AU",
            "UVV-Prüfung", "Reparatur", "Unfall", "Bremsen", "Elektrik", "Sonstiges"
        ])
        form.addRow("Art*:", self.maintenance_type)
        
        self.maint_mileage = QSpinBox()
        self.maint_mileage.setRange(0, 9999999)
        self.maint_mileage.setSuffix(" km")
        form.addRow("Km-Stand:", self.maint_mileage)
        
        self.maint_description = QTextEdit()
        self.maint_description.setMaximumHeight(80)
        self.maint_description.setPlaceholderText("Beschreibung der durchgeführten Arbeiten...")
        form.addRow("Beschreibung:", self.maint_description)
        
        self.workshop = QLineEdit()
        self.workshop.setPlaceholderText("Name der Werkstatt")
        form.addRow("Werkstatt:", self.workshop)
        
        self.parts_cost = QDoubleSpinBox()
        self.parts_cost.setRange(0, 999999)
        self.parts_cost.setDecimals(2)
        self.parts_cost.setSuffix(" €")
        self.parts_cost.valueChanged.connect(self._calc_total)
        form.addRow("Materialkosten:", self.parts_cost)
        
        self.labor_cost = QDoubleSpinBox()
        self.labor_cost.setRange(0, 999999)
        self.labor_cost.setDecimals(2)
        self.labor_cost.setSuffix(" €")
        self.labor_cost.valueChanged.connect(self._calc_total)
        form.addRow("Arbeitskosten:", self.labor_cost)
        
        self.total_cost = QDoubleSpinBox()
        self.total_cost.setRange(0, 999999)
        self.total_cost.setDecimals(2)
        self.total_cost.setSuffix(" €")
        form.addRow("Gesamtkosten:", self.total_cost)
        
        self.next_maintenance = QDateEdit()
        self.next_maintenance.setCalendarPopup(True)
        self.next_maintenance.setSpecialValueText("Nicht festgelegt")
        form.addRow("Nächste Wartung:", self.next_maintenance)
        
        self.maint_notes = QTextEdit()
        self.maint_notes.setMaximumHeight(60)
        self.maint_notes.setPlaceholderText("Weitere Bemerkungen...")
        form.addRow("Notizen:", self.maint_notes)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_resources(self):
        session = self.db.get_session()
        try:
            vehicles = session.execute(
                select(Vehicle).where(Vehicle.is_deleted == False).order_by(Vehicle.license_plate)
            ).scalars().all()
            self.maint_vehicle_combo.addItem("-- Fahrzeug wählen --", None)
            for v in vehicles:
                self.maint_vehicle_combo.addItem(f"{v.license_plate} - {v.manufacturer or ''} {v.model or ''}", str(v.id))
            
            equipment_list = session.execute(
                select(Equipment).where(Equipment.is_deleted == False).order_by(Equipment.name)
            ).scalars().all()
            self.maint_equipment_combo.addItem("-- Gerät wählen --", None)
            for e in equipment_list:
                self.maint_equipment_combo.addItem(f"{e.equipment_number} - {e.name}", str(e.id))
        finally:
            session.close()
    
    def _on_type_changed(self, index):
        is_vehicle = index == 0
        self.maint_vehicle_combo.setVisible(is_vehicle)
        self.maint_equipment_combo.setVisible(not is_vehicle)
    
    def _calc_total(self):
        total = self.parts_cost.value() + self.labor_cost.value()
        self.total_cost.setValue(total)
    
    def save(self):
        is_vehicle = self.resource_type.currentIndex() == 0
        
        if is_vehicle:
            resource_id = self.maint_vehicle_combo.currentData()
            if not resource_id:
                QMessageBox.warning(self, "Fehler", "Bitte Fahrzeug auswählen.")
                return
        else:
            resource_id = self.maint_equipment_combo.currentData()
            if not resource_id:
                QMessageBox.warning(self, "Fehler", "Bitte Gerät auswählen.")
                return
        
        session = self.db.get_session()
        try:
            if is_vehicle:
                maintenance = VehicleMaintenance()
                maintenance.vehicle_id = uuid.UUID(resource_id)
                maintenance.mileage_at_maintenance = self.maint_mileage.value() if self.maint_mileage.value() > 0 else None
            else:
                maintenance = EquipmentMaintenance()
                maintenance.equipment_id = uuid.UUID(resource_id)
            
            maintenance.maintenance_date = self.maintenance_date.date().toPyDate()
            maintenance.maintenance_type = self.maintenance_type.currentText()
            maintenance.description = self.maint_description.toPlainText().strip() or None
            maintenance.workshop_name = self.workshop.text().strip() or None
            maintenance.parts_cost = str(self.parts_cost.value()) if self.parts_cost.value() > 0 else None
            maintenance.labor_cost = str(self.labor_cost.value()) if self.labor_cost.value() > 0 else None
            maintenance.total_cost = str(self.total_cost.value()) if self.total_cost.value() > 0 else None
            maintenance.notes = self.maint_notes.toPlainText().strip() or None
            
            next_date = self.next_maintenance.date()
            if next_date.isValid() and next_date.year() > 2000:
                maintenance.next_maintenance_date = next_date.toPyDate()
            
            if self.user and hasattr(self.user, 'tenant_id'):
                maintenance.tenant_id = self.user.tenant_id
            
            session.add(maintenance)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class ReservationDialog(QDialog):
    """Dialog zum Erstellen von Reservierungen"""
    
    def __init__(self, db_service, reservation_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.reservation_id = reservation_id
        self.user = user
        self.setup_ui()
        self._load_resources()
    
    def setup_ui(self):
        self.setWindowTitle("Reservierung erstellen")
        self.setMinimumSize(500, 450)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.res_resource_type = QComboBox()
        self.res_resource_type.addItems(["Fahrzeug", "Gerät/Maschine"])
        self.res_resource_type.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Ressourcentyp:", self.res_resource_type)
        
        self.res_vehicle_combo = QComboBox()
        form.addRow("Fahrzeug:", self.res_vehicle_combo)
        
        self.res_equipment_combo = QComboBox()
        self.res_equipment_combo.setVisible(False)
        form.addRow("Gerät:", self.res_equipment_combo)
        
        period_label = QLabel("--- Zeitraum ---")
        period_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(period_label)
        
        self.res_start_date = QDateEdit()
        self.res_start_date.setCalendarPopup(True)
        self.res_start_date.setDate(QDate.currentDate())
        form.addRow("Von Datum*:", self.res_start_date)
        
        self.res_start_time = QTimeEdit()
        self.res_start_time.setTime(QTime(7, 0))
        form.addRow("Von Uhrzeit:", self.res_start_time)
        
        self.res_end_date = QDateEdit()
        self.res_end_date.setCalendarPopup(True)
        self.res_end_date.setDate(QDate.currentDate())
        form.addRow("Bis Datum*:", self.res_end_date)
        
        self.res_end_time = QTimeEdit()
        self.res_end_time.setTime(QTime(17, 0))
        form.addRow("Bis Uhrzeit:", self.res_end_time)
        
        details_label = QLabel("--- Details ---")
        details_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(details_label)
        
        self.res_purpose = QLineEdit()
        self.res_purpose.setPlaceholderText("z.B. Baustelle Müller, Materialtransport")
        form.addRow("Zweck*:", self.res_purpose)
        
        self.res_status = QComboBox()
        self.res_status.addItem("Ausstehend", "pending")
        self.res_status.addItem("Bestätigt", "confirmed")
        form.addRow("Status:", self.res_status)
        
        self.res_notes = QTextEdit()
        self.res_notes.setMaximumHeight(60)
        self.res_notes.setPlaceholderText("Zusätzliche Informationen...")
        form.addRow("Notizen:", self.res_notes)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_resources(self):
        session = self.db.get_session()
        try:
            vehicles = session.execute(
                select(Vehicle).where(Vehicle.is_deleted == False).order_by(Vehicle.license_plate)
            ).scalars().all()
            self.res_vehicle_combo.addItem("-- Fahrzeug wählen --", None)
            for v in vehicles:
                self.res_vehicle_combo.addItem(f"{v.license_plate} - {v.manufacturer or ''} {v.model or ''}", str(v.id))
            
            equipment_list = session.execute(
                select(Equipment).where(Equipment.is_deleted == False).order_by(Equipment.name)
            ).scalars().all()
            self.res_equipment_combo.addItem("-- Gerät wählen --", None)
            for e in equipment_list:
                self.res_equipment_combo.addItem(f"{e.equipment_number} - {e.name}", str(e.id))
        finally:
            session.close()
    
    def _on_type_changed(self, index):
        is_vehicle = index == 0
        self.res_vehicle_combo.setVisible(is_vehicle)
        self.res_equipment_combo.setVisible(not is_vehicle)
    
    def save(self):
        is_vehicle = self.res_resource_type.currentIndex() == 0
        
        if is_vehicle:
            resource_id = self.res_vehicle_combo.currentData()
            if not resource_id:
                QMessageBox.warning(self, "Fehler", "Bitte Fahrzeug auswählen.")
                return
        else:
            resource_id = self.res_equipment_combo.currentData()
            if not resource_id:
                QMessageBox.warning(self, "Fehler", "Bitte Gerät auswählen.")
                return
        
        if not self.res_purpose.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Zweck der Reservierung eingeben.")
            return
        
        session = self.db.get_session()
        try:
            reservation = EquipmentReservation()
            
            if is_vehicle:
                reservation.vehicle_id = uuid.UUID(resource_id)
            else:
                reservation.equipment_id = uuid.UUID(resource_id)
            
            reservation.start_date = self.res_start_date.date().toPyDate()
            reservation.start_time = self.res_start_time.time().toString("HH:mm")
            reservation.end_date = self.res_end_date.date().toPyDate()
            reservation.end_time = self.res_end_time.time().toString("HH:mm")
            reservation.purpose = self.res_purpose.text().strip()
            reservation.status = self.res_status.currentData()
            reservation.notes = self.res_notes.toPlainText().strip() or None
            
            # reserved_by_id verweist auf employees - nicht setzen
            
            if self.user and hasattr(self.user, 'tenant_id'):
                reservation.tenant_id = self.user.tenant_id
            
            session.add(reservation)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
