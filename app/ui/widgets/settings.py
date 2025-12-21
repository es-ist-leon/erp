"""
Settings Widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import uuid

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
        
        layout.addWidget(tabs)
    
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
