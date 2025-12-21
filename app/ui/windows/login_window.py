"""
Login Window - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QCheckBox, QGraphicsDropShadowEffect,
    QWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from app.ui.styles import COLORS


class LoginWindow(QDialog):
    """Modern login dialog window"""
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setup_ui()
        
        # Create initial admin if needed
        self.auth_service.create_initial_admin()
    
    def setup_ui(self):
        self.setWindowTitle("HolzbauERP - Anmeldung")
        self.setFixedSize(460, 600)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # Main background gradient
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['secondary']}, stop:1 {COLORS['primary_dark']});
            }}
            QLabel {{
                background: transparent;
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(0)
        
        # Card container
        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            QFrame#loginCard {
                background: white;
                border-radius: 16px;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== HEADER =====
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['secondary']}, stop:1 {COLORS['primary']});
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 16, 0, 16)
        header_layout.setSpacing(4)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo = QLabel("🏠")
        logo.setFont(QFont("Segoe UI Emoji", 32))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: white;")
        header_layout.addWidget(logo)
        
        title = QLabel("HolzbauERP")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        card_layout.addWidget(header)
        
        # ===== FORM CONTENT =====
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(32, 24, 32, 24)
        form_layout.setSpacing(0)
        
        # Welcome text
        welcome = QLabel("Willkommen zurück")
        welcome.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        welcome.setStyleSheet(f"color: {COLORS['text_primary']}; margin-bottom: 4px;")
        form_layout.addWidget(welcome)
        
        subtitle = QLabel("Melden Sie sich an, um fortzufahren")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; margin-bottom: 20px;")
        form_layout.addWidget(subtitle)
        
        # ===== EMAIL FIELD =====
        email_label = QLabel("E-MAIL-ADRESSE")
        email_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        email_label.setStyleSheet(f"color: {COLORS['text_secondary']}; letter-spacing: 0.5px; margin-bottom: 6px; margin-top: 8px;")
        form_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ihre@email.de")
        self.email_input.setText("admin@holzbau-erp.de")
        self.email_input.setMinimumHeight(44)
        self.email_input.setStyleSheet(self._get_input_style())
        form_layout.addWidget(self.email_input)
        
        # Spacer
        form_layout.addSpacing(16)
        
        # ===== PASSWORD FIELD =====
        password_label = QLabel("PASSWORT")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        password_label.setStyleSheet(f"color: {COLORS['text_secondary']}; letter-spacing: 0.5px; margin-bottom: 6px;")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("admin123")
        self.password_input.setMinimumHeight(44)
        self.password_input.setStyleSheet(self._get_input_style())
        form_layout.addWidget(self.password_input)
        
        # Spacer
        form_layout.addSpacing(12)
        
        # ===== REMEMBER ME =====
        self.remember_check = QCheckBox("Angemeldet bleiben")
        self.remember_check.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_secondary']};
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['gray_200']};
                border-radius: 4px;
                background: white;
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        form_layout.addWidget(self.remember_check)
        
        # Spacer
        form_layout.addSpacing(20)
        
        # ===== LOGIN BUTTON =====
        self.login_btn = QPushButton("Anmelden")
        self.login_btn.setMinimumHeight(46)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
            }}
            QPushButton:pressed {{
                background: {COLORS['primary_dark']};
            }}
            QPushButton:disabled {{
                background: {COLORS['gray_300']};
            }}
        """)
        self.login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_btn)
        
        # Spacer
        form_layout.addSpacing(20)
        
        # ===== DIVIDER =====
        divider_widget = QWidget()
        divider_layout = QHBoxLayout(divider_widget)
        divider_layout.setContentsMargins(0, 0, 0, 0)
        divider_layout.setSpacing(12)
        
        line1 = QFrame()
        line1.setFixedHeight(1)
        line1.setStyleSheet(f"background: {COLORS['gray_100']};")
        line1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        divider_layout.addWidget(line1)
        
        or_label = QLabel("oder")
        or_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        divider_layout.addWidget(or_label)
        
        line2 = QFrame()
        line2.setFixedHeight(1)
        line2.setStyleSheet(f"background: {COLORS['gray_100']};")
        line2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        divider_layout.addWidget(line2)
        
        form_layout.addWidget(divider_widget)
        
        # Spacer
        form_layout.addSpacing(20)
        
        # ===== REGISTER BUTTON =====
        register_btn = QPushButton("Neues Konto erstellen")
        register_btn.setMinimumHeight(46)
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        register_btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_50']};
            }}
        """)
        register_btn.clicked.connect(self.show_register)
        form_layout.addWidget(register_btn)
        
        # Version at bottom
        form_layout.addStretch()
        
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"color: {COLORS['gray_300']}; font-size: 11px; margin-top: 16px;")
        form_layout.addWidget(version)
        
        card_layout.addWidget(form_container)
        main_layout.addWidget(card)
        
        # Connections
        self.password_input.returnPressed.connect(self.handle_login)
        self.email_input.returnPressed.connect(lambda: self.password_input.setFocus())
        
        # Set focus
        self.email_input.setFocus()
    
    def _get_input_style(self):
        return f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 2px solid {COLORS['gray_100']};
                border-radius: 8px;
                font-size: 14px;
                background: {COLORS['gray_50']};
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
                background: white;
            }}
            QLineEdit:hover:!focus {{
                border-color: {COLORS['gray_200']};
            }}
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
