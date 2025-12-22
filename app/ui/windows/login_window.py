"""
Login Window - Professional Material Design 3
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QCheckBox, QGraphicsDropShadowEffect,
    QWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from app.ui.material_theme import MATERIAL_COLORS, CORNER_RADIUS
from app.ui.material_components import MaterialButton, MaterialTextField, MaterialCard


class LoginWindow(QDialog):
    """Professional Material Design login dialog"""
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setup_ui()
        
        # Create initial admin if needed
        self.auth_service.create_initial_admin()
    
    def setup_ui(self):
        self.setWindowTitle("HolzbauERP - Anmeldung")
        self.setFixedSize(440, 580)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # Clean professional background
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
        main_layout.setSpacing(0)
        
        # Card container - clean white card
        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            QFrame#loginCard {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # Subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== HEADER - Professional with company branding =====
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: #1565C0;
                border-top-left-radius: 11px;
                border-top-right-radius: 11px;
            }
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 16, 0, 16)
        header_layout.setSpacing(4)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Company icon
        logo = QLabel("🏗️")
        logo.setFont(QFont("Segoe UI Emoji", 28))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: white;")
        header_layout.addWidget(logo)
        
        # Title
        title = QLabel("HolzbauERP")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.DemiBold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; letter-spacing: 0.5px;")
        header_layout.addWidget(title)
        
        card_layout.addWidget(header)
        
        # ===== FORM CONTENT =====
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(32, 28, 32, 28)
        form_layout.setSpacing(0)
        
        # Welcome text
        welcome = QLabel("Anmeldung")
        welcome.setFont(QFont("Segoe UI", 18, QFont.Weight.DemiBold))
        welcome.setStyleSheet("color: #212121; margin-bottom: 4px;")
        form_layout.addWidget(welcome)
        
        subtitle = QLabel("Bitte melden Sie sich mit Ihren Zugangsdaten an")
        subtitle.setStyleSheet("color: #757575; font-size: 13px; margin-bottom: 24px;")
        form_layout.addWidget(subtitle)
        
        # ===== EMAIL FIELD =====
        email_label = QLabel("E-Mail-Adresse")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        email_label.setStyleSheet("color: #424242; margin-bottom: 6px;")
        form_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ihre@email.de")
        self.email_input.setText("admin@holzbau-erp.de")
        self.email_input.setMinimumHeight(44)
        self.email_input.setStyleSheet(self._get_input_style())
        form_layout.addWidget(self.email_input)
        
        form_layout.addSpacing(16)
        
        # ===== PASSWORD FIELD =====
        password_label = QLabel("Passwort")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        password_label.setStyleSheet("color: #424242; margin-bottom: 6px;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort eingeben")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("admin123")
        self.password_input.setMinimumHeight(44)
        self.password_input.setStyleSheet(self._get_input_style())
        form_layout.addWidget(self.password_input)
        
        form_layout.addSpacing(12)
        
        # ===== REMEMBER ME =====
        self.remember_check = QCheckBox("Angemeldet bleiben")
        self.remember_check.setStyleSheet("""
            QCheckBox {
                color: #616161;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #9e9e9e;
                border-radius: 3px;
                background: white;
            }
            QCheckBox::indicator:hover {
                border-color: #1565C0;
            }
            QCheckBox::indicator:checked {
                background: #1565C0;
                border-color: #1565C0;
            }
        """)
        form_layout.addWidget(self.remember_check)
        
        form_layout.addSpacing(24)
        
        # ===== LOGIN BUTTON =====
        self.login_btn = QPushButton("Anmelden")
        self.login_btn.setMinimumHeight(48)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_btn)
        
        form_layout.addSpacing(16)
        
        # ===== DIVIDER =====
        divider_widget = QWidget()
        divider_layout = QHBoxLayout(divider_widget)
        divider_layout.setContentsMargins(0, 0, 0, 0)
        divider_layout.setSpacing(12)
        
        line1 = QFrame()
        line1.setFixedHeight(1)
        line1.setStyleSheet("background: #e0e0e0;")
        line1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        divider_layout.addWidget(line1)
        
        or_label = QLabel("oder")
        or_label.setStyleSheet("color: #9e9e9e; font-size: 12px;")
        divider_layout.addWidget(or_label)
        
        line2 = QFrame()
        line2.setFixedHeight(1)
        line2.setStyleSheet("background: #e0e0e0;")
        line2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        divider_layout.addWidget(line2)
        
        form_layout.addWidget(divider_widget)
        
        form_layout.addSpacing(16)
        
        # ===== REGISTER BUTTON =====
        register_btn = QPushButton("Neues Konto erstellen")
        register_btn.setMinimumHeight(48)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1565C0;
                border: 1px solid #1565C0;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(21, 101, 192, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(21, 101, 192, 0.12);
            }
        """)
        register_btn.clicked.connect(self.show_register)
        form_layout.addWidget(register_btn)
        
        # Version
        form_layout.addStretch()
        
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #bdbdbd; font-size: 11px; margin-top: 12px;")
        form_layout.addWidget(version)
        
        card_layout.addWidget(form_container)
        main_layout.addWidget(card)
        
        # Connections
        self.password_input.returnPressed.connect(self.handle_login)
        self.email_input.returnPressed.connect(lambda: self.password_input.setFocus())
        
        # Set focus
        self.email_input.setFocus()
    
    def _get_input_style(self):
        """Professional input field style"""
        return """
            QLineEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                color: #212121;
            }
            QLineEdit:focus {
                border: 2px solid #1565C0;
                background-color: white;
            }
            QLineEdit:hover:!focus {
                border-color: #bdbdbd;
            }
            QLineEdit::placeholder {
                color: #9e9e9e;
            }
        """
    
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Fehler", "Bitte E-Mail und Passwort eingeben.")
            return
        
        self.login_btn.setText("Anmelden...")
        self.login_btn.setEnabled(False)
        
        success, message = self.auth_service.login(email, password)
        
        self.login_btn.setText("Anmelden")
        self.login_btn.setEnabled(True)
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Anmeldung fehlgeschlagen", message)
    
    def show_register(self):
        from app.ui.dialogs.register_dialog import RegisterDialog
        dialog = RegisterDialog(self.auth_service, self)
        if dialog.exec():
            # Auto-fill email after registration
            self.email_input.setText(dialog.email)
            self.password_input.clear()
            self.password_input.setFocus()
