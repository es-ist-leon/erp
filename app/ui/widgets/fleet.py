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

from app.ui.styles import COLORS, get_button_style, CARD_STYLE


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
        QMessageBox.information(self, "Neues Fahrzeug", "Fahrzeug-Dialog wird geöffnet...")
    
    def _add_crane(self):
        QMessageBox.information(self, "Neuer Kran", "Kran-Dialog wird geöffnet...")
    
    def _add_equipment(self):
        QMessageBox.information(self, "Neues Gerät", "Geräte-Dialog wird geöffnet...")
    
    def _add_fuel_entry(self):
        QMessageBox.information(self, "Tankvorgang", "Tankvorgang-Dialog wird geöffnet...")
    
    def _add_trip(self):
        QMessageBox.information(self, "Neue Fahrt", "Fahrt-Dialog wird geöffnet...")
    
    def _add_maintenance(self):
        QMessageBox.information(self, "Wartung erfassen", "Wartungs-Dialog wird geöffnet...")
    
    def _add_reservation(self):
        QMessageBox.information(self, "Neue Reservierung", "Reservierungs-Dialog wird geöffnet...")
    
    def refresh(self):
        """Refresh all data"""
        pass
