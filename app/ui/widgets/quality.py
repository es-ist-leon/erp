"""
Qualitätskontrolle Widget - Quality Management
Mängelmanagement, Prüfungen, Zertifikate, Gewährleistung
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QFrame, QDialog, QFormLayout,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTimeEdit, QTabWidget, QScrollArea, QGroupBox, QCheckBox,
    QFileDialog, QListWidget, QListWidgetItem, QMessageBox,
    QHeaderView, QSplitter, QTreeWidget, QTreeWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, QDate, QTime, QSize, QByteArray
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon, QImage
from datetime import datetime, date
import uuid

from sqlalchemy import select, func
from app.ui.styles import COLORS, get_button_style, CARD_STYLE
from shared.models import (
    Defect, DefectSeverity, DefectStatus, QualityCheck, QualityCheckType,
    Warranty, Certificate, Project, Customer
)


class QualityWidget(QWidget):
    """Qualitätskontrolle und -management"""
    
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
        self.tabs.addTab(self._create_defects_tab(), "⚠️ Mängelmanagement")
        self.tabs.addTab(self._create_inspections_tab(), "🔍 Qualitätsprüfungen")
        self.tabs.addTab(self._create_checklists_tab(), "📋 Prüfpläne")
        self.tabs.addTab(self._create_warranty_tab(), "🛡️ Gewährleistung")
        self.tabs.addTab(self._create_certificates_tab(), "📜 Zertifikate")
        self.tabs.addTab(self._create_reports_tab(), "📊 Auswertungen")
        
        layout.addWidget(self.tabs)
    
    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet(CARD_STYLE)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        title = QLabel("✅ Qualitätskontrolle")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick stats
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(24)
        
        for label, value, color in [
            ("Offene Mängel", "8", COLORS['danger']),
            ("In Bearbeitung", "5", COLORS['warning']),
            ("Prüfungen heute", "3", COLORS['primary']),
            ("Gewährleistungen", "12", COLORS['info'])
        ]:
            stat = QVBoxLayout()
            stat_value = QLabel(value)
            stat_value.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
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
    
    def _create_defects_tab(self) -> QWidget:
        """Mängelmanagement mit Fotos vorher/nachher"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Left: Defects list
        left_panel = QFrame()
        left_panel.setStyleSheet(CARD_STYLE)
        left_layout = QVBoxLayout(left_panel)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Mangel suchen...")
        search.setMaximumWidth(250)
        toolbar.addWidget(search)
        
        project_combo = QComboBox()
        project_combo.addItems(["Alle Projekte"])
        toolbar.addWidget(project_combo)
        
        status_combo = QComboBox()
        status_combo.addItems(["Alle Status", "Offen", "In Bearbeitung", "Behoben", "Abgenommen", "Abgelehnt"])
        toolbar.addWidget(status_combo)
        
        severity_combo = QComboBox()
        severity_combo.addItems(["Alle Schweregrade", "Kritisch", "Schwer", "Mittel", "Leicht"])
        toolbar.addWidget(severity_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Mangel melden")
        add_btn.setStyleSheet(get_button_style('danger'))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_defect)
        toolbar.addWidget(add_btn)
        
        left_layout.addLayout(toolbar)
        
        # Defects table
        self.defects_table = QTableWidget()
        self.defects_table.setColumnCount(10)
        self.defects_table.setHorizontalHeaderLabels([
            "Nr.", "Projekt", "Bauabschnitt", "Beschreibung", "Schwere",
            "Status", "Verantwortlich", "Frist", "Kosten", "Aktionen"
        ])
        self.defects_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.defects_table.setStyleSheet(self._table_style())
        self.defects_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.defects_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.defects_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.defects_table.cellClicked.connect(self._on_defect_row_clicked)
        left_layout.addWidget(self.defects_table)
        
        layout.addWidget(left_panel, 2)
        
        # Right: Defect details
        right_panel = QFrame()
        right_panel.setStyleSheet(CARD_STYLE)
        right_panel.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("📋 Mangeldetails"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        # Basic info
        info_group = QGroupBox("Grunddaten")
        info_group.setStyleSheet(self._group_style())
        info_layout = QFormLayout(info_group)
        
        self.defect_number = QLabel("---")
        info_layout.addRow("Mangel-Nr.:", self.defect_number)
        
        self.defect_project = QLabel("---")
        info_layout.addRow("Projekt:", self.defect_project)
        
        self.defect_location = QLabel("---")
        info_layout.addRow("Ort/Bauabschnitt:", self.defect_location)
        
        self.defect_category = QLabel("---")
        info_layout.addRow("Kategorie:", self.defect_category)
        
        self.defect_severity = QLabel("---")
        info_layout.addRow("Schweregrad:", self.defect_severity)
        
        detail_layout.addWidget(info_group)
        
        # Description
        desc_group = QGroupBox("Beschreibung")
        desc_group.setStyleSheet(self._group_style())
        desc_layout = QVBoxLayout(desc_group)
        
        self.defect_description = QTextEdit()
        self.defect_description.setReadOnly(True)
        self.defect_description.setMaximumHeight(80)
        desc_layout.addWidget(self.defect_description)
        
        detail_layout.addWidget(desc_group)
        
        # Photos before/after - mit Thumbnails
        photos_group = QGroupBox("📸 Fotos")
        photos_group.setStyleSheet(self._group_style())
        photos_layout = QHBoxLayout(photos_group)
        
        # Before
        before_frame = QFrame()
        before_layout = QVBoxLayout(before_frame)
        before_layout.addWidget(QLabel("Vorher:"))
        
        self.photos_before_list = QListWidget()
        self.photos_before_list.setMaximumHeight(140)
        self.photos_before_list.setIconSize(QSize(80, 80))
        self.photos_before_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photos_before_list.setFlow(QListWidget.Flow.LeftToRight)
        self.photos_before_list.setWrapping(True)
        self.photos_before_list.setSpacing(4)
        self.photos_before_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 4px;
                background: {COLORS['gray_50']};
            }}
            QListWidget::item {{
                padding: 4px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['primary']}20;
            }}
        """)
        self.photos_before_list.itemDoubleClicked.connect(lambda item: self._show_photo_fullscreen(item, "before"))
        before_layout.addWidget(self.photos_before_list)
        photos_layout.addWidget(before_frame)
        
        # After
        after_frame = QFrame()
        after_layout = QVBoxLayout(after_frame)
        after_layout.addWidget(QLabel("Nachher:"))
        
        self.photos_after_list = QListWidget()
        self.photos_after_list.setMaximumHeight(140)
        self.photos_after_list.setIconSize(QSize(80, 80))
        self.photos_after_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photos_after_list.setFlow(QListWidget.Flow.LeftToRight)
        self.photos_after_list.setWrapping(True)
        self.photos_after_list.setSpacing(4)
        self.photos_after_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 4px;
                background: {COLORS['gray_50']};
            }}
            QListWidget::item {{
                padding: 4px;
            }}
            QListWidget::item:hover {{
                background: {COLORS['primary']}20;
            }}
        """)
        self.photos_after_list.itemDoubleClicked.connect(lambda item: self._show_photo_fullscreen(item, "after"))
        after_layout.addWidget(self.photos_after_list)
        photos_layout.addWidget(after_frame)
        
        detail_layout.addWidget(photos_group)
        
        # Costs
        costs_group = QGroupBox("💰 Kosten & Rückforderung")
        costs_group.setStyleSheet(self._group_style())
        costs_layout = QFormLayout(costs_group)
        
        self.defect_cost_material = QLabel("€ 0,00")
        costs_layout.addRow("Materialkosten:", self.defect_cost_material)
        
        self.defect_cost_labor = QLabel("€ 0,00")
        costs_layout.addRow("Arbeitskosten:", self.defect_cost_labor)
        
        self.defect_cost_total = QLabel("€ 0,00")
        self.defect_cost_total.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        costs_layout.addRow("Gesamtkosten:", self.defect_cost_total)
        
        self.defect_chargeback = QComboBox()
        self.defect_chargeback.addItems(["Keine Rückforderung", "Subunternehmer", "Lieferant", "Bauherr"])
        costs_layout.addRow("Rückforderung an:", self.defect_chargeback)
        
        self.defect_chargeback_status = QLabel("---")
        costs_layout.addRow("Status:", self.defect_chargeback_status)
        
        detail_layout.addWidget(costs_group)
        
        # Status & Assignment
        status_group = QGroupBox("📌 Status & Zuweisung")
        status_group.setStyleSheet(self._group_style())
        status_layout = QFormLayout(status_group)
        
        self.defect_status_combo = QComboBox()
        self.defect_status_combo.addItems(["Offen", "In Bearbeitung", "Behoben", "Zur Abnahme", "Abgenommen", "Abgelehnt"])
        status_layout.addRow("Status:", self.defect_status_combo)
        
        self.defect_assignee = QComboBox()
        self.defect_assignee.addItems(["--- Zuweisen ---"])
        status_layout.addRow("Zuständig:", self.defect_assignee)
        
        self.defect_deadline = QDateEdit()
        self.defect_deadline.setCalendarPopup(True)
        status_layout.addRow("Frist:", self.defect_deadline)
        
        detail_layout.addWidget(status_group)
        
        detail_layout.addStretch()
        scroll.setWidget(detail_widget)
        right_layout.addWidget(scroll)
        
        # Save button
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self._save_defect_changes)
        right_layout.addWidget(save_btn)
        
        layout.addWidget(right_panel)
        
        # Initialisierung
        self._selected_defect_id = None
        
        return tab
    
    def _create_inspections_tab(self) -> QWidget:
        """Qualitätsprüfungen mit Messwerten"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Prüfung suchen...")
        search.setMaximumWidth(250)
        toolbar.addWidget(search)
        
        project_combo = QComboBox()
        project_combo.addItems(["Alle Projekte"])
        toolbar.addWidget(project_combo)
        
        type_combo = QComboBox()
        type_combo.addItems([
            "Alle Prüfungen", "Materialprüfung", "Maßprüfung", "Oberflächenprüfung",
            "Feuchtemessung", "Statikprüfung", "Brandschutzprüfung", "Schallschutzprüfung"
        ])
        toolbar.addWidget(type_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neue Prüfung")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_inspection)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Inspections table
        self.inspections_table = QTableWidget()
        self.inspections_table.setColumnCount(10)
        self.inspections_table.setHorizontalHeaderLabels([
            "Datum", "Projekt", "Prüfart", "Bauabschnitt", "Prüfer",
            "Ergebnis", "Messwerte", "Abweichungen", "Status", "Aktionen"
        ])
        self.inspections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inspections_table.setStyleSheet(self._table_style())
        layout.addWidget(self.inspections_table)
        
        # Measurement values section
        measurements_group = QGroupBox("📏 Messwerte der ausgewählten Prüfung")
        measurements_group.setStyleSheet(self._group_style())
        measurements_layout = QVBoxLayout(measurements_group)
        
        self.measurements_table = QTableWidget()
        self.measurements_table.setColumnCount(7)
        self.measurements_table.setHorizontalHeaderLabels([
            "Messpunkt", "Parameter", "Sollwert", "Istwert", "Einheit", "Toleranz", "Bewertung"
        ])
        self.measurements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.measurements_table.setStyleSheet(self._table_style())
        self.measurements_table.setMaximumHeight(200)
        measurements_layout.addWidget(self.measurements_table)
        
        layout.addWidget(measurements_group)
        
        return tab
    
    def _create_checklists_tab(self) -> QWidget:
        """Prüfplan-Vorlagen"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Left: Checklist templates
        left_panel = QFrame()
        left_panel.setStyleSheet(CARD_STYLE)
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("📋 Prüfplan-Vorlagen"))
        
        toolbar = QHBoxLayout()
        add_template_btn = QPushButton("➕ Neue Vorlage")
        add_template_btn.setStyleSheet(get_button_style('primary'))
        add_template_btn.clicked.connect(self._add_checklist_template)
        toolbar.addWidget(add_template_btn)
        toolbar.addStretch()
        left_layout.addLayout(toolbar)
        
        self.templates_list = QListWidget()
        self.templates_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['gray_100']};
            }}
            QListWidget::item:hover {{
                background: {COLORS['gray_50']};
            }}
            QListWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        self.templates_list.itemClicked.connect(self._on_template_selected)
        
        # Vorlagen-Daten (später aus DB)
        self._checklist_templates = {
            "holzrahmen_wand": {
                "name": "Holzrahmenbau - Wandaufbau",
                "icon": "🏠",
                "category": "Holzbau",
                "description": "Prüfung des Wandaufbaus nach Holzrahmenbaurichtlinie",
                "items": [
                    {"nr": 1, "punkt": "Schwellenholz auf Feuchtigkeit prüfen", "methode": "Messgerät", "soll": "< 20%", "toleranz": "± 2%", "pflicht": True},
                    {"nr": 2, "punkt": "Ständerabstand kontrollieren", "methode": "Messen", "soll": "62,5 cm", "toleranz": "± 2 mm", "pflicht": True},
                    {"nr": 3, "punkt": "Dämmung vollflächig eingebaut", "methode": "Sichtkontrolle", "soll": "100%", "toleranz": "-", "pflicht": True},
                    {"nr": 4, "punkt": "Dampfbremse luftdicht verklebt", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                    {"nr": 5, "punkt": "Installationsebene vorhanden", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": False},
                ]
            },
            "holzbalken_boden": {
                "name": "Holzbalkenboden - Prüfung",
                "icon": "🪵",
                "category": "Holzbau",
                "description": "Prüfung von Holzbalkendecken",
                "items": [
                    {"nr": 1, "punkt": "Balkenquerschnitt prüfen", "methode": "Messen", "soll": "lt. Statik", "toleranz": "± 5 mm", "pflicht": True},
                    {"nr": 2, "punkt": "Balkenabstand kontrollieren", "methode": "Messen", "soll": "lt. Plan", "toleranz": "± 10 mm", "pflicht": True},
                    {"nr": 3, "punkt": "Auflagertiefe prüfen", "methode": "Messen", "soll": "≥ 10 cm", "toleranz": "-", "pflicht": True},
                    {"nr": 4, "punkt": "Holzfeuchte messen", "methode": "Messgerät", "soll": "< 18%", "toleranz": "± 2%", "pflicht": True},
                ]
            },
            "dachstuhl": {
                "name": "Dachstuhl - Abbundkontrolle",
                "icon": "🏗️",
                "category": "Holzbau",
                "description": "Kontrolle des Dachstuhl-Abbunds",
                "items": [
                    {"nr": 1, "punkt": "Sparrenquerschnitt", "methode": "Messen", "soll": "lt. Statik", "toleranz": "± 3 mm", "pflicht": True},
                    {"nr": 2, "punkt": "Sparrenabstand", "methode": "Messen", "soll": "lt. Plan", "toleranz": "± 10 mm", "pflicht": True},
                    {"nr": 3, "punkt": "Dachneigung", "methode": "Winkelmesser", "soll": "lt. Plan", "toleranz": "± 0,5°", "pflicht": True},
                    {"nr": 4, "punkt": "Verbindungsmittel korrekt", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                    {"nr": 5, "punkt": "First gerade", "methode": "Schnur/Laser", "soll": "Ja", "toleranz": "± 5 mm", "pflicht": True},
                ]
            },
            "verbindungsmittel": {
                "name": "Verbindungsmittel - Prüfung",
                "icon": "🔩",
                "category": "Statik",
                "description": "Prüfung der Verbindungsmittel nach EC5",
                "items": [
                    {"nr": 1, "punkt": "Nageltyp korrekt", "methode": "Sichtkontrolle", "soll": "lt. Statik", "toleranz": "-", "pflicht": True},
                    {"nr": 2, "punkt": "Nagelanzahl", "methode": "Zählen", "soll": "lt. Statik", "toleranz": "-", "pflicht": True},
                    {"nr": 3, "punkt": "Randabstände eingehalten", "methode": "Messen", "soll": "lt. EC5", "toleranz": "-", "pflicht": True},
                    {"nr": 4, "punkt": "Schraubeneinschraubtiefe", "methode": "Messen", "soll": "lt. Zulassung", "toleranz": "-", "pflicht": True},
                ]
            },
            "feuchte": {
                "name": "Feuchtemessung - Holz",
                "icon": "💧",
                "category": "Holzbau",
                "description": "Holzfeuchtemessung nach DIN",
                "items": [
                    {"nr": 1, "punkt": "Konstruktionsholz KVH", "methode": "Messgerät", "soll": "≤ 15%", "toleranz": "± 3%", "pflicht": True},
                    {"nr": 2, "punkt": "BSH-Träger", "methode": "Messgerät", "soll": "≤ 12%", "toleranz": "± 2%", "pflicht": True},
                    {"nr": 3, "punkt": "Schalung/Lattung", "methode": "Messgerät", "soll": "≤ 20%", "toleranz": "± 3%", "pflicht": False},
                ]
            },
            "masshaltigkeit": {
                "name": "Maßhaltigkeit - Bauteile",
                "icon": "📐",
                "category": "Holzbau",
                "description": "Maßkontrolle vorgefertigter Bauteile",
                "items": [
                    {"nr": 1, "punkt": "Elementlänge", "methode": "Messen", "soll": "lt. Plan", "toleranz": "± 3 mm/m", "pflicht": True},
                    {"nr": 2, "punkt": "Elementbreite", "methode": "Messen", "soll": "lt. Plan", "toleranz": "± 2 mm", "pflicht": True},
                    {"nr": 3, "punkt": "Diagonalen gleich", "methode": "Messen", "soll": "Δ < 3 mm", "toleranz": "-", "pflicht": True},
                    {"nr": 4, "punkt": "Rechtwinkligkeit", "methode": "Winkelmesser", "soll": "90°", "toleranz": "± 0,5°", "pflicht": True},
                ]
            },
            "brandschutz": {
                "name": "Brandschutz - Bekleidung",
                "icon": "🔥",
                "category": "Brandschutz",
                "description": "Prüfung der Brandschutzbekleidung",
                "items": [
                    {"nr": 1, "punkt": "Plattentyp korrekt (F30/F60/F90)", "methode": "Sichtkontrolle", "soll": "lt. Plan", "toleranz": "-", "pflicht": True},
                    {"nr": 2, "punkt": "Plattendicke", "methode": "Messen", "soll": "lt. Zulassung", "toleranz": "-", "pflicht": True},
                    {"nr": 3, "punkt": "Befestigungsabstände", "methode": "Messen", "soll": "lt. Zulassung", "toleranz": "-", "pflicht": True},
                    {"nr": 4, "punkt": "Fugen verspachtelt", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                ]
            },
            "schallschutz": {
                "name": "Schallschutz - Deckenaufbau",
                "icon": "🔇",
                "category": "Schallschutz",
                "description": "Prüfung Schallschutzmaßnahmen Decke",
                "items": [
                    {"nr": 1, "punkt": "Trittschalldämmung verlegt", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                    {"nr": 2, "punkt": "Randdämmstreifen eingebaut", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                    {"nr": 3, "punkt": "Estrich schwimmend", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                    {"nr": 4, "punkt": "Rohrdurchführungen entkoppelt", "methode": "Sichtkontrolle", "soll": "Ja", "toleranz": "-", "pflicht": True},
                ]
            },
        }
        
        # Templates zur Liste hinzufügen
        for key, template in self._checklist_templates.items():
            item = QListWidgetItem(f"{template['icon']} {template['name']}")
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.templates_list.addItem(item)
        
        left_layout.addWidget(self.templates_list)
        
        layout.addWidget(left_panel)
        
        # Right: Checklist editor
        right_panel = QFrame()
        right_panel.setStyleSheet(CARD_STYLE)
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("✏️ Prüfplan bearbeiten"))
        
        # Template info
        info_layout = QFormLayout()
        
        self.template_name = QLineEdit()
        self.template_name.setPlaceholderText("Name der Vorlage")
        info_layout.addRow("Name:", self.template_name)
        
        self.template_category = QComboBox()
        self.template_category.addItems(["Holzbau", "Statik", "Brandschutz", "Schallschutz", "Wärmeschutz"])
        info_layout.addRow("Kategorie:", self.template_category)
        
        self.template_desc = QTextEdit()
        self.template_desc.setMaximumHeight(60)
        self.template_desc.setPlaceholderText("Beschreibung der Prüfung...")
        info_layout.addRow("Beschreibung:", self.template_desc)
        
        right_layout.addLayout(info_layout)
        
        # Checklist items
        items_group = QGroupBox("Prüfpunkte")
        items_group.setStyleSheet(self._group_style())
        items_layout = QVBoxLayout(items_group)
        
        items_toolbar = QHBoxLayout()
        add_item_btn = QPushButton("➕ Prüfpunkt hinzufügen")
        add_item_btn.setStyleSheet(get_button_style('secondary'))
        add_item_btn.clicked.connect(self._add_checklist_item)
        items_toolbar.addWidget(add_item_btn)
        items_toolbar.addStretch()
        items_layout.addLayout(items_toolbar)
        
        self.checklist_items_table = QTableWidget()
        self.checklist_items_table.setColumnCount(6)
        self.checklist_items_table.setHorizontalHeaderLabels([
            "Nr.", "Prüfpunkt", "Prüfmethode", "Sollwert", "Toleranz", "Pflicht"
        ])
        self.checklist_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.checklist_items_table.setStyleSheet(self._table_style())
        self.checklist_items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        items_layout.addWidget(self.checklist_items_table)
        
        right_layout.addWidget(items_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        use_template_btn = QPushButton("📋 Prüfung starten")
        use_template_btn.setStyleSheet(get_button_style('success'))
        use_template_btn.clicked.connect(self._start_inspection_from_template)
        btn_layout.addWidget(use_template_btn)
        
        btn_layout.addStretch()
        
        save_btn = QPushButton("💾 Vorlage speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.clicked.connect(self._save_checklist_template)
        btn_layout.addWidget(save_btn)
        
        right_layout.addLayout(btn_layout)
        
        layout.addWidget(right_panel, 2)
        
        # Erste Vorlage auswählen
        if self.templates_list.count() > 0:
            self.templates_list.setCurrentRow(0)
            first_key = self.templates_list.item(0).data(Qt.ItemDataRole.UserRole)
            self._load_template_details(first_key)
        
        return tab
    
    def _on_template_selected(self, item: QListWidgetItem):
        """Wird aufgerufen wenn eine Vorlage ausgewählt wird"""
        template_key = item.data(Qt.ItemDataRole.UserRole)
        if template_key:
            self._load_template_details(template_key)
    
    def _load_template_details(self, template_key: str):
        """Lädt die Details einer Vorlage in den Editor"""
        if template_key not in self._checklist_templates:
            return
        
        template = self._checklist_templates[template_key]
        self._current_template_key = template_key
        
        # Grunddaten laden
        self.template_name.setText(template['name'])
        
        # Kategorie setzen
        category_index = self.template_category.findText(template['category'])
        if category_index >= 0:
            self.template_category.setCurrentIndex(category_index)
        
        self.template_desc.setText(template.get('description', ''))
        
        # Prüfpunkte laden
        items = template.get('items', [])
        self.checklist_items_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.checklist_items_table.setItem(row, 0, QTableWidgetItem(str(item.get('nr', row + 1))))
            self.checklist_items_table.setItem(row, 1, QTableWidgetItem(item.get('punkt', '')))
            self.checklist_items_table.setItem(row, 2, QTableWidgetItem(item.get('methode', '')))
            self.checklist_items_table.setItem(row, 3, QTableWidgetItem(item.get('soll', '')))
            self.checklist_items_table.setItem(row, 4, QTableWidgetItem(item.get('toleranz', '')))
            
            # Pflicht als Checkbox
            pflicht_item = QTableWidgetItem()
            pflicht_item.setCheckState(Qt.CheckState.Checked if item.get('pflicht', False) else Qt.CheckState.Unchecked)
            self.checklist_items_table.setItem(row, 5, pflicht_item)
    
    def _add_checklist_item(self):
        """Fügt einen neuen Prüfpunkt hinzu"""
        row = self.checklist_items_table.rowCount()
        self.checklist_items_table.insertRow(row)
        self.checklist_items_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.checklist_items_table.setItem(row, 1, QTableWidgetItem(""))
        self.checklist_items_table.setItem(row, 2, QTableWidgetItem(""))
        self.checklist_items_table.setItem(row, 3, QTableWidgetItem(""))
        self.checklist_items_table.setItem(row, 4, QTableWidgetItem(""))
        
        pflicht_item = QTableWidgetItem()
        pflicht_item.setCheckState(Qt.CheckState.Unchecked)
        self.checklist_items_table.setItem(row, 5, pflicht_item)
    
    def _save_checklist_template(self):
        """Speichert die aktuelle Vorlage"""
        if not hasattr(self, '_current_template_key'):
            QMessageBox.warning(self, "Fehler", "Keine Vorlage ausgewählt")
            return
        
        # Daten sammeln
        name = self.template_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte Namen eingeben")
            return
        
        items = []
        for row in range(self.checklist_items_table.rowCount()):
            item = {
                'nr': int(self.checklist_items_table.item(row, 0).text() or row + 1),
                'punkt': self.checklist_items_table.item(row, 1).text() if self.checklist_items_table.item(row, 1) else '',
                'methode': self.checklist_items_table.item(row, 2).text() if self.checklist_items_table.item(row, 2) else '',
                'soll': self.checklist_items_table.item(row, 3).text() if self.checklist_items_table.item(row, 3) else '',
                'toleranz': self.checklist_items_table.item(row, 4).text() if self.checklist_items_table.item(row, 4) else '',
                'pflicht': self.checklist_items_table.item(row, 5).checkState() == Qt.CheckState.Checked if self.checklist_items_table.item(row, 5) else False,
            }
            if item['punkt']:  # Nur nicht-leere Zeilen
                items.append(item)
        
        # Vorlage aktualisieren
        self._checklist_templates[self._current_template_key] = {
            'name': name,
            'icon': self._checklist_templates[self._current_template_key].get('icon', '📋'),
            'category': self.template_category.currentText(),
            'description': self.template_desc.toPlainText(),
            'items': items
        }
        
        # Liste aktualisieren
        for i in range(self.templates_list.count()):
            item = self.templates_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self._current_template_key:
                template = self._checklist_templates[self._current_template_key]
                item.setText(f"{template['icon']} {template['name']}")
                break
        
        QMessageBox.information(self, "Erfolg", "Vorlage wurde gespeichert")
    
    def _start_inspection_from_template(self):
        """Startet eine Prüfung basierend auf der ausgewählten Vorlage"""
        if not hasattr(self, '_current_template_key') or self._current_template_key not in self._checklist_templates:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst eine Vorlage auswählen")
            return
        
        template = self._checklist_templates[self._current_template_key]
        
        # Prüfungs-Dialog mit vorausgefüllten Daten öffnen
        dialog = InspectionDialog(self.db_service, user=self.user, parent=self)
        
        # Vorlage-Daten setzen (falls Dialog entsprechende Felder hat)
        if hasattr(dialog, 'subject') and hasattr(dialog.subject, 'setText'):
            dialog.subject.setText(template['name'])
        
        if dialog.exec():
            self.refresh()
            QMessageBox.information(self, "Erfolg", f"Prüfung '{template['name']}' wurde erstellt")
    
    def _create_warranty_tab(self) -> QWidget:
        """Gewährleistungsverwaltung mit Einbehalten"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Summary cards
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px; padding: 16px;")
        summary_layout = QHBoxLayout(summary_frame)
        
        for label, value, subtext, color in [
            ("Aktive Gewährleistungen", "24", "davon 3 kritisch", COLORS['primary']),
            ("Einbehalt gesamt", "€ 85.400", "12 Projekte", COLORS['warning']),
            ("Ablaufend (30 Tage)", "5", "Prüfung erforderlich", COLORS['danger']),
            ("Freigegebene Einbehalte", "€ 42.000", "dieses Jahr", COLORS['success'])
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 1px solid {COLORS['gray_200']};
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(4)
            
            card_value = QLabel(value)
            card_value.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            card_value.setStyleSheet(f"color: {color};")
            card_layout.addWidget(card_value)
            
            card_label = QLabel(label)
            card_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            card_layout.addWidget(card_label)
            
            card_sub = QLabel(subtext)
            card_sub.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
            card_layout.addWidget(card_sub)
            
            summary_layout.addWidget(card)
        
        layout.addWidget(summary_frame)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Gewährleistung suchen...")
        search.setMaximumWidth(250)
        toolbar.addWidget(search)
        
        status_combo = QComboBox()
        status_combo.addItems(["Alle Status", "Aktiv", "Ablaufend", "Abgelaufen", "Freigegeben"])
        toolbar.addWidget(status_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neue Gewährleistung")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_warranty)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Warranty table
        self.warranty_table = QTableWidget()
        self.warranty_table.setColumnCount(11)
        self.warranty_table.setHorizontalHeaderLabels([
            "Projekt", "Gewerk", "Beginn", "Ende", "Dauer", "Einbehalt",
            "Einbehalt %", "Bürgschaft", "Status", "Restzeit", "Aktionen"
        ])
        self.warranty_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.warranty_table.setStyleSheet(self._table_style())
        layout.addWidget(self.warranty_table)
        
        return tab
    
    def _create_certificates_tab(self) -> QWidget:
        """Zertifikate (CE, Statik, FSC/PEFC)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Zertifikat suchen...")
        search.setMaximumWidth(250)
        toolbar.addWidget(search)
        
        type_combo = QComboBox()
        type_combo.addItems([
            "Alle Typen", "CE-Kennzeichnung", "Statiknachweis", "FSC", "PEFC",
            "Ü-Zeichen", "AbZ", "ETA", "Prüfzeugnis", "Werksbescheinigung"
        ])
        toolbar.addWidget(type_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Zertifikat hinzufügen")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_certificate)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Certificate categories
        categories_frame = QFrame()
        categories_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px; padding: 12px;")
        categories_layout = QHBoxLayout(categories_frame)
        
        for icon, label, count in [
            ("🏷️", "CE-Kennzeichnung", 45),
            ("📐", "Statik", 23),
            ("🌲", "FSC/PEFC", 18),
            ("✅", "Ü-Zeichen", 12),
            ("📋", "AbZ/ETA", 8),
            ("🔬", "Prüfzeugnisse", 34)
        ]:
            cat_btn = QPushButton(f"{icon} {label} ({count})")
            cat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cat_btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    border: 1px solid {COLORS['gray_200']};
                    border-radius: 6px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: {COLORS['primary']};
                    color: white;
                    border-color: {COLORS['primary']};
                }}
            """)
            categories_layout.addWidget(cat_btn)
        
        layout.addWidget(categories_frame)
        
        # Certificates table
        self.certificates_table = QTableWidget()
        self.certificates_table.setColumnCount(10)
        self.certificates_table.setHorizontalHeaderLabels([
            "Zertifikat-Nr.", "Typ", "Bezeichnung", "Produkt/Material",
            "Aussteller", "Ausstellungsdatum", "Gültig bis", "Projekt", "Dokument", "Aktionen"
        ])
        self.certificates_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.certificates_table.setStyleSheet(self._table_style())
        layout.addWidget(self.certificates_table)
        
        return tab
    
    def _create_reports_tab(self) -> QWidget:
        """Auswertungen und Statistiken"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Filter bar
        filter_frame = QFrame()
        filter_frame.setStyleSheet(CARD_STYLE)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        
        filter_layout.addWidget(QLabel("Zeitraum:"))
        period_combo = QComboBox()
        period_combo.addItems(["Dieses Jahr", "Dieses Quartal", "Dieser Monat", "Letzte 12 Monate"])
        filter_layout.addWidget(period_combo)
        
        filter_layout.addWidget(QLabel("Projekt:"))
        project_combo = QComboBox()
        project_combo.addItems(["Alle Projekte"])
        filter_layout.addWidget(project_combo)
        
        filter_layout.addStretch()
        
        export_btn = QPushButton("📄 Report exportieren")
        export_btn.setStyleSheet(get_button_style('secondary'))
        export_btn.clicked.connect(self._export_defects_report)
        filter_layout.addWidget(export_btn)
        
        layout.addWidget(filter_frame)
        
        # KPI Cards
        kpi_frame = QHBoxLayout()
        
        for title, value, change, positive in [
            ("Mängelquote", "2.3%", "-0.5%", True),
            ("Ø Behebungszeit", "4.2 Tage", "-1.1", True),
            ("Nachbesserungskosten", "€ 12.450", "+€ 2.100", False),
            ("Prüfungen bestanden", "94%", "+3%", True)
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 1px solid {COLORS['gray_200']};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            
            card_title = QLabel(title)
            card_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            card_layout.addWidget(card_title)
            
            value_layout = QHBoxLayout()
            card_value = QLabel(value)
            card_value.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
            value_layout.addWidget(card_value)
            
            change_label = QLabel(change)
            change_color = COLORS['success'] if positive else COLORS['danger']
            change_label.setStyleSheet(f"color: {change_color}; font-size: 12px; font-weight: bold;")
            value_layout.addWidget(change_label)
            value_layout.addStretch()
            
            card_layout.addLayout(value_layout)
            kpi_frame.addWidget(card)
        
        layout.addLayout(kpi_frame)
        
        # Charts placeholder
        charts_frame = QHBoxLayout()
        
        for chart_title in ["Mängel nach Kategorie", "Mängel nach Schweregrad", "Trend Mängelquote"]:
            chart = QFrame()
            chart.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 1px solid {COLORS['gray_200']};
                    border-radius: 8px;
                }}
            """)
            chart.setMinimumHeight(250)
            chart_layout = QVBoxLayout(chart)
            
            chart_header = QLabel(f"📊 {chart_title}")
            chart_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            chart_header.setStyleSheet(f"padding: 12px; border-bottom: 1px solid {COLORS['gray_100']};")
            chart_layout.addWidget(chart_header)
            
            chart_placeholder = QLabel("📈 Chart wird hier angezeigt")
            chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_placeholder.setStyleSheet(f"color: {COLORS['gray_400']};")
            chart_layout.addWidget(chart_placeholder)
            
            charts_frame.addWidget(chart)
        
        layout.addLayout(charts_frame)
        
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
                font-size: 13px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                background: white;
            }}
        """
    
    # Event handlers
    def _on_defect_row_clicked(self, row: int, column: int):
        """Zeigt Details des ausgewählten Mangels"""
        defect_id_item = self.defects_table.item(row, 0)
        if not defect_id_item:
            return
        
        defect_id = defect_id_item.data(Qt.ItemDataRole.UserRole)
        if not defect_id:
            return
        
        self._load_defect_details(defect_id)
    
    def _on_defect_selected(self, item):
        """Legacy handler - ruft row clicked auf"""
        self._on_defect_row_clicked(item.row(), 0)
    
    def _load_defect_details(self, defect_id: str):
        """Lädt die Details eines Mangels in das rechte Panel"""
        session = self.db_service.get_session()
        try:
            defect = session.get(Defect, defect_id)
            if not defect:
                return
            
            # Speichere aktuelle ID für späteres Speichern
            self._selected_defect_id = defect_id
            
            # Grunddaten
            self.defect_number.setText(defect.defect_number or "---")
            
            # Projekt laden
            if defect.project_id:
                project = session.get(Project, defect.project_id)
                self.defect_project.setText(f"{project.project_number} - {project.name}" if project else "---")
            else:
                self.defect_project.setText("---")
            
            self.defect_location.setText(defect.location or defect.building_part or "---")
            self.defect_category.setText(defect.defect_type or defect.category or "---")
            
            # Schweregrad
            severity_names = {
                DefectSeverity.COSMETIC: "🟢 Kosmetisch",
                DefectSeverity.MINOR: "🟡 Leicht",
                DefectSeverity.MAJOR: "🟠 Mittel",
                DefectSeverity.CRITICAL: "🔴 Kritisch",
            }
            self.defect_severity.setText(severity_names.get(defect.severity, "---"))
            
            # Beschreibung
            self.defect_description.setText(defect.description or "")
            
            # Kosten
            self.defect_cost_total.setText(f"€ {defect.estimated_cost or '0,00'}")
            if defect.actual_cost:
                self.defect_cost_total.setText(f"€ {defect.actual_cost}")
            
            # Status setzen
            status_map = {
                DefectStatus.OPEN: 0,
                DefectStatus.IN_PROGRESS: 1,
                DefectStatus.FIXED: 2,
                DefectStatus.VERIFIED: 4,
                DefectStatus.REJECTED: 5,
            }
            self.defect_status_combo.setCurrentIndex(status_map.get(defect.status, 0))
            
            # Frist
            if defect.remediation_deadline:
                self.defect_deadline.setDate(QDate(
                    defect.remediation_deadline.year,
                    defect.remediation_deadline.month,
                    defect.remediation_deadline.day
                ))
            
            # Fotos laden
            self._load_defect_photos(defect_id)
            
        except Exception as e:
            print(f"Fehler beim Laden der Mangeldetails: {e}")
        finally:
            session.close()
    
    def _load_defect_photos(self, defect_id: str):
        """Lädt die Fotos eines Mangels mit Thumbnails"""
        self.photos_before_list.clear()
        self.photos_after_list.clear()
        
        # FileService für späteren Zugriff speichern
        self._current_file_service = None
        
        try:
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                from shared.services.file_service import FileService
                file_service = FileService.get_instance(str(self.user.tenant_id))
                self._current_file_service = file_service
                
                if file_service.is_connected():
                    # Fotos Vorher laden
                    photos_before = file_service.list_files(
                        entity_type="defect",
                        entity_id=defect_id,
                        upload_type="photo_before"
                    )
                    self._add_photo_thumbnails(photos_before, self.photos_before_list, file_service)
                    
                    if not photos_before:
                        item = QListWidgetItem("Keine Fotos")
                        self.photos_before_list.addItem(item)
                    
                    # Fotos Nachher laden
                    photos_after = file_service.list_files(
                        entity_type="defect",
                        entity_id=defect_id,
                        upload_type="photo_after"
                    )
                    self._add_photo_thumbnails(photos_after, self.photos_after_list, file_service)
                    
                    if not photos_after:
                        item = QListWidgetItem("Keine Fotos")
                        self.photos_after_list.addItem(item)
                else:
                    self.photos_before_list.addItem(QListWidgetItem("⚠️ Keine Verbindung"))
                    self.photos_after_list.addItem(QListWidgetItem("⚠️ Keine Verbindung"))
            else:
                self.photos_before_list.addItem(QListWidgetItem("Keine Fotos"))
                self.photos_after_list.addItem(QListWidgetItem("Keine Fotos"))
                
        except Exception as e:
            print(f"Fehler beim Laden der Fotos: {e}")
            self.photos_before_list.addItem(QListWidgetItem(f"Fehler"))
            self.photos_after_list.addItem(QListWidgetItem(f"Fehler"))
    
    def _add_photo_thumbnails(self, photos: list, list_widget: QListWidget, file_service):
        """Fügt Foto-Thumbnails zur Liste hinzu"""
        for photo in photos:
            try:
                # Datei herunterladen
                result = file_service.download_file(photo['id'])
                if result:
                    file_data, filename, content_type = result
                    
                    # Pixmap aus Bytes erstellen
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(file_data))
                    
                    if not pixmap.isNull():
                        # Thumbnail erstellen
                        thumbnail = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        
                        item = QListWidgetItem()
                        item.setIcon(QIcon(thumbnail))
                        item.setText(filename[:15] + "..." if len(filename) > 15 else filename)
                        item.setData(Qt.ItemDataRole.UserRole, photo['id'])
                        item.setToolTip(f"{filename}\nDoppelklick für Vollbild")
                        list_widget.addItem(item)
                    else:
                        # Fallback wenn Bild nicht geladen werden kann
                        item = QListWidgetItem(f"🖼️ {photo['filename']}")
                        item.setData(Qt.ItemDataRole.UserRole, photo['id'])
                        list_widget.addItem(item)
                else:
                    item = QListWidgetItem(f"🖼️ {photo['filename']}")
                    item.setData(Qt.ItemDataRole.UserRole, photo['id'])
                    list_widget.addItem(item)
                    
            except Exception as e:
                print(f"Fehler beim Laden des Thumbnails: {e}")
                item = QListWidgetItem(f"🖼️ {photo.get('filename', 'Unbekannt')}")
                item.setData(Qt.ItemDataRole.UserRole, photo['id'])
                list_widget.addItem(item)
    
    def _show_photo_fullscreen(self, item: QListWidgetItem, photo_type: str):
        """Zeigt ein Foto im Vollbild-Dialog"""
        file_id = item.data(Qt.ItemDataRole.UserRole)
        if not file_id or not self._current_file_service:
            return
        
        try:
            result = self._current_file_service.download_file(file_id)
            if not result:
                QMessageBox.warning(self, "Fehler", "Foto konnte nicht geladen werden")
                return
            
            file_data, filename, content_type = result
            
            # Vollbild-Dialog erstellen
            dialog = QDialog(self)
            dialog.setWindowTitle(f"📷 {filename}")
            dialog.setMinimumSize(800, 600)
            dialog.setStyleSheet("background: #1a1a1a;")
            
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Bild laden
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(file_data))
            
            if pixmap.isNull():
                QMessageBox.warning(self, "Fehler", "Bild konnte nicht angezeigt werden")
                return
            
            # Scrollbereich für großes Bild
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: none; background: #1a1a1a;")
            
            # Bild-Label
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Bild skalieren um ins Fenster zu passen
            screen_size = dialog.screen().availableGeometry()
            max_width = screen_size.width() - 100
            max_height = screen_size.height() - 150
            
            scaled_pixmap = pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
            
            scroll.setWidget(image_label)
            layout.addWidget(scroll)
            
            # Toolbar unten
            toolbar = QFrame()
            toolbar.setStyleSheet("background: #2d2d2d; padding: 8px;")
            toolbar_layout = QHBoxLayout(toolbar)
            
            info_label = QLabel(f"📷 {filename} | {pixmap.width()} x {pixmap.height()} px")
            info_label.setStyleSheet("color: white; font-size: 12px;")
            toolbar_layout.addWidget(info_label)
            
            toolbar_layout.addStretch()
            
            close_btn = QPushButton("✕ Schließen")
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
            close_btn.clicked.connect(dialog.close)
            toolbar_layout.addWidget(close_btn)
            
            layout.addWidget(toolbar)
            
            # Dialog maximiert anzeigen
            dialog.showMaximized()
            dialog.exec()
            
        except Exception as e:
            print(f"Fehler beim Anzeigen des Fotos: {e}")
            QMessageBox.warning(self, "Fehler", f"Fehler: {e}")
    
    def _save_defect_changes(self):
        """Speichert Änderungen am ausgewählten Mangel"""
        if not hasattr(self, '_selected_defect_id') or not self._selected_defect_id:
            QMessageBox.warning(self, "Fehler", "Kein Mangel ausgewählt")
            return
        
        session = self.db_service.get_session()
        try:
            defect = session.get(Defect, self._selected_defect_id)
            if not defect:
                QMessageBox.warning(self, "Fehler", "Mangel nicht gefunden")
                return
            
            # Status aktualisieren
            status_map = {
                0: DefectStatus.OPEN,
                1: DefectStatus.IN_PROGRESS,
                2: DefectStatus.FIXED,
                3: DefectStatus.FIXED,  # Zur Abnahme
                4: DefectStatus.VERIFIED,
                5: DefectStatus.REJECTED,
            }
            defect.status = status_map.get(self.defect_status_combo.currentIndex(), DefectStatus.OPEN)
            
            # Frist aktualisieren
            defect.remediation_deadline = self.defect_deadline.date().toPyDate()
            
            session.commit()
            QMessageBox.information(self, "Erfolg", "Änderungen wurden gespeichert")
            self._load_defects()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
    
    def _add_defect(self):
        """Mangel melden"""
        dialog = DefectDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_inspection(self):
        """Neue Qualitätsprüfung"""
        dialog = InspectionDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_checklist_template(self):
        """Erstellt eine neue Prüfplan-Vorlage"""
        import uuid
        new_key = f"custom_{uuid.uuid4().hex[:8]}"
        
        self._checklist_templates[new_key] = {
            'name': 'Neue Vorlage',
            'icon': '📋',
            'category': 'Holzbau',
            'description': '',
            'items': []
        }
        
        # Zur Liste hinzufügen
        item = QListWidgetItem("📋 Neue Vorlage")
        item.setData(Qt.ItemDataRole.UserRole, new_key)
        self.templates_list.addItem(item)
        
        # Auswählen und laden
        self.templates_list.setCurrentItem(item)
        self._load_template_details(new_key)
    
    def _export_defects_report(self):
        """Exportiert Mängelliste als PDF"""
        from shared.services.export_service import ExportService
        
        # Datei-Dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "PDF speichern",
            f"Maengelliste_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Dateien (*.pdf);;Excel Dateien (*.xlsx)"
        )
        
        if not filename:
            return
        
        try:
            # Mängel laden
            session = self.db_service.get_session()
            query = select(Defect).where(Defect.is_deleted == False).order_by(Defect.detected_date.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Defect.tenant_id == self.user.tenant_id)
            defects = session.execute(query).scalars().all()
            session.close()
            
            if filename.endswith('.xlsx'):
                # Excel Export
                columns = [
                    {"key": "defect_number", "label": "Nr.", "width": 15},
                    {"key": "title", "label": "Titel", "width": 40},
                    {"key": "severity", "label": "Schwere", "width": 15},
                    {"key": "status", "label": "Status", "width": 15},
                    {"key": "location", "label": "Ort", "width": 25},
                    {"key": "deadline", "label": "Frist", "width": 15},
                ]
                
                data = []
                for d in defects:
                    data.append({
                        "defect_number": d.defect_number or '',
                        "title": d.title or '',
                        "severity": d.severity.name if d.severity else '',
                        "status": d.status.name if d.status else '',
                        "location": d.location or d.building_part or '',
                        "deadline": d.remediation_deadline.strftime('%d.%m.%Y') if d.remediation_deadline else '',
                    })
                
                ExportService.export_to_excel(
                    data=data,
                    columns=columns,
                    title="Mängelliste",
                    filename=filename
                )
            else:
                # PDF Export
                ExportService.export_defects_pdf(
                    defects=defects,
                    filename=filename
                )
            
            QMessageBox.information(self, "Erfolg", f"Export wurde erstellt:\n{filename}")
            
            # Datei öffnen
            import os
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Export fehlgeschlagen: {e}")
    
    def _add_warranty(self):
        """Neue Gewährleistung"""
        dialog = WarrantyDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_certificate(self):
        """Neues Zertifikat"""
        dialog = CertificateDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def refresh(self):
        """Refresh all data"""
        self._load_defects()
        self._load_inspections()
        self._load_warranties()
        self._load_certificates()
    
    def _load_defects(self):
        """Lädt alle Mängel"""
        session = self.db_service.get_session()
        try:
            query = select(Defect).where(Defect.is_deleted == False).order_by(Defect.detected_date.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Defect.tenant_id == self.user.tenant_id)
            
            defects = session.execute(query).scalars().all()
            self.defects_table.setRowCount(len(defects))
            
            severity_names = {
                DefectSeverity.COSMETIC: "Kosmetisch",
                DefectSeverity.MINOR: "Leicht",
                DefectSeverity.MAJOR: "Mittel",
                DefectSeverity.CRITICAL: "Kritisch",
            }
            status_names = {
                DefectStatus.OPEN: "Offen",
                DefectStatus.IN_PROGRESS: "In Bearbeitung",
                DefectStatus.FIXED: "Behoben",
                DefectStatus.VERIFIED: "Abgenommen",
                DefectStatus.REJECTED: "Abgelehnt",
            }
            
            for row, d in enumerate(defects):
                self.defects_table.setItem(row, 0, QTableWidgetItem(d.defect_number or ""))
                self.defects_table.setItem(row, 1, QTableWidgetItem(""))  # Projekt
                self.defects_table.setItem(row, 2, QTableWidgetItem(d.building_part or ""))
                self.defects_table.setItem(row, 3, QTableWidgetItem(d.title or ""))
                self.defects_table.setItem(row, 4, QTableWidgetItem(severity_names.get(d.severity, "")))
                self.defects_table.setItem(row, 5, QTableWidgetItem(status_names.get(d.status, "")))
                self.defects_table.setItem(row, 6, QTableWidgetItem(""))  # Verantwortlich
                self.defects_table.setItem(row, 7, QTableWidgetItem(d.remediation_deadline.strftime("%d.%m.%Y") if d.remediation_deadline else ""))
                self.defects_table.setItem(row, 8, QTableWidgetItem(d.actual_cost or ""))
                
                self.defects_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(d.id))
        finally:
            session.close()
    
    def _load_inspections(self):
        """Lädt alle Prüfungen"""
        session = self.db_service.get_session()
        try:
            query = select(QualityCheck).where(QualityCheck.is_deleted == False).order_by(QualityCheck.check_date.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(QualityCheck.tenant_id == self.user.tenant_id)
            
            checks = session.execute(query).scalars().all()
            self.inspections_table.setRowCount(len(checks))
            
            for row, c in enumerate(checks):
                self.inspections_table.setItem(row, 0, QTableWidgetItem(c.check_date.strftime("%d.%m.%Y") if c.check_date else ""))
                self.inspections_table.setItem(row, 1, QTableWidgetItem(""))  # Projekt
                self.inspections_table.setItem(row, 2, QTableWidgetItem(str(c.check_type.value) if c.check_type else ""))
                self.inspections_table.setItem(row, 3, QTableWidgetItem(c.subject or ""))
                self.inspections_table.setItem(row, 4, QTableWidgetItem(""))  # Prüfer
                self.inspections_table.setItem(row, 5, QTableWidgetItem(c.overall_result or ""))
                self.inspections_table.setItem(row, 6, QTableWidgetItem(""))  # Messwerte
                self.inspections_table.setItem(row, 7, QTableWidgetItem(str(c.deviations_found or 0)))
                self.inspections_table.setItem(row, 8, QTableWidgetItem(c.decision or ""))
                
                self.inspections_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(c.id))
        finally:
            session.close()
    
    def _load_warranties(self):
        """Lädt alle Gewährleistungen"""
        session = self.db_service.get_session()
        try:
            query = select(Warranty).where(Warranty.is_deleted == False).order_by(Warranty.warranty_end)
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Warranty.tenant_id == self.user.tenant_id)
            
            warranties = session.execute(query).scalars().all()
            self.warranty_table.setRowCount(len(warranties))
            
            for row, w in enumerate(warranties):
                self.warranty_table.setItem(row, 0, QTableWidgetItem(""))  # Projekt
                self.warranty_table.setItem(row, 1, QTableWidgetItem(""))  # Gewerk
                self.warranty_table.setItem(row, 2, QTableWidgetItem(w.warranty_start.strftime("%d.%m.%Y") if w.warranty_start else ""))
                self.warranty_table.setItem(row, 3, QTableWidgetItem(w.warranty_end.strftime("%d.%m.%Y") if w.warranty_end else ""))
                self.warranty_table.setItem(row, 4, QTableWidgetItem(f"{w.warranty_months or 0} Monate"))
                self.warranty_table.setItem(row, 5, QTableWidgetItem(w.retention_amount or ""))
                self.warranty_table.setItem(row, 6, QTableWidgetItem(w.retention_percent or ""))
                self.warranty_table.setItem(row, 7, QTableWidgetItem("Ja" if w.bank_guarantee else "Nein"))
                self.warranty_table.setItem(row, 8, QTableWidgetItem(w.status or ""))
                
                # Restzeit berechnen
                if w.warranty_end:
                    days_left = (w.warranty_end - date.today()).days
                    self.warranty_table.setItem(row, 9, QTableWidgetItem(f"{days_left} Tage"))
                
                self.warranty_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(w.id))
        finally:
            session.close()
    
    def _load_certificates(self):
        """Lädt alle Zertifikate"""
        session = self.db_service.get_session()
        try:
            query = select(Certificate).where(Certificate.is_deleted == False).order_by(Certificate.issue_date.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Certificate.tenant_id == self.user.tenant_id)
            
            certs = session.execute(query).scalars().all()
            self.certificates_table.setRowCount(len(certs))
            
            for row, c in enumerate(certs):
                self.certificates_table.setItem(row, 0, QTableWidgetItem(c.certificate_number or ""))
                self.certificates_table.setItem(row, 1, QTableWidgetItem(c.certificate_type or ""))
                self.certificates_table.setItem(row, 2, QTableWidgetItem(c.name or ""))
                self.certificates_table.setItem(row, 3, QTableWidgetItem(""))  # Produkt
                self.certificates_table.setItem(row, 4, QTableWidgetItem(c.issuer or ""))
                self.certificates_table.setItem(row, 5, QTableWidgetItem(c.issue_date.strftime("%d.%m.%Y") if c.issue_date else ""))
                self.certificates_table.setItem(row, 6, QTableWidgetItem(c.valid_until.strftime("%d.%m.%Y") if c.valid_until else ""))
                self.certificates_table.setItem(row, 7, QTableWidgetItem(""))  # Projekt
                
                self.certificates_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(c.id))
        finally:
            session.close()


