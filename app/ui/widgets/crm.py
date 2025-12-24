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
import uuid

from sqlalchemy import select, func
from app.ui.styles import COLORS, get_button_style, CARD_STYLE
from shared.models import Lead, Activity, Campaign, Task, Customer, Project


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
        assignee_combo.addItem("--- Zuweisen ---", None)
        assignee_combo.addItem("Ich", self.user.id if self.user else None)
        # Mitarbeiter aus DB laden
        try:
            from app.models.employee import Employee
            employees = self.db_service.get_session().query(Employee).filter(
                Employee.is_deleted == False
            ).limit(20).all()
            for emp in employees:
                name = f"{emp.first_name or ''} {emp.last_name or ''}".strip()
                if name:
                    assignee_combo.addItem(name, emp.id)
        except Exception:
            pass
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
        """Neuen Lead erstellen"""
        dialog = LeadDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_opportunity(self):
        """Neue Opportunity erstellen"""
        dialog = OpportunityDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_campaign(self):
        """Neue Kampagne erstellen"""
        dialog = CampaignDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def _add_task(self):
        """Neue Aufgabe erstellen"""
        dialog = TaskDialog(self.db_service, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def refresh(self):
        """Refresh all data"""
        self._load_leads()
        self._load_campaigns()
        self._load_tasks()
    
    def _load_leads(self):
        """Lädt alle Leads"""
        session = self.db_service.get_session()
        try:
            query = select(Lead).where(Lead.is_deleted == False).order_by(Lead.created_at.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Lead.tenant_id == self.user.tenant_id)
            
            leads = session.execute(query).scalars().all()
            self.leads_table.setRowCount(len(leads))
            
            status_names = {
                "new": "Neu", "contacted": "Kontaktiert", "qualified": "Qualifiziert",
                "proposal": "Angebot", "negotiation": "Verhandlung", "won": "Gewonnen", "lost": "Verloren"
            }
            
            for row, l in enumerate(leads):
                score_item = QTableWidgetItem(str(l.score or 0))
                self.leads_table.setItem(row, 0, score_item)
                self.leads_table.setItem(row, 1, QTableWidgetItem(l.company_name or ""))
                self.leads_table.setItem(row, 2, QTableWidgetItem(f"{l.first_name or ''} {l.last_name or ''}".strip()))
                self.leads_table.setItem(row, 3, QTableWidgetItem(l.email or ""))
                self.leads_table.setItem(row, 4, QTableWidgetItem(l.phone or ""))
                self.leads_table.setItem(row, 5, QTableWidgetItem(l.source or ""))
                self.leads_table.setItem(row, 6, QTableWidgetItem(status_names.get(l.status, l.status or "")))
                self.leads_table.setItem(row, 7, QTableWidgetItem(l.estimated_budget or ""))
                self.leads_table.setItem(row, 8, QTableWidgetItem(l.last_contact_date.strftime("%d.%m.%Y") if l.last_contact_date else ""))
                self.leads_table.setItem(row, 9, QTableWidgetItem(""))
                
                self.leads_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(l.id))
        finally:
            session.close()
    
    def _load_campaigns(self):
        """Lädt alle Kampagnen"""
        session = self.db_service.get_session()
        try:
            query = select(Campaign).where(Campaign.is_deleted == False).order_by(Campaign.start_date.desc())
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Campaign.tenant_id == self.user.tenant_id)
            
            campaigns = session.execute(query).scalars().all()
            self.campaigns_table.setRowCount(len(campaigns))
            
            for row, c in enumerate(campaigns):
                self.campaigns_table.setItem(row, 0, QTableWidgetItem(c.name or ""))
                self.campaigns_table.setItem(row, 1, QTableWidgetItem(c.campaign_type or ""))
                self.campaigns_table.setItem(row, 2, QTableWidgetItem(c.status or ""))
                self.campaigns_table.setItem(row, 3, QTableWidgetItem(c.start_date.strftime("%d.%m.%Y") if c.start_date else ""))
                self.campaigns_table.setItem(row, 4, QTableWidgetItem(c.end_date.strftime("%d.%m.%Y") if c.end_date else ""))
                self.campaigns_table.setItem(row, 5, QTableWidgetItem(c.budget or ""))
                self.campaigns_table.setItem(row, 6, QTableWidgetItem(c.actual_cost or ""))
                self.campaigns_table.setItem(row, 7, QTableWidgetItem(str(c.actual_leads or 0)))
                self.campaigns_table.setItem(row, 8, QTableWidgetItem(str(c.actual_conversions or 0)))
                self.campaigns_table.setItem(row, 9, QTableWidgetItem(c.actual_revenue or ""))
                
                self.campaigns_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(c.id))
        finally:
            session.close()
    
    def _load_tasks(self):
        """Lädt alle Aufgaben"""
        session = self.db_service.get_session()
        try:
            query = select(Task).where(Task.is_deleted == False).order_by(Task.due_date)
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Task.tenant_id == self.user.tenant_id)
            
            tasks = session.execute(query).scalars().all()
            self.tasks_table.setRowCount(len(tasks))
            
            priority_icons = {"high": "🔴", "normal": "🟡", "low": "🟢", "urgent": "🔴🔴"}
            
            for row, t in enumerate(tasks):
                check_item = QTableWidgetItem()
                check_item.setCheckState(Qt.CheckState.Checked if t.status == "completed" else Qt.CheckState.Unchecked)
                self.tasks_table.setItem(row, 0, check_item)
                self.tasks_table.setItem(row, 1, QTableWidgetItem(priority_icons.get(t.priority, "🟡")))
                self.tasks_table.setItem(row, 2, QTableWidgetItem(t.title or ""))
                self.tasks_table.setItem(row, 3, QTableWidgetItem(""))  # Bezug
                self.tasks_table.setItem(row, 4, QTableWidgetItem(t.due_date.strftime("%d.%m.%Y") if t.due_date else ""))
                self.tasks_table.setItem(row, 5, QTableWidgetItem("Ja" if t.is_recurring else "Nein"))
                self.tasks_table.setItem(row, 6, QTableWidgetItem(""))  # Zugewiesen
                
                self.tasks_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(t.id))
        finally:
            session.close()


