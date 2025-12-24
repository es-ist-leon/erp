"""
Payroll Widget - Lohnverwaltung und Gehaltsabrechnung UI
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QDialog, QFormLayout, QMessageBox, QTabWidget, QHeaderView,
    QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QFrame, QProgressBar, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, date
from decimal import Decimal


class PayrollWidget(QWidget):
    """Hauptwidget für die Lohnverwaltung"""
    
    def __init__(self, db_service, user):
        super().__init__()
        self.db_service = db_service
        self.user = user
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #f8fafc;
            }
            QTabBar::tab {
                background: #e2e8f0;
                color: #64748b;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: #f8fafc;
                color: #1e293b;
            }
            QTabBar::tab:hover:!selected {
                background: #cbd5e1;
            }
        """)
        
        # Tabs hinzufügen
        self.tabs.addTab(self._create_dashboard_tab(), "📊 Übersicht")
        self.tabs.addTab(self._create_payslips_tab(), "📄 Lohnabrechnungen")
        self.tabs.addTab(self._create_employees_tab(), "👥 Mitarbeiter")
        self.tabs.addTab(self._create_salary_tab(), "💵 Gehaltsstrukturen")
        self.tabs.addTab(self._create_deductions_tab(), "📉 Abzüge & Zulagen")
        self.tabs.addTab(self._create_bonuses_tab(), "🎁 Sonderzahlungen")
        self.tabs.addTab(self._create_reports_tab(), "📈 Berichte & Meldungen")
        self.tabs.addTab(self._create_settings_tab(), "⚙️ Einstellungen")
        
        layout.addWidget(self.tabs)
    
    def _create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom: 1px solid #e2e8f0;
                padding: 16px;
            }
        """)
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        
        # Titel
        title = QLabel("💼 Lohnverwaltung")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Aktuelle Periode
        period_label = QLabel("Aktuelle Periode:")
        period_label.setStyleSheet("color: #64748b; border: none;")
        layout.addWidget(period_label)
        
        self.current_period = QComboBox()
        self.current_period.addItems([
            "Dezember 2025", "November 2025", "Oktober 2025",
            "September 2025", "August 2025"
        ])
        self.current_period.setStyleSheet(self._input_style())
        layout.addWidget(self.current_period)
        
        # Schnellaktionen
        btn_style = """
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """
        
        run_payroll_btn = QPushButton("▶️ Lohnlauf starten")
        run_payroll_btn.setStyleSheet(btn_style.replace("#3b82f6", "#10b981").replace("#2563eb", "#059669"))
        run_payroll_btn.clicked.connect(self.start_payroll_run)
        layout.addWidget(run_payroll_btn)
        
        return header
    
    def _create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        kpis = [
            ("Personalkosten (Monat)", "€ 145.230,00", "32 Mitarbeiter", "#3b82f6"),
            ("Bruttolohn Ø", "€ 3.850,00", "pro Mitarbeiter", "#10b981"),
            ("SV-Beiträge AG", "€ 28.450,00", "19.6%", "#f59e0b"),
            ("Lohnsteuer", "€ 22.180,00", "zu melden", "#8b5cf6"),
        ]
        
        for title, value, subtitle, color in kpis:
            card = self._create_kpi_card(title, value, subtitle, color)
            kpi_layout.addWidget(card)
        
        layout.addLayout(kpi_layout)
        
        # Zwei Spalten
        content_layout = QHBoxLayout()
        
        # Lohnlauf Status
        status_group = QGroupBox("📊 Lohnlauf Status - Dezember 2025")
        status_group.setStyleSheet(self._group_style())
        status_layout = QVBoxLayout(status_group)
        
        # Progress
        progress_layout = QVBoxLayout()
        
        steps = [
            ("✅ Daten erfasst", 100, True),
            ("✅ Abwesenheiten verarbeitet", 100, True),
            ("🔄 Berechnungen", 65, False),
            ("⏳ Prüfung", 0, False),
            ("⏳ Freigabe", 0, False),
            ("⏳ Auszahlung", 0, False),
        ]
        
        for step_name, progress, completed in steps:
            step_widget = QWidget()
            step_layout = QHBoxLayout(step_widget)
            step_layout.setContentsMargins(0, 4, 0, 4)
            
            label = QLabel(step_name)
            label.setFixedWidth(200)
            if completed:
                label.setStyleSheet("color: #10b981;")
            step_layout.addWidget(label)
            
            progress_bar = QProgressBar()
            progress_bar.setValue(progress)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background: #e2e8f0;
                    height: 8px;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background: #10b981;
                    border-radius: 4px;
                }
            """)
            step_layout.addWidget(progress_bar)
            
            progress_layout.addWidget(step_widget)
        
        status_layout.addLayout(progress_layout)
        
        # Action Buttons
        actions_layout = QHBoxLayout()
        
        continue_btn = QPushButton("▶️ Fortsetzen")
        continue_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        actions_layout.addWidget(continue_btn)
        
        details_btn = QPushButton("📋 Details")
        details_btn.setStyleSheet(self._button_style())
        actions_layout.addWidget(details_btn)
        
        actions_layout.addStretch()
        status_layout.addLayout(actions_layout)
        
        content_layout.addWidget(status_group, 2)
        
        # Schnellzugriff
        quick_group = QGroupBox("⚡ Schnellzugriff")
        quick_group.setStyleSheet(self._group_style())
        quick_layout = QVBoxLayout(quick_group)
        
        quick_actions = [
            ("📄 Neue Lohnabrechnung", self.new_payslip),
            ("👤 Mitarbeiter anlegen", self.new_employee),
            ("📅 Abwesenheit erfassen", self.new_absence),
            ("💰 Bonus erfassen", self.new_bonus),
            ("📤 SV-Meldung erstellen", self.create_sv_report),
            ("📑 Lohnsteuer-Anmeldung", self.create_tax_report),
        ]
        
        for text, callback in quick_actions:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f1f5f9;
                    border: 1px solid #e2e8f0;
                    padding: 12px;
                    border-radius: 6px;
                    text-align: left;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                }
            """)
            btn.clicked.connect(callback)
            quick_layout.addWidget(btn)
        
        quick_layout.addStretch()
        content_layout.addWidget(quick_group, 1)
        
        layout.addLayout(content_layout)
        
        # Letzte Aktivitäten
        recent_group = QGroupBox("📝 Letzte Aktivitäten")
        recent_group.setStyleSheet(self._group_style())
        recent_layout = QVBoxLayout(recent_group)
        
        activities = [
            ("Lohnabrechnung erstellt", "Max Mustermann", "vor 2 Stunden"),
            ("Bonus genehmigt", "Erika Muster", "vor 3 Stunden"),
            ("Krankheit erfasst", "Hans Beispiel", "vor 5 Stunden"),
            ("SV-Meldung übermittelt", "System", "gestern"),
        ]
        
        for title, name, time in activities:
            activity = QLabel(f"• {title} - {name} ({time})")
            activity.setStyleSheet("color: #64748b; padding: 4px 0;")
            recent_layout.addWidget(activity)
        
        layout.addWidget(recent_group)
        
        return widget
    
    def _create_payslips_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Filter
        toolbar.addWidget(QLabel("Periode:"))
        period_filter = QComboBox()
        period_filter.addItems([
            "Dezember 2025", "November 2025", "Oktober 2025"
        ])
        period_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(period_filter)
        
        toolbar.addWidget(QLabel("Status:"))
        status_filter = QComboBox()
        status_filter.addItems(["Alle", "Entwurf", "Berechnet", "Freigegeben", "Ausgezahlt"])
        status_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(status_filter)
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Mitarbeiter suchen...")
        search.setStyleSheet(self._input_style())
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        new_btn = QPushButton("+ Neue Abrechnung")
        new_btn.setStyleSheet(self._button_style())
        new_btn.clicked.connect(self.new_payslip)
        toolbar.addWidget(new_btn)
        
        batch_btn = QPushButton("📦 Sammelabrechnung")
        batch_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        toolbar.addWidget(batch_btn)
        
        layout.addLayout(toolbar)
        
        # Tabelle
        self.payslips_table = QTableWidget()
        self.payslips_table.setColumnCount(10)
        self.payslips_table.setHorizontalHeaderLabels([
            "Nr.", "Mitarbeiter", "Pers.-Nr.", "Brutto", "SV AN",
            "Steuer", "Netto", "AG-Kosten", "Status", "Aktionen"
        ])
        self.payslips_table.horizontalHeader().setStretchLastSection(True)
        self.payslips_table.setStyleSheet(self._table_style())
        
        # Daten aus Datenbank laden
        self._load_payslips_data()
        
        layout.addWidget(self.payslips_table)
        
        # Summenzeile
        sums_layout = QHBoxLayout()
        sums_layout.addStretch()
        
        sums = [
            ("Brutto gesamt:", "€ 11.500,00"),
            ("SV AN gesamt:", "€ 2.173,50"),
            ("Steuer gesamt:", "€ 1.720,00"),
            ("Netto gesamt:", "€ 7.606,50"),
            ("AG-Kosten gesamt:", "€ 13.767,50"),
        ]
        
        for label, value in sums:
            sum_label = QLabel(f"{label} {value}")
            sum_label.setStyleSheet("font-weight: bold; margin-left: 20px;")
            sums_layout.addWidget(sum_label)
        
        layout.addLayout(sums_layout)
        
        return widget
    
    def _create_employees_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Mitarbeiter suchen...")
        search.setStyleSheet(self._input_style())
        search.setFixedWidth(300)
        toolbar.addWidget(search)
        
        toolbar.addWidget(QLabel("Abteilung:"))
        dept_filter = QComboBox()
        dept_filter.addItems(["Alle", "Produktion", "Montage", "Verwaltung", "Planung"])
        dept_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(dept_filter)
        
        toolbar.addStretch()
        
        new_btn = QPushButton("+ Mitarbeiter anlegen")
        new_btn.setStyleSheet(self._button_style())
        new_btn.clicked.connect(self.new_employee)
        toolbar.addWidget(new_btn)
        
        layout.addLayout(toolbar)
        
        # Tabelle
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(9)
        self.employees_table.setHorizontalHeaderLabels([
            "Pers.-Nr.", "Name", "Abteilung", "Position", "Eintrittsdatum",
            "Stunden/Woche", "Gehalt", "Steuerklasse", "Status"
        ])
        self.employees_table.setStyleSheet(self._table_style())
        
        # Daten aus Datenbank laden
        self._load_employees_table_data()
        
        layout.addWidget(self.employees_table)
        
        return widget
    
    def _create_salary_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Gehaltsbestandteile
        components_group = QGroupBox("💵 Gehaltsbestandteile")
        components_group.setStyleSheet(self._group_style())
        components_layout = QVBoxLayout(components_group)
        
        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("+ Neue Komponente")
        add_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(add_btn)
        toolbar.addStretch()
        components_layout.addLayout(toolbar)
        
        # Tabelle
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(6)
        self.components_table.setHorizontalHeaderLabels([
            "Code", "Bezeichnung", "Typ", "Berechnung", "Steuerpflichtig", "SV-pflichtig"
        ])
        self.components_table.setStyleSheet(self._table_style())
        
        components = [
            ("GRUND", "Grundgehalt", "Bezug", "Fest", "✓", "✓"),
            ("UEBER", "Überstunden", "Bezug", "Stunden × Satz", "✓", "✓"),
            ("FAHRT", "Fahrkostenzuschuss", "Bezug", "Fest", "✗", "✗"),
            ("LST", "Lohnsteuer", "Abzug", "Steuertabelle", "-", "-"),
            ("KV_AN", "Krankenversicherung AN", "Abzug", "% vom Brutto", "-", "-"),
            ("RV_AN", "Rentenversicherung AN", "Abzug", "9.3% vom Brutto", "-", "-"),
        ]
        
        self.components_table.setRowCount(len(components))
        for row, data in enumerate(components):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 2:  # Typ
                    if value == "Bezug":
                        item.setForeground(QColor("#10b981"))
                    else:
                        item.setForeground(QColor("#ef4444"))
                self.components_table.setItem(row, col, item)
        
        components_layout.addWidget(self.components_table)
        layout.addWidget(components_group)
        
        # Tarifgruppen
        tariff_group = QGroupBox("📋 Tarifgruppen / Lohngruppen")
        tariff_group.setStyleSheet(self._group_style())
        tariff_layout = QVBoxLayout(tariff_group)
        
        self.tariff_table = QTableWidget()
        self.tariff_table.setColumnCount(5)
        self.tariff_table.setHorizontalHeaderLabels([
            "Lohngruppe", "Bezeichnung", "Stundensatz", "Monatsgehalt", "Mitarbeiter"
        ])
        self.tariff_table.setStyleSheet(self._table_style())
        
        tariffs = [
            ("LG1", "Hilfsarbeiter", "€ 15,00", "€ 2.600,00", "3"),
            ("LG2", "Facharbeiter", "€ 18,50", "€ 3.200,00", "12"),
            ("LG3", "Vorarbeiter", "€ 22,00", "€ 3.800,00", "5"),
            ("LG4", "Meister", "€ 26,00", "€ 4.500,00", "2"),
        ]
        
        self.tariff_table.setRowCount(len(tariffs))
        for row, data in enumerate(tariffs):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                self.tariff_table.setItem(row, col, item)
        
        tariff_layout.addWidget(self.tariff_table)
        layout.addWidget(tariff_group)
        
        return widget
    
    def _create_deductions_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Splitter für Abzüge und Zulagen
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Abzüge
        deductions_group = QGroupBox("📉 Abzüge")
        deductions_group.setStyleSheet(self._group_style())
        deductions_layout = QVBoxLayout(deductions_group)
        
        self.deductions_table = QTableWidget()
        self.deductions_table.setColumnCount(5)
        self.deductions_table.setHorizontalHeaderLabels([
            "Mitarbeiter", "Typ", "Betrag", "Von", "Bis"
        ])
        self.deductions_table.setStyleSheet(self._table_style())
        
        deductions = [
            ("Max Mustermann", "Vorschuss", "€ 500,00", "01.12.2025", "31.12.2025"),
            ("Hans Beispiel", "Pfändung", "€ 350,00", "01.01.2025", "offen"),
        ]
        
        self.deductions_table.setRowCount(len(deductions))
        for row, data in enumerate(deductions):
            for col, value in enumerate(data):
                self.deductions_table.setItem(row, col, QTableWidgetItem(value))
        
        deductions_layout.addWidget(self.deductions_table)
        
        add_deduction_btn = QPushButton("+ Abzug hinzufügen")
        add_deduction_btn.setStyleSheet(self._button_style())
        deductions_layout.addWidget(add_deduction_btn)
        
        splitter.addWidget(deductions_group)
        
        # Zulagen
        allowances_group = QGroupBox("📈 Zulagen")
        allowances_group.setStyleSheet(self._group_style())
        allowances_layout = QVBoxLayout(allowances_group)
        
        self.allowances_table = QTableWidget()
        self.allowances_table.setColumnCount(5)
        self.allowances_table.setHorizontalHeaderLabels([
            "Mitarbeiter", "Typ", "Betrag", "Von", "Bis"
        ])
        self.allowances_table.setStyleSheet(self._table_style())
        
        allowances = [
            ("Max Mustermann", "Fahrtkostenzuschuss", "€ 100,00", "01.01.2025", "31.12.2025"),
            ("Erika Muster", "VWL", "€ 40,00", "01.01.2025", "31.12.2025"),
            ("Hans Beispiel", "Nachtschichtzulage", "€ 150,00", "01.12.2025", "31.12.2025"),
        ]
        
        self.allowances_table.setRowCount(len(allowances))
        for row, data in enumerate(allowances):
            for col, value in enumerate(data):
                self.allowances_table.setItem(row, col, QTableWidgetItem(value))
        
        allowances_layout.addWidget(self.allowances_table)
        
        add_allowance_btn = QPushButton("+ Zulage hinzufügen")
        add_allowance_btn.setStyleSheet(self._button_style())
        allowances_layout.addWidget(add_allowance_btn)
        
        splitter.addWidget(allowances_group)
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_bonuses_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        new_bonus_btn = QPushButton("+ Neuer Bonus")
        new_bonus_btn.setStyleSheet(self._button_style())
        new_bonus_btn.clicked.connect(self.new_bonus)
        toolbar.addWidget(new_bonus_btn)
        
        mass_bonus_btn = QPushButton("📦 Sammelbonus")
        mass_bonus_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        toolbar.addWidget(mass_bonus_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Geplante Sonderzahlungen
        planned_group = QGroupBox("📅 Geplante Sonderzahlungen")
        planned_group.setStyleSheet(self._group_style())
        planned_layout = QVBoxLayout(planned_group)
        
        self.bonuses_table = QTableWidget()
        self.bonuses_table.setColumnCount(7)
        self.bonuses_table.setHorizontalHeaderLabels([
            "Mitarbeiter", "Art", "Bezeichnung", "Bruttobetrag",
            "Auszahlung", "Genehmigt", "Status"
        ])
        self.bonuses_table.setStyleSheet(self._table_style())
        
        bonuses = [
            ("Alle", "Weihnachtsgeld", "Weihnachtsgeld 2025", "€ 45.000,00", "Dez 2025", "✓", "Geplant"),
            ("Max Mustermann", "Leistungsbonus", "Q4 Bonus", "€ 1.500,00", "Dez 2025", "✓", "Genehmigt"),
            ("Erika Muster", "Jubiläum", "10 Jahre Betriebszugehörigkeit", "€ 1.000,00", "Jan 2026", "✗", "Ausstehend"),
        ]
        
        self.bonuses_table.setRowCount(len(bonuses))
        for row, data in enumerate(bonuses):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 6:  # Status
                    if value == "Genehmigt":
                        item.setForeground(QColor("#10b981"))
                    elif value == "Geplant":
                        item.setForeground(QColor("#3b82f6"))
                    else:
                        item.setForeground(QColor("#f59e0b"))
                self.bonuses_table.setItem(row, col, item)
        
        planned_layout.addWidget(self.bonuses_table)
        layout.addWidget(planned_group)
        
        return widget
    
    def _create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Meldungen
        reports_layout = QHBoxLayout()
        
        reports = [
            ("📤 SV-Meldung", "Sozialversicherungsmeldung erstellen", self.create_sv_report),
            ("📑 Lohnsteuer", "Lohnsteuer-Anmeldung (ELSTER)", self.create_tax_report),
            ("📊 Lohnjournal", "Lohnjournal drucken", self.print_payroll_journal),
            ("📋 Jahresmeldung", "SV-Jahresmeldung", self.create_annual_report),
            ("📄 Lohnkonten", "Lohnkonten drucken", self.print_wage_accounts),
            ("💰 Statistik", "Lohnstatistik", self.show_statistics),
        ]
        
        for icon_title, description, callback in reports:
            card = self._create_report_card(icon_title, description, callback)
            reports_layout.addWidget(card)
        
        layout.addLayout(reports_layout)
        
        # Letzte Meldungen
        history_group = QGroupBox("📜 Meldungshistorie")
        history_group.setStyleSheet(self._group_style())
        history_layout = QVBoxLayout(history_group)
        
        self.reports_history_table = QTableWidget()
        self.reports_history_table.setColumnCount(6)
        self.reports_history_table.setHorizontalHeaderLabels([
            "Datum", "Meldungsart", "Zeitraum", "Referenz", "Status", "Aktionen"
        ])
        self.reports_history_table.setStyleSheet(self._table_style())
        
        history = [
            ("15.12.2025", "Lohnsteuer-Anmeldung", "Nov 2025", "LST-2025-11", "Übermittelt", ""),
            ("10.12.2025", "SV-Beitragsmeldung", "Nov 2025", "SV-2025-11", "Übermittelt", ""),
            ("15.11.2025", "Lohnsteuer-Anmeldung", "Okt 2025", "LST-2025-10", "Übermittelt", ""),
        ]
        
        self.reports_history_table.setRowCount(len(history))
        for row, data in enumerate(history):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 4 and value == "Übermittelt":
                    item.setForeground(QColor("#10b981"))
                self.reports_history_table.setItem(row, col, item)
        
        history_layout.addWidget(self.reports_history_table)
        layout.addWidget(history_group)
        
        return widget
    
    def _create_settings_tab(self):
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f8fafc; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Allgemeine Einstellungen
        general_group = QGroupBox("⚙️ Allgemeine Einstellungen")
        general_group.setStyleSheet(self._group_style())
        general_form = QFormLayout(general_group)
        
        self.payroll_day = QSpinBox()
        self.payroll_day.setRange(1, 28)
        self.payroll_day.setValue(25)
        general_form.addRow("Auszahlungstag:", self.payroll_day)
        
        self.sv_number = QLineEdit()
        self.sv_number.setPlaceholderText("Betriebsnummer Sozialversicherung")
        general_form.addRow("Betriebsnummer:", self.sv_number)
        
        self.tax_number = QLineEdit()
        self.tax_number.setPlaceholderText("Steuernummer Lohnsteuer")
        general_form.addRow("Steuernummer:", self.tax_number)
        
        layout.addWidget(general_group)
        
        # SV-Beitragssätze
        sv_group = QGroupBox("📊 Sozialversicherungsbeiträge 2025")
        sv_group.setStyleSheet(self._group_style())
        sv_form = QFormLayout(sv_group)
        
        sv_rates = [
            ("Krankenversicherung:", "14,6 % + Zusatzbeitrag"),
            ("Rentenversicherung:", "18,6 %"),
            ("Arbeitslosenversicherung:", "2,6 %"),
            ("Pflegeversicherung:", "3,4 %"),
            ("Beitragsbemessungsgrenze KV:", "€ 62.100 / Jahr"),
            ("Beitragsbemessungsgrenze RV:", "€ 90.600 / Jahr (West)"),
        ]
        
        for label, value in sv_rates:
            value_label = QLabel(value)
            value_label.setStyleSheet("font-weight: bold;")
            sv_form.addRow(label, value_label)
        
        layout.addWidget(sv_group)
        
        # Bankverbindung
        bank_group = QGroupBox("🏦 Bankverbindung für Gehaltszahlungen")
        bank_group.setStyleSheet(self._group_style())
        bank_form = QFormLayout(bank_group)
        
        self.salary_bank = QLineEdit()
        self.salary_bank.setPlaceholderText("Bankname")
        bank_form.addRow("Bank:", self.salary_bank)
        
        self.salary_iban = QLineEdit()
        self.salary_iban.setPlaceholderText("DE...")
        bank_form.addRow("IBAN:", self.salary_iban)
        
        self.salary_bic = QLineEdit()
        self.salary_bic.setPlaceholderText("BIC")
        bank_form.addRow("BIC:", self.salary_bic)
        
        layout.addWidget(bank_group)
        
        # Speichern Button
        save_btn = QPushButton("💾 Einstellungen speichern")
        save_btn.setStyleSheet(self._button_style())
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        return widget
    
    def _create_kpi_card(self, title, value, subtitle, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        layout.addWidget(subtitle_label)
        
        return card
    
    def _create_report_card(self, title, description, callback):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QFrame:hover {
                border-color: #3b82f6;
            }
        """)
        card.setFixedSize(180, 160)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #64748b; font-size: 11px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        btn = QPushButton("Erstellen")
        btn.setStyleSheet(self._button_style())
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
        return card
    
    def _group_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """
    
    def _table_style(self):
        return """
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
            QHeaderView::section {
                background: #f8fafc;
                color: #64748b;
                font-weight: 600;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
            }
        """
    
    def _input_style(self):
        return """
            QLineEdit, QComboBox, QSpinBox {
                padding: 10px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #3b82f6;
            }
        """
    
    def _button_style(self):
        return """
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """
    
    # === AKTIONEN ===
    
    def _load_payslips_data(self):
        """Lädt Lohnabrechnungen aus der Datenbank"""
        try:
            # Leere Tabelle für neue Daten
            self.payslips_table.setRowCount(0)
            # Echte Daten würden hier aus der DB geladen
        except Exception as e:
            print(f"Fehler beim Laden der Lohnabrechnungen: {e}")
    
    def _load_employees_table_data(self):
        """Lädt Mitarbeiter aus der Datenbank"""
        try:
            from app.models.employee import Employee
            employees = self.db_service.get_session().query(Employee).filter(
                Employee.is_deleted == False
            ).all()
            
            self.employees_table.setRowCount(len(employees))
            for row, emp in enumerate(employees):
                # Pers.-Nr.
                self.employees_table.setItem(row, 0, QTableWidgetItem(emp.employee_number or ""))
                # Name
                name = f"{emp.first_name or ''} {emp.last_name or ''}".strip()
                self.employees_table.setItem(row, 1, QTableWidgetItem(name))
                # Abteilung
                self.employees_table.setItem(row, 2, QTableWidgetItem(emp.department or ""))
                # Position
                self.employees_table.setItem(row, 3, QTableWidgetItem(emp.position or ""))
                # Eintrittsdatum
                entry = emp.entry_date.strftime("%d.%m.%Y") if emp.entry_date else ""
                self.employees_table.setItem(row, 4, QTableWidgetItem(entry))
                # Stunden/Woche
                hours = str(emp.weekly_hours) if emp.weekly_hours else "40"
                self.employees_table.setItem(row, 5, QTableWidgetItem(hours))
                # Gehalt
                salary = f"€ {emp.salary:,.2f}" if emp.salary else ""
                item = QTableWidgetItem(salary)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.employees_table.setItem(row, 6, item)
                # Steuerklasse
                self.employees_table.setItem(row, 7, QTableWidgetItem(str(emp.tax_class) if emp.tax_class else ""))
                # Status
                status = emp.employment_status or "Aktiv"
                status_item = QTableWidgetItem(status)
                if status == "Aktiv":
                    status_item.setForeground(QColor("#10b981"))
                elif status == "Teilzeit":
                    status_item.setForeground(QColor("#3b82f6"))
                self.employees_table.setItem(row, 8, status_item)
        except Exception as e:
            print(f"Fehler beim Laden der Mitarbeiter: {e}")
    
    def start_payroll_run(self):
        """Startet den Lohnlauf"""
        QMessageBox.information(self, "Lohnlauf", "Lohnlauf wird gestartet...")
    
    def new_payslip(self):
        """Neue Lohnabrechnung erstellen"""
        dialog = PayslipDialog(self.db_service, self.user, self)
        dialog.exec()
    
    def new_employee(self):
        """Neuen Mitarbeiter anlegen"""
        QMessageBox.information(self, "Info", "Mitarbeiter-Dialog wird implementiert...")
    
    def new_absence(self):
        """Abwesenheit erfassen"""
        QMessageBox.information(self, "Info", "Abwesenheit erfassen...")
    
    def new_bonus(self):
        """Bonus erfassen"""
        dialog = BonusDialog(self.db_service, self.user, self)
        dialog.exec()
    
    def create_sv_report(self):
        """SV-Meldung erstellen"""
        QMessageBox.information(self, "Info", "SV-Meldung wird erstellt...")
    
    def create_tax_report(self):
        """Lohnsteuer-Anmeldung erstellen"""
        QMessageBox.information(self, "Info", "Lohnsteuer-Anmeldung wird erstellt...")
    
    def print_payroll_journal(self):
        """Lohnjournal drucken"""
        QMessageBox.information(self, "Info", "Lohnjournal wird erstellt...")
    
    def create_annual_report(self):
        """Jahresmeldung erstellen"""
        QMessageBox.information(self, "Info", "Jahresmeldung wird erstellt...")
    
    def print_wage_accounts(self):
        """Lohnkonten drucken"""
        QMessageBox.information(self, "Info", "Lohnkonten werden erstellt...")
    
    def show_statistics(self):
        """Statistik anzeigen"""
        QMessageBox.information(self, "Info", "Statistik wird angezeigt...")
    
    def save_settings(self):
        """Einstellungen speichern"""
        QMessageBox.information(self, "Erfolg", "Einstellungen wurden gespeichert!")


class PayslipDialog(QDialog):
    """Dialog für neue Lohnabrechnung"""
    
    def __init__(self, db_service, user, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.setWindowTitle("Neue Lohnabrechnung")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Mitarbeiter auswählen
        employee_group = QGroupBox("👤 Mitarbeiter")
        employee_form = QFormLayout(employee_group)
        
        self.employee_combo = QComboBox()
        self._load_employees_combo()
        employee_form.addRow("Mitarbeiter:", self.employee_combo)
        
        self.period_combo = QComboBox()
        self._load_periods_combo()
        employee_form.addRow("Abrechnungsperiode:", self.period_combo)
        
        layout.addWidget(employee_group)
        
        # Arbeitszeit
        time_group = QGroupBox("⏰ Arbeitszeit")
        time_form = QFormLayout(time_group)
        
        self.work_days = QSpinBox()
        self.work_days.setRange(0, 31)
        self.work_days.setValue(22)
        time_form.addRow("Arbeitstage:", self.work_days)
        
        self.work_hours = QDoubleSpinBox()
        self.work_hours.setRange(0, 400)
        self.work_hours.setValue(176)
        time_form.addRow("Arbeitsstunden:", self.work_hours)
        
        self.overtime_hours = QDoubleSpinBox()
        self.overtime_hours.setRange(0, 100)
        self.overtime_hours.setValue(0)
        time_form.addRow("Überstunden:", self.overtime_hours)
        
        layout.addWidget(time_group)
        
        # Berechnung
        calc_group = QGroupBox("💰 Berechnung")
        calc_layout = QVBoxLayout(calc_group)
        
        calc_btn = QPushButton("🔄 Berechnen")
        calc_btn.clicked.connect(self.calculate)
        calc_layout.addWidget(calc_btn)
        
        # Ergebnisse
        self.result_layout = QFormLayout()
        self.gross_label = QLabel("€ 0,00")
        self.gross_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.result_layout.addRow("Brutto:", self.gross_label)
        
        self.tax_label = QLabel("€ 0,00")
        self.result_layout.addRow("Lohnsteuer:", self.tax_label)
        
        self.sv_label = QLabel("€ 0,00")
        self.result_layout.addRow("SV AN:", self.sv_label)
        
        self.net_label = QLabel("€ 0,00")
        self.net_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.net_label.setStyleSheet("color: #10b981;")
        self.result_layout.addRow("Netto:", self.net_label)
        
        calc_layout.addLayout(self.result_layout)
        layout.addWidget(calc_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
        """)
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_employees_combo(self):
        """Lädt Mitarbeiter in Combobox"""
        try:
            from app.models.employee import Employee
            employees = self.db_service.get_session().query(Employee).filter(
                Employee.is_deleted == False
            ).all()
            for emp in employees:
                name = f"{emp.first_name or ''} {emp.last_name or ''} ({emp.employee_number or ''})".strip()
                self.employee_combo.addItem(name, emp.id)
        except Exception as e:
            print(f"Fehler beim Laden der Mitarbeiter: {e}")
    
    def _load_periods_combo(self):
        """Lädt Abrechnungsperioden"""
        from datetime import datetime
        now = datetime.now()
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
                  "Juli", "August", "September", "Oktober", "November", "Dezember"]
        for i in range(6):
            month_idx = (now.month - 1 - i) % 12
            year = now.year if (now.month - i) > 0 else now.year - 1
            self.period_combo.addItem(f"{months[month_idx]} {year}")
    
    def calculate(self):
        """Berechnet die Lohnabrechnung"""
        # Beispielberechnung
        self.gross_label.setText("€ 4.500,00")
        self.tax_label.setText("€ 720,00")
        self.sv_label.setText("€ 850,50")
        self.net_label.setText("€ 2.929,50")
    
    def save(self):
        """Speichert die Lohnabrechnung"""
        QMessageBox.information(self, "Erfolg", "Lohnabrechnung wurde gespeichert!")
        self.accept()


