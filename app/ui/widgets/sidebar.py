"""
Sidebar Navigation Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor

from app.ui.styles import COLORS


class SidebarButton(QPushButton):
    """Modern sidebar navigation button with hover effects"""
    
    def __init__(self, icon: str, text: str, name: str):
        super().__init__()
        self.icon_text = icon
        self.label_text = text
        self.name = name
        self.setText(f"  {icon}    {text}")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setStyleSheet(self._get_style())
    
    def _get_style(self):
        return f"""
            QPushButton {{
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                color: rgba(255, 255, 255, 0.75);
                background: transparent;
                margin: 2px 12px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.08);
                color: white;
            }}
            QPushButton:checked {{
                background: rgba(1, 118, 211, 0.3);
                color: white;
                font-weight: 600;
                border-left: 3px solid {COLORS['primary_light']};
                border-radius: 0 8px 8px 0;
                margin-left: 0;
                padding-left: 32px;
            }}
        """


class Sidebar(QFrame):
    """Modern sidebar navigation panel"""
    
    navigation_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.buttons = {}
        self.setObjectName("sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedWidth(260)
        self.setStyleSheet(f"""
            QFrame#sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['secondary']}, stop:1 #01315e);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Logo/Brand area
        brand_frame = QFrame()
        brand_frame.setFixedHeight(80)
        brand_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.2);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo icon
        logo = QLabel("🏠")
        logo.setFont(QFont("Segoe UI", 28))
        logo.setStyleSheet("background: transparent;")
        brand_layout.addWidget(logo)
        
        # Brand text
        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(0)
        
        brand_name = QLabel("HolzbauERP")
        brand_name.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        brand_name.setStyleSheet("color: white; background: transparent;")
        brand_text_layout.addWidget(brand_name)
        
        brand_sub = QLabel("Enterprise")
        brand_sub.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px; background: transparent;")
        brand_text_layout.addWidget(brand_sub)
        
        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()
        
        layout.addWidget(brand_frame)
        
        # Section label
        section_label = QLabel("  HAUPTMENÜ")
        section_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.4);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 20px 20px 8px 20px;
            background: transparent;
        """)
        layout.addWidget(section_label)
        
        # Navigation items
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("👥", "Kunden", "customers"),
            ("🏗️", "Projekte", "projects"),
            ("📋", "Bautagebuch", "construction_diary"),
            ("📦", "Material", "materials"),
            ("🚚", "Lieferanten", "suppliers"),
            ("📋", "Aufträge", "orders"),
            ("💰", "Rechnungen", "invoices"),
            ("👷", "Mitarbeiter", "employees"),
            ("🚗", "Fuhrpark", "fleet"),
            ("🤝", "CRM", "crm"),
            ("✅", "Qualität", "quality"),
            ("📒", "Buchhaltung", "accounting"),
            ("💼", "Lohnverwaltung", "payroll"),
            ("🏦", "Finanzen", "finance"),
        ]
        
        for icon, text, name in nav_items:
            btn = SidebarButton(icon, text, name)
            btn.clicked.connect(lambda checked, n=name: self._on_click(n))
            self.buttons[name] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Bottom section
        bottom_label = QLabel("  SYSTEM")
        bottom_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.4);
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 8px 20px;
            background: transparent;
        """)
        layout.addWidget(bottom_label)
        
        # Telemetry
        telemetry_btn = SidebarButton("📈", "Telemetrie", "telemetry")
        telemetry_btn.clicked.connect(lambda: self._on_click("telemetry"))
        self.buttons["telemetry"] = telemetry_btn
        layout.addWidget(telemetry_btn)
        
        # Settings
        settings_btn = SidebarButton("⚙️", "Einstellungen", "settings")
        settings_btn.clicked.connect(lambda: self._on_click("settings"))
        self.buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)
        
        # Help button
        help_btn = SidebarButton("❓", "Hilfe & Support", "help")
        help_btn.clicked.connect(lambda: self._on_click("help"))
        self.buttons["help"] = help_btn
        layout.addWidget(help_btn)
        
        layout.addSpacing(20)
    
    def _on_click(self, name: str):
        self.navigation_clicked.emit(name)
    
    def set_active(self, name: str):
        """Set active navigation item"""
        for btn_name, btn in self.buttons.items():
            btn.setChecked(btn_name == name)
