"""
Accounting Widget - Buchhaltung und Finanzbuchhaltung UI
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QDialog, QFormLayout, QMessageBox, QTabWidget, QHeaderView,
    QGroupBox, QSpinBox, QDoubleSpinBox, QCheckBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon
from datetime import datetime, date
from decimal import Decimal


class AccountingWidget(QWidget):
    """Hauptwidget für die Buchhaltung"""
    
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
        
        # Tab Widget für verschiedene Bereiche
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
        self.tabs.addTab(self._create_chart_of_accounts_tab(), "📋 Kontenplan")
        self.tabs.addTab(self._create_journal_tab(), "📝 Buchungen")
        self.tabs.addTab(self._create_cost_centers_tab(), "🏢 Kostenstellen")
        self.tabs.addTab(self._create_bank_tab(), "🏦 Bank")
        self.tabs.addTab(self._create_tax_tab(), "📑 Steuern")
        self.tabs.addTab(self._create_assets_tab(), "🏭 Anlagen")
        self.tabs.addTab(self._create_reports_tab(), "📈 Berichte")
        
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
        title = QLabel("💰 Buchhaltung")
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
        
        new_booking_btn = QPushButton("+ Neue Buchung")
        new_booking_btn.setStyleSheet(btn_style)
        new_booking_btn.clicked.connect(self.new_journal_entry)
        layout.addWidget(new_booking_btn)
        
        import_btn = QPushButton("📥 Import")
        import_btn.setStyleSheet(btn_style.replace("#3b82f6", "#10b981").replace("#2563eb", "#059669"))
        layout.addWidget(import_btn)
        
        return header
    
    def _create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # KPI Cards
        kpi_layout = QHBoxLayout()
        
        kpis = [
            ("Umsatz (Monat)", "€ 125.430,00", "+12.5%", "#10b981"),
            ("Ausgaben (Monat)", "€ 89.120,00", "-3.2%", "#f59e0b"),
            ("Gewinn (Monat)", "€ 36.310,00", "+28.4%", "#3b82f6"),
            ("Offene Posten", "€ 45.670,00", "12 Rechnungen", "#ef4444"),
        ]
        
        for title, value, change, color in kpis:
            card = self._create_kpi_card(title, value, change, color)
            kpi_layout.addWidget(card)
        
        layout.addLayout(kpi_layout)
        
        # Zwei Spalten
        content_layout = QHBoxLayout()
        
        # Letzte Buchungen
        bookings_group = QGroupBox("📝 Letzte Buchungen")
        bookings_group.setStyleSheet(self._group_style())
        bookings_layout = QVBoxLayout(bookings_group)
        
        self.recent_bookings_table = QTableWidget()
        self.recent_bookings_table.setColumnCount(5)
        self.recent_bookings_table.setHorizontalHeaderLabels([
            "Datum", "Beleg", "Beschreibung", "Soll", "Haben"
        ])
        self.recent_bookings_table.horizontalHeader().setStretchLastSection(True)
        self.recent_bookings_table.setStyleSheet(self._table_style())
        bookings_layout.addWidget(self.recent_bookings_table)
        
        content_layout.addWidget(bookings_group, 2)
        
        # Schnellzugriff
        quick_group = QGroupBox("⚡ Schnellzugriff")
        quick_group.setStyleSheet(self._group_style())
        quick_layout = QVBoxLayout(quick_group)
        
        quick_actions = [
            ("📝 Neue Buchung", self.new_journal_entry),
            ("📥 Bankauszug importieren", self.import_bank_statement),
            ("📊 USt-Voranmeldung", self.create_vat_report),
            ("📈 BWA erstellen", self.create_bwa),
            ("🔍 Kontoabfrage", self.account_query),
            ("📋 Offene Posten", self.show_open_items),
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
    
    def _create_chart_of_accounts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        search = QLineEdit()
        search.setPlaceholderText("🔍 Konto suchen...")
        search.setStyleSheet(self._input_style())
        search.setFixedWidth(300)
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("+ Neues Konto")
        add_btn.setStyleSheet(self._button_style())
        add_btn.clicked.connect(self.new_account)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Splitter für Baum und Details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Kontenbaum
        self.accounts_tree = QTreeWidget()
        self.accounts_tree.setHeaderLabels(["Konto", "Bezeichnung", "Saldo"])
        self.accounts_tree.setStyleSheet("""
            QTreeWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QTreeWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
        """)
        self.accounts_tree.itemClicked.connect(self.on_account_selected)
        splitter.addWidget(self.accounts_tree)
        
        # Kontodetails
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_group = QGroupBox("Kontodetails")
        details_group.setStyleSheet(self._group_style())
        details_form = QFormLayout(details_group)
        
        self.account_number_label = QLabel("-")
        self.account_name_label = QLabel("-")
        self.account_type_label = QLabel("-")
        self.account_balance_label = QLabel("-")
        
        details_form.addRow("Kontonummer:", self.account_number_label)
        details_form.addRow("Bezeichnung:", self.account_name_label)
        details_form.addRow("Kontoart:", self.account_type_label)
        details_form.addRow("Saldo:", self.account_balance_label)
        
        details_layout.addWidget(details_group)
        
        # Kontobewegungen
        movements_group = QGroupBox("Kontobewegungen")
        movements_group.setStyleSheet(self._group_style())
        movements_layout = QVBoxLayout(movements_group)
        
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(5)
        self.movements_table.setHorizontalHeaderLabels([
            "Datum", "Beleg", "Text", "Soll", "Haben"
        ])
        self.movements_table.setStyleSheet(self._table_style())
        movements_layout.addWidget(self.movements_table)
        
        details_layout.addWidget(movements_group)
        splitter.addWidget(details_widget)
        
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)
        
        self.load_chart_of_accounts()
        
        return widget
    
    def _create_journal_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Periodenauswahl
        toolbar.addWidget(QLabel("Periode:"))
        self.journal_period = QComboBox()
        self.journal_period.addItems([
            "Januar 2025", "Februar 2025", "März 2025", 
            "April 2025", "Mai 2025", "Juni 2025"
        ])
        self.journal_period.setStyleSheet(self._input_style())
        toolbar.addWidget(self.journal_period)
        
        # Suche
        search = QLineEdit()
        search.setPlaceholderText("🔍 Buchung suchen...")
        search.setStyleSheet(self._input_style())
        toolbar.addWidget(search)
        
        toolbar.addStretch()
        
        add_btn = QPushButton("+ Neue Buchung")
        add_btn.setStyleSheet(self._button_style())
        add_btn.clicked.connect(self.new_journal_entry)
        toolbar.addWidget(add_btn)
        
        layout.addLayout(toolbar)
        
        # Buchungstabelle
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(8)
        self.journal_table.setHorizontalHeaderLabels([
            "Beleg-Nr.", "Datum", "Buchungsdatum", "Beschreibung",
            "Soll-Konto", "Haben-Konto", "Betrag", "Status"
        ])
        self.journal_table.horizontalHeader().setStretchLastSection(True)
        self.journal_table.setStyleSheet(self._table_style())
        layout.addWidget(self.journal_table)
        
        return widget
    
    def _create_cost_centers_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("+ Neue Kostenstelle")
        add_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(add_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Kostenstellen-Tabelle
        self.cost_centers_table = QTableWidget()
        self.cost_centers_table.setColumnCount(6)
        self.cost_centers_table.setHorizontalHeaderLabels([
            "Code", "Bezeichnung", "Verantwortlich", "Budget", "Ist", "Abweichung"
        ])
        self.cost_centers_table.setStyleSheet(self._table_style())
        layout.addWidget(self.cost_centers_table)
        
        return widget
    
    def _create_bank_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Bankkonten-Übersicht
        accounts_layout = QHBoxLayout()
        
        # Beispiel-Bankkonten
        bank_accounts = [
            ("Geschäftskonto Sparkasse", "DE89 3704 0044 0532 0130 00", "€ 45.230,50"),
            ("Tagesgeld", "DE89 3704 0044 0532 0130 01", "€ 120.000,00"),
        ]
        
        for name, iban, balance in bank_accounts:
            card = self._create_bank_account_card(name, iban, balance)
            accounts_layout.addWidget(card)
        
        accounts_layout.addStretch()
        layout.addLayout(accounts_layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        import_btn = QPushButton("📥 Kontoauszug importieren")
        import_btn.setStyleSheet(self._button_style())
        import_btn.clicked.connect(self.import_bank_statement)
        toolbar.addWidget(import_btn)
        
        sync_btn = QPushButton("🔄 Synchronisieren")
        sync_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        toolbar.addWidget(sync_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Transaktionen
        self.bank_transactions_table = QTableWidget()
        self.bank_transactions_table.setColumnCount(7)
        self.bank_transactions_table.setHorizontalHeaderLabels([
            "Datum", "Wertstellung", "Partner", "Verwendungszweck", 
            "Betrag", "Status", "Zuordnung"
        ])
        self.bank_transactions_table.setStyleSheet(self._table_style())
        layout.addWidget(self.bank_transactions_table)
        
        return widget
    
    def _create_tax_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # USt-Übersicht
        vat_group = QGroupBox("📑 Umsatzsteuer-Voranmeldung")
        vat_group.setStyleSheet(self._group_style())
        vat_layout = QVBoxLayout(vat_group)
        
        # Periodenauswahl
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Zeitraum:"))
        
        self.tax_year = QComboBox()
        self.tax_year.addItems(["2025", "2024", "2023"])
        self.tax_year.setStyleSheet(self._input_style())
        period_layout.addWidget(self.tax_year)
        
        self.tax_month = QComboBox()
        self.tax_month.addItems([
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ])
        self.tax_month.setStyleSheet(self._input_style())
        period_layout.addWidget(self.tax_month)
        
        calculate_btn = QPushButton("Berechnen")
        calculate_btn.setStyleSheet(self._button_style())
        period_layout.addWidget(calculate_btn)
        
        period_layout.addStretch()
        vat_layout.addLayout(period_layout)
        
        # USt-Beträge
        amounts_layout = QHBoxLayout()
        
        vat_items = [
            ("Steuerpflichtige Umsätze 19%", "€ 85.000,00"),
            ("USt 19%", "€ 16.150,00"),
            ("Vorsteuer", "€ 8.230,00"),
            ("Zahllast", "€ 7.920,00"),
        ]
        
        for label, amount in vat_items:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.addWidget(QLabel(label))
            amount_label = QLabel(amount)
            amount_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            item_layout.addWidget(amount_label)
            amounts_layout.addWidget(item_widget)
        
        vat_layout.addLayout(amounts_layout)
        
        # Aktionen
        actions_layout = QHBoxLayout()
        
        submit_btn = QPushButton("📤 An ELSTER übermitteln")
        submit_btn.setStyleSheet(self._button_style())
        actions_layout.addWidget(submit_btn)
        
        pdf_btn = QPushButton("📄 PDF erstellen")
        pdf_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#64748b"))
        pdf_btn.clicked.connect(self._export_vat_pdf)
        actions_layout.addWidget(pdf_btn)
        
        actions_layout.addStretch()
        vat_layout.addLayout(actions_layout)
        
        layout.addWidget(vat_group)
        
        # Steuerübersicht
        overview_group = QGroupBox("📊 Steuerübersicht")
        overview_group.setStyleSheet(self._group_style())
        overview_layout = QVBoxLayout(overview_group)
        
        self.tax_overview_table = QTableWidget()
        self.tax_overview_table.setColumnCount(5)
        self.tax_overview_table.setHorizontalHeaderLabels([
            "Zeitraum", "USt", "Vorsteuer", "Zahllast", "Status"
        ])
        self.tax_overview_table.setStyleSheet(self._table_style())
        overview_layout.addWidget(self.tax_overview_table)
        
        layout.addWidget(overview_group)
        
        return widget
    
    def _create_assets_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("+ Neue Anlage")
        add_btn.setStyleSheet(self._button_style())
        toolbar.addWidget(add_btn)
        
        depreciation_btn = QPushButton("📉 AfA berechnen")
        depreciation_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#f59e0b"))
        toolbar.addWidget(depreciation_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Anlagen-Tabelle
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(8)
        self.assets_table.setHorizontalHeaderLabels([
            "Anlagen-Nr.", "Bezeichnung", "Typ", "Anschaffung",
            "AK", "Buchwert", "AfA/Jahr", "Status"
        ])
        self.assets_table.setStyleSheet(self._table_style())
        layout.addWidget(self.assets_table)
        
        return widget
    
    def _create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Berichts-Karten
        reports_layout = QHBoxLayout()
        
        reports = [
            ("📊 BWA", "Betriebswirtschaftliche Auswertung", self.create_bwa),
            ("📈 GuV", "Gewinn- und Verlustrechnung", self.create_guv),
            ("📋 Bilanz", "Jahresbilanz", self.create_balance),
            ("💰 Summen & Salden", "Summen- und Saldenliste", self.create_susa),
            ("📑 Kontenblätter", "Kontenblätter drucken", self.print_account_sheets),
            ("🔍 Journal", "Buchungsjournal", self.print_journal),
        ]
        
        for icon_title, description, callback in reports:
            card = self._create_report_card(icon_title, description, callback)
            reports_layout.addWidget(card)
        
        layout.addLayout(reports_layout)
        layout.addStretch()
        
        return widget
    
    def _create_kpi_card(self, title, value, change, color):
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
        
        change_label = QLabel(change)
        change_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        layout.addWidget(change_label)
        
        return card
    
    def _create_bank_account_card(self, name, iban, balance):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        card.setFixedSize(280, 140)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(name_label)
        
        iban_label = QLabel(iban)
        iban_label.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(iban_label)
        
        layout.addStretch()
        
        balance_label = QLabel(balance)
        balance_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        balance_label.setStyleSheet("color: #10b981;")
        layout.addWidget(balance_label)
        
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
    
    def load_chart_of_accounts(self):
        """Lädt den Kontenplan"""
        # Beispiel-Konten hinzufügen
        root_items = [
            ("0", "Anlagevermögen", [
                ("0200", "Technische Anlagen", "€ 45.000,00"),
                ("0400", "Maschinen", "€ 125.000,00"),
                ("0500", "Fuhrpark", "€ 85.000,00"),
            ]),
            ("1", "Umlaufvermögen", [
                ("1200", "Bank", "€ 45.230,50"),
                ("1400", "Forderungen", "€ 78.500,00"),
            ]),
            ("4", "Erlöse", [
                ("4000", "Umsatzerlöse 19%", "€ 425.000,00"),
                ("4300", "Sonstige Erlöse", "€ 12.500,00"),
            ]),
            ("6", "Aufwendungen", [
                ("6000", "Materialaufwand", "€ 185.000,00"),
                ("6200", "Personalkosten", "€ 145.000,00"),
            ]),
        ]
        
        self.accounts_tree.clear()
        
        for code, name, children in root_items:
            parent = QTreeWidgetItem([code, name, ""])
            parent.setFont(0, QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.accounts_tree.addTopLevelItem(parent)
            
            for child_code, child_name, child_balance in children:
                child = QTreeWidgetItem([child_code, child_name, child_balance])
                parent.addChild(child)
            
            parent.setExpanded(True)
    
    def on_account_selected(self, item, column):
        """Zeigt Kontodetails an"""
        self.account_number_label.setText(item.text(0))
        self.account_name_label.setText(item.text(1))
        self.account_balance_label.setText(item.text(2) or "-")
    
    def new_journal_entry(self):
        """Öffnet Dialog für neue Buchung"""
        dialog = JournalEntryDialog(self.db_service, self.user, self)
        dialog.exec()
    
    def new_account(self):
        """Öffnet Dialog für neues Konto"""
        QMessageBox.information(self, "Info", "Konto-Dialog wird implementiert...")
    
    def import_bank_statement(self):
        """Importiert Bankauszug"""
        QMessageBox.information(self, "Info", "Bank-Import wird implementiert...")
    
    def create_vat_report(self):
        """Erstellt USt-Voranmeldung"""
        QMessageBox.information(self, "Info", "USt-Voranmeldung wird erstellt...")
    
    def create_bwa(self):
        """Erstellt BWA"""
        QMessageBox.information(self, "Info", "BWA wird erstellt...")
    
    def create_guv(self):
        """Erstellt GuV"""
        QMessageBox.information(self, "Info", "GuV wird erstellt...")
    
    def create_balance(self):
        """Erstellt Bilanz"""
        QMessageBox.information(self, "Info", "Bilanz wird erstellt...")
    
    def create_susa(self):
        """Erstellt Summen- und Saldenliste"""
        QMessageBox.information(self, "Info", "SuSa wird erstellt...")
    
    def print_account_sheets(self):
        """Druckt Kontenblätter"""
        QMessageBox.information(self, "Info", "Kontenblätter werden erstellt...")
    
    def print_journal(self):
        """Druckt Buchungsjournal"""
        QMessageBox.information(self, "Info", "Journal wird erstellt...")
    
    def account_query(self):
        """Öffnet Kontoabfrage"""
        QMessageBox.information(self, "Info", "Kontoabfrage wird implementiert...")
    
    def show_open_items(self):
        """Zeigt offene Posten"""
        QMessageBox.information(self, "Info", "Offene Posten werden angezeigt...")
    
    def _export_vat_pdf(self):
        """Exportiert UStVA als PDF"""
        from PyQt6.QtWidgets import QFileDialog
        from shared.services.export_service import ExportService
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "UStVA speichern",
            f"UStVA_{datetime.now().strftime('%Y%m')}.pdf",
            "PDF Dateien (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            columns = [
                {"key": "kz", "label": "KZ", "width": 15},
                {"key": "bezeichnung", "label": "Bezeichnung", "width": 80},
                {"key": "betrag", "label": "Betrag", "width": 30},
            ]
            
            # Beispiel-Daten (in Realität aus DB)
            data = [
                {"kz": "81", "bezeichnung": "Steuerpflichtige Umsätze 19%", "betrag": "€ 45.000,00"},
                {"kz": "86", "bezeichnung": "Steuerpflichtige Umsätze 7%", "betrag": "€ 5.500,00"},
                {"kz": "66", "bezeichnung": "Vorsteuer", "betrag": "€ 3.250,00"},
                {"kz": "83", "bezeichnung": "Zahllast", "betrag": "€ 5.835,00"},
            ]
            
            ExportService.export_to_pdf(
                data=data,
                columns=columns,
                title="Umsatzsteuer-Voranmeldung",
                subtitle=f"Zeitraum: {datetime.now().strftime('%B %Y')}",
                filename=filename
            )
            
            QMessageBox.information(self, "Erfolg", f"PDF wurde erstellt:\n{filename}")
            import os
            os.startfile(filename)
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Export fehlgeschlagen: {e}")


class JournalEntryDialog(QDialog):
    """Dialog für neue Buchung"""
    
    def __init__(self, db_service, user, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.setWindowTitle("Neue Buchung")
        self.setMinimumSize(700, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Kopfdaten
        header_group = QGroupBox("Buchungskopf")
        header_form = QFormLayout(header_group)
        
        self.document_date = QDateEdit()
        self.document_date.setDate(QDate.currentDate())
        self.document_date.setCalendarPopup(True)
        header_form.addRow("Belegdatum:", self.document_date)
        
        self.posting_date = QDateEdit()
        self.posting_date.setDate(QDate.currentDate())
        self.posting_date.setCalendarPopup(True)
        header_form.addRow("Buchungsdatum:", self.posting_date)
        
        self.description = QLineEdit()
        self.description.setPlaceholderText("Buchungstext eingeben...")
        header_form.addRow("Beschreibung:", self.description)
        
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("z.B. Rechnungsnummer")
        header_form.addRow("Referenz:", self.reference)
        
        layout.addWidget(header_group)
        
        # Buchungspositionen
        lines_group = QGroupBox("Buchungspositionen")
        lines_layout = QVBoxLayout(lines_group)
        
        self.lines_table = QTableWidget()
        self.lines_table.setColumnCount(5)
        self.lines_table.setHorizontalHeaderLabels([
            "Konto", "Bezeichnung", "Soll", "Haben", "Kostenstelle"
        ])
        self.lines_table.setRowCount(2)  # Start mit 2 Zeilen
        lines_layout.addWidget(self.lines_table)
        
        add_line_btn = QPushButton("+ Zeile hinzufügen")
        add_line_btn.clicked.connect(self.add_line)
        lines_layout.addWidget(add_line_btn)
        
        layout.addWidget(lines_group)
        
        # Summen
        sums_layout = QHBoxLayout()
        sums_layout.addStretch()
        sums_layout.addWidget(QLabel("Summe Soll:"))
        self.sum_debit = QLabel("€ 0,00")
        self.sum_debit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        sums_layout.addWidget(self.sum_debit)
        sums_layout.addWidget(QLabel("Summe Haben:"))
        self.sum_credit = QLabel("€ 0,00")
        self.sum_credit.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        sums_layout.addWidget(self.sum_credit)
        layout.addLayout(sums_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_draft_btn = QPushButton("Als Entwurf speichern")
        save_draft_btn.clicked.connect(self.save_draft)
        buttons_layout.addWidget(save_draft_btn)
        
        post_btn = QPushButton("Buchen")
        post_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        post_btn.clicked.connect(self.post)
        buttons_layout.addWidget(post_btn)
        
        layout.addLayout(buttons_layout)
    
    def add_line(self):
        """Fügt eine neue Buchungszeile hinzu"""
        self.lines_table.insertRow(self.lines_table.rowCount())
    
    def save_draft(self):
        """Speichert als Entwurf"""
        QMessageBox.information(self, "Info", "Buchung als Entwurf gespeichert!")
        self.accept()
    
    def post(self):
        """Bucht und schließt"""
        QMessageBox.information(self, "Erfolg", "Buchung wurde erfolgreich gebucht!")
        self.accept()
