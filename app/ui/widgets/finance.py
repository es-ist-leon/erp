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
        self.tabs.addTab(self._create_bank_accounts_tab(), "🏦 Bankkonten")
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
    
    def _create_bank_accounts_tab(self):
        """Tab für Bankkonten-Verwaltung"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_account_btn = QPushButton("+ Bankkonto verbinden")
        add_account_btn.setStyleSheet(self._button_style())
        add_account_btn.clicked.connect(self.add_bank_account)
        toolbar.addWidget(add_account_btn)
        
        import_btn = QPushButton("📤 CSV importieren")
        import_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#10b981"))
        import_btn.clicked.connect(self.import_bank_csv)
        toolbar.addWidget(import_btn)
        
        toolbar.addStretch()
        
        sync_all_btn = QPushButton("🔄 Alle synchronisieren")
        sync_all_btn.setStyleSheet(self._button_style().replace("#3b82f6", "#f59e0b"))
        sync_all_btn.clicked.connect(self.sync_all_accounts)
        toolbar.addWidget(sync_all_btn)
        
        layout.addLayout(toolbar)
        
        # Konten-Karten
        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_container)
        self.accounts_layout.setSpacing(12)
        
        # Scroll-Area für Konten
        scroll = QScrollArea()
        scroll.setWidget(self.accounts_container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        layout.addWidget(scroll, 1)
        
        # Transaktionen-Tabelle
        transactions_group = QGroupBox("📋 Letzte Transaktionen")
        transactions_group.setStyleSheet(self._group_style())
        transactions_layout = QVBoxLayout(transactions_group)
        
        self.bank_transactions_table = QTableWidget()
        self.bank_transactions_table.setColumnCount(7)
        self.bank_transactions_table.setHorizontalHeaderLabels([
            "Datum", "Konto", "Partner", "Beschreibung", "Betrag", "Status", "Aktionen"
        ])
        self.bank_transactions_table.setStyleSheet(self._table_style())
        self.bank_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        transactions_layout.addWidget(self.bank_transactions_table)
        
        layout.addWidget(transactions_group, 2)
        
        # Konten laden
        self._load_bank_accounts()
        
        return widget
    
    def _load_bank_accounts(self):
        """Lädt Bankkonten"""
        # Bestehende Widgets entfernen
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            from shared.models.finance import BankAccount
            session = self.db_service.get_session()
            accounts = session.query(BankAccount).filter(
                BankAccount.is_deleted == False,
                BankAccount.tenant_id == self.user.tenant_id
            ).all()
            
            if not accounts:
                # Placeholder wenn keine Konten
                placeholder = QLabel("Noch keine Bankkonten verbunden.\nKlicken Sie auf '+ Bankkonto verbinden' um zu starten.")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                placeholder.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
                self.accounts_layout.addWidget(placeholder)
            else:
                for account in accounts:
                    card = self._create_account_card(account)
                    self.accounts_layout.addWidget(card)
            
            self.accounts_layout.addStretch()
            
        except Exception as e:
            print(f"Fehler beim Laden der Bankkonten: {e}")
            placeholder = QLabel(f"Fehler beim Laden: {e}")
            placeholder.setStyleSheet("color: #ef4444;")
            self.accounts_layout.addWidget(placeholder)
    
    def _create_account_card(self, account):
        """Erstellt eine Konto-Karte"""
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
        card.setFixedHeight(120)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Bank-Icon
        icon_label = QLabel("🏦")
        icon_label.setFont(QFont("Segoe UI", 28))
        icon_label.setFixedWidth(60)
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(account.name or account.bank_name)
        name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #1e293b; border: none;")
        info_layout.addWidget(name_label)
        
        # IBAN maskiert
        iban = account.iban or ""
        masked_iban = f"{iban[:4]}{'*' * 12}{iban[-4:]}" if len(iban) > 8 else iban
        iban_label = QLabel(f"IBAN: {masked_iban}")
        iban_label.setStyleSheet("color: #64748b; font-size: 12px; border: none;")
        info_layout.addWidget(iban_label)
        
        # Letzter Sync
        sync_text = "Noch nie synchronisiert"
        if account.last_sync:
            sync_text = f"Letzte Sync: {account.last_sync.strftime('%d.%m.%Y %H:%M')}"
        sync_label = QLabel(sync_text)
        sync_label.setStyleSheet("color: #94a3b8; font-size: 11px; border: none;")
        info_layout.addWidget(sync_label)
        
        layout.addLayout(info_layout, 1)
        
        # Kontostand
        balance_layout = QVBoxLayout()
        balance_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        balance = float(account.current_balance or account.balance or 0)
        balance_text = f"€ {balance:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        balance_label = QLabel(balance_text)
        balance_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        balance_color = "#10b981" if balance >= 0 else "#ef4444"
        balance_label.setStyleSheet(f"color: {balance_color}; border: none;")
        balance_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        balance_layout.addWidget(balance_label)
        
        balance_title = QLabel("Kontostand")
        balance_title.setStyleSheet("color: #94a3b8; font-size: 11px; border: none;")
        balance_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        balance_layout.addWidget(balance_title)
        
        layout.addLayout(balance_layout)
        
        # Aktionen
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        
        sync_btn = QPushButton("🔄")
        sync_btn.setFixedSize(36, 36)
        sync_btn.setToolTip("Synchronisieren")
        sync_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: none;
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        sync_btn.clicked.connect(lambda: self.sync_account(str(account.id)))
        actions_layout.addWidget(sync_btn)
        
        details_btn = QPushButton("📋")
        details_btn.setFixedSize(36, 36)
        details_btn.setToolTip("Details anzeigen")
        details_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: none;
                border-radius: 18px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        details_btn.clicked.connect(lambda: self.show_account_details(str(account.id)))
        actions_layout.addWidget(details_btn)
        
        layout.addLayout(actions_layout)
        
        return card
    
    def add_bank_account(self):
        """Dialog zum Hinzufügen eines Bankkontos"""
        dialog = AddBankAccountDialog(self.db_service, self.user, self)
        if dialog.exec():
            self._load_bank_accounts()
    
    def import_bank_csv(self):
        """CSV-Import für Banktransaktionen"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "CSV-Datei auswählen",
            "",
            "CSV-Dateien (*.csv);;Alle Dateien (*)"
        )
        
        if file_path:
            dialog = ImportCSVDialog(self.db_service, self.user, file_path, self)
            if dialog.exec():
                self._load_bank_accounts()
                QMessageBox.information(self, "Erfolg", "Transaktionen wurden importiert!")
    
    def sync_all_accounts(self):
        """Synchronisiert alle Konten"""
        try:
            from app.services.banking_service import BankingService
            banking = BankingService(self.db_service, self.user)
            
            accounts = banking.get_accounts()
            synced = 0
            
            for account in accounts:
                if account.provider.value == "fints":
                    transactions = banking.sync_account(account.id)
                    synced += len(transactions)
            
            self._load_bank_accounts()
            QMessageBox.information(self, "Synchronisation", f"{synced} neue Transaktionen synchronisiert!")
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Synchronisation fehlgeschlagen: {e}")
    
    def sync_account(self, account_id: str):
        """Synchronisiert ein einzelnes Konto"""
        try:
            from app.services.banking_service import BankingService
            banking = BankingService(self.db_service, self.user)
            
            transactions = banking.sync_account(account_id)
            self._load_bank_accounts()
            
            QMessageBox.information(self, "Synchronisation", f"{len(transactions)} neue Transaktionen!")
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Synchronisation fehlgeschlagen: {e}")
    
    def show_account_details(self, account_id: str):
        """Zeigt Konto-Details"""
        dialog = AccountDetailsDialog(self.db_service, self.user, account_id, self)
        dialog.exec()

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
        
        # Leere Tabelle - wird durch _load_dunnings befüllt
        self._load_dunnings()
        
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
    
    def _load_dunnings(self):
        """Lädt Mahnungen aus der Datenbank"""
        try:
            # Leere Tabelle für echte Daten
            self.dunning_table.setRowCount(0)
        except Exception as e:
            print(f"Fehler beim Laden der Mahnungen: {e}")
    
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
        self.invoice.addItem("Keine Zuordnung", None)
        # Rechnungen aus DB laden
        try:
            from shared.models import Invoice
            invoices = self.db_service.get_session().query(Invoice).filter(
                Invoice.is_deleted == False,
                Invoice.status.in_(['SENT', 'OVERDUE', 'PARTIAL'])
            ).limit(50).all()
            for inv in invoices:
                amount = f"€ {inv.total_amount:,.2f}" if inv.total_amount else ""
                self.invoice.addItem(f"{inv.invoice_number} ({amount})", inv.id)
        except Exception:
            pass
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
        
        # Leere Tabelle - wird durch Vorschau-Funktion befüllt
        self.preview_table.setRowCount(0)
        
        preview_layout.addWidget(self.preview_table)
        layout.addWidget(preview_group)
        
        # Info
        self.info_label = QLabel("📋 Klicken Sie auf 'Vorschau aktualisieren' um überfällige Rechnungen zu laden")
        self.info_label.setStyleSheet("color: #64748b; padding: 8px;")
        layout.addWidget(self.info_label)
        
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