class BonusDialog(QDialog):
    """Dialog für Bonus/Sonderzahlung"""
    
    def __init__(self, db_service, user, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.setWindowTitle("Neue Sonderzahlung")
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.employee_combo = QComboBox()
        self.employee_combo.addItem("Alle Mitarbeiter", None)
        self._load_employees_combo()
        form.addRow("Mitarbeiter:", self.employee_combo)
        
        self.bonus_type = QComboBox()
        self.bonus_type.addItems([
            "Leistungsbonus",
            "Weihnachtsgeld",
            "Urlaubsgeld",
            "Jubiläumszuwendung",
            "Provision",
            "Sonstiges"
        ])
        form.addRow("Art:", self.bonus_type)
        
        self.description = QLineEdit()
        self.description.setPlaceholderText("Beschreibung der Sonderzahlung")
        form.addRow("Bezeichnung:", self.description)
        
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 1000000)
        self.amount.setPrefix("€ ")
        self.amount.setDecimals(2)
        form.addRow("Bruttobetrag:", self.amount)
        
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        form.addRow("Auszahlung:", self.payment_date)
        
        self.reason = QTextEdit()
        self.reason.setPlaceholderText("Begründung (optional)")
        self.reason.setMaximumHeight(80)
        form.addRow("Begründung:", self.reason)
        
        layout.addLayout(form)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
        """)
        save_btn.clicked.connect(self.save)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def save(self):
        """Speichert die Sonderzahlung"""
        QMessageBox.information(self, "Erfolg", "Sonderzahlung wurde erfasst!")
        self.accept()
    
    def _load_employees_combo(self):
        """Lädt Mitarbeiter in Combobox"""
        try:
            from app.models.employee import Employee
            employees = self.db_service.get_session().query(Employee).filter(
                Employee.is_deleted == False
            ).all()
            for emp in employees:
                name = f"{emp.first_name or ''} {emp.last_name or ''} ({emp.employee_number or ''})".strip()
                self.employee_combo.addItem(name, emp.id)
        except Exception as e:
            print(f"Fehler beim Laden der Mitarbeiter: {e}")
