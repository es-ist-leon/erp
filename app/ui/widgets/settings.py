"""
Settings Widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QComboBox, QFrame,
    QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import uuid
from datetime import datetime

from shared.models import User, Tenant
from shared.utils.security import hash_password, verify_password


class SettingsWidget(QWidget):
    """Settings page"""
    
    def __init__(self, db_service, user):
        super().__init__()
        self.db = db_service
        self.user = user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Tabs
        tabs = QTabWidget()
        
        # Company Settings
        company_tab = QWidget()
        company_layout = QVBoxLayout(company_tab)
        
        company_group = QGroupBox("Firmendaten")
        company_form = QFormLayout(company_group)
        
        self.company_name = QLineEdit()
        company_form.addRow("Firmenname:", self.company_name)
        
        self.tax_id = QLineEdit()
        self.tax_id.setPlaceholderText("DE123456789")
        company_form.addRow("USt-IdNr.:", self.tax_id)
        
        self.street = QLineEdit()
        company_form.addRow("Straße:", self.street)
        
        addr_layout = QHBoxLayout()
        self.postal_code = QLineEdit()
        self.postal_code.setMaximumWidth(100)
        addr_layout.addWidget(self.postal_code)
        self.city = QLineEdit()
        addr_layout.addWidget(self.city)
        company_form.addRow("PLZ / Stadt:", addr_layout)
        
        self.phone = QLineEdit()
        company_form.addRow("Telefon:", self.phone)
        
        self.email = QLineEdit()
        company_form.addRow("E-Mail:", self.email)
        
        self.website = QLineEdit()
        self.website.setPlaceholderText("www.meine-firma.de")
        company_form.addRow("Website:", self.website)
        
        company_layout.addWidget(company_group)
        
        # Bank details
        bank_group = QGroupBox("Bankverbindung")
        bank_form = QFormLayout(bank_group)
        
        self.bank_name = QLineEdit()
        bank_form.addRow("Bank:", self.bank_name)
        
        self.iban = QLineEdit()
        self.iban.setPlaceholderText("DE89 3704 0044 0532 0130 00")
        bank_form.addRow("IBAN:", self.iban)
        
        self.bic = QLineEdit()
        bank_form.addRow("BIC:", self.bic)
        
        company_layout.addWidget(bank_group)
        company_layout.addStretch()
        
        save_company_btn = QPushButton("Speichern")
        save_company_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        save_company_btn.clicked.connect(self.save_company)
        company_layout.addWidget(save_company_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        tabs.addTab(company_tab, "🏢 Firma")
        
        # User Settings
        user_tab = QWidget()
        user_layout = QVBoxLayout(user_tab)
        
        user_group = QGroupBox("Benutzerprofil")
        user_form = QFormLayout(user_group)
        
        self.user_email = QLineEdit()
        self.user_email.setReadOnly(True)
        user_form.addRow("E-Mail:", self.user_email)
        
        self.user_first = QLineEdit()
        user_form.addRow("Vorname:", self.user_first)
        
        self.user_last = QLineEdit()
        user_form.addRow("Nachname:", self.user_last)
        
        user_layout.addWidget(user_group)
        
        # Password change
        pw_group = QGroupBox("Passwort ändern")
        pw_form = QFormLayout(pw_group)
        
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)
        pw_form.addRow("Aktuelles Passwort:", self.old_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        pw_form.addRow("Neues Passwort:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        pw_form.addRow("Passwort bestätigen:", self.confirm_password)
        
        user_layout.addWidget(pw_group)
        user_layout.addStretch()
        
        save_user_btn = QPushButton("Speichern")
        save_user_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        save_user_btn.clicked.connect(self.save_user)
        user_layout.addWidget(save_user_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        tabs.addTab(user_tab, "👤 Benutzer")
        
        # About Tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo = QLabel("🏠 HolzbauERP")
        logo.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        logo.setStyleSheet("color: #2563eb;")
        about_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("color: #666; font-size: 16px;")
        about_layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Enterprise Resource Planning für Holzbaubetriebe")
        desc.setStyleSheet("color: #333; margin-top: 20px;")
        about_layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)
        
        copyright_label = QLabel("© 2024 HolzbauERP")
        copyright_label.setStyleSheet("color: #999; margin-top: 40px;")
        about_layout.addWidget(copyright_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        tabs.addTab(about_tab, "ℹ️ Über")
        
        # Banking Tab
        banking_tab = self._create_banking_tab()
        tabs.addTab(banking_tab, "🏦 Banking")
        
        layout.addWidget(tabs)
    
    def _create_banking_tab(self):
        """Erstellt den Banking-Tab für Kontoanbindung"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Bankkonten verbinden")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(header)
        
        desc = QLabel("Verbinden Sie Ihre Bankkonten für automatischen Zahlungsabgleich oder importieren Sie Kontodaten manuell via CSV.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_fints_btn = QPushButton("🔗 FinTS-Konto hinzufügen")
        add_fints_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        add_fints_btn.clicked.connect(self._add_fints_account)
        btn_layout.addWidget(add_fints_btn)
        
        add_manual_btn = QPushButton("📄 Manuelles Konto hinzufügen")
        add_manual_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #059669;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #047857; }
        """)
        add_manual_btn.clicked.connect(self._add_manual_account)
        btn_layout.addWidget(add_manual_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Accounts table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(6)
        self.accounts_table.setHorizontalHeaderLabels([
            "Bank", "IBAN", "Kontoinhaber", "Saldo", "Letzte Sync", "Aktionen"
        ])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.accounts_table)
        
        # Transactions section
        tx_header = QLabel("Letzte Transaktionen")
        tx_header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        tx_header.setStyleSheet("margin-top: 20px;")
        layout.addWidget(tx_header)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Datum", "Betrag", "Partner", "Verwendungszweck", "Status", "Zuordnung"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
        """)
        self.transactions_table.setMaximumHeight(250)
        layout.addWidget(self.transactions_table)
        
        # CSV Import
        import_layout = QHBoxLayout()
        import_btn = QPushButton("📥 CSV importieren")
        import_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #4f46e5; }
        """)
        import_btn.clicked.connect(self._import_csv)
        import_layout.addWidget(import_btn)
        
        auto_match_btn = QPushButton("🔄 Auto-Zuordnung")
        auto_match_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        auto_match_btn.clicked.connect(self._auto_match)
        import_layout.addWidget(auto_match_btn)
        
        import_layout.addStretch()
        layout.addLayout(import_layout)
        
        return tab
    
    def _get_banking_service(self):
        """Initialisiert Banking Service"""
        try:
            from app.services.banking_service import BankingService
            return BankingService(self.db, self.user)
        except Exception as e:
            print(f"Banking Service Fehler: {e}")
            return None
    
    def _load_bank_accounts(self):
        """Lädt Bankkonten in die Tabelle"""
        service = self._get_banking_service()
        if not service:
            return
        
        accounts = service.get_accounts()
        self.accounts_table.setRowCount(len(accounts))
        
        for row, acc in enumerate(accounts):
            self.accounts_table.setItem(row, 0, QTableWidgetItem(acc.bank_name))
            self.accounts_table.setItem(row, 1, QTableWidgetItem(acc.masked_iban()))
            self.accounts_table.setItem(row, 2, QTableWidgetItem(acc.account_holder))
            
            balance_item = QTableWidgetItem(f"{acc.balance:,.2f} {acc.currency}")
            if acc.balance >= 0:
                balance_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                balance_item.setForeground(Qt.GlobalColor.red)
            self.accounts_table.setItem(row, 3, balance_item)
            
            sync_text = acc.last_sync.strftime("%d.%m.%Y %H:%M") if acc.last_sync else "Nie"
            self.accounts_table.setItem(row, 4, QTableWidgetItem(sync_text))
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            
            sync_btn = QPushButton("🔄")
            sync_btn.setToolTip("Synchronisieren")
            sync_btn.setFixedSize(30, 30)
            sync_btn.clicked.connect(lambda checked, aid=acc.id: self._sync_account(aid))
            action_layout.addWidget(sync_btn)
            
            del_btn = QPushButton("🗑️")
            del_btn.setToolTip("Entfernen")
            del_btn.setFixedSize(30, 30)
            del_btn.clicked.connect(lambda checked, aid=acc.id: self._remove_account(aid))
            action_layout.addWidget(del_btn)
            
            self.accounts_table.setCellWidget(row, 5, action_widget)
    
    def _load_transactions(self):
        """Lädt Transaktionen in die Tabelle"""
        service = self._get_banking_service()
        if not service:
            return
        
        accounts = service.get_accounts()
        all_transactions = []
        
        for acc in accounts:
            txs = service.get_transactions(acc.id)
            all_transactions.extend(txs[:20])  # Limit per account
        
        # Sort by date
        all_transactions.sort(key=lambda x: x.date, reverse=True)
        all_transactions = all_transactions[:50]  # Limit total
        
        self.transactions_table.setRowCount(len(all_transactions))
        
        for row, tx in enumerate(all_transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(tx.date.strftime("%d.%m.%Y")))
            
            amount_item = QTableWidgetItem(f"{tx.amount:,.2f} {tx.currency}")
            if tx.amount >= 0:
                amount_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                amount_item.setForeground(Qt.GlobalColor.red)
            self.transactions_table.setItem(row, 1, amount_item)
            
            self.transactions_table.setItem(row, 2, QTableWidgetItem(tx.partner_name or "-"))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(tx.description[:50] if tx.description else "-"))
            
            status = "✅ Zugeordnet" if tx.is_matched else "⏳ Offen"
            self.transactions_table.setItem(row, 4, QTableWidgetItem(status))
            
            match_text = ""
            if tx.matched_invoice_id:
                match_text = f"Rechnung"
            self.transactions_table.setItem(row, 5, QTableWidgetItem(match_text))
    
    def _add_fints_account(self):
        """Öffnet Dialog zum Hinzufügen eines FinTS-Kontos"""
        dialog = AddBankAccountDialog(self.db, self.user, use_fints=True, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_bank_accounts()
            QMessageBox.information(self, "Erfolg", "Bankkonto wurde hinzugefügt.")
    
    def _add_manual_account(self):
        """Öffnet Dialog zum manuellen Hinzufügen eines Kontos"""
        dialog = AddBankAccountDialog(self.db, self.user, use_fints=False, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_bank_accounts()
            QMessageBox.information(self, "Erfolg", "Bankkonto wurde hinzugefügt.")
    
    def _sync_account(self, account_id: str):
        """Synchronisiert ein Bankkonto"""
        service = self._get_banking_service()
        if not service:
            QMessageBox.warning(self, "Fehler", "Banking Service nicht verfügbar.")
            return
        
        try:
            transactions = service.sync_account(account_id)
            self._load_bank_accounts()
            self._load_transactions()
            QMessageBox.information(self, "Erfolg", f"{len(transactions)} Transaktionen synchronisiert.")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Sync fehlgeschlagen: {e}")
    
    def _remove_account(self, account_id: str):
        """Entfernt ein Bankkonto"""
        reply = QMessageBox.question(
            self, "Bankkonto entfernen",
            "Möchten Sie dieses Bankkonto wirklich entfernen?\n\nAlle zugehörigen Transaktionen bleiben erhalten.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            service = self._get_banking_service()
            if service and service.remove_account(account_id):
                self._load_bank_accounts()
                QMessageBox.information(self, "Erfolg", "Bankkonto wurde entfernt.")
            else:
                QMessageBox.warning(self, "Fehler", "Bankkonto konnte nicht entfernt werden.")
    
    def _import_csv(self):
        """Importiert Transaktionen aus CSV"""
        service = self._get_banking_service()
        if not service:
            QMessageBox.warning(self, "Fehler", "Banking Service nicht verfügbar.")
            return
        
        accounts = service.get_accounts()
        if not accounts:
            QMessageBox.warning(self, "Fehler", "Bitte fügen Sie zuerst ein Bankkonto hinzu.")
            return
        
        # Select account
        account = accounts[0]  # Use first account for now
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSV-Datei auswählen", "",
            "CSV-Dateien (*.csv);;Alle Dateien (*.*)"
        )
        
        if file_path:
            try:
                transactions = service.import_csv(account.id, file_path)
                self._load_transactions()
                QMessageBox.information(self, "Erfolg", f"{len(transactions)} Transaktionen importiert.")
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Import fehlgeschlagen: {e}")
    
    def _auto_match(self):
        """Führt automatisches Matching durch"""
        service = self._get_banking_service()
        if not service:
            QMessageBox.warning(self, "Fehler", "Banking Service nicht verfügbar.")
            return
        
        accounts = service.get_accounts()
        total_matched = 0
        
        for acc in accounts:
            matched = service.auto_match_transactions(acc.id)
            total_matched += matched
        
        self._load_transactions()
        QMessageBox.information(self, "Auto-Zuordnung", f"{total_matched} Transaktionen wurden automatisch zugeordnet.")
    
    def load_data(self):
        """Load current settings data"""
        # User data
        self.user_email.setText(self.user.email)
        self.user_first.setText(self.user.first_name or "")
        self.user_last.setText(self.user.last_name or "")
        
        # Company/Tenant data
        if self.user.tenant_id:
            session = self.db.get_session()
            try:
                tenant = session.get(Tenant, self.user.tenant_id)
                if tenant:
                    self.company_name.setText(tenant.company_name or "")
                    self.tax_id.setText(tenant.tax_id or "")
                    self.street.setText(tenant.street or "")
                    self.postal_code.setText(tenant.postal_code or "")
                    self.city.setText(tenant.city or "")
                    self.phone.setText(tenant.phone or "")
                    self.email.setText(tenant.email or "")
                    self.website.setText(tenant.website or "")
                    self.bank_name.setText(tenant.bank_name or "")
                    self.iban.setText(tenant.iban or "")
                    self.bic.setText(tenant.bic or "")
            finally:
                session.close()
        
        # Load bank accounts
        self._load_bank_accounts()
        self._load_transactions()
    
    def refresh(self):
        self.load_data()
    
    def save_company(self):
        """Save company/tenant settings"""
        if not self.user.tenant_id:
            QMessageBox.warning(self, "Fehler", "Keine Firma zugeordnet.")
            return
        
        session = self.db.get_session()
        try:
            tenant = session.get(Tenant, self.user.tenant_id)
            if not tenant:
                QMessageBox.warning(self, "Fehler", "Firma nicht gefunden.")
                return
            
            tenant.company_name = self.company_name.text().strip() or None
            tenant.name = tenant.company_name or tenant.name
            tenant.tax_id = self.tax_id.text().strip() or None
            tenant.street = self.street.text().strip() or None
            tenant.postal_code = self.postal_code.text().strip() or None
            tenant.city = self.city.text().strip() or None
            tenant.phone = self.phone.text().strip() or None
            tenant.email = self.email.text().strip() or None
            tenant.website = self.website.text().strip() or None
            tenant.bank_name = self.bank_name.text().strip() or None
            tenant.iban = self.iban.text().strip() or None
            tenant.bic = self.bic.text().strip() or None
            
            session.commit()
            
            # Update user data
            self.user.company_name = tenant.company_name
            self.user.tenant_name = tenant.name
            
            QMessageBox.information(self, "Erfolg", "Firmendaten wurden gespeichert.")
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
    
    def save_user(self):
        """Save user settings and optionally change password"""
        session = self.db.get_session()
        try:
            user = session.get(User, self.user.id)
            if not user:
                QMessageBox.warning(self, "Fehler", "Benutzer nicht gefunden.")
                return
            
            # Update profile
            user.first_name = self.user_first.text().strip() or None
            user.last_name = self.user_last.text().strip() or None
            
            # Check password change
            old_pw = self.old_password.text()
            new_pw = self.new_password.text()
            confirm_pw = self.confirm_password.text()
            
            if new_pw:
                if not old_pw:
                    QMessageBox.warning(self, "Fehler", "Bitte geben Sie Ihr aktuelles Passwort ein.")
                    return
                
                if not verify_password(old_pw, user.hashed_password):
                    QMessageBox.warning(self, "Fehler", "Das aktuelle Passwort ist falsch.")
                    return
                
                if new_pw != confirm_pw:
                    QMessageBox.warning(self, "Fehler", "Die neuen Passwörter stimmen nicht überein.")
                    return
                
                if len(new_pw) < 6:
                    QMessageBox.warning(self, "Fehler", "Das Passwort muss mindestens 6 Zeichen haben.")
                    return
                
                user.hashed_password = hash_password(new_pw)
            
            session.commit()
            
            # Update local user data
            self.user.first_name = user.first_name
            self.user.last_name = user.last_name
            
            # Clear password fields
            self.old_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
            
            QMessageBox.information(self, "Erfolg", "Benutzerdaten wurden gespeichert.")
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()


class AddBankAccountDialog(QDialog):
    """Dialog zum Hinzufügen eines Bankkontos"""
    
    def __init__(self, db_service, user, use_fints=False, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.user = user
        self.use_fints = use_fints
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Bankkonto hinzufügen")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form
        form_layout = QFormLayout()
        
        # Bank selection (for FinTS)
        if self.use_fints:
            # Search field for banks
            search_layout = QVBoxLayout()
            self.bank_search = QLineEdit()
            self.bank_search.setPlaceholderText("🔍 Bank suchen (Name, BLZ oder BIC eingeben)...")
            self.bank_search.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 13px;
                }
                QLineEdit:focus { border-color: #2563eb; }
            """)
            self.bank_search.textChanged.connect(self._filter_banks)
            search_layout.addWidget(self.bank_search)
            
            self.bank_combo = QComboBox()
            self.bank_combo.setMaxVisibleItems(15)
            self.bank_combo.setStyleSheet("""
                QComboBox {
                    padding: 10px;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    min-width: 350px;
                }
                QComboBox:focus { border-color: #2563eb; }
                QComboBox::drop-down { border: none; padding-right: 10px; }
            """)
            
            # Alle deutschen Banken mit BIC - dynamisch aus BankingService laden und erweitern
            try:
                from app.services.banking_service import BankingService
                
                # BIC-Mapping für bekannte Banken
                bic_map = {
                    "10070000": "DEUTDEBBXXX", "10070024": "DEUTDEDBBER", "37040044": "COBADEFFXXX",
                    "50040000": "COBADEFFXXX", "12030000": "BYLADEM1001", "50010517": "INGDDEFFXXX",
                    "70020270": "HYVEDEMM", "50010060": "PBNKDEFFXXX", "20050550": "HASPDEHH",
                    "37050198": "COLSDE33XXX", "66050101": "KARSDE66XXX", "50050201": "HELADEF1822",
                    "70050000": "BYLADEMMXXX", "60050101": "SOLADEST600", "10050000": "BELADEBEXXX",
                    "25050000": "NOLADE2HXXX", "30050000": "WELADEDLLEV", "70150000": "SSKMDEMM",
                    "75050000": "SSKNDE77XXX", "30050110": "DUSSDEDDXXX", "36050105": "SPESDE3EXXX",
                    "43050001": "DORTDE33XXX", "48050161": "SPBIDE3BXXX", "60090100": "VOBADES2XXX",
                    "70090100": "GENODEF1INP", "10090000": "BEVODEBBXXX", "50090500": "GENODE51FVB",
                    "30020900": "CMCIDEDDXXX", "43060967": "GENODED1GLS", "30060010": "DAAEDEDDXXX",
                    "25020600": "VOWADE2BXXX", "70090500": "GENODEF1S04", "20090500": "GENODEF1S10",
                    "37060590": "GENODED1SPK", "76090500": "GENODEF1S08", "66090800": "BBKRDE6KXXX",
                }
                
                all_banks = BankingService.GERMAN_BANKS
                self.all_banks = []
                for code, info in sorted(all_banks.items(), key=lambda x: x[1].get("name", "")):
                    name = info.get("name", "Unbekannte Bank")
                    bic = bic_map.get(code, "")
                    self.all_banks.append((code, name, bic))
                    
            except Exception as e:
                # Fallback zu statischer Liste
                self.all_banks = [
                    # Großbanken
                    ("10070000", "Deutsche Bank", "DEUTDEBBXXX"),
                    ("10070024", "Deutsche Bank Privat- und Geschäftskunden", "DEUTDEDBBER"),
                    ("37040044", "Commerzbank", "COBADEFFXXX"),
                    ("50040000", "Commerzbank Frankfurt", "COBADEFFXXX"),
                    ("12030000", "Deutsche Kreditbank (DKB)", "BYLADEM1001"),
                    ("50010517", "ING", "INGDDEFFXXX"),
                    ("70020270", "HypoVereinsbank (UniCredit)", "HYVEDEMM"),
                    ("50010060", "Postbank", "PBNKDEFFXXX"),
                    ("20050550", "Hamburger Sparkasse (Haspa)", "HASPDEHH"),
                    ("37050198", "Sparkasse KölnBonn", "COLSDE33XXX"),
                    ("66050101", "Sparkasse Karlsruhe", "KARSDE66XXX"),
                    ("50050201", "Frankfurter Sparkasse", "HELADEF1822"),
                ]
            
            self.bank_combo.addItem("-- Bank wählen oder suchen --", ("", "", ""))
            for code, name, bic in self.all_banks:
                self.bank_combo.addItem(f"{name} (BLZ: {code})", (code, name, bic))
            
            search_layout.addWidget(self.bank_combo)
            form_layout.addRow("Bank:", search_layout)
        else:
            self.bank_name_input = QLineEdit()
            self.bank_name_input.setPlaceholderText("z.B. Sparkasse München")
            form_layout.addRow("Bankname:", self.bank_name_input)
        
        # IBAN
        self.iban_input = QLineEdit()
        self.iban_input.setPlaceholderText("DE89 3704 0044 0532 0130 00")
        form_layout.addRow("IBAN:", self.iban_input)
        
        # Account holder
        self.holder_input = QLineEdit()
        self.holder_input.setPlaceholderText("Max Mustermann GmbH")
        form_layout.addRow("Kontoinhaber:", self.holder_input)
        
        # FinTS credentials
        if self.use_fints:
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("background-color: #e2e8f0;")
            layout.addWidget(separator)
            
            cred_label = QLabel("FinTS Zugangsdaten (optional)")
            cred_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            layout.addWidget(cred_label)
            
            cred_note = QLabel("Für automatische Synchronisation. Die Daten werden verschlüsselt gespeichert.")
            cred_note.setWordWrap(True)
            cred_note.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(cred_note)
            
            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText("Online-Banking Benutzerkennung")
            form_layout.addRow("Benutzer:", self.username_input)
            
            self.pin_input = QLineEdit()
            self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pin_input.setPlaceholderText("PIN/Passwort")
            form_layout.addRow("PIN:", self.pin_input)
            
            warning = QLabel("⚠️ Hinweis: FinTS-Sync erfordert ggf. TAN-Eingabe und ist nicht bei allen Banken automatisiert möglich.")
            warning.setWordWrap(True)
            warning.setStyleSheet("color: #d97706; font-size: 11px; margin-top: 10px;")
            layout.addWidget(warning)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        save_btn.clicked.connect(self.save_account)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def save_account(self):
        """Speichert das Bankkonto"""
        iban = self.iban_input.text().strip().replace(" ", "").upper()
        holder = self.holder_input.text().strip()
        
        if not iban:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie eine IBAN ein.")
            return
        
        if not holder:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie den Kontoinhaber ein.")
            return
        
        # Validate IBAN (simple check)
        if len(iban) < 15 or len(iban) > 34:
            QMessageBox.warning(self, "Fehler", "Die IBAN scheint ungültig zu sein.")
            return
        
        try:
            from app.services.banking_service import BankingService, BankingProvider
            
            service = BankingService(self.db, self.user)
            
            if self.use_fints:
                bank_data = self.bank_combo.currentData()
                if bank_data and bank_data[0]:
                    bank_code = bank_data[0]
                    bank_name = bank_data[1]
                else:
                    bank_code = iban[4:12] if len(iban) >= 12 else ""
                    bank_name = "Unbekannte Bank"
                username = self.username_input.text().strip()
                pin = self.pin_input.text()
                provider = BankingProvider.FINTS if username and pin else BankingProvider.MANUAL
                
                account = service.add_account(
                    bank_code=bank_code,
                    iban=iban,
                    account_holder=holder,
                    bank_name=bank_name,
                    username=username,
                    pin=pin,
                    provider=provider
                )
            else:
                bank_name = self.bank_name_input.text().strip() or "Unbekannte Bank"
                bank_code = iban[4:12] if len(iban) >= 12 else ""
                
                account = service.add_account(
                    bank_code=bank_code,
                    iban=iban,
                    account_holder=holder,
                    provider=BankingProvider.MANUAL
                )
            
            if account:
                self.accept()
            else:
                QMessageBox.warning(self, "Fehler", "Bankkonto konnte nicht erstellt werden.")
                
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler: {e}")
    
    def _filter_banks(self, text):
        """Filtert die Bankliste basierend auf Sucheingabe"""
        if not hasattr(self, 'bank_combo') or not hasattr(self, 'all_banks'):
            return
        
        search_lower = text.lower().strip()
        self.bank_combo.clear()
        self.bank_combo.addItem("-- Bank wählen oder suchen --", ("", "", ""))
        
        for code, name, bic in self.all_banks:
            if (search_lower in name.lower() or 
                search_lower in code or 
                search_lower in bic.lower()):
                self.bank_combo.addItem(f"{name} (BLZ: {code})", (code, name, bic))
        
        # Show all if search is empty
        if not search_lower:
            self.bank_combo.clear()
            self.bank_combo.addItem("-- Bank wählen oder suchen --", ("", "", ""))
            for code, name, bic in self.all_banks:
                self.bank_combo.addItem(f"{name} (BLZ: {code})", (code, name, bic))
