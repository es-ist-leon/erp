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
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, date

from app.ui.styles import COLORS, get_button_style, CARD_STYLE


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
        self.defects_table.itemClicked.connect(self._on_defect_selected)
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
        
        # Photos before/after
        photos_group = QGroupBox("📸 Fotos")
        photos_group.setStyleSheet(self._group_style())
        photos_layout = QHBoxLayout(photos_group)
        
        # Before
        before_frame = QFrame()
        before_layout = QVBoxLayout(before_frame)
        before_layout.addWidget(QLabel("Vorher:"))
        
        before_photo = QFrame()
        before_photo.setFixedSize(150, 150)
        before_photo.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_100']};
                border: 2px dashed {COLORS['gray_300']};
                border-radius: 8px;
            }}
        """)
        before_inner = QVBoxLayout(before_photo)
        before_inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        before_icon = QLabel("📷")
        before_icon.setFont(QFont("Segoe UI", 24))
        before_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        before_inner.addWidget(before_icon)
        before_layout.addWidget(before_photo)
        
        add_before_btn = QPushButton("+ Foto hinzufügen")
        add_before_btn.setStyleSheet(get_button_style('secondary'))
        before_layout.addWidget(add_before_btn)
        photos_layout.addWidget(before_frame)
        
        # After
        after_frame = QFrame()
        after_layout = QVBoxLayout(after_frame)
        after_layout.addWidget(QLabel("Nachher:"))
        
        after_photo = QFrame()
        after_photo.setFixedSize(150, 150)
        after_photo.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_100']};
                border: 2px dashed {COLORS['gray_300']};
                border-radius: 8px;
            }}
        """)
        after_inner = QVBoxLayout(after_photo)
        after_inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        after_icon = QLabel("📷")
        after_icon.setFont(QFont("Segoe UI", 24))
        after_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        after_inner.addWidget(after_icon)
        after_layout.addWidget(after_photo)
        
        add_after_btn = QPushButton("+ Foto hinzufügen")
        add_after_btn.setStyleSheet(get_button_style('secondary'))
        after_layout.addWidget(add_after_btn)
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
        right_layout.addWidget(save_btn)
        
        layout.addWidget(right_panel)
        
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
            QListWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        
        # Sample templates
        templates = [
            "🏠 Holzrahmenbau - Wandaufbau",
            "🪵 Holzbalkenboden - Prüfung",
            "🏗️ Dachstuhl - Abbundkontrolle",
            "🔩 Verbindungsmittel - Prüfung",
            "💧 Feuchtemessung - Holz",
            "📐 Maßhaltigkeit - Bauteile",
            "🔥 Brandschutz - Bekleidung",
            "🔇 Schallschutz - Deckenaufbau"
        ]
        for t in templates:
            self.templates_list.addItem(t)
        
        left_layout.addWidget(self.templates_list)
        
        layout.addWidget(left_panel)
        
        # Right: Checklist editor
        right_panel = QFrame()
        right_panel.setStyleSheet(CARD_STYLE)
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("✏️ Prüfplan bearbeiten"))
        
        # Template info
        info_layout = QFormLayout()
        
        template_name = QLineEdit()
        template_name.setText("Holzrahmenbau - Wandaufbau")
        info_layout.addRow("Name:", template_name)
        
        template_category = QComboBox()
        template_category.addItems(["Holzbau", "Statik", "Brandschutz", "Schallschutz", "Wärmeschutz"])
        info_layout.addRow("Kategorie:", template_category)
        
        template_desc = QTextEdit()
        template_desc.setMaximumHeight(60)
        template_desc.setPlaceholderText("Beschreibung der Prüfung...")
        info_layout.addRow("Beschreibung:", template_desc)
        
        right_layout.addLayout(info_layout)
        
        # Checklist items
        items_group = QGroupBox("Prüfpunkte")
        items_group.setStyleSheet(self._group_style())
        items_layout = QVBoxLayout(items_group)
        
        items_toolbar = QHBoxLayout()
        add_item_btn = QPushButton("➕ Prüfpunkt hinzufügen")
        add_item_btn.setStyleSheet(get_button_style('secondary'))
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
        items_layout.addWidget(self.checklist_items_table)
        
        right_layout.addWidget(items_group)
        
        # Save button
        save_btn = QPushButton("💾 Vorlage speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        right_layout.addWidget(save_btn)
        
        layout.addWidget(right_panel, 2)
        
        return tab
    
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
    def _on_defect_selected(self, item):
        pass
    
    def _add_defect(self):
        QMessageBox.information(self, "Mangel melden", "Mangel-Dialog wird geöffnet...")
    
    def _add_inspection(self):
        QMessageBox.information(self, "Neue Prüfung", "Prüfungs-Dialog wird geöffnet...")
    
    def _add_checklist_template(self):
        QMessageBox.information(self, "Neue Vorlage", "Vorlagen-Dialog wird geöffnet...")
    
    def _add_warranty(self):
        QMessageBox.information(self, "Neue Gewährleistung", "Gewährleistungs-Dialog wird geöffnet...")
    
    def _add_certificate(self):
        QMessageBox.information(self, "Neues Zertifikat", "Zertifikat-Dialog wird geöffnet...")
    
    def refresh(self):
        """Refresh all data"""
        pass
