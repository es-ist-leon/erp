"""
Finance Widget - Finanzverwaltung, Zahlungen und Mahnwesen UI
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


class FinanceWidget(QWidget):
    """Hauptwidget für die Finanzverwaltung"""
    
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
        self.tabs.addTab(self._create_payments_tab(), "💳 Zahlungen")
        self.tabs.addTab(self._create_receivables_tab(), "📥 Forderungen")
        self.tabs.addTab(self._create_payables_tab(), "📤 Verbindlichkeiten")
        self.tabs.addTab(self._create_dunning_tab(), "⚠️ Mahnwesen")
        self.tabs.addTab(self._create_cashflow_tab(), "💰 Liquidität")
        self.tabs.addTab(self._create_loans_tab(), "🏦 Kredite")
        
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
        title = QLabel("🏦 Finanzverwaltung")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(title)
        
        layout.addStretch()
        
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
        
        new_payment_btn = QPushButton("+ Neue Zahlung")
        new_payment_btn.setStyleSheet(btn_style)
        new_payment_btn.clicked.connect(self.new_payment)
        layout.addWidget(new_payment_btn)
        
        dunning_btn = QPushButton("⚠️ Mahnlauf")
        dunning_btn.setStyleSheet(btn_style.replace("#3b82f6", "#f59e0b").replace("#2563eb", "#d97706"))
        dunning_btn.clicked.connect(self.start_dunning_run)
        layout.addWidget(dunning_btn)
        
        return header
    
    def _create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        kpis = [
            ("Kontostand", "€ 165.430,50", "2 Konten", "#10b981"),
            ("Offene Forderungen", "€ 78.500,00", "24 Rechnungen", "#3b82f6"),
            ("Offene Verbindlichkeiten", "€ 45.200,00", "12 Rechnungen", "#f59e0b"),
            ("Überfällig", "€ 12.350,00", "5 Mahnungen", "#ef4444"),
        ]
        
        for title, value, subtitle, color in kpis:
            card = self._create_kpi_card(title, value, subtitle, color)
            kpi_layout.addWidget(card)
        
        layout.addLayout(kpi_layout)
        
        # Zwei Spalten
        content_layout = QHBoxLayout()
        
        # Anstehende Zahlungen
        upcoming_group = QGroupBox("📅 Anstehende Zahlungen (7 Tage)")
        upcoming_group.setStyleSheet(self._group_style())
        upcoming_layout = QVBoxLayout(upcoming_group)
        
        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(5)
        self.upcoming_table.setHorizontalHeaderLabels([
            "Fällig", "Empfänger", "Betreff", "Betrag", "Status"
        ])
        self.upcoming_table.setStyleSheet(self._table_style())
        
        upcoming = [
            ("22.12.2025", "Holz Müller GmbH", "RE-2025-234", "€ 4.500,00", "Offen"),
            ("23.12.2025", "Mitarbeiter Gehälter", "Dezember 2025", "€ 45.000,00", "Geplant"),
            ("27.12.2025", "Versicherung AG", "Prämie Q1/2026", "€ 2.800,00", "Offen"),
        ]
        
        self.upcoming_table.setRowCount(len(upcoming))
        for row, data in enumerate(upcoming):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 4:
                    if value == "Geplant":
                        item.setForeground(QColor("#3b82f6"))
                    else:
                        item.setForeground(QColor("#f59e0b"))
                self.upcoming_table.setItem(row, col, item)
        
        upcoming_layout.addWidget(self.upcoming_table)
        content_layout.addWidget(upcoming_group, 2)
        
        # Schnellzugriff
        quick_group = QGroupBox("⚡ Schnellzugriff")
        quick_group.setStyleSheet(self._group_style())
        quick_layout = QVBoxLayout(quick_group)
        
        quick_actions = [
            ("💳 Zahlung erfassen", self.new_payment),
            ("📥 Zahlungseingang", self.record_incoming_payment),
            ("⚠️ Mahnlauf starten", self.start_dunning_run),
            ("📊 Offene Posten", self.show_open_items),
            ("💰 Liquiditätsplanung", self.show_cashflow),
            ("🔄 Bankabgleich", self.bank_reconciliation),
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
        
        return widget
    
    def _create_payments_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Filter
        toolbar.addWidget(QLabel("Richtung:"))
        direction_filter = QComboBox()
        direction_filter.addItems(["Alle", "Ausgehend", "Eingehend"])
        direction_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(direction_filter)
        
        toolbar.addWidget(QLabel("Status:"))
        status_filter = QComboBox()
        status_filter.addItems(["Alle", "Offen", "Geplant", "Abgeschlossen"])
        status_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(status_filter)
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Suchen...")
        search.setStyleSheet(self._input_style())
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        new_btn = QPushButton("+ Neue Zahlung")
        new_btn.setStyleSheet(self._button_style())
        new_btn.clicked.connect(self.new_payment)
        toolbar.addWidget(new_btn)
        
        sepa_btn = QPushButton("📤 SEPA-Export")
        sepa_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        toolbar.addWidget(sepa_btn)
        
        layout.addLayout(toolbar)
        
        # Tabelle
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(9)
        self.payments_table.setHorizontalHeaderLabels([
            "Nr.", "Datum", "Richtung", "Partner", "Referenz",
            "Betrag", "Methode", "Status", "Aktionen"
        ])
        self.payments_table.setStyleSheet(self._table_style())
        
        payments = [
            ("Z-2025-0234", "20.12.2025", "📤 Ausgehend", "Holz Müller GmbH", "RE-2025-234", "€ 4.500,00", "SEPA", "Abgeschlossen"),
            ("Z-2025-0233", "19.12.2025", "📥 Eingehend", "Bauherr Schmidt", "AR-2025-189", "€ 12.500,00", "Überweisung", "Abgeschlossen"),
            ("Z-2025-0232", "18.12.2025", "📤 Ausgehend", "Stadtwerke", "Strom 12/25", "€ 850,00", "Lastschrift", "Abgeschlossen"),
        ]
        
        self.payments_table.setRowCount(len(payments))
        for row, data in enumerate(payments):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 2:
                    if "Eingehend" in value:
                        item.setForeground(QColor("#10b981"))
                    else:
                        item.setForeground(QColor("#ef4444"))
                if col == 7:
                    item.setForeground(QColor("#10b981"))
                self.payments_table.setItem(row, col, item)
        
        layout.addWidget(self.payments_table)
        
        return widget
    
    def _create_receivables_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # KPIs
        kpi_layout = QHBoxLayout()
        
        kpis = [
            ("Offene Forderungen", "€ 78.500,00", "#3b82f6"),
            ("Davon überfällig", "€ 12.350,00", "#ef4444"),
            ("DSO (Tage)", "32", "#f59e0b"),
        ]
        
        for title, value, color in kpis:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 8px;
                    border-left: 4px solid {color};
                    padding: 12px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(title))
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            card_layout.addWidget(value_label)
            kpi_layout.addWidget(card)
        
        kpi_layout.addStretch()
        layout.addLayout(kpi_layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("Alter:"))
        age_filter = QComboBox()
        age_filter.addItems(["Alle", "< 30 Tage", "30-60 Tage", "60-90 Tage", "> 90 Tage"])
        age_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(age_filter)
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Kunde suchen...")
        search.setStyleSheet(self._input_style())
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        remind_btn = QPushButton("📧 Erinnerung senden")
        remind_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(remind_btn)
        
        layout.addLayout(toolbar)
        
        # Tabelle
        self.receivables_table = QTableWidget()
        self.receivables_table.setColumnCount(8)
        self.receivables_table.setHorizontalHeaderLabels([
            "Rechnung", "Kunde", "Datum", "Fällig", "Betrag",
            "Offen", "Tage überfällig", "Status"
        ])
        self.receivables_table.setStyleSheet(self._table_style())
        
        receivables = [
            ("AR-2025-195", "Bauherr Müller", "01.12.2025", "15.12.2025", "€ 15.000,00", "€ 15.000,00", "6", "Überfällig"),
            ("AR-2025-190", "Familie Schmidt", "25.11.2025", "25.12.2025", "€ 8.500,00", "€ 8.500,00", "-4", "Offen"),
            ("AR-2025-185", "Firma Weber", "15.11.2025", "15.12.2025", "€ 22.000,00", "€ 12.000,00", "6", "Teilbezahlt"),
        ]
        
        self.receivables_table.setRowCount(len(receivables))
        for row, data in enumerate(receivables):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 7:
                    if value == "Überfällig":
                        item.setForeground(QColor("#ef4444"))
                    elif value == "Teilbezahlt":
                        item.setForeground(QColor("#f59e0b"))
                    else:
                        item.setForeground(QColor("#10b981"))
                self.receivables_table.setItem(row, col, item)
        
        layout.addWidget(self.receivables_table)
        
        return widget
    
    def _create_payables_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("Fälligkeit:"))
        due_filter = QComboBox()
        due_filter.addItems(["Alle", "Diese Woche", "Dieser Monat", "Überfällig"])
        due_filter.setStyleSheet(self._input_style())
        toolbar.addWidget(due_filter)
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Lieferant suchen...")
        search.setStyleSheet(self._input_style())
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        pay_btn = QPushButton("💳 Zahlungen ausführen")
        pay_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        toolbar.addWidget(pay_btn)
        
        layout.addLayout(toolbar)
        
        # Tabelle
        self.payables_table = QTableWidget()
        self.payables_table.setColumnCount(8)
        self.payables_table.setHorizontalHeaderLabels([
            "☐", "Rechnung", "Lieferant", "Datum", "Fällig",
            "Betrag", "Skonto bis", "Aktionen"
        ])
        self.payables_table.setStyleSheet(self._table_style())
        
        payables = [
            ("☐", "ER-2025-456", "Holz Müller GmbH", "10.12.2025", "24.12.2025", "€ 4.500,00", "17.12. (2%)", ""),
            ("☐", "ER-2025-455", "Baumarkt XY", "05.12.2025", "20.12.2025", "€ 1.200,00", "-", ""),
            ("☐", "ER-2025-450", "Schrauben AG", "01.12.2025", "15.12.2025", "€ 850,00", "08.12. (3%)", ""),
        ]
        
        self.payables_table.setRowCount(len(payables))
        for row, data in enumerate(payables):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                self.payables_table.setItem(row, col, item)
        
        layout.addWidget(self.payables_table)
        
        # Summe
        sum_layout = QHBoxLayout()
        sum_layout.addStretch()
        sum_label = QLabel("Summe ausgewählt: € 0,00")
        sum_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        sum_layout.addWidget(sum_label)
        layout.addLayout(sum_layout)
        
        return widget
    
    def _create_dunning_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Übersicht
        overview_layout = QHBoxLayout()
        
        dunning_stats = [
            ("Zahlungserinnerungen", "3", "#3b82f6"),
            ("1. Mahnung", "2", "#f59e0b"),
            ("2. Mahnung", "1", "#ef4444"),
            ("3. Mahnung / Inkasso", "0", "#7f1d1d"),
        ]
        
        for title, count, color in dunning_stats:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 8px;
                    border-top: 4px solid {color};
                    padding: 16px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            
            count_label = QLabel(count)
            count_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(count_label)
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("color: #64748b;")
            card_layout.addWidget(title_label)
            
            overview_layout.addWidget(card)
        
        layout.addLayout(overview_layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        new_run_btn = QPushButton("▶️ Mahnlauf starten")
        new_run_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#f59e0b"))
        new_run_btn.clicked.connect(self.start_dunning_run)
        toolbar.addWidget(new_run_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Offene Mahnungen
        self.dunning_table = QTableWidget()
        self.dunning_table.setColumnCount(8)
        self.dunning_table.setHorizontalHeaderLabels([
            "Mahnung", "Kunde", "Stufe", "Offener Betrag",
            "Mahngebühr", "Verzugszinsen", "Gesamt", "Status"
        ])
        self.dunning_table.setStyleSheet(self._table_style())
        
        dunnings = [
            ("M-2025-045", "Bauherr Müller", "1. Mahnung", "€ 15.000,00", "€ 5,00", "€ 25,00", "€ 15.030,00", "Versendet"),
            ("M-2025-044", "Firma Weber", "Erinnerung", "€ 12.000,00", "€ 0,00", "€ 0,00", "€ 12.000,00", "Erstellt"),
            ("M-2025-043", "Herr Beispiel", "2. Mahnung", "€ 3.500,00", "€ 10,00", "€ 45,00", "€ 3.555,00", "Versendet"),
        ]
        
        self.dunning_table.setRowCount(len(dunnings))
        for row, data in enumerate(dunnings):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 2:
                    if "2. Mahnung" in value:
                        item.setForeground(QColor("#ef4444"))
                    elif "1. Mahnung" in value:
                        item.setForeground(QColor("#f59e0b"))
                    else:
                        item.setForeground(QColor("#3b82f6"))
                self.dunning_table.setItem(row, col, item)
        
        layout.addWidget(self.dunning_table)
        
        return widget
    
    def _create_cashflow_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_layout.addWidget(QLabel("Zeitraum:"))
        period_combo = QComboBox()
        period_combo.addItems(["Nächste 4 Wochen", "Nächste 3 Monate", "Nächstes Quartal"])
        period_combo.setStyleSheet(self._input_style())
        header_layout.addWidget(period_combo)
        
        header_layout.addStretch()
        
        new_forecast_btn = QPushButton("+ Neue Planung")
        new_forecast_btn.setStyleSheet(self._button_style())
        header_layout.addWidget(new_forecast_btn)
        
        layout.addLayout(header_layout)
        
        # Liquiditätsübersicht
        cashflow_group = QGroupBox("💰 Liquiditätsprognose")
        cashflow_group.setStyleSheet(self._group_style())
        cashflow_layout = QVBoxLayout(cashflow_group)
        
        self.cashflow_table = QTableWidget()
        self.cashflow_table.setColumnCount(6)
        self.cashflow_table.setHorizontalHeaderLabels([
            "Woche", "Anfangsbestand", "Einnahmen", "Ausgaben", "Netto", "Endbestand"
        ])
        self.cashflow_table.setStyleSheet(self._table_style())
        
        cashflow = [
            ("KW 51", "€ 165.430", "€ 25.000", "€ 52.000", "-€ 27.000", "€ 138.430"),
            ("KW 52", "€ 138.430", "€ 35.000", "€ 15.000", "+€ 20.000", "€ 158.430"),
            ("KW 01", "€ 158.430", "€ 45.000", "€ 48.000", "-€ 3.000", "€ 155.430"),
            ("KW 02", "€ 155.430", "€ 30.000", "€ 25.000", "+€ 5.000", "€ 160.430"),
        ]
        
        self.cashflow_table.setRowCount(len(cashflow))
        for row, data in enumerate(cashflow):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 4:
                    if value.startswith("-"):
                        item.setForeground(QColor("#ef4444"))
                    else:
                        item.setForeground(QColor("#10b981"))
                self.cashflow_table.setItem(row, col, item)
        
        cashflow_layout.addWidget(self.cashflow_table)
        layout.addWidget(cashflow_group)
        
        return widget
    
    def _create_loans_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        new_loan_btn = QPushButton("+ Neuer Kredit")
        new_loan_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(new_loan_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Kredite
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(9)
        self.loans_table.setHorizontalHeaderLabels([
            "Kredit-Nr.", "Bezeichnung", "Kreditgeber", "Kreditsumme",
            "Restschuld", "Zinssatz", "Rate/Monat", "Nächste Rate", "Status"
        ])
        self.loans_table.setStyleSheet(self._table_style())
        
        loans = [
            ("K-2020-001", "Betriebsmittelkredit", "Sparkasse", "€ 100.000", "€ 65.000", "3,5%", "€ 1.850", "01.01.2026", "Aktiv"),
            ("K-2022-001", "Maschinenfinanzierung", "VR Bank", "€ 50.000", "€ 35.000", "4,2%", "€ 980", "01.01.2026", "Aktiv"),
        ]
        
        self.loans_table.setRowCount(len(loans))
        for row, data in enumerate(loans):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                if col == 8:
                    item.setForeground(QColor("#10b981"))
                self.loans_table.setItem(row, col, item)
        
        layout.addWidget(self.loans_table)
        
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
            QLineEdit, QComboBox {
                padding: 10px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
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
    
    def new_payment(self):
        """Neue Zahlung erfassen"""
        dialog = PaymentDialog(self.db_service, self.user, self)
        dialog.exec()
    
    def record_incoming_payment(self):
        """Zahlungseingang erfassen"""
        QMessageBox.information(self, "Info", "Zahlungseingang erfassen...")
    
    def start_dunning_run(self):
        """Mahnlauf starten"""
        dialog = DunningRunDialog(self.db_service, self.user, self)
        dialog.exec()
    
    def show_open_items(self):
        """Offene Posten anzeigen"""
        QMessageBox.information(self, "Info", "Offene Posten werden angezeigt...")
    
    def show_cashflow(self):
        """Liquiditätsplanung anzeigen"""
        self.tabs.setCurrentIndex(5)  # Liquiditäts-Tab
    
    def bank_reconciliation(self):
        """Bankabgleich starten"""
        QMessageBox.information(self, "Info", "Bankabgleich wird gestartet...")


class PaymentDialog(QDialog):
    """Dialog für neue Zahlung"""
    
    def __init__(self, db_service, user, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.setWindowTitle("Neue Zahlung")
        self.setMinimumSize(500, 450)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Richtung
        self.direction = QComboBox()
        self.direction.addItems(["Ausgehende Zahlung", "Eingehende Zahlung"])
        form.addRow("Richtung:", self.direction)
        
        # Empfänger/Absender
        self.partner = QComboBox()
        self.partner.setEditable(True)
        self.partner.addItems([
            "Holz Müller GmbH",
            "Baumarkt XY",
            "Versicherung AG",
        ])
        form.addRow("Empfänger:", self.partner)
        
        # Betrag
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 10000000)
        self.amount.setPrefix("€ ")
        self.amount.setDecimals(2)
        form.addRow("Betrag:", self.amount)
        
        # Datum
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        form.addRow("Zahlungsdatum:", self.payment_date)
        
        # Methode
        self.method = QComboBox()
        self.method.addItems(["SEPA-Überweisung", "Lastschrift", "Bar", "Kreditkarte"])
        form.addRow("Zahlungsmethode:", self.method)
        
        # Referenz
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("z.B. Rechnungsnummer")
        form.addRow("Referenz:", self.reference)
        
        # Verwendungszweck
        self.purpose = QTextEdit()
        self.purpose.setPlaceholderText("Verwendungszweck")
        self.purpose.setMaximumHeight(80)
        form.addRow("Verwendungszweck:", self.purpose)
        
        # Rechnung zuordnen
        self.invoice = QComboBox()
        self.invoice.addItems([
            "Keine Zuordnung",
            "RE-2025-234 (€ 4.500,00)",
            "RE-2025-233 (€ 1.200,00)",
        ])
        form.addRow("Rechnung zuordnen:", self.invoice)
        
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
        """Speichert die Zahlung"""
        QMessageBox.information(self, "Erfolg", "Zahlung wurde erfasst!")
        self.accept()


class DunningRunDialog(QDialog):
    """Dialog für Mahnlauf"""
    
    def __init__(self, db_service, user, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.setWindowTitle("Mahnlauf starten")
        self.setMinimumSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Einstellungen
        settings_group = QGroupBox("⚙️ Mahnlauf-Einstellungen")
        settings_form = QFormLayout(settings_group)
        
        self.reference_date = QDateEdit()
        self.reference_date.setDate(QDate.currentDate())
        self.reference_date.setCalendarPopup(True)
        settings_form.addRow("Stichtag:", self.reference_date)
        
        self.min_amount = QDoubleSpinBox()
        self.min_amount.setRange(0, 10000)
        self.min_amount.setValue(5)
        self.min_amount.setPrefix("€ ")
        settings_form.addRow("Mindestbetrag:", self.min_amount)
        
        self.grace_days = QSpinBox()
        self.grace_days.setRange(0, 30)
        self.grace_days.setValue(3)
        settings_form.addRow("Karenzzeit (Tage):", self.grace_days)
        
        layout.addWidget(settings_group)
        
        # Vorschau
        preview_group = QGroupBox("👁️ Vorschau - Zu mahnende Posten")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(6)
        self.preview_table.setHorizontalHeaderLabels([
            "☐", "Kunde", "Rechnung", "Betrag", "Überfällig", "Stufe"
        ])
        
        preview_data = [
            ("☑", "Bauherr Müller", "AR-2025-195", "€ 15.000,00", "6 Tage", "1. Mahnung"),
            ("☑", "Firma Weber", "AR-2025-185", "€ 12.000,00", "6 Tage", "Erinnerung"),
            ("☑", "Herr Beispiel", "AR-2025-170", "€ 3.500,00", "21 Tage", "2. Mahnung"),
        ]
        
        self.preview_table.setRowCount(len(preview_data))
        for row, data in enumerate(preview_data):
            for col, value in enumerate(data):
                self.preview_table.setItem(row, col, QTableWidgetItem(value))
        
        preview_layout.addWidget(self.preview_table)
        layout.addWidget(preview_group)
        
        # Info
        info_label = QLabel("📋 3 Mahnungen werden erstellt (Gesamtbetrag: € 30.500,00)")
        info_label.setStyleSheet("color: #64748b; padding: 8px;")
        layout.addWidget(info_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        preview_btn = QPushButton("👁️ Vorschau aktualisieren")
        buttons_layout.addWidget(preview_btn)
        
        run_btn = QPushButton("▶️ Mahnlauf starten")
        run_btn.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        run_btn.clicked.connect(self.start_run)
        buttons_layout.addWidget(run_btn)
        
        layout.addLayout(buttons_layout)
    
    def start_run(self):
        """Startet den Mahnlauf"""
        QMessageBox.information(self, "Mahnlauf", "Mahnlauf wurde erfolgreich durchgeführt!\n\n3 Mahnungen wurden erstellt.")
        self.accept()
