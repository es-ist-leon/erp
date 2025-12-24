"""
Bautagebuch Widget - Construction Diary Management
Tägliche Dokumentation von Baustellen
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QFrame, QDialog, QFormLayout,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTimeEdit, QTabWidget, QScrollArea, QGroupBox, QCheckBox,
    QFileDialog, QListWidget, QListWidgetItem, QMessageBox,
    QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon
from datetime import datetime, date, time
from decimal import Decimal
import json
import uuid

from sqlalchemy import select
from app.ui.styles import COLORS, get_button_style, CARD_STYLE
from shared.models import ConstructionDiary, Project, WeatherCondition


class ConstructionDiaryWidget(QWidget):
    """Bautagebuch - Tägliche Baustellendokumentation"""
    
    def __init__(self, db_service, user):
        super().__init__()
        self.db_service = db_service
        self.user = user
        # Store user info from UserData object
        self.user_display_name = "Benutzer"
        if user:
            try:
                first = getattr(user, 'first_name', '') or ''
                last = getattr(user, 'last_name', '') or ''
                username = getattr(user, 'username', 'Benutzer') or 'Benutzer'
                self.user_display_name = f"{first} {last}".strip() or username
            except:
                self.user_display_name = "Benutzer"
        self.current_project = None
        self.current_entry = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Project/Entry list
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right: Entry details with tabs
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 900])
        layout.addWidget(splitter)
    
    def _create_header(self) -> QFrame:
        """Header mit Aktionsbuttons"""
        header = QFrame()
        header.setStyleSheet(CARD_STYLE)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        # Title
        title = QLabel("📋 Bautagebuch")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Project selector
        header_layout.addWidget(QLabel("Projekt:"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(250)
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)
        header_layout.addWidget(self.project_combo)
        
        header_layout.addStretch()
        
        # Action buttons
        new_btn = QPushButton("➕ Neuer Eintrag")
        new_btn.setStyleSheet(get_button_style('primary'))
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self._new_entry)
        header_layout.addWidget(new_btn)
        
        export_btn = QPushButton("📄 PDF Export")
        export_btn.setStyleSheet(get_button_style('secondary'))
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.clicked.connect(self._export_pdf)
        header_layout.addWidget(export_btn)
        
        return header
    
    def _create_left_panel(self) -> QFrame:
        """Linkes Panel mit Einträgen"""
        panel = QFrame()
        panel.setStyleSheet(CARD_STYLE)
        panel.setMinimumWidth(280)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Search
        search = QLineEdit()
        search.setPlaceholderText("🔍 Einträge suchen...")
        search.textChanged.connect(self._filter_entries)
        layout.addWidget(search)
        
        # Date filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Von:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("Bis:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_layout.addWidget(self.date_to)
        layout.addLayout(date_layout)
        
        # Entry tree
        self.entry_tree = QTreeWidget()
        self.entry_tree.setHeaderLabels(["Datum", "Status"])
        self.entry_tree.itemClicked.connect(self._on_entry_selected)
        self.entry_tree.setStyleSheet(f"""
            QTreeWidget {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['gray_100']};
            }}
            QTreeWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        layout.addWidget(self.entry_tree)
        
        return panel
    
    def _create_right_panel(self) -> QFrame:
        """Rechtes Panel mit Details"""
        panel = QFrame()
        panel.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: white;
            }}
            QTabBar::tab {{
                padding: 12px 24px;
                margin-right: 4px;
                background: {COLORS['gray_50']};
                border: none;
                border-bottom: 3px solid transparent;
            }}
            QTabBar::tab:selected {{
                background: white;
                border-bottom: 3px solid {COLORS['primary']};
                font-weight: bold;
            }}
        """)
        
        # Tab 1: Allgemein & Wetter
        self.tabs.addTab(self._create_general_tab(), "🌤️ Allgemein & Wetter")
        
        # Tab 2: Personal
        self.tabs.addTab(self._create_personnel_tab(), "👷 Personal")
        
        # Tab 3: Arbeitsfortschritt
        self.tabs.addTab(self._create_progress_tab(), "📈 Arbeitsfortschritt")
        
        # Tab 4: Material & Lieferungen
        self.tabs.addTab(self._create_material_tab(), "📦 Material & Lieferungen")
        
        # Tab 5: Besucher & Besprechungen
        self.tabs.addTab(self._create_visitors_tab(), "🤝 Besucher & Besprechungen")
        
        # Tab 6: Vorkommnisse
        self.tabs.addTab(self._create_incidents_tab(), "⚠️ Vorkommnisse")
        
        # Tab 7: Unterschriften
        self.tabs.addTab(self._create_signatures_tab(), "✍️ Unterschriften")
        
        layout.addWidget(self.tabs)
        
        # Save button
        save_frame = QFrame()
        save_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-top: 1px solid {COLORS['gray_200']};")
        save_layout = QHBoxLayout(save_frame)
        save_layout.setContentsMargins(20, 12, 20, 12)
        save_layout.addStretch()
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_entry)
        save_layout.addWidget(save_btn)
        
        layout.addWidget(save_frame)
        
        return panel
    
    def _create_general_tab(self) -> QWidget:
        """Allgemeine Daten und Wetter"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Datum und Status
        general_group = QGroupBox("Allgemeine Angaben")
        general_group.setStyleSheet(self._group_style())
        general_layout = QFormLayout(general_group)
        general_layout.setSpacing(12)
        
        self.entry_date = QDateEdit()
        self.entry_date.setDate(QDate.currentDate())
        self.entry_date.setCalendarPopup(True)
        general_layout.addRow("Datum:", self.entry_date)
        
        self.entry_number = QLineEdit()
        self.entry_number.setPlaceholderText("Wird automatisch generiert")
        self.entry_number.setReadOnly(True)
        general_layout.addRow("Eintrag-Nr.:", self.entry_number)
        
        self.author = QLineEdit()
        self.author.setText(self.user_display_name)
        general_layout.addRow("Erstellt von:", self.author)
        
        self.entry_status = QComboBox()
        self.entry_status.addItems(["Entwurf", "Abgeschlossen", "Geprüft", "Freigegeben"])
        general_layout.addRow("Status:", self.entry_status)
        
        layout.addWidget(general_group)
        
        # Wetter Morgens
        weather_morning = QGroupBox("☀️ Wetter Morgens (06:00 - 10:00)")
        weather_morning.setStyleSheet(self._group_style())
        wm_layout = QFormLayout(weather_morning)
        wm_layout.setSpacing(12)
        
        self.weather_morning_condition = QComboBox()
        self.weather_morning_condition.addItems([
            "Sonnig", "Leicht bewölkt", "Bewölkt", "Stark bewölkt", 
            "Nebel", "Leichter Regen", "Regen", "Starkregen",
            "Gewitter", "Schneefall", "Hagel", "Frost"
        ])
        wm_layout.addRow("Witterung:", self.weather_morning_condition)
        
        self.weather_morning_temp = QDoubleSpinBox()
        self.weather_morning_temp.setRange(-40, 50)
        self.weather_morning_temp.setSuffix(" °C")
        wm_layout.addRow("Temperatur:", self.weather_morning_temp)
        
        self.weather_morning_humidity = QSpinBox()
        self.weather_morning_humidity.setRange(0, 100)
        self.weather_morning_humidity.setSuffix(" %")
        wm_layout.addRow("Luftfeuchtigkeit:", self.weather_morning_humidity)
        
        self.weather_morning_wind = QComboBox()
        self.weather_morning_wind.addItems(["Windstill", "Leicht", "Mäßig", "Stark", "Sturm"])
        wm_layout.addRow("Wind:", self.weather_morning_wind)
        
        self.weather_morning_precipitation = QDoubleSpinBox()
        self.weather_morning_precipitation.setRange(0, 500)
        self.weather_morning_precipitation.setSuffix(" mm")
        wm_layout.addRow("Niederschlag:", self.weather_morning_precipitation)
        
        layout.addWidget(weather_morning)
        
        # Wetter Mittags
        weather_noon = QGroupBox("🌤️ Wetter Mittags (10:00 - 14:00)")
        weather_noon.setStyleSheet(self._group_style())
        wn_layout = QFormLayout(weather_noon)
        wn_layout.setSpacing(12)
        
        self.weather_noon_condition = QComboBox()
        self.weather_noon_condition.addItems([
            "Sonnig", "Leicht bewölkt", "Bewölkt", "Stark bewölkt", 
            "Nebel", "Leichter Regen", "Regen", "Starkregen",
            "Gewitter", "Schneefall", "Hagel", "Frost"
        ])
        wn_layout.addRow("Witterung:", self.weather_noon_condition)
        
        self.weather_noon_temp = QDoubleSpinBox()
        self.weather_noon_temp.setRange(-40, 50)
        self.weather_noon_temp.setSuffix(" °C")
        wn_layout.addRow("Temperatur:", self.weather_noon_temp)
        
        self.weather_noon_humidity = QSpinBox()
        self.weather_noon_humidity.setRange(0, 100)
        self.weather_noon_humidity.setSuffix(" %")
        wn_layout.addRow("Luftfeuchtigkeit:", self.weather_noon_humidity)
        
        self.weather_noon_wind = QComboBox()
        self.weather_noon_wind.addItems(["Windstill", "Leicht", "Mäßig", "Stark", "Sturm"])
        wn_layout.addRow("Wind:", self.weather_noon_wind)
        
        self.weather_noon_precipitation = QDoubleSpinBox()
        self.weather_noon_precipitation.setRange(0, 500)
        self.weather_noon_precipitation.setSuffix(" mm")
        wn_layout.addRow("Niederschlag:", self.weather_noon_precipitation)
        
        layout.addWidget(weather_noon)
        
        # Wetter Abends
        weather_evening = QGroupBox("🌙 Wetter Abends (14:00 - 18:00)")
        weather_evening.setStyleSheet(self._group_style())
        we_layout = QFormLayout(weather_evening)
        we_layout.setSpacing(12)
        
        self.weather_evening_condition = QComboBox()
        self.weather_evening_condition.addItems([
            "Sonnig", "Leicht bewölkt", "Bewölkt", "Stark bewölkt", 
            "Nebel", "Leichter Regen", "Regen", "Starkregen",
            "Gewitter", "Schneefall", "Hagel", "Frost"
        ])
        we_layout.addRow("Witterung:", self.weather_evening_condition)
        
        self.weather_evening_temp = QDoubleSpinBox()
        self.weather_evening_temp.setRange(-40, 50)
        self.weather_evening_temp.setSuffix(" °C")
        we_layout.addRow("Temperatur:", self.weather_evening_temp)
        
        self.weather_evening_humidity = QSpinBox()
        self.weather_evening_humidity.setRange(0, 100)
        self.weather_evening_humidity.setSuffix(" %")
        we_layout.addRow("Luftfeuchtigkeit:", self.weather_evening_humidity)
        
        self.weather_evening_wind = QComboBox()
        self.weather_evening_wind.addItems(["Windstill", "Leicht", "Mäßig", "Stark", "Sturm"])
        we_layout.addRow("Wind:", self.weather_evening_wind)
        
        self.weather_evening_precipitation = QDoubleSpinBox()
        self.weather_evening_precipitation.setRange(0, 500)
        self.weather_evening_precipitation.setSuffix(" mm")
        we_layout.addRow("Niederschlag:", self.weather_evening_precipitation)
        
        layout.addWidget(weather_evening)
        
        # Arbeitszeit
        worktime_group = QGroupBox("⏰ Arbeitszeiten")
        worktime_group.setStyleSheet(self._group_style())
        wt_layout = QFormLayout(worktime_group)
        wt_layout.setSpacing(12)
        
        self.work_start = QTimeEdit()
        self.work_start.setTime(QTime(7, 0))
        wt_layout.addRow("Arbeitsbeginn:", self.work_start)
        
        self.work_end = QTimeEdit()
        self.work_end.setTime(QTime(16, 30))
        wt_layout.addRow("Arbeitsende:", self.work_end)
        
        self.break_duration = QSpinBox()
        self.break_duration.setRange(0, 120)
        self.break_duration.setValue(30)
        self.break_duration.setSuffix(" min")
        wt_layout.addRow("Pausenzeit:", self.break_duration)
        
        self.workable = QCheckBox("Arbeitsfähig")
        self.workable.setChecked(True)
        wt_layout.addRow("", self.workable)
        
        self.work_notes = QTextEdit()
        self.work_notes.setMaximumHeight(80)
        self.work_notes.setPlaceholderText("Anmerkungen zu den Arbeitszeiten...")
        wt_layout.addRow("Anmerkungen:", self.work_notes)
        
        layout.addWidget(worktime_group)
        
        layout.addStretch()
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        return tab
    
    def _create_personnel_tab(self) -> QWidget:
        """Personal und Subunternehmer"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Eigenes Personal
        own_group = QGroupBox("👷 Eigenes Personal")
        own_group.setStyleSheet(self._group_style())
        own_layout = QVBoxLayout(own_group)
        
        # Toolbar
        own_toolbar = QHBoxLayout()
        add_own_btn = QPushButton("➕ Mitarbeiter hinzufügen")
        add_own_btn.setStyleSheet(get_button_style('primary'))
        add_own_btn.clicked.connect(self._add_own_personnel)
        own_toolbar.addWidget(add_own_btn)
        own_toolbar.addStretch()
        own_layout.addLayout(own_toolbar)
        
        self.own_personnel_table = QTableWidget()
        self.own_personnel_table.setColumnCount(7)
        self.own_personnel_table.setHorizontalHeaderLabels([
            "Mitarbeiter", "Funktion", "Von", "Bis", "Stunden", "Tätigkeit", "Aktionen"
        ])
        self.own_personnel_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.own_personnel_table.setStyleSheet(self._table_style())
        own_layout.addWidget(self.own_personnel_table)
        
        # Zusammenfassung
        own_summary = QHBoxLayout()
        own_summary.addWidget(QLabel("Gesamt:"))
        self.own_personnel_count = QLabel("0 Mitarbeiter")
        self.own_personnel_count.setStyleSheet("font-weight: bold;")
        own_summary.addWidget(self.own_personnel_count)
        own_summary.addWidget(QLabel("| Stunden:"))
        self.own_personnel_hours = QLabel("0.0 h")
        self.own_personnel_hours.setStyleSheet("font-weight: bold;")
        own_summary.addWidget(self.own_personnel_hours)
        own_summary.addStretch()
        own_layout.addLayout(own_summary)
        
        layout.addWidget(own_group)
        
        # Subunternehmer
        sub_group = QGroupBox("🏢 Subunternehmer / Nachunternehmer")
        sub_group.setStyleSheet(self._group_style())
        sub_layout = QVBoxLayout(sub_group)
        
        sub_toolbar = QHBoxLayout()
        add_sub_btn = QPushButton("➕ Subunternehmer hinzufügen")
        add_sub_btn.setStyleSheet(get_button_style('primary'))
        add_sub_btn.clicked.connect(self._add_subcontractor)
        sub_toolbar.addWidget(add_sub_btn)
        sub_toolbar.addStretch()
        sub_layout.addLayout(sub_toolbar)
        
        self.subcontractor_table = QTableWidget()
        self.subcontractor_table.setColumnCount(8)
        self.subcontractor_table.setHorizontalHeaderLabels([
            "Firma", "Gewerk", "Anzahl", "Von", "Bis", "Stunden", "Tätigkeit", "Aktionen"
        ])
        self.subcontractor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.subcontractor_table.setStyleSheet(self._table_style())
        sub_layout.addWidget(self.subcontractor_table)
        
        # Zusammenfassung
        sub_summary = QHBoxLayout()
        sub_summary.addWidget(QLabel("Gesamt:"))
        self.subcontractor_count = QLabel("0 Firmen / 0 Personen")
        self.subcontractor_count.setStyleSheet("font-weight: bold;")
        sub_summary.addWidget(self.subcontractor_count)
        sub_summary.addWidget(QLabel("| Stunden:"))
        self.subcontractor_hours = QLabel("0.0 h")
        self.subcontractor_hours.setStyleSheet("font-weight: bold;")
        sub_summary.addWidget(self.subcontractor_hours)
        sub_summary.addStretch()
        sub_layout.addLayout(sub_summary)
        
        layout.addWidget(sub_group)
        
        return tab
    
    def _create_progress_tab(self) -> QWidget:
        """Arbeitsfortschritt mit Fotos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Ausgeführte Arbeiten
        work_group = QGroupBox("📋 Ausgeführte Arbeiten")
        work_group.setStyleSheet(self._group_style())
        work_layout = QVBoxLayout(work_group)
        
        work_toolbar = QHBoxLayout()
        add_work_btn = QPushButton("➕ Arbeit hinzufügen")
        add_work_btn.setStyleSheet(get_button_style('primary'))
        add_work_btn.clicked.connect(self._add_work_item)
        work_toolbar.addWidget(add_work_btn)
        work_toolbar.addStretch()
        work_layout.addLayout(work_toolbar)
        
        self.work_table = QTableWidget()
        self.work_table.setColumnCount(7)
        self.work_table.setHorizontalHeaderLabels([
            "Bauabschnitt", "Gewerk", "Beschreibung", "Menge", "Einheit", "Fortschritt %", "Aktionen"
        ])
        self.work_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.work_table.setStyleSheet(self._table_style())
        work_layout.addWidget(self.work_table)
        
        layout.addWidget(work_group)
        
        # Fotos
        photos_group = QGroupBox("📸 Fotodokumentation")
        photos_group.setStyleSheet(self._group_style())
        photos_layout = QVBoxLayout(photos_group)
        
        photos_toolbar = QHBoxLayout()
        add_photo_btn = QPushButton("📷 Foto hinzufügen")
        add_photo_btn.setStyleSheet(get_button_style('primary'))
        add_photo_btn.clicked.connect(self._add_photo)
        photos_toolbar.addWidget(add_photo_btn)
        
        take_photo_btn = QPushButton("📱 Foto aufnehmen")
        take_photo_btn.setStyleSheet(get_button_style('secondary'))
        photos_toolbar.addWidget(take_photo_btn)
        photos_toolbar.addStretch()
        photos_layout.addLayout(photos_toolbar)
        
        self.photos_list = QListWidget()
        self.photos_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photos_list.setIconSize(QSize(120, 120))
        self.photos_list.setMinimumHeight(200)
        self.photos_list.setStyleSheet(f"""
            QListWidget {{
                border: 2px dashed {COLORS['gray_300']};
                border-radius: 8px;
                background: {COLORS['gray_50']};
            }}
        """)
        photos_layout.addWidget(self.photos_list)
        
        layout.addWidget(photos_group)
        
        # Tagesnotizen
        notes_group = QGroupBox("📝 Tagesnotizen zum Fortschritt")
        notes_group.setStyleSheet(self._group_style())
        notes_layout = QVBoxLayout(notes_group)
        
        self.progress_notes = QTextEdit()
        self.progress_notes.setPlaceholderText("Beschreibung der heute durchgeführten Arbeiten, Besonderheiten, Abweichungen vom Bauablaufplan...")
        self.progress_notes.setMinimumHeight(100)
        notes_layout.addWidget(self.progress_notes)
        
        layout.addWidget(notes_group)
        
        return tab
    
    def _create_material_tab(self) -> QWidget:
        """Material und Lieferungen"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Lieferungen
        delivery_group = QGroupBox("🚚 Lieferungen")
        delivery_group.setStyleSheet(self._group_style())
        delivery_layout = QVBoxLayout(delivery_group)
        
        delivery_toolbar = QHBoxLayout()
        add_delivery_btn = QPushButton("➕ Lieferung erfassen")
        add_delivery_btn.setStyleSheet(get_button_style('primary'))
        add_delivery_btn.clicked.connect(self._add_delivery)
        delivery_toolbar.addWidget(add_delivery_btn)
        delivery_toolbar.addStretch()
        delivery_layout.addLayout(delivery_toolbar)
        
        self.delivery_table = QTableWidget()
        self.delivery_table.setColumnCount(8)
        self.delivery_table.setHorizontalHeaderLabels([
            "Zeit", "Lieferant", "Material", "Menge", "Einheit", "Lieferschein-Nr.", "Angenommen von", "Aktionen"
        ])
        self.delivery_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.delivery_table.setStyleSheet(self._table_style())
        delivery_layout.addWidget(self.delivery_table)
        
        layout.addWidget(delivery_group)
        
        # Materialeinsatz
        material_group = QGroupBox("📦 Materialeinsatz / -verbrauch")
        material_group.setStyleSheet(self._group_style())
        material_layout = QVBoxLayout(material_group)
        
        material_toolbar = QHBoxLayout()
        add_material_btn = QPushButton("➕ Material erfassen")
        add_material_btn.setStyleSheet(get_button_style('primary'))
        add_material_btn.clicked.connect(self._add_material_usage)
        material_toolbar.addWidget(add_material_btn)
        material_toolbar.addStretch()
        material_layout.addLayout(material_toolbar)
        
        self.material_table = QTableWidget()
        self.material_table.setColumnCount(7)
        self.material_table.setHorizontalHeaderLabels([
            "Material", "Artikel-Nr.", "Menge", "Einheit", "Verwendung", "Bauabschnitt", "Aktionen"
        ])
        self.material_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.material_table.setStyleSheet(self._table_style())
        material_layout.addWidget(self.material_table)
        
        layout.addWidget(material_group)
        
        # Geräte-/Maschineneinsatz
        equipment_group = QGroupBox("🔧 Geräte- und Maschineneinsatz")
        equipment_group.setStyleSheet(self._group_style())
        equipment_layout = QVBoxLayout(equipment_group)
        
        equipment_toolbar = QHBoxLayout()
        add_equipment_btn = QPushButton("➕ Gerät erfassen")
        add_equipment_btn.setStyleSheet(get_button_style('primary'))
        add_equipment_btn.clicked.connect(self._add_equipment_usage)
        equipment_toolbar.addWidget(add_equipment_btn)
        equipment_toolbar.addStretch()
        equipment_layout.addLayout(equipment_toolbar)
        
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(7)
        self.equipment_table.setHorizontalHeaderLabels([
            "Gerät/Maschine", "Kennzeichen", "Einsatzzeit", "Betriebsstunden", "Tätigkeit", "Fahrer/Bediener", "Aktionen"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.equipment_table.setStyleSheet(self._table_style())
        equipment_layout.addWidget(self.equipment_table)
        
        layout.addWidget(equipment_group)
        
        return tab
    
    def _create_visitors_tab(self) -> QWidget:
        """Besucher und Besprechungen"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Besucher
        visitors_group = QGroupBox("👥 Besucher auf der Baustelle")
        visitors_group.setStyleSheet(self._group_style())
        visitors_layout = QVBoxLayout(visitors_group)
        
        visitors_toolbar = QHBoxLayout()
        add_visitor_btn = QPushButton("➕ Besucher erfassen")
        add_visitor_btn.setStyleSheet(get_button_style('primary'))
        add_visitor_btn.clicked.connect(self._add_visitor)
        visitors_toolbar.addWidget(add_visitor_btn)
        visitors_toolbar.addStretch()
        visitors_layout.addLayout(visitors_toolbar)
        
        self.visitors_table = QTableWidget()
        self.visitors_table.setColumnCount(7)
        self.visitors_table.setHorizontalHeaderLabels([
            "Name", "Firma/Funktion", "Ankunft", "Abgang", "Grund des Besuchs", "Unterwiesen", "Aktionen"
        ])
        self.visitors_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.visitors_table.setStyleSheet(self._table_style())
        visitors_layout.addWidget(self.visitors_table)
        
        layout.addWidget(visitors_group)
        
        # Besprechungen
        meetings_group = QGroupBox("🤝 Besprechungen / Baubesprechungen")
        meetings_group.setStyleSheet(self._group_style())
        meetings_layout = QVBoxLayout(meetings_group)
        
        meetings_toolbar = QHBoxLayout()
        add_meeting_btn = QPushButton("➕ Besprechung erfassen")
        add_meeting_btn.setStyleSheet(get_button_style('primary'))
        add_meeting_btn.clicked.connect(self._add_meeting)
        meetings_toolbar.addWidget(add_meeting_btn)
        meetings_toolbar.addStretch()
        meetings_layout.addLayout(meetings_toolbar)
        
        self.meetings_table = QTableWidget()
        self.meetings_table.setColumnCount(6)
        self.meetings_table.setHorizontalHeaderLabels([
            "Zeit", "Thema", "Teilnehmer", "Ergebnisse/Beschlüsse", "Protokoll", "Aktionen"
        ])
        self.meetings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.meetings_table.setStyleSheet(self._table_style())
        meetings_layout.addWidget(self.meetings_table)
        
        layout.addWidget(meetings_group)
        
        # Behördliche Kontrollen
        inspections_group = QGroupBox("🏛️ Behördliche Kontrollen / Prüfungen")
        inspections_group.setStyleSheet(self._group_style())
        inspections_layout = QVBoxLayout(inspections_group)
        
        inspections_toolbar = QHBoxLayout()
        add_inspection_btn = QPushButton("➕ Kontrolle erfassen")
        add_inspection_btn.setStyleSheet(get_button_style('primary'))
        add_inspection_btn.clicked.connect(self._add_inspection)
        inspections_toolbar.addWidget(add_inspection_btn)
        inspections_toolbar.addStretch()
        inspections_layout.addLayout(inspections_toolbar)
        
        self.inspections_table = QTableWidget()
        self.inspections_table.setColumnCount(6)
        self.inspections_table.setHorizontalHeaderLabels([
            "Behörde/Prüfer", "Art der Prüfung", "Ergebnis", "Auflagen", "Frist", "Aktionen"
        ])
        self.inspections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inspections_table.setStyleSheet(self._table_style())
        inspections_layout.addWidget(self.inspections_table)
        
        layout.addWidget(inspections_group)
        
        return tab
    
    def _create_incidents_tab(self) -> QWidget:
        """Vorkommnisse und Verzögerungen"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Vorkommnisse
        incidents_group = QGroupBox("⚠️ Besondere Vorkommnisse")
        incidents_group.setStyleSheet(self._group_style())
        incidents_layout = QVBoxLayout(incidents_group)
        
        incidents_toolbar = QHBoxLayout()
        add_incident_btn = QPushButton("➕ Vorkommnis melden")
        add_incident_btn.setStyleSheet(get_button_style('danger'))
        add_incident_btn.clicked.connect(self._add_incident)
        incidents_toolbar.addWidget(add_incident_btn)
        incidents_toolbar.addStretch()
        incidents_layout.addLayout(incidents_toolbar)
        
        self.incidents_table = QTableWidget()
        self.incidents_table.setColumnCount(7)
        self.incidents_table.setHorizontalHeaderLabels([
            "Zeit", "Art", "Schwere", "Beschreibung", "Maßnahmen", "Fotos", "Aktionen"
        ])
        self.incidents_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.incidents_table.setStyleSheet(self._table_style())
        incidents_layout.addWidget(self.incidents_table)
        
        layout.addWidget(incidents_group)
        
        # Unfälle
        accidents_group = QGroupBox("🚨 Arbeitsunfälle")
        accidents_group.setStyleSheet(self._group_style())
        accidents_layout = QVBoxLayout(accidents_group)
        
        accidents_toolbar = QHBoxLayout()
        add_accident_btn = QPushButton("➕ Unfall melden")
        add_accident_btn.setStyleSheet(get_button_style('danger'))
        add_accident_btn.clicked.connect(self._add_accident)
        accidents_toolbar.addWidget(add_accident_btn)
        accidents_toolbar.addStretch()
        accidents_layout.addLayout(accidents_toolbar)
        
        self.accidents_table = QTableWidget()
        self.accidents_table.setColumnCount(8)
        self.accidents_table.setHorizontalHeaderLabels([
            "Zeit", "Person", "Art der Verletzung", "Hergang", "Erste Hilfe", "BG gemeldet", "Arztbesuch", "Aktionen"
        ])
        self.accidents_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.accidents_table.setStyleSheet(self._table_style())
        accidents_layout.addWidget(self.accidents_table)
        
        layout.addWidget(accidents_group)
        
        # Verzögerungen
        delays_group = QGroupBox("⏱️ Verzögerungen / Behinderungen")
        delays_group.setStyleSheet(self._group_style())
        delays_layout = QVBoxLayout(delays_group)
        
        delays_toolbar = QHBoxLayout()
        add_delay_btn = QPushButton("➕ Verzögerung melden")
        add_delay_btn.setStyleSheet(get_button_style('warning'))
        add_delay_btn.clicked.connect(self._add_delay)
        delays_toolbar.addWidget(add_delay_btn)
        delays_toolbar.addStretch()
        delays_layout.addLayout(delays_toolbar)
        
        self.delays_table = QTableWidget()
        self.delays_table.setColumnCount(7)
        self.delays_table.setHorizontalHeaderLabels([
            "Bauabschnitt", "Ursache", "Verantwortlich", "Dauer", "Auswirkung", "Behinderungsanzeige", "Aktionen"
        ])
        self.delays_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.delays_table.setStyleSheet(self._table_style())
        delays_layout.addWidget(self.delays_table)
        
        layout.addWidget(delays_group)
        
        return tab
    
    def _create_signatures_tab(self) -> QWidget:
        """Digitale Unterschriften"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Bauleiter
        site_manager_group = QGroupBox("👷 Bauleiter")
        site_manager_group.setStyleSheet(self._group_style())
        sm_layout = QFormLayout(site_manager_group)
        
        self.site_manager_name = QLineEdit()
        sm_layout.addRow("Name:", self.site_manager_name)
        
        self.site_manager_date = QDateEdit()
        self.site_manager_date.setDate(QDate.currentDate())
        self.site_manager_date.setCalendarPopup(True)
        sm_layout.addRow("Datum:", self.site_manager_date)
        
        signature_frame = QFrame()
        signature_frame.setFixedHeight(100)
        signature_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['gray_300']};
                border-radius: 8px;
                background: {COLORS['gray_50']};
            }}
        """)
        signature_layout = QVBoxLayout(signature_frame)
        signature_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sign_label = QLabel("✍️ Hier klicken zum Unterschreiben")
        sign_label.setStyleSheet(f"color: {COLORS['gray_400']};")
        signature_layout.addWidget(sign_label)
        sm_layout.addRow("Unterschrift:", signature_frame)
        
        layout.addWidget(site_manager_group)
        
        # Auftraggeber
        client_group = QGroupBox("🏢 Auftraggeber / Bauherr")
        client_group.setStyleSheet(self._group_style())
        client_layout = QFormLayout(client_group)
        
        self.client_name = QLineEdit()
        client_layout.addRow("Name:", self.client_name)
        
        self.client_date = QDateEdit()
        self.client_date.setDate(QDate.currentDate())
        self.client_date.setCalendarPopup(True)
        client_layout.addRow("Datum:", self.client_date)
        
        client_signature_frame = QFrame()
        client_signature_frame.setFixedHeight(100)
        client_signature_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['gray_300']};
                border-radius: 8px;
                background: {COLORS['gray_50']};
            }}
        """)
        client_signature_layout = QVBoxLayout(client_signature_frame)
        client_signature_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        client_sign_label = QLabel("✍️ Hier klicken zum Unterschreiben")
        client_sign_label.setStyleSheet(f"color: {COLORS['gray_400']};")
        client_signature_layout.addWidget(client_sign_label)
        client_layout.addRow("Unterschrift:", client_signature_frame)
        
        layout.addWidget(client_group)
        
        # Hinweise
        hints_frame = QFrame()
        hints_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['warning']}20;
                border: 1px solid {COLORS['warning']};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        hints_layout = QVBoxLayout(hints_frame)
        hints_label = QLabel("ℹ️ Hinweis: Mit der digitalen Unterschrift bestätigen Sie die Richtigkeit und Vollständigkeit der Angaben im Bautagebuch.")
        hints_label.setWordWrap(True)
        hints_layout.addWidget(hints_label)
        layout.addWidget(hints_frame)
        
        layout.addStretch()
        
        return tab
    
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
    
    def _table_style(self) -> str:
        return f"""
            QTableWidget {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                gridline-color: {COLORS['gray_100']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background: {COLORS['gray_50']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {COLORS['gray_200']};
                font-weight: bold;
            }}
        """
    
    # Event handlers
    def _on_project_changed(self, index):
        """Wird aufgerufen wenn ein Projekt ausgewählt wird"""
        project_id = self.project_combo.currentData()
        if project_id:
            self.current_project = uuid.UUID(project_id)
            self.current_entry = None
            self._load_entries()
        else:
            self.current_project = None
            self.entry_tree.clear()
    
    def _filter_entries(self, text):
        """Filtert Einträge nach Suchtext"""
        for i in range(self.entry_tree.topLevelItemCount()):
            item = self.entry_tree.topLevelItem(i)
            if item:
                visible = text.lower() in item.text(0).lower() or text.lower() in item.text(1).lower()
                item.setHidden(not visible)
    
    def _on_entry_selected(self, item):
        """Lädt einen ausgewählten Eintrag"""
        entry_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not entry_id:
            return
        
        session = self.db_service.get_session()
        try:
            diary = session.get(ConstructionDiary, uuid.UUID(entry_id))
            if diary:
                self.current_entry = diary.id
                self.entry_number.setText(diary.diary_number or "")
                
                if diary.diary_date:
                    self.entry_date.setDate(QDate(diary.diary_date.year, diary.diary_date.month, diary.diary_date.day))
                
                if diary.work_start_time:
                    self.work_start.setTime(QTime(diary.work_start_time.hour, diary.work_start_time.minute))
                if diary.work_end_time:
                    self.work_end.setTime(QTime(diary.work_end_time.hour, diary.work_end_time.minute))
                
                self.break_duration.setValue(diary.break_duration_minutes or 0)
                self.workable.setChecked(diary.work_possible if diary.work_possible is not None else True)
                
                self.progress_notes.setPlainText(diary.work_performed or "")
                self.site_manager_name.setText(diary.site_manager_signature or "")
                
                status_map = {"draft": 0, "submitted": 1, "approved": 2}
                self.entry_status.setCurrentIndex(status_map.get(diary.status, 0))
        finally:
            session.close()
    
    def _new_entry(self):
        """Erstellt einen neuen Bautagebuch-Eintrag"""
        if not self.current_project:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        
        self.current_entry = None
        self.entry_number.setText("")
        self.entry_date.setDate(QDate.currentDate())
        self.work_start.setTime(QTime(7, 0))
        self.work_end.setTime(QTime(16, 30))
        self.break_duration.setValue(30)
        self.workable.setChecked(True)
        self.progress_notes.clear()
        self.site_manager_name.clear()
        self.entry_status.setCurrentIndex(0)
        
        QMessageBox.information(self, "Neuer Eintrag", "Neuer Bautagebuch-Eintrag wurde vorbereitet. Füllen Sie die Felder aus und klicken Sie auf Speichern.")
    
    def _export_pdf(self):
        """Exportiert das Bautagebuch als PDF"""
        if not self.current_project:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        from shared.services.export_service import ExportService
        
        # Datei-Dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern",
            f"Bautagebuch_{self.current_project.project_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Dateien (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            # Einträge laden
            session = self.db_service.get_session()
            entries = session.execute(
                select(ConstructionDiary)
                .where(ConstructionDiary.project_id == self.current_project.id)
                .where(ConstructionDiary.is_deleted == False)
                .order_by(ConstructionDiary.entry_date.desc())
            ).scalars().all()
            session.close()
            
            # Export
            ExportService.export_construction_diary_pdf(
                entries=entries,
                project_name=f"{self.current_project.project_number} - {self.current_project.name}",
                filename=filename
            )
            
            QMessageBox.information(self, "Erfolg", f"PDF wurde erstellt:\n{filename}")
            
            # PDF öffnen
            import os
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Export fehlgeschlagen: {e}")
    
    def _save_entry(self):
        """Speichert den Bautagebuch-Eintrag in die Datenbank"""
        if not self.current_project:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        
        session = self.db_service.get_session()
        try:
            # Neuen Eintrag erstellen oder bestehenden bearbeiten
            if self.current_entry:
                diary = session.get(ConstructionDiary, self.current_entry)
            else:
                diary = ConstructionDiary()
                diary.id = uuid.uuid4()
                # Generiere Tagebuchnummer
                from sqlalchemy import func
                count = session.execute(select(func.count(ConstructionDiary.id))).scalar() or 0
                diary.diary_number = f"BT{datetime.now().year}{count + 1:05d}"
                diary.project_id = self.current_project
                if self.user and hasattr(self.user, 'tenant_id'):
                    diary.tenant_id = self.user.tenant_id
            
            # Datum
            diary.diary_date = self.entry_date.date().toPyDate()
            diary.calendar_week = diary.diary_date.isocalendar()[1]
            
            # Arbeitszeiten
            diary.work_start_time = self.work_start.time().toPyTime()
            diary.work_end_time = self.work_end.time().toPyTime()
            diary.break_duration_minutes = self.break_duration.value()
            diary.work_possible = self.workable.isChecked()
            
            # Wetter-Mapping
            weather_map = {
                "Sonnig": WeatherCondition.SUNNY,
                "Leicht bewölkt": WeatherCondition.PARTLY_CLOUDY,
                "Bewölkt": WeatherCondition.CLOUDY,
                "Stark bewölkt": WeatherCondition.OVERCAST,
                "Nebel": WeatherCondition.FOG,
                "Leichter Regen": WeatherCondition.LIGHT_RAIN,
                "Regen": WeatherCondition.RAIN,
                "Starkregen": WeatherCondition.HEAVY_RAIN,
                "Gewitter": WeatherCondition.THUNDERSTORM,
                "Schneefall": WeatherCondition.SNOW,
                "Hagel": WeatherCondition.HAIL,
                "Frost": WeatherCondition.FROST,
            }
            
            # Wetter morgens
            morning_condition = self.weather_morning_condition.currentText()
            diary.weather_morning = weather_map.get(morning_condition)
            diary.temperature_morning = str(self.weather_morning_temp.value()) if self.weather_morning_temp.value() != 0 else None
            
            # Wetter nachmittags
            noon_condition = self.weather_noon_condition.currentText()
            diary.weather_afternoon = weather_map.get(noon_condition)
            diary.temperature_afternoon = str(self.weather_noon_temp.value()) if self.weather_noon_temp.value() != 0 else None
            
            # Personal
            diary.own_workers_count = self.own_personnel_table.rowCount()
            diary.subcontractor_workers_count = self.subcontractor_table.rowCount()
            diary.total_workers = diary.own_workers_count + diary.subcontractor_workers_count
            
            # Arbeitsfortschritt (Notizen)
            diary.work_performed = self.progress_notes.toPlainText().strip() or None
            
            # Status
            status_map = {"Entwurf": "draft", "Abgeschlossen": "submitted", "Geprüft": "approved", "Freigegeben": "approved"}
            diary.status = status_map.get(self.entry_status.currentText(), "draft")
            
            # Unterschriften
            diary.site_manager_signature = self.site_manager_name.text().strip() or None
            if diary.site_manager_signature:
                diary.site_manager_signed_at = datetime.now()
            
            if not self.current_entry:
                session.add(diary)
            
            session.commit()
            self.current_entry = diary.id
            self.entry_number.setText(diary.diary_number)
            QMessageBox.information(self, "Gespeichert", "Bautagebuch-Eintrag wurde erfolgreich gespeichert.")
            self._load_entries()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
    
    def _add_own_personnel(self):
        pass
    
    def _add_subcontractor(self):
        pass
    
    def _add_work_item(self):
        pass
    
    def _add_photo(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Fotos auswählen", "", "Bilder (*.png *.jpg *.jpeg *.bmp)")
        if files:
            for file in files:
                item = QListWidgetItem(file.split("/")[-1])
                self.photos_list.addItem(item)
    
    def _add_delivery(self):
        pass
    
    def _add_material_usage(self):
        pass
    
    def _add_equipment_usage(self):
        pass
    
    def _add_visitor(self):
        pass
    
    def _add_meeting(self):
        pass
    
    def _add_inspection(self):
        pass
    
    def _add_incident(self):
        pass
    
    def _add_accident(self):
        pass
    
    def _add_delay(self):
        pass
    
    def refresh(self):
        """Refresh data - Lädt Projekte und Einträge"""
        self._load_projects()
        if self.current_project:
            self._load_entries()
    
    def _load_projects(self):
        """Lädt alle Projekte in die Combobox"""
        session = self.db_service.get_session()
        try:
            self.project_combo.clear()
            self.project_combo.addItem("-- Projekt wählen --", None)
            
            query = select(Project).where(Project.is_deleted == False).order_by(Project.project_number.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Project.tenant_id == self.user.tenant_id)
            
            projects = session.execute(query).scalars().all()
            for p in projects:
                self.project_combo.addItem(f"{p.project_number} - {p.name}", str(p.id))
        finally:
            session.close()
    
    def _load_entries(self):
        """Lädt alle Bautagebuch-Einträge für das aktuelle Projekt"""
        if not self.current_project:
            return
        
        session = self.db_service.get_session()
        try:
            self.entry_tree.clear()
            
            query = select(ConstructionDiary).where(
                ConstructionDiary.project_id == self.current_project,
                ConstructionDiary.is_deleted == False
            ).order_by(ConstructionDiary.diary_date.desc())
            
            entries = session.execute(query).scalars().all()
            
            status_names = {"draft": "Entwurf", "submitted": "Abgeschlossen", "approved": "Freigegeben"}
            
            for entry in entries:
                item = QTreeWidgetItem([
                    entry.diary_date.strftime("%d.%m.%Y") if entry.diary_date else "",
                    status_names.get(entry.status, entry.status or "")
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, str(entry.id))
                self.entry_tree.addTopLevelItem(item)
        finally:
            session.close()
