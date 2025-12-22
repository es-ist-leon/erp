"""
Register Dialog - Professional Design
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QMessageBox, QFrame, QWidget, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class RegisterDialog(QDialog):
    """Professional registration dialog"""
    
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.email = ""
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Registrierung - HolzbauERP")
        self.setFixedSize(440, 560)
        
        # Clean background
        self.setStyleSheet("""
            QDialog {
                background: #f5f5f5;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # Card container
        card = QFrame()
        card.setObjectName("registerCard")
        card.setStyleSheet("""
            QFrame#registerCard {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(0)
        
        # Header
        header_icon = QLabel("👤")
        header_icon.setFont(QFont("Segoe UI Emoji", 24))
        header_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_icon.setStyleSheet("color: #1565C0;")
        card_layout.addWidget(header_icon)
        
        title = QLabel("Neues Konto erstellen")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #212121; margin-top: 8px;")
        card_layout.addWidget(title)
        
        subtitle = QLabel("Erstellen Sie ein kostenloses Konto")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #757575; font-size: 13px; margin-bottom: 20px;")
        card_layout.addWidget(subtitle)
        
        # Form fields
        self._add_field_label(card_layout, "E-MAIL-ADRESSE *")
        self.email_input = self._create_input("ihre@email.de")
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(12)
        
        self._add_field_label(card_layout, "BENUTZERNAME *")
        self.username_input = self._create_input("benutzername")
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(12)
        
        # Name row
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(12)
        
        first_col = QWidget()
        first_layout = QVBoxLayout(first_col)
        first_layout.setContentsMargins(0, 0, 0, 0)
        first_layout.setSpacing(4)
        first_label = QLabel("VORNAME")
        first_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        first_label.setStyleSheet("color: #757575; letter-spacing: 0.5px;")
        first_layout.addWidget(first_label)
        self.first_name_input = self._create_input("Max")
        first_layout.addWidget(self.first_name_input)
        name_layout.addWidget(first_col)
        
        last_col = QWidget()
        last_layout = QVBoxLayout(last_col)
        last_layout.setContentsMargins(0, 0, 0, 0)
        last_layout.setSpacing(4)
        last_label = QLabel("NACHNAME")
        last_label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        last_label.setStyleSheet("color: #757575; letter-spacing: 0.5px;")
        last_layout.addWidget(last_label)
        self.last_name_input = self._create_input("Mustermann")
        last_layout.addWidget(self.last_name_input)
        name_layout.addWidget(last_col)
        
        card_layout.addWidget(name_widget)
        card_layout.addSpacing(12)
        
        self._add_field_label(card_layout, "PASSWORT *")
        self.password_input = self._create_input("••••••••", password=True)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(12)
        
        self._add_field_label(card_layout, "PASSWORT BESTÄTIGEN *")
        self.confirm_input = self._create_input("••••••••", password=True)
        card_layout.addWidget(self.confirm_input)
        card_layout.addSpacing(20)
        
        # Register button
        register_btn = QPushButton("Konto erstellen")
        register_btn.setMinimumHeight(44)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        register_btn.setStyleSheet("""
            QPushButton {
                background: #1565C0;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #0D47A1;
            }
        """)
        register_btn.clicked.connect(self.register)
        card_layout.addWidget(register_btn)
        
        card_layout.addSpacing(12)
        
        # Cancel button
        cancel_btn = QPushButton("Zurück zur Anmeldung")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFont(QFont("Segoe UI", 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #757575;
                border: none;
            }
            QPushButton:hover {
                color: #1565C0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        card_layout.addWidget(cancel_btn)
        
        main_layout.addWidget(card)
        
        # Set focus
        self.email_input.setFocus()
    
    def _add_field_label(self, layout, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        label.setStyleSheet("color: #757575; letter-spacing: 0.5px; margin-bottom: 4px;")
        layout.addWidget(label)
    
    def _create_input(self, placeholder, password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setMinimumHeight(40)
        if password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 13px;
                background: #fafafa;
                color: #212121;
            }
            QLineEdit:focus {
                border: 2px solid #1565C0;
                background: white;
            }
            QLineEdit:hover:!focus {
                border-color: #bdbdbd;
            }
        """)
        return input_field
    
    def register(self):
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        
        if not email or not username or not password:
            QMessageBox.warning(self, "Fehler", "Bitte alle Pflichtfelder ausfüllen.")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Fehler", "Passwörter stimmen nicht überein.")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Fehler", "Passwort muss mindestens 6 Zeichen haben.")
            return
        
        success, message = self.auth_service.register(
            email, username, password, first_name, last_name
        )
        
        if success:
            self.email = email
            QMessageBox.information(self, "Erfolg", "Registrierung erfolgreich! Sie können sich jetzt anmelden.")
            self.accept()
        else:
            QMessageBox.warning(self, "Fehler", message)