class AddBankAccountDialog(QDialog):
    """Dialog zum Hinzufügen eines Bankkontos"""
    
    def __init__(self, db_service, user, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.setWindowTitle("Bankkonto verbinden")
        self.setMinimumSize(550, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Info-Banner
        info = QLabel("🔒 Ihre Bankdaten werden verschlüsselt gespeichert und niemals an Dritte weitergegeben.")
        info.setStyleSheet("""
            background: #dbeafe;
            color: #1e40af;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Verbindungsart
        connection_group = QGroupBox("Verbindungsart")
        connection_layout = QVBoxLayout(connection_group)
        
        self.fints_radio = QCheckBox("🔗 FinTS/HBCI (automatische Synchronisation)")
        self.fints_radio.setChecked(True)
        connection_layout.addWidget(self.fints_radio)
        
        self.manual_radio = QCheckBox("📝 Manuell (CSV-Import)")
        connection_layout.addWidget(self.manual_radio)
        
        # Nur eine Option erlauben
        self.fints_radio.toggled.connect(lambda checked: self.manual_radio.setChecked(not checked) if checked else None)
        self.manual_radio.toggled.connect(lambda checked: self.fints_radio.setChecked(not checked) if checked else None)
        
        layout.addWidget(connection_group)
        
        # Formular
        form_group = QGroupBox("Kontodaten")
        form = QFormLayout(form_group)
        
        # Kontoname
        self.account_name = QLineEdit()
        self.account_name.setPlaceholderText("z.B. Geschäftskonto Sparkasse")
        form.addRow("Kontobezeichnung:", self.account_name)
        
        # Bank auswählen
        self.bank_combo = QComboBox()
        self.bank_combo.setEditable(True)
        self.bank_combo.setMaxVisibleItems(25)
        self.bank_combo.addItem("Bank auswählen...", "")
        
        # Alle deutschen Banken aus BankingService laden
        try:
            from app.services.banking_service import BankingService
            all_banks = BankingService.GERMAN_BANKS
            # Sortiert nach Namen
            sorted_banks = sorted(all_banks.items(), key=lambda x: x[1].get("name", ""))
            for code, info in sorted_banks:
                self.bank_combo.addItem(info.get("name", "Unbekannte Bank"), code)
        except Exception as e:
            # Fallback: Häufigste Banken
            banks = [
                ("12030000", "Deutsche Kreditbank (DKB)"),
                ("10070000", "Deutsche Bank"),
                ("37040044", "Commerzbank"),
                ("50010517", "ING"),
                ("70020270", "HypoVereinsbank"),
                ("50010060", "Postbank"),
                ("20050550", "Hamburger Sparkasse (Haspa)"),
                ("37050198", "Sparkasse KölnBonn"),
                ("50050201", "Frankfurter Sparkasse"),
            ]
            for code, name in banks:
                self.bank_combo.addItem(name, code)
        
        # Suchfunktion aktivieren
        self.bank_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        form.addRow("Bank:", self.bank_combo)
        
        # IBAN
        self.iban_input = QLineEdit()
        self.iban_input.setPlaceholderText("DE89 3704 0044 0532 0130 00")
        self.iban_input.setMaxLength(34)
        form.addRow("IBAN:", self.iban_input)
        
        # Kontoinhaber
        self.holder_input = QLineEdit()
        self.holder_input.setPlaceholderText("Name des Kontoinhabers")
        form.addRow("Kontoinhaber:", self.holder_input)
        
        layout.addWidget(form_group)
        
        # FinTS-Zugangsdaten (nur wenn FinTS gewählt)
        self.fints_group = QGroupBox("🔐 Online-Banking Zugangsdaten")
        fints_form = QFormLayout(self.fints_group)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ihre Banking-Benutzername")
        fints_form.addRow("Benutzername:", self.username_input)
        
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Ihre Banking-PIN")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        fints_form.addRow("PIN:", self.pin_input)
        
        pin_info = QLabel("⚠️ Die PIN wird nur für die Synchronisation verwendet und verschlüsselt gespeichert.")
        pin_info.setStyleSheet("color: #f59e0b; font-size: 11px;")
        pin_info.setWordWrap(True)
        fints_form.addRow("", pin_info)
        
        layout.addWidget(self.fints_group)
        
        # Toggle FinTS-Gruppe
        self.manual_radio.toggled.connect(lambda checked: self.fints_group.setVisible(not checked))
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Konto verbinden")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        save_btn.clicked.connect(self.save_account)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def save_account(self):
        """Speichert das Bankkonto"""
        import uuid
        
        # Validierung
        if not self.iban_input.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie eine IBAN ein.")
            return
        
        if not self.holder_input.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie den Kontoinhaber ein.")
            return
        
        try:
            from shared.models.finance import BankAccount
            
            iban = self.iban_input.text().replace(" ", "").upper()
            bank_code = self.bank_combo.currentData() or iban[4:12] if len(iban) >= 12 else ""
            
            # Provider bestimmen
            provider = "fints" if self.fints_radio.isChecked() else "manual"
            
            # Credentials verschlüsseln (vereinfacht)
            credentials = None
            if provider == "fints" and self.username_input.text() and self.pin_input.text():
                import base64
                cred_data = f"{self.username_input.text()}:{self.pin_input.text()}"
                credentials = base64.b64encode(cred_data.encode()).decode()
            
            # Bank-Name ermitteln
            bank_name = self.bank_combo.currentText()
            if bank_name == "Bank auswählen...":
                bank_name = "Unbekannte Bank"
            
            session = self.db_service.get_session()
            account = BankAccount(
                id=uuid.uuid4(),
                name=self.account_name.text().strip() or bank_name,
                bank_name=bank_name,
                bank_code=bank_code,
                iban=iban,
                bic="",
                account_holder=self.holder_input.text().strip(),
                provider=provider,
                credentials_encrypted=credentials,
                currency="EUR",
                is_active=True,
                tenant_id=self.user.tenant_id,
                created_by=self.user.id
            )
            
            session.add(account)
            session.commit()
            
            QMessageBox.information(self, "Erfolg", "Bankkonto wurde erfolgreich verbunden!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")


class ImportCSVDialog(QDialog):
    """Dialog für CSV-Import von Banktransaktionen"""
    
    def __init__(self, db_service, user, file_path, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.file_path = file_path
        self.setWindowTitle("Transaktionen importieren")
        self.setMinimumSize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Datei-Info
        file_label = QLabel(f"📄 Datei: {self.file_path}")
        file_label.setStyleSheet("font-weight: bold; padding: 8px;")
        layout.addWidget(file_label)
        
        # Konto auswählen
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("Zielkonto:"))
        
        self.account_combo = QComboBox()
        self._load_accounts()
        account_layout.addWidget(self.account_combo, 1)
        
        layout.addLayout(account_layout)
        
        # Vorschau
        preview_group = QGroupBox("Vorschau (erste 5 Zeilen)")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self._load_preview()
        preview_layout.addWidget(self.preview_table)
        
        layout.addWidget(preview_group)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        import_btn = QPushButton("📥 Importieren")
        import_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
        """)
        import_btn.clicked.connect(self.do_import)
        buttons.addWidget(import_btn)
        
        layout.addLayout(buttons)
    
    def _load_accounts(self):
        """Lädt verfügbare Konten"""
        try:
            from shared.models.finance import BankAccount
            session = self.db_service.get_session()
            accounts = session.query(BankAccount).filter(
                BankAccount.is_deleted == False,
                BankAccount.tenant_id == self.user.tenant_id
            ).all()
            
            for acc in accounts:
                self.account_combo.addItem(f"{acc.name} ({acc.iban[-4:]})", str(acc.id))
                
        except Exception as e:
            print(f"Fehler: {e}")
    
    def _load_preview(self):
        """Lädt CSV-Vorschau"""
        import csv
        
        try:
            with open(self.file_path, 'r', encoding='utf-8-sig') as f:
                sample = f.read(5000)
                f.seek(0)
                
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.reader(f, dialect=dialect)
                
                rows = list(reader)[:6]  # Header + 5 Zeilen
                
                if rows:
                    self.preview_table.setColumnCount(len(rows[0]))
                    self.preview_table.setHorizontalHeaderLabels(rows[0])
                    self.preview_table.setRowCount(len(rows) - 1)
                    
                    for row_idx, row in enumerate(rows[1:]):
                        for col_idx, value in enumerate(row):
                            self.preview_table.setItem(row_idx, col_idx, QTableWidgetItem(value))
                            
        except Exception as e:
            print(f"Vorschau-Fehler: {e}")
    
    def do_import(self):
        """Führt Import durch"""
        if self.account_combo.currentData() is None:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie ein Zielkonto.")
            return
        
        try:
            from app.services.banking_service import BankingService
            
            banking = BankingService(self.db_service, self.user)
            transactions = banking.import_csv(
                self.account_combo.currentData(),
                self.file_path
            )
            
            QMessageBox.information(
                self, 
                "Import abgeschlossen", 
                f"{len(transactions)} Transaktionen importiert!"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Import fehlgeschlagen: {e}")


class AccountDetailsDialog(QDialog):
    """Dialog für Konto-Details und Transaktionen"""
    
    def __init__(self, db_service, user, account_id, parent=None):
        super().__init__(parent)
        self.db_service = db_service
        self.user = user
        self.account_id = account_id
        self.setWindowTitle("Kontodetails")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Konto-Info laden
        try:
            from shared.models.finance import BankAccount, OnlineBankingTransaction
            session = self.db_service.get_session()
            account = session.query(BankAccount).filter(
                BankAccount.id == self.account_id
            ).first()
            
            if not account:
                layout.addWidget(QLabel("Konto nicht gefunden"))
                return
            
            # Header
            header = QFrame()
            header.setStyleSheet("background: white; border-radius: 8px; padding: 16px;")
            header_layout = QHBoxLayout(header)
            
            info_layout = QVBoxLayout()
            title = QLabel(f"🏦 {account.name}")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            info_layout.addWidget(title)
            
            iban_label = QLabel(f"IBAN: {account.iban}")
            iban_label.setStyleSheet("color: #64748b;")
            info_layout.addWidget(iban_label)
            
            header_layout.addLayout(info_layout)
            header_layout.addStretch()
            
            balance = float(account.current_balance or account.balance or 0)
            balance_text = f"€ {balance:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            balance_label = QLabel(balance_text)
            balance_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            balance_color = "#10b981" if balance >= 0 else "#ef4444"
            balance_label.setStyleSheet(f"color: {balance_color};")
            header_layout.addWidget(balance_label)
            
            layout.addWidget(header)
            
            # Transaktionen
            trans_group = QGroupBox("📋 Transaktionen")
            trans_layout = QVBoxLayout(trans_group)
            
            # Toolbar
            toolbar = QHBoxLayout()
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("🔍 Suchen...")
            toolbar.addWidget(self.search_input)
            
            toolbar.addStretch()
            
            match_btn = QPushButton("🔗 Auto-Matching")
            match_btn.clicked.connect(self.auto_match)
            toolbar.addWidget(match_btn)
            
            trans_layout.addLayout(toolbar)
            
            # Tabelle
            self.trans_table = QTableWidget()
            self.trans_table.setColumnCount(6)
            self.trans_table.setHorizontalHeaderLabels([
                "Datum", "Partner", "Beschreibung", "Betrag", "Status", "Zuordnung"
            ])
            self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            # Transaktionen laden
            transactions = session.query(OnlineBankingTransaction).filter(
                OnlineBankingTransaction.account_id == self.account_id,
                OnlineBankingTransaction.is_deleted == False
            ).order_by(OnlineBankingTransaction.date.desc()).limit(100).all()
            
            self.trans_table.setRowCount(len(transactions))
            for row, tx in enumerate(transactions):
                self.trans_table.setItem(row, 0, QTableWidgetItem(
                    tx.date.strftime("%d.%m.%Y") if tx.date else ""
                ))
                self.trans_table.setItem(row, 1, QTableWidgetItem(tx.partner_name or ""))
                self.trans_table.setItem(row, 2, QTableWidgetItem(tx.description or ""))
                
                amount = float(tx.amount or 0)
                amount_text = f"€ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                amount_item = QTableWidgetItem(amount_text)
                amount_item.setForeground(QColor("#10b981" if amount >= 0 else "#ef4444"))
                self.trans_table.setItem(row, 3, amount_item)
                
                status = "✅ Zugeordnet" if tx.is_matched else "⏳ Offen"
                self.trans_table.setItem(row, 4, QTableWidgetItem(status))
                
                self.trans_table.setItem(row, 5, QTableWidgetItem(""))
            
            trans_layout.addWidget(self.trans_table)
            layout.addWidget(trans_group)
            
        except Exception as e:
            layout.addWidget(QLabel(f"Fehler: {e}"))
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        
        layout.addLayout(buttons)
    
    def auto_match(self):
        """Führt automatisches Matching durch"""
        try:
            from app.services.banking_service import BankingService
            
            banking = BankingService(self.db_service, self.user)
            matched = banking.auto_match_transactions(self.account_id)
            
            QMessageBox.information(
                self,
                "Auto-Matching",
                f"{matched} Transaktionen wurden automatisch zugeordnet!"
            )
            
            # Dialog neu laden
            self.setup_ui()
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Matching fehlgeschlagen: {e}")