class LeadDialog(QDialog):
    """Dialog zum Erstellen von Leads"""
    
    def __init__(self, db_service, lead_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.lead_id = lead_id
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Neuer Lead")
        self.setMinimumSize(600, 600)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        # Firma
        firma_label = QLabel("--- Firmendaten ---")
        firma_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(firma_label)
        
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Firmenname")
        form.addRow("Firma:", self.company_name)
        
        self.industry = QComboBox()
        self.industry.setEditable(True)
        self.industry.addItems(["", "Bauherr privat", "Bauträger", "Architekturbüro", "Generalunternehmer", "Kommune", "Industrie"])
        form.addRow("Branche:", self.industry)
        
        # Kontakt
        kontakt_label = QLabel("--- Ansprechpartner ---")
        kontakt_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(kontakt_label)
        
        self.first_name = QLineEdit()
        form.addRow("Vorname:", self.first_name)
        
        self.last_name = QLineEdit()
        form.addRow("Nachname:", self.last_name)
        
        self.position = QLineEdit()
        self.position.setPlaceholderText("z.B. Geschäftsführer, Bauleiter")
        form.addRow("Position:", self.position)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@beispiel.de")
        form.addRow("E-Mail:", self.email)
        
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+49 123 456789")
        form.addRow("Telefon:", self.phone)
        
        # Lead-Details
        details_label = QLabel("--- Lead-Details ---")
        details_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(details_label)
        
        self.source = QComboBox()
        self.source.addItem("Website", "website")
        self.source.addItem("Empfehlung", "referral")
        self.source.addItem("Messe", "trade_show")
        self.source.addItem("Kaltakquise", "cold_call")
        self.source.addItem("Social Media", "social_media")
        self.source.addItem("Werbung", "advertising")
        self.source.addItem("Sonstige", "other")
        form.addRow("Quelle:", self.source)
        
        self.status = QComboBox()
        self.status.addItem("Neu", "new")
        self.status.addItem("Kontaktiert", "contacted")
        self.status.addItem("Qualifiziert", "qualified")
        self.status.addItem("Angebot", "proposal")
        form.addRow("Status:", self.status)
        
        self.score = QSpinBox()
        self.score.setRange(0, 100)
        self.score.setValue(50)
        self.score.setSuffix(" Punkte")
        form.addRow("Lead-Score:", self.score)
        
        self.estimated_budget = QLineEdit()
        self.estimated_budget.setPlaceholderText("z.B. € 300.000 - 400.000")
        form.addRow("Budget:", self.estimated_budget)
        
        self.project_type = QComboBox()
        self.project_type.addItems(["", "Einfamilienhaus", "Mehrfamilienhaus", "Anbau/Aufstockung", "Gewerbebau", "Öffentlicher Bau"])
        form.addRow("Projektinteresse:", self.project_type)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Beschreibung der Anfrage...")
        form.addRow("Beschreibung:", self.description)
        
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
    
    def save(self):
        session = self.db.get_session()
        try:
            lead = Lead()
            count = session.execute(select(func.count(Lead.id))).scalar() or 0
            lead.lead_number = f"L{datetime.now().year}{count + 1:05d}"
            
            lead.company_name = self.company_name.text().strip() or None
            lead.industry = self.industry.currentText() or None
            lead.first_name = self.first_name.text().strip() or None
            lead.last_name = self.last_name.text().strip() or None
            lead.position = self.position.text().strip() or None
            lead.email = self.email.text().strip() or None
            lead.phone = self.phone.text().strip() or None
            lead.source = self.source.currentData()
            lead.status = self.status.currentData()
            lead.score = self.score.value()
            lead.estimated_budget = self.estimated_budget.text().strip() or None
            lead.project_type_interest = self.project_type.currentText() or None
            lead.description = self.description.toPlainText().strip() or None
            lead.first_contact_date = date.today()
            
            if self.user and hasattr(self.user, 'tenant_id'):
                lead.tenant_id = self.user.tenant_id
            # assigned_to_id verweist auf employees - nicht setzen
            
            session.add(lead)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class OpportunityDialog(QDialog):
    """Dialog zum Erstellen von Opportunities (vereinfacht als Lead mit höherem Status)"""
    
    def __init__(self, db_service, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.user = user
        self.setup_ui()
        self._load_customers()
    
    def setup_ui(self):
        self.setWindowTitle("Neue Opportunity")
        self.setMinimumSize(550, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("z.B. Neubau EFH Familie Müller")
        form.addRow("Bezeichnung*:", self.name)
        
        self.customer_combo = QComboBox()
        form.addRow("Kunde:", self.customer_combo)
        
        self.value = QDoubleSpinBox()
        self.value.setRange(0, 99999999)
        self.value.setDecimals(2)
        self.value.setSuffix(" €")
        form.addRow("Wert*:", self.value)
        
        self.probability = QSpinBox()
        self.probability.setRange(0, 100)
        self.probability.setValue(50)
        self.probability.setSuffix(" %")
        form.addRow("Wahrscheinlichkeit:", self.probability)
        
        self.stage = QComboBox()
        self.stage.addItem("Erstgespräch", "contacted")
        self.stage.addItem("Bedarfsanalyse", "qualified")
        self.stage.addItem("Angebot", "proposal")
        self.stage.addItem("Verhandlung", "negotiation")
        form.addRow("Phase:", self.stage)
        
        self.expected_close = QDateEdit()
        self.expected_close.setCalendarPopup(True)
        self.expected_close.setDate(QDate.currentDate().addMonths(3))
        form.addRow("Erwarteter Abschluss:", self.expected_close)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setPlaceholderText("Beschreibung der Opportunity...")
        form.addRow("Beschreibung:", self.description)
        
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
    
    def _load_customers(self):
        session = self.db.get_session()
        try:
            query = select(Customer).where(Customer.is_deleted == False).order_by(Customer.company_name)
            customers = session.execute(query).scalars().all()
            self.customer_combo.addItem("-- Kunde wählen --", None)
            for c in customers:
                name = c.company_name or f"{c.first_name} {c.last_name}"
                self.customer_combo.addItem(f"{c.customer_number} - {name}", str(c.id))
        finally:
            session.close()
    
    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Bezeichnung eingeben.")
            return
        
        session = self.db.get_session()
        try:
            # Opportunity als Lead mit erweiterten Feldern speichern
            lead = Lead()
            count = session.execute(select(func.count(Lead.id))).scalar() or 0
            lead.lead_number = f"OPP{datetime.now().year}{count + 1:05d}"
            
            lead.company_name = self.name.text().strip()
            lead.status = self.stage.currentData()
            lead.score = self.probability.value()
            lead.estimated_budget = str(self.value.value())
            lead.description = self.description.toPlainText().strip() or None
            lead.first_contact_date = date.today()
            
            if self.user and hasattr(self.user, 'tenant_id'):
                lead.tenant_id = self.user.tenant_id
            
            session.add(lead)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class CampaignDialog(QDialog):
    """Dialog zum Erstellen von Marketing-Kampagnen"""
    
    def __init__(self, db_service, campaign_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.campaign_id = campaign_id
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Neue Kampagne")
        self.setMinimumSize(550, 500)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("Kampagnenname")
        form.addRow("Name*:", self.name)
        
        self.campaign_type = QComboBox()
        self.campaign_type.addItems(["E-Mail-Kampagne", "Messe", "Event", "Social Media", "Print-Werbung", "Online-Anzeigen", "Sonstiges"])
        form.addRow("Typ:", self.campaign_type)
        
        self.status = QComboBox()
        self.status.addItem("Geplant", "planned")
        self.status.addItem("Aktiv", "active")
        self.status.addItem("Pausiert", "paused")
        self.status.addItem("Abgeschlossen", "completed")
        form.addRow("Status:", self.status)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        form.addRow("Startdatum:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        form.addRow("Enddatum:", self.end_date)
        
        self.budget = QDoubleSpinBox()
        self.budget.setRange(0, 9999999)
        self.budget.setDecimals(2)
        self.budget.setSuffix(" €")
        form.addRow("Budget:", self.budget)
        
        # Ziele
        ziele_label = QLabel("--- Ziele ---")
        ziele_label.setStyleSheet("font-weight: bold; color: #374151;")
        form.addRow(ziele_label)
        
        self.target_leads = QSpinBox()
        self.target_leads.setRange(0, 9999)
        form.addRow("Ziel-Leads:", self.target_leads)
        
        self.target_conversions = QSpinBox()
        self.target_conversions.setRange(0, 999)
        form.addRow("Ziel-Conversions:", self.target_conversions)
        
        self.target_revenue = QDoubleSpinBox()
        self.target_revenue.setRange(0, 99999999)
        self.target_revenue.setDecimals(2)
        self.target_revenue.setSuffix(" €")
        form.addRow("Ziel-Umsatz:", self.target_revenue)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Beschreibung der Kampagne...")
        form.addRow("Beschreibung:", self.description)
        
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
    
    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Kampagnenname eingeben.")
            return
        
        session = self.db.get_session()
        try:
            campaign = Campaign()
            campaign.name = self.name.text().strip()
            campaign.campaign_type = self.campaign_type.currentText()
            campaign.status = self.status.currentData()
            campaign.start_date = self.start_date.date().toPyDate()
            campaign.end_date = self.end_date.date().toPyDate()
            campaign.budget = str(self.budget.value()) if self.budget.value() > 0 else None
            campaign.target_leads = self.target_leads.value() if self.target_leads.value() > 0 else None
            campaign.target_conversions = self.target_conversions.value() if self.target_conversions.value() > 0 else None
            campaign.target_revenue = str(self.target_revenue.value()) if self.target_revenue.value() > 0 else None
            campaign.description = self.description.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                campaign.tenant_id = self.user.tenant_id
            # responsible_id verweist auf employees - nicht setzen
            
            session.add(campaign)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class TaskDialog(QDialog):
    """Dialog zum Erstellen von Aufgaben"""
    
    def __init__(self, db_service, task_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.task_id = task_id
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Neue Aufgabe")
        self.setMinimumSize(500, 450)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.title = QLineEdit()
        self.title.setPlaceholderText("Aufgabentitel")
        form.addRow("Titel*:", self.title)
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Beschreibung der Aufgabe...")
        form.addRow("Beschreibung:", self.description)
        
        self.priority = QComboBox()
        self.priority.addItem("🟢 Niedrig", "low")
        self.priority.addItem("🟡 Normal", "normal")
        self.priority.addItem("🔴 Hoch", "high")
        self.priority.addItem("🔴🔴 Dringend", "urgent")
        self.priority.setCurrentIndex(1)
        form.addRow("Priorität:", self.priority)
        
        self.status = QComboBox()
        self.status.addItem("Offen", "open")
        self.status.addItem("In Bearbeitung", "in_progress")
        self.status.addItem("Erledigt", "completed")
        form.addRow("Status:", self.status)
        
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate().addDays(7))
        form.addRow("Fällig am:", self.due_date)
        
        self.estimated_hours = QDoubleSpinBox()
        self.estimated_hours.setRange(0, 999)
        self.estimated_hours.setDecimals(1)
        self.estimated_hours.setSuffix(" Std")
        form.addRow("Geschätzter Aufwand:", self.estimated_hours)
        
        # Wiederholung
        self.is_recurring = QCheckBox("Wiederkehrende Aufgabe")
        form.addRow("", self.is_recurring)
        
        self.recurrence = QComboBox()
        self.recurrence.addItems(["Täglich", "Wöchentlich", "Monatlich", "Jährlich"])
        self.recurrence.setEnabled(False)
        self.is_recurring.toggled.connect(self.recurrence.setEnabled)
        form.addRow("Wiederholung:", self.recurrence)
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Weitere Notizen...")
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
    
    def save(self):
        if not self.title.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Titel eingeben.")
            return
        
        session = self.db.get_session()
        try:
            task = Task()
            count = session.execute(select(func.count(Task.id))).scalar() or 0
            task.task_number = f"T{datetime.now().year}{count + 1:05d}"
            
            task.title = self.title.text().strip()
            task.description = self.description.toPlainText().strip() or None
            task.priority = self.priority.currentData()
            task.status = self.status.currentData()
            task.due_date = self.due_date.date().toPyDate()
            task.estimated_hours = str(self.estimated_hours.value()) if self.estimated_hours.value() > 0 else None
            task.is_recurring = self.is_recurring.isChecked()
            if task.is_recurring:
                recurrence_map = {"Täglich": "daily", "Wöchentlich": "weekly", "Monatlich": "monthly", "Jährlich": "yearly"}
                task.recurrence_pattern = recurrence_map.get(self.recurrence.currentText())
            task.notes = self.notes.toPlainText().strip() or None
            
            if self.user and hasattr(self.user, 'tenant_id'):
                task.tenant_id = self.user.tenant_id
            # assigned_to_id/assigned_by_id verweisen auf employees - nicht setzen
            
            session.add(task)
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
