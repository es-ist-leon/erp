"""
CRM Widget - Customer Relationship Management
Aktivitäten, Leads, Kampagnen, Aufgaben
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QFrame, QDialog, QFormLayout,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit,
    QTimeEdit, QTabWidget, QScrollArea, QGroupBox, QCheckBox,
    QListWidget, QListWidgetItem, QMessageBox, QHeaderView,
    QSplitter, QTreeWidget, QTreeWidgetItem, QCalendarWidget,
    QProgressBar, QSlider
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, date

from app.ui.styles import COLORS, get_button_style, CARD_STYLE


class CRMWidget(QWidget):
    """CRM - Kundenbeziehungsmanagement"""
    
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
        self.tabs.addTab(self._create_activities_tab(), "📞 Aktivitäten")
        self.tabs.addTab(self._create_leads_tab(), "🎯 Leads")
        self.tabs.addTab(self._create_opportunities_tab(), "💼 Opportunities")
        self.tabs.addTab(self._create_campaigns_tab(), "📢 Kampagnen")
        self.tabs.addTab(self._create_tasks_tab(), "✅ Aufgaben")
        self.tabs.addTab(self._create_pipeline_tab(), "📊 Pipeline")
        
        layout.addWidget(self.tabs)
    
    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setStyleSheet(CARD_STYLE)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        title = QLabel("🤝 CRM")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Quick stats
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(24)
        
        for label, value, color in [
            ("Offene Leads", "24", COLORS['primary']),
            ("Opportunities", "12", COLORS['success']),
            ("Aufgaben heute", "8", COLORS['warning']),
            ("Pipeline-Wert", "€ 450k", COLORS['info'])
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
    
    def _create_activities_tab(self) -> QWidget:
        """Aktivitäten (Telefonate, E-Mails, Besprechungen)"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Left: Activity list
        left_panel = QFrame()
        left_panel.setStyleSheet(CARD_STYLE)
        left_layout = QVBoxLayout(left_panel)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Aktivität suchen...")
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        # Activity type buttons
        for icon, tooltip in [("📞", "Anruf"), ("📧", "E-Mail"), ("🤝", "Meeting"), ("📝", "Notiz")]:
            btn = QPushButton(icon)
            btn.setToolTip(f"Neue {tooltip}")
            btn.setFixedSize(36, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['gray_50']};
                    border: 1px solid {COLORS['gray_200']};
                    border-radius: 8px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background: {COLORS['primary']};
                    color: white;
                }}
            """)
            toolbar.addWidget(btn)
        
        left_layout.addLayout(toolbar)
        
        # Filter
        filter_layout = QHBoxLayout()
        type_combo = QComboBox()
        type_combo.addItems(["Alle Typen", "Anrufe", "E-Mails", "Meetings", "Notizen"])
        filter_layout.addWidget(type_combo)
        
        date_combo = QComboBox()
        date_combo.addItems(["Alle Zeiträume", "Heute", "Diese Woche", "Dieser Monat", "Letzter Monat"])
        filter_layout.addWidget(date_combo)
        left_layout.addLayout(filter_layout)
        
        # Activities table
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(7)
        self.activities_table.setHorizontalHeaderLabels([
            "Typ", "Datum/Zeit", "Kunde", "Betreff", "Mitarbeiter", "Status", "Aktionen"
        ])
        self.activities_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.activities_table.setStyleSheet(self._table_style())
        left_layout.addWidget(self.activities_table)
        
        layout.addWidget(left_panel, 2)
        
        # Right: Activity detail / Quick log
        right_panel = QFrame()
        right_panel.setStyleSheet(CARD_STYLE)
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("📝 Schnelleingabe"))
        
        # Activity type
        type_group = QGroupBox("Aktivitätstyp")
        type_group.setStyleSheet(self._group_style())
        type_layout = QHBoxLayout(type_group)
        
        for icon, name in [("📞", "Anruf"), ("📧", "E-Mail"), ("🤝", "Meeting"), ("📝", "Notiz")]:
            btn = QPushButton(f"{icon}\n{name}")
            btn.setCheckable(True)
            btn.setFixedSize(70, 60)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    border: 2px solid {COLORS['gray_200']};
                    border-radius: 8px;
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    background: {COLORS['primary']}20;
                    border-color: {COLORS['primary']};
                }}
                QPushButton:hover {{
                    border-color: {COLORS['primary']};
                }}
            """)
            type_layout.addWidget(btn)
        
        right_layout.addWidget(type_group)
        
        # Quick form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        customer_combo = QComboBox()
        customer_combo.setEditable(True)
        customer_combo.addItems(["--- Kunde auswählen ---"])
        form_layout.addRow("Kunde:", customer_combo)
        
        contact_combo = QComboBox()
        contact_combo.addItems(["--- Kontakt auswählen ---"])
        form_layout.addRow("Kontakt:", contact_combo)
        
        subject_edit = QLineEdit()
        subject_edit.setPlaceholderText("Betreff der Aktivität")
        form_layout.addRow("Betreff:", subject_edit)
        
        notes_edit = QTextEdit()
        notes_edit.setPlaceholderText("Notizen zur Aktivität...")
        notes_edit.setMaximumHeight(100)
        form_layout.addRow("Notizen:", notes_edit)
        
        outcome_combo = QComboBox()
        outcome_combo.addItems(["Erfolgreich", "Nicht erreicht", "Rückruf vereinbart", "Termin vereinbart"])
        form_layout.addRow("Ergebnis:", outcome_combo)
        
        followup_check = QCheckBox("Folgeaktivität erstellen")
        form_layout.addRow("", followup_check)
        
        right_layout.addLayout(form_layout)
        
        # Save button
        save_btn = QPushButton("💾 Aktivität speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        right_layout.addWidget(save_btn)
        
        right_layout.addStretch()
        
        layout.addWidget(right_panel)
        
        return tab
    
    def _create_leads_tab(self) -> QWidget:
        """Lead-Management mit Score"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Lead suchen...")
        search.setMaximumWidth(300)
        toolbar.addWidget(search)
        
        status_combo = QComboBox()
        status_combo.addItems(["Alle Status", "Neu", "Kontaktiert", "Qualifiziert", "Angebot", "Verhandlung", "Gewonnen", "Verloren"])
        toolbar.addWidget(status_combo)
        
        source_combo = QComboBox()
        source_combo.addItems(["Alle Quellen", "Website", "Empfehlung", "Messe", "Kaltakquise", "Social Media", "Anzeige"])
        toolbar.addWidget(source_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neuer Lead")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_lead)
        toolbar.addWidget(add_btn)
        
        import_btn = QPushButton("📥 Import")
        import_btn.setStyleSheet(get_button_style('secondary'))
        toolbar.addWidget(import_btn)
        
        layout.addLayout(toolbar)
        
        # Lead scoring info
        scoring_frame = QFrame()
        scoring_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['info']}15;
                border: 1px solid {COLORS['info']}50;
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        scoring_layout = QHBoxLayout(scoring_frame)
        
        scoring_layout.addWidget(QLabel("🎯 Lead-Scoring:"))
        
        for score, label, color in [
            ("80-100", "Heiß", COLORS['danger']),
            ("60-79", "Warm", COLORS['warning']),
            ("40-59", "Lauwarm", COLORS['info']),
            ("0-39", "Kalt", COLORS['gray_400'])
        ]:
            score_badge = QLabel(f"● {score} = {label}")
            score_badge.setStyleSheet(f"color: {color}; font-weight: bold;")
            scoring_layout.addWidget(score_badge)
        
        scoring_layout.addStretch()
        layout.addWidget(scoring_frame)
        
        # Leads table
        self.leads_table = QTableWidget()
        self.leads_table.setColumnCount(11)
        self.leads_table.setHorizontalHeaderLabels([
            "Score", "Firma", "Kontakt", "E-Mail", "Telefon", "Quelle",
            "Status", "Potenzial", "Letzte Aktivität", "Verantwortlich", "Aktionen"
        ])
        self.leads_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.leads_table.setStyleSheet(self._table_style())
        layout.addWidget(self.leads_table)
        
        return tab
    
    def _create_opportunities_tab(self) -> QWidget:
        """Opportunities / Verkaufschancen"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Opportunity suchen...")
        search.setMaximumWidth(300)
        toolbar.addWidget(search)
        
        stage_combo = QComboBox()
        stage_combo.addItems(["Alle Phasen", "Erstgespräch", "Bedarfsanalyse", "Angebot", "Verhandlung", "Abschluss"])
        toolbar.addWidget(stage_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neue Opportunity")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_opportunity)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Opportunities table
        self.opportunities_table = QTableWidget()
        self.opportunities_table.setColumnCount(10)
        self.opportunities_table.setHorizontalHeaderLabels([
            "Name", "Kunde", "Wert", "Wahrscheinlichkeit", "Gewichteter Wert",
            "Phase", "Erwarteter Abschluss", "Nächste Aktivität", "Verantwortlich", "Aktionen"
        ])
        self.opportunities_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.opportunities_table.setStyleSheet(self._table_style())
        layout.addWidget(self.opportunities_table)
        
        return tab
    
    def _create_campaigns_tab(self) -> QWidget:
        """Marketing-Kampagnen mit ROI-Tracking"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Kampagne suchen...")
        search.setMaximumWidth(300)
        toolbar.addWidget(search)
        
        type_combo = QComboBox()
        type_combo.addItems(["Alle Typen", "E-Mail", "Event", "Messe", "Social Media", "Print", "Online-Anzeigen"])
        toolbar.addWidget(type_combo)
        
        status_combo = QComboBox()
        status_combo.addItems(["Alle Status", "Geplant", "Aktiv", "Pausiert", "Abgeschlossen"])
        toolbar.addWidget(status_combo)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("➕ Neue Kampagne")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_campaign)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Campaign statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px; padding: 16px;")
        stats_layout = QHBoxLayout(stats_frame)
        
        for label, value, subtext in [
            ("Aktive Kampagnen", "5", "von 12 gesamt"),
            ("Gesamtbudget", "€ 25.000", "verbleibend: € 8.500"),
            ("Leads generiert", "156", "diese Woche: 23"),
            ("Durchschn. ROI", "245%", "Ziel: 200%")
        ]:
            stat_widget = QVBoxLayout()
            stat_value = QLabel(value)
            stat_value.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            stat_value.setStyleSheet(f"color: {COLORS['primary']};")
            stat_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(stat_value)
            
            stat_label = QLabel(label)
            stat_label.setStyleSheet("font-weight: bold;")
            stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(stat_label)
            
            stat_sub = QLabel(subtext)
            stat_sub.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
            stat_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_widget.addWidget(stat_sub)
            
            stats_layout.addLayout(stat_widget)
        
        layout.addWidget(stats_frame)
        
        # Campaigns table
        self.campaigns_table = QTableWidget()
        self.campaigns_table.setColumnCount(12)
        self.campaigns_table.setHorizontalHeaderLabels([
            "Name", "Typ", "Status", "Start", "Ende", "Budget",
            "Ausgaben", "Leads", "Conversions", "Umsatz", "ROI", "Aktionen"
        ])
        self.campaigns_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.campaigns_table.setStyleSheet(self._table_style())
        layout.addWidget(self.campaigns_table)
        
        return tab
    
    def _create_tasks_tab(self) -> QWidget:
        """Aufgabenverwaltung mit Wiederholungen"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Left: Task list
        left_panel = QFrame()
        left_panel.setStyleSheet(CARD_STYLE)
        left_layout = QVBoxLayout(left_panel)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Neue Aufgabe")
        add_btn.setStyleSheet(get_button_style('primary'))
        add_btn.clicked.connect(self._add_task)
        toolbar.addWidget(add_btn)
        
        toolbar.addStretch()
        
        view_combo = QComboBox()
        view_combo.addItems(["Meine Aufgaben", "Team-Aufgaben", "Alle Aufgaben"])
        toolbar.addWidget(view_combo)
        
        left_layout.addLayout(toolbar)
        
        # Filter tabs
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(4, 4, 4, 4)
        
        for label, count in [("Heute", 5), ("Diese Woche", 12), ("Überfällig", 3), ("Alle", 45)]:
            btn = QPushButton(f"{label} ({count})")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    color: {COLORS['text_secondary']};
                }}
                QPushButton:checked {{
                    background: white;
                    color: {COLORS['primary']};
                    font-weight: bold;
                }}
                QPushButton:hover:!checked {{
                    background: {COLORS['gray_100']};
                }}
            """)
            if label == "Heute":
                btn.setChecked(True)
            filter_layout.addWidget(btn)
        
        left_layout.addWidget(filter_frame)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(8)
        self.tasks_table.setHorizontalHeaderLabels([
            "✓", "Priorität", "Aufgabe", "Bezug", "Fällig", "Wiederholen", "Zugewiesen", "Aktionen"
        ])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tasks_table.setStyleSheet(self._table_style())
        left_layout.addWidget(self.tasks_table)
        
        layout.addWidget(left_panel, 2)
        
        # Right: Task detail / Quick add
        right_panel = QFrame()
        right_panel.setStyleSheet(CARD_STYLE)
        right_panel.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("📝 Aufgabe erstellen"))
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("Aufgabentitel")
        form_layout.addRow("Titel:", title_edit)
        
        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("Beschreibung...")
        desc_edit.setMaximumHeight(80)
        form_layout.addRow("Beschreibung:", desc_edit)
        
        priority_combo = QComboBox()
        priority_combo.addItems(["🔴 Hoch", "🟡 Mittel", "🟢 Niedrig"])
        form_layout.addRow("Priorität:", priority_combo)
        
        due_date = QDateEdit()
        due_date.setDate(QDate.currentDate())
        due_date.setCalendarPopup(True)
        form_layout.addRow("Fällig am:", due_date)
        
        assignee_combo = QComboBox()
        assignee_combo.addItems(["--- Zuweisen ---", "Ich", "Max Mustermann", "Anna Schmidt"])
        form_layout.addRow("Zugewiesen:", assignee_combo)
        
        # Relation
        relation_combo = QComboBox()
        relation_combo.addItems(["--- Ohne Bezug ---", "Kunde", "Projekt", "Lead", "Opportunity"])
        form_layout.addRow("Bezug:", relation_combo)
        
        # Repeat
        repeat_group = QGroupBox("🔄 Wiederholung")
        repeat_group.setStyleSheet(self._group_style())
        repeat_layout = QFormLayout(repeat_group)
        
        repeat_combo = QComboBox()
        repeat_combo.addItems(["Keine", "Täglich", "Wöchentlich", "Monatlich", "Jährlich", "Benutzerdefiniert"])
        repeat_layout.addRow("Intervall:", repeat_combo)
        
        repeat_end = QDateEdit()
        repeat_end.setCalendarPopup(True)
        repeat_layout.addRow("Ende:", repeat_end)
        
        form_layout.addRow(repeat_group)
        
        right_layout.addLayout(form_layout)
        
        # Save button
        save_btn = QPushButton("💾 Aufgabe speichern")
        save_btn.setStyleSheet(get_button_style('primary'))
        right_layout.addWidget(save_btn)
        
        right_layout.addStretch()
        
        layout.addWidget(right_panel)
        
        return tab
    
    def _create_pipeline_tab(self) -> QWidget:
        """Sales Pipeline Übersicht"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Pipeline header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📊 Sales Pipeline"))
        header_layout.addStretch()
        
        period_combo = QComboBox()
        period_combo.addItems(["Dieses Quartal", "Diesen Monat", "Diese Woche", "Dieses Jahr"])
        header_layout.addWidget(period_combo)
        
        layout.addLayout(header_layout)
        
        # Pipeline stages (Kanban-style)
        stages_frame = QFrame()
        stages_layout = QHBoxLayout(stages_frame)
        stages_layout.setSpacing(16)
        
        stages = [
            ("Erstgespräch", "€ 120.000", 5, COLORS['gray_400']),
            ("Bedarfsanalyse", "€ 85.000", 3, COLORS['info']),
            ("Angebot", "€ 150.000", 4, COLORS['warning']),
            ("Verhandlung", "€ 95.000", 2, COLORS['primary']),
            ("Abschluss", "€ 45.000", 1, COLORS['success'])
        ]
        
        for stage_name, value, count, color in stages:
            stage_card = QFrame()
            stage_card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 1px solid {COLORS['gray_200']};
                    border-top: 4px solid {color};
                    border-radius: 8px;
                }}
            """)
            stage_card.setMinimumWidth(200)
            stage_layout = QVBoxLayout(stage_card)
            stage_layout.setContentsMargins(16, 16, 16, 16)
            
            # Header
            stage_header = QHBoxLayout()
            stage_label = QLabel(stage_name)
            stage_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            stage_header.addWidget(stage_label)
            
            count_badge = QLabel(str(count))
            count_badge.setFixedSize(24, 24)
            count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count_badge.setStyleSheet(f"""
                background: {COLORS['gray_100']};
                border-radius: 12px;
                font-weight: bold;
                font-size: 11px;
            """)
            stage_header.addWidget(count_badge)
            stage_layout.addLayout(stage_header)
            
            # Value
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            value_label.setStyleSheet(f"color: {color};")
            stage_layout.addWidget(value_label)
            
            # Progress bar
            progress = QProgressBar()
            progress.setMaximum(100)
            progress.setValue(count * 20)
            progress.setTextVisible(False)
            progress.setFixedHeight(6)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    background: {COLORS['gray_100']};
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background: {color};
                    border-radius: 3px;
                }}
            """)
            stage_layout.addWidget(progress)
            
            # Placeholder for deals
            deals_list = QListWidget()
            deals_list.setMaximumHeight(300)
            deals_list.setStyleSheet(f"""
                QListWidget {{
                    border: none;
                    background: transparent;
                }}
                QListWidget::item {{
                    padding: 8px;
                    margin: 4px 0;
                    background: {COLORS['gray_50']};
                    border-radius: 6px;
                }}
                QListWidget::item:hover {{
                    background: {COLORS['gray_100']};
                }}
            """)
            
            # Sample items
            for i in range(min(count, 3)):
                item = QListWidgetItem(f"Deal {i+1} - € {(i+1)*15000:,}")
                deals_list.addItem(item)
            
            stage_layout.addWidget(deals_list)
            stage_layout.addStretch()
            
            stages_layout.addWidget(stage_card)
        
        layout.addWidget(stages_frame)
        
        # Summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"background: {COLORS['gray_50']}; border-radius: 8px; padding: 16px;")
        summary_layout = QHBoxLayout(summary_frame)
        
        for label, value in [
            ("Gesamt-Pipeline", "€ 495.000"),
            ("Gewichteter Wert", "€ 198.000"),
            ("Ø Abschlussrate", "35%"),
            ("Ø Verkaufszyklus", "45 Tage")
        ]:
            item = QVBoxLayout()
            item_value = QLabel(value)
            item_value.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            item_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.addWidget(item_value)
            
            item_label = QLabel(label)
            item_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            item_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.addWidget(item_label)
            
            summary_layout.addLayout(item)
        
        layout.addWidget(summary_frame)
        
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
    def _add_lead(self):
        QMessageBox.information(self, "Neuer Lead", "Lead-Dialog wird geöffnet...")
    
    def _add_opportunity(self):
        QMessageBox.information(self, "Neue Opportunity", "Opportunity-Dialog wird geöffnet...")
    
    def _add_campaign(self):
        QMessageBox.information(self, "Neue Kampagne", "Kampagnen-Dialog wird geöffnet...")
    
    def _add_task(self):
        QMessageBox.information(self, "Neue Aufgabe", "Aufgaben-Dialog wird geöffnet...")
    
    def refresh(self):
        """Refresh all data"""
        pass