class DefectDialog(QDialog):
    """Dialog zum Erfassen von Mängeln"""
    
    def __init__(self, db_service, defect_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.defect_id = defect_id
        self.user = user
        self.file_service = None
        self._init_file_service()
        self.setup_ui()
        self._load_projects()
    
    def _init_file_service(self):
        """Initialisiert den FileService"""
        try:
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                from shared.services.file_service import FileService
                self.file_service = FileService.get_instance(str(self.user.tenant_id))
        except Exception as e:
            print(f"FileService konnte nicht initialisiert werden: {e}")
    
    def setup_ui(self):
        self.setWindowTitle("Mangel melden")
        self.setMinimumSize(700, 700)
        
        layout = QVBoxLayout(self)
        
        # Scrollbereich für Formular
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.project_combo = QComboBox()
        form.addRow("Projekt:", self.project_combo)
        
        self.title = QLineEdit()
        self.title.setPlaceholderText("Kurzbezeichnung des Mangels")
        form.addRow("Titel*:", self.title)
        
        self.severity = QComboBox()
        self.severity.addItem("Kosmetisch", "cosmetic")
        self.severity.addItem("Leicht", "minor")
        self.severity.addItem("Mittel", "major")
        self.severity.addItem("Kritisch", "critical")
        self.severity.setCurrentIndex(1)
        form.addRow("Schweregrad*:", self.severity)
        
        self.status = QComboBox()
        self.status.addItem("Offen", "open")
        self.status.addItem("Anerkannt", "acknowledged")
        self.status.addItem("In Bearbeitung", "in_progress")
        self.status.addItem("Behoben", "fixed")
        self.status.addItem("Verifiziert", "verified")
        form.addRow("Status:", self.status)
        
        self.defect_type = QComboBox()
        self.defect_type.addItems([
            "Maßabweichung", "Oberflächenmangel", "Feuchtigkeitsschaden",
            "Montagedefekt", "Materialfehler", "Transportschaden", "Sonstiges"
        ])
        form.addRow("Mangelart:", self.defect_type)
        
        self.detected_date = QDateEdit()
        self.detected_date.setCalendarPopup(True)
        self.detected_date.setDate(QDate.currentDate())
        form.addRow("Feststellungsdatum*:", self.detected_date)
        
        self.location = QLineEdit()
        self.location.setPlaceholderText("z.B. EG, Wohnzimmer, Wand Nord")
        form.addRow("Ort/Bauabschnitt:", self.location)
        
        self.building_part = QLineEdit()
        self.building_part.setPlaceholderText("z.B. Wandelement W-01")
        form.addRow("Bauteil:", self.building_part)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setPlaceholderText("Ausführliche Beschreibung des Mangels...")
        form.addRow("Beschreibung*:", self.description)
        
        self.deadline = QDateEdit()
        self.deadline.setCalendarPopup(True)
        self.deadline.setDate(QDate.currentDate().addDays(14))
        form.addRow("Frist:", self.deadline)
        
        self.estimated_cost = QDoubleSpinBox()
        self.estimated_cost.setRange(0, 999999)
        self.estimated_cost.setDecimals(2)
        self.estimated_cost.setSuffix(" €")
        form.addRow("Geschätzte Kosten:", self.estimated_cost)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Weitere Notizen...")
        form.addRow("Notizen:", self.notes)
        
        form_layout.addLayout(form)
        
        # Foto-Upload Widgets
        photos_frame = QFrame()
        photos_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px; padding: 8px;")
        photos_layout = QHBoxLayout(photos_frame)
        
        # Fotos Vorher
        from app.ui.widgets.file_upload import PhotoUploadWidget
        user_id = str(self.user.id) if self.user and hasattr(self.user, 'id') else None
        
        self.photos_before = PhotoUploadWidget(
            file_service=self.file_service,
            entity_type="defect",
            entity_id=self.defect_id,
            upload_type="photo_before",
            user_id=user_id,
            title="Fotos Vorher",
            max_files=5
        )
        photos_layout.addWidget(self.photos_before)
        
        # Fotos Nachher
        self.photos_after = PhotoUploadWidget(
            file_service=self.file_service,
            entity_type="defect",
            entity_id=self.defect_id,
            upload_type="photo_after",
            user_id=user_id,
            title="Fotos Nachher",
            max_files=5
        )
        photos_layout.addWidget(self.photos_after)
        
        form_layout.addWidget(photos_frame)
        
        # Dokumente
        from app.ui.widgets.file_upload import FileUploadWidget
        self.documents = FileUploadWidget(
            file_service=self.file_service,
            entity_type="defect",
            entity_id=self.defect_id,
            upload_type="document",
            user_id=user_id,
            title="Dokumente",
            max_files=10
        )
        form_layout.addWidget(self.documents)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
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
    
    def _load_projects(self):
        session = self.db.get_session()
        try:
            query = select(Project).where(Project.is_deleted == False).order_by(Project.project_number.desc())
            projects = session.execute(query).scalars().all()
            self.project_combo.addItem("-- Projekt wählen --", None)
            for p in projects:
                self.project_combo.addItem(f"{p.project_number} - {p.name}", str(p.id))
        finally:
            session.close()
    
    def save(self):
        if not self.title.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Titel eingeben.")
            return
        if not self.description.toPlainText().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Beschreibung eingeben.")
            return
        
        session = self.db.get_session()
        try:
            defect = Defect()
            count = session.execute(select(func.count(Defect.id))).scalar() or 0
            defect.defect_number = f"M{datetime.now().year}{count + 1:05d}"
            
            project_id = self.project_combo.currentData()
            if project_id:
                defect.project_id = uuid.UUID(project_id)
            
            defect.title = self.title.text().strip()
            defect.severity = DefectSeverity(self.severity.currentData())
            defect.status = DefectStatus(self.status.currentData())
            defect.defect_type = self.defect_type.currentText()
            defect.detected_date = self.detected_date.date().toPyDate()
            defect.location = self.location.text().strip() or None
            defect.building_part = self.building_part.text().strip() or None
            defect.description = self.description.toPlainText().strip()
            defect.remediation_deadline = self.deadline.date().toPyDate()
            defect.estimated_cost = str(self.estimated_cost.value()) if self.estimated_cost.value() > 0 else None
            defect.notes = self.notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                defect.tenant_id = self.user.tenant_id
            # Note: detected_by_id verweist auf employees, nicht auf user
            # Wir setzen es als external name stattdessen
            if self.user:
                user_name = getattr(self.user, 'username', None) or getattr(self.user, 'email', 'Unbekannt')
                defect.detected_by_external = user_name
            
            session.add(defect)
            session.flush()  # ID generieren
            
            # Dateien speichern
            defect_id_str = str(defect.id)
            self.photos_before.save_pending_files(defect_id_str)
            self.photos_after.save_pending_files(defect_id_str)
            self.documents.save_pending_files(defect_id_str)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class InspectionDialog(QDialog):
    """Dialog zum Erfassen von Qualitätsprüfungen"""
    
    def __init__(self, db_service, inspection_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.inspection_id = inspection_id
        self.user = user
        self.setup_ui()
        self._load_projects()
    
    def setup_ui(self):
        self.setWindowTitle("Qualitätsprüfung erfassen")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.project_combo = QComboBox()
        form.addRow("Projekt:", self.project_combo)
        
        self.check_type = QComboBox()
        self.check_type.addItem("Wareneingangsprüfung", "incoming_inspection")
        self.check_type.addItem("Fertigungsbegleitend", "in_process")
        self.check_type.addItem("Endkontrolle", "final_inspection")
        self.check_type.addItem("Montageprüfung", "installation")
        self.check_type.addItem("Abnahmeprüfung", "acceptance")
        form.addRow("Prüfart*:", self.check_type)
        
        self.check_date = QDateEdit()
        self.check_date.setCalendarPopup(True)
        self.check_date.setDate(QDate.currentDate())
        form.addRow("Prüfdatum*:", self.check_date)
        
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("z.B. Wandelemente Charge W-2024-01")
        form.addRow("Prüfgegenstand*:", self.subject)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Beschreibung der Prüfung...")
        form.addRow("Beschreibung:", self.description)
        
        self.overall_result = QComboBox()
        self.overall_result.addItems(["Bestanden", "Nicht bestanden", "Bedingt freigegeben"])
        form.addRow("Ergebnis:", self.overall_result)
        
        self.deviations = QSpinBox()
        self.deviations.setRange(0, 999)
        form.addRow("Anzahl Abweichungen:", self.deviations)
        
        self.deviations_desc = QTextEdit()
        self.deviations_desc.setMaximumHeight(60)
        self.deviations_desc.setPlaceholderText("Beschreibung der Abweichungen...")
        form.addRow("Abweichungen:", self.deviations_desc)
        
        self.decision = QComboBox()
        self.decision.addItems(["Freigabe", "Nacharbeit erforderlich", "Sperrung", "Sonderfreigabe"])
        form.addRow("Entscheidung:", self.decision)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Weitere Bemerkungen...")
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
    
    def _load_projects(self):
        session = self.db.get_session()
        try:
            query = select(Project).where(Project.is_deleted == False).order_by(Project.project_number.desc())
            projects = session.execute(query).scalars().all()
            self.project_combo.addItem("-- Projekt wählen --", None)
            for p in projects:
                self.project_combo.addItem(f"{p.project_number} - {p.name}", str(p.id))
        finally:
            session.close()
    
    def save(self):
        if not self.subject.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Prüfgegenstand eingeben.")
            return
        
        session = self.db.get_session()
        try:
            check = QualityCheck()
            count = session.execute(select(func.count(QualityCheck.id))).scalar() or 0
            check.check_number = f"QC{datetime.now().year}{count + 1:05d}"
            
            project_id = self.project_combo.currentData()
            if project_id:
                check.project_id = uuid.UUID(project_id)
            
            check.check_type = QualityCheckType(self.check_type.currentData())
            check.check_date = self.check_date.date().toPyDate()
            check.subject = self.subject.text().strip()
            check.description = self.description.toPlainText().strip() or None
            
            result_map = {"Bestanden": "passed", "Nicht bestanden": "failed", "Bedingt freigegeben": "conditional"}
            check.overall_result = result_map.get(self.overall_result.currentText(), "passed")
            
            check.deviations_found = self.deviations.value()
            check.deviations_description = self.deviations_desc.toPlainText().strip() or None
            check.decision = self.decision.currentText()
            check.notes = self.notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                check.tenant_id = self.user.tenant_id
            # inspector_id verweist auf employees - external_inspector stattdessen
            if self.user:
                user_name = getattr(self.user, 'username', None) or getattr(self.user, 'email', 'Unbekannt')
                check.external_inspector = user_name
            
            session.add(check)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class WarrantyDialog(QDialog):
    """Dialog zum Erfassen von Gewährleistungen"""
    
    def __init__(self, db_service, warranty_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.warranty_id = warranty_id
        self.user = user
        self.setup_ui()
        self._load_data()
    
    def setup_ui(self):
        self.setWindowTitle("Gewährleistung erfassen")
        self.setMinimumSize(550, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.project_combo = QComboBox()
        form.addRow("Projekt*:", self.project_combo)
        
        self.customer_combo = QComboBox()
        form.addRow("Kunde*:", self.customer_combo)
        
        self.acceptance_date = QDateEdit()
        self.acceptance_date.setCalendarPopup(True)
        self.acceptance_date.setDate(QDate.currentDate())
        form.addRow("Abnahmedatum*:", self.acceptance_date)
        
        self.warranty_start = QDateEdit()
        self.warranty_start.setCalendarPopup(True)
        self.warranty_start.setDate(QDate.currentDate())
        form.addRow("Gewährleistungsbeginn*:", self.warranty_start)
        
        self.warranty_months = QSpinBox()
        self.warranty_months.setRange(1, 120)
        self.warranty_months.setValue(60)
        self.warranty_months.setSuffix(" Monate")
        self.warranty_months.valueChanged.connect(self._calc_end_date)
        form.addRow("Gewährleistungsdauer:", self.warranty_months)
        
        self.warranty_end = QDateEdit()
        self.warranty_end.setCalendarPopup(True)
        self.warranty_end.setDate(QDate.currentDate().addMonths(60))
        form.addRow("Gewährleistungsende:", self.warranty_end)
        
        # Einbehalt
        einbehalt_label = QLabel("--- Sicherheitseinbehalt ---")
        einbehalt_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(einbehalt_label)
        
        self.retention_amount = QDoubleSpinBox()
        self.retention_amount.setRange(0, 9999999)
        self.retention_amount.setDecimals(2)
        self.retention_amount.setSuffix(" €")
        form.addRow("Einbehalt Betrag:", self.retention_amount)
        
        self.retention_percent = QDoubleSpinBox()
        self.retention_percent.setRange(0, 20)
        self.retention_percent.setDecimals(1)
        self.retention_percent.setSuffix(" %")
        self.retention_percent.setValue(5)
        form.addRow("Einbehalt Prozent:", self.retention_percent)
        
        self.bank_guarantee = QCheckBox("Bankbürgschaft statt Einbehalt")
        form.addRow("", self.bank_guarantee)
        
        self.guarantee_amount = QDoubleSpinBox()
        self.guarantee_amount.setRange(0, 9999999)
        self.guarantee_amount.setDecimals(2)
        self.guarantee_amount.setSuffix(" €")
        form.addRow("Bürgschaftsbetrag:", self.guarantee_amount)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Bemerkungen...")
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
    
    def _load_data(self):
        session = self.db.get_session()
        try:
            # Projekte
            projects = session.execute(
                select(Project).where(Project.is_deleted == False).order_by(Project.project_number.desc())
            ).scalars().all()
            self.project_combo.addItem("-- Projekt wählen --", None)
            for p in projects:
                self.project_combo.addItem(f"{p.project_number} - {p.name}", str(p.id))
            
            # Kunden
            customers = session.execute(
                select(Customer).where(Customer.is_deleted == False).order_by(Customer.company_name)
            ).scalars().all()
            self.customer_combo.addItem("-- Kunde wählen --", None)
            for c in customers:
                name = c.company_name or f"{c.first_name} {c.last_name}"
                self.customer_combo.addItem(f"{c.customer_number} - {name}", str(c.id))
        finally:
            session.close()
    
    def _calc_end_date(self):
        start = self.warranty_start.date()
        months = self.warranty_months.value()
        self.warranty_end.setDate(start.addMonths(months))
    
    def save(self):
        project_id = self.project_combo.currentData()
        customer_id = self.customer_combo.currentData()
        
        if not project_id:
            QMessageBox.warning(self, "Fehler", "Bitte Projekt auswählen.")
            return
        if not customer_id:
            QMessageBox.warning(self, "Fehler", "Bitte Kunde auswählen.")
            return
        
        session = self.db.get_session()
        try:
            warranty = Warranty()
            count = session.execute(select(func.count(Warranty.id))).scalar() or 0
            warranty.warranty_number = f"GW{datetime.now().year}{count + 1:05d}"
            
            warranty.project_id = uuid.UUID(project_id)
            warranty.customer_id = uuid.UUID(customer_id)
            warranty.acceptance_date = self.acceptance_date.date().toPyDate()
            warranty.warranty_start = self.warranty_start.date().toPyDate()
            warranty.warranty_end = self.warranty_end.date().toPyDate()
            warranty.warranty_months = self.warranty_months.value()
            
            warranty.retention_amount = str(self.retention_amount.value()) if self.retention_amount.value() > 0 else None
            warranty.retention_percent = str(self.retention_percent.value()) if self.retention_percent.value() > 0 else None
            warranty.bank_guarantee = self.bank_guarantee.isChecked()
            warranty.guarantee_amount = str(self.guarantee_amount.value()) if self.guarantee_amount.value() > 0 else None
            warranty.notes = self.notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                warranty.tenant_id = self.user.tenant_id
            
            session.add(warranty)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class CertificateDialog(QDialog):
    """Dialog zum Erfassen von Zertifikaten"""
    
    def __init__(self, db_service, certificate_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.certificate_id = certificate_id
        self.user = user
        self.setup_ui()
        self._load_projects()
    
    def setup_ui(self):
        self.setWindowTitle("Zertifikat erfassen")
        self.setMinimumSize(550, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.certificate_number = QLineEdit()
        self.certificate_number.setPlaceholderText("z.B. CE-2024-001")
        form.addRow("Zertifikat-Nr.*:", self.certificate_number)
        
        self.certificate_type = QComboBox()
        self.certificate_type.addItems([
            "CE-Kennzeichnung", "Leistungserklärung (DoP)", "FSC", "PEFC",
            "Ü-Zeichen", "AbZ", "ETA", "Statikprüfung", "Brandschutznachweis",
            "Werksbescheinigung", "Prüfzeugnis", "Sonstiges"
        ])
        form.addRow("Zertifikatstyp*:", self.certificate_type)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("Bezeichnung des Zertifikats")
        form.addRow("Bezeichnung*:", self.name)
        
        self.project_combo = QComboBox()
        form.addRow("Projekt:", self.project_combo)
        
        self.issuer = QLineEdit()
        self.issuer.setPlaceholderText("z.B. TÜV Süd, MPA Stuttgart")
        form.addRow("Aussteller:", self.issuer)
        
        self.issue_date = QDateEdit()
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setDate(QDate.currentDate())
        form.addRow("Ausstellungsdatum:", self.issue_date)
        
        self.valid_from = QDateEdit()
        self.valid_from.setCalendarPopup(True)
        self.valid_from.setDate(QDate.currentDate())
        form.addRow("Gültig ab:", self.valid_from)
        
        self.valid_until = QDateEdit()
        self.valid_until.setCalendarPopup(True)
        self.valid_until.setSpecialValueText("Unbefristet")
        form.addRow("Gültig bis:", self.valid_until)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Beschreibung, Geltungsbereich...")
        form.addRow("Beschreibung:", self.description)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Weitere Bemerkungen...")
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
    
    def _load_projects(self):
        session = self.db.get_session()
        try:
            query = select(Project).where(Project.is_deleted == False).order_by(Project.project_number.desc())
            projects = session.execute(query).scalars().all()
            self.project_combo.addItem("-- Kein Projekt --", None)
            for p in projects:
                self.project_combo.addItem(f"{p.project_number} - {p.name}", str(p.id))
        finally:
            session.close()
    
    def save(self):
        if not self.certificate_number.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Zertifikat-Nr. eingeben.")
            return
        if not self.name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Bezeichnung eingeben.")
            return
        
        session = self.db.get_session()
        try:
            cert = Certificate()
            cert.certificate_number = self.certificate_number.text().strip()
            cert.certificate_type = self.certificate_type.currentText()
            cert.name = self.name.text().strip()
            
            project_id = self.project_combo.currentData()
            if project_id:
                cert.project_id = uuid.UUID(project_id)
            
            cert.issuer = self.issuer.text().strip() or None
            cert.issue_date = self.issue_date.date().toPyDate()
            cert.valid_from = self.valid_from.date().toPyDate()
            
            valid_until = self.valid_until.date()
            if valid_until.isValid() and valid_until.year() > 2000:
                cert.valid_until = valid_until.toPyDate()
            
            cert.description = self.description.toPlainText().strip() or None
            cert.notes = self.notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                cert.tenant_id = self.user.tenant_id
            
            session.add(cert)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
