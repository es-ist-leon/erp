"""
Sidebar Navigation Widget - Material Design 3 with Responsive Support
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor

from app.ui.material_theme import MATERIAL_COLORS, CORNER_RADIUS


class SidebarButton(QPushButton):
    """Material Design navigation item with collapse support"""
    
    def __init__(self, icon: str, text: str, name: str):
        super().__init__()
        self.icon_text = icon
        self.label_text = text
        self.name = name
        self._collapsed = False
        self.setText(f"  {icon}    {text}")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(48)
        self.setStyleSheet(self._get_style())
        self.setToolTip(text)
    
    def set_collapsed(self, collapsed: bool):
        """Toggle between collapsed (icon only) and expanded mode"""
        self._collapsed = collapsed
        if collapsed:
            self.setText(f"  {self.icon_text}")
            self.setStyleSheet(self._get_collapsed_style())
        else:
            self.setText(f"  {self.icon_text}    {self.label_text}")
            self.setStyleSheet(self._get_style())
    
    def _get_collapsed_style(self):
        return f"""
            QPushButton {{
                text-align: center;
                padding: 12px 0px;
                border: none;
                border-radius: 24px;
                font-size: 18px;
                color: {MATERIAL_COLORS['on_surface_variant']};
                background: transparent;
                margin: 2px 8px;
            }}
            QPushButton:hover {{
                background: {MATERIAL_COLORS['surface_container_highest']};
                color: {MATERIAL_COLORS['on_surface']};
            }}
            QPushButton:checked {{
                background: rgba(25, 118, 210, 0.12);
                color: {MATERIAL_COLORS['primary']};
            }}
        """
    
    def _get_style(self):
        return f"""
            QPushButton {{
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 24px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Roboto', 'Segoe UI', sans-serif;
                color: {MATERIAL_COLORS['on_surface_variant']};
                background: transparent;
                margin: 2px 12px;
            }}
            QPushButton:hover {{
                background: {MATERIAL_COLORS['surface_container_highest']};
                color: {MATERIAL_COLORS['on_surface']};
            }}
            QPushButton:checked {{
                background: rgba(25, 118, 210, 0.12);
                color: {MATERIAL_COLORS['primary']};
                font-weight: 600;
            }}
        """


class Sidebar(QFrame):
    """Material Design Navigation Drawer with Responsive Collapse"""
    
    navigation_clicked = pyqtSignal(str)
    collapsed_changed = pyqtSignal(bool)
    
    EXPANDED_WIDTH = 260
    COLLAPSED_WIDTH = 72
    
    def __init__(self):
        super().__init__()
        self.buttons = {}
        self._collapsed = False
        self._labels = []
        self._dividers = []
        self.setObjectName("sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedWidth(self.EXPANDED_WIDTH)
        self.setStyleSheet(f"""
            QFrame#sidebar {{
                background: {MATERIAL_COLORS['surface']};
                border-right: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Brand area with collapse toggle
        brand_frame = QFrame()
        brand_frame.setFixedHeight(64)
        brand_frame.setStyleSheet(f"""
            QFrame {{
                background: {MATERIAL_COLORS['primary']};
                border: none;
            }}
        """)
        
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(16, 0, 8, 0)
        brand_layout.setSpacing(12)
        
        # Logo icon
        logo = QLabel("🏗️")
        logo.setFont(QFont("Segoe UI Emoji", 24))
        logo.setStyleSheet("background: transparent;")
        brand_layout.addWidget(logo)
        
        # Brand text container (hidden when collapsed)
        self.brand_text_container = QWidget()
        brand_text_layout = QVBoxLayout(self.brand_text_container)
        brand_text_layout.setContentsMargins(0, 0, 0, 0)
        brand_text_layout.setSpacing(0)
        
        brand_name = QLabel("HolzbauERP")
        brand_name.setFont(QFont("Roboto", 16, QFont.Weight.Medium))
        brand_name.setStyleSheet(f"color: {MATERIAL_COLORS['on_primary']}; background: transparent;")
        brand_text_layout.addWidget(brand_name)
        
        brand_sub = QLabel("Enterprise")
        brand_sub.setStyleSheet(f"color: rgba(255,255,255,0.7); font-size: 10px; font-family: 'Roboto'; background: transparent;")
        brand_text_layout.addWidget(brand_sub)
        
        brand_layout.addWidget(self.brand_text_container)
        brand_layout.addStretch()
        
        # Collapse toggle button
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFixedSize(32, 32)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.15);
                border: none;
                border-radius: 16px;
                color: white;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.25);
            }}
        """)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        brand_layout.addWidget(self.collapse_btn)
        
        layout.addWidget(brand_frame)
        
        # Scrollable navigation area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 8, 0, 8)
        nav_layout.setSpacing(4)
        
        # Section: Main Menu
        section_label = QLabel("HAUPTMENÜ")
        section_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface_variant']};
            font-size: 11px;
            font-weight: 500;
            font-family: 'Roboto';
            letter-spacing: 1px;
            padding: 12px 20px 8px 20px;
            background: transparent;
        """)
        self._labels.append(section_label)
        nav_layout.addWidget(section_label)
        
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
        ]
        
        for icon, text, name in nav_items:
            btn = SidebarButton(icon, text, name)
            btn.clicked.connect(lambda checked, n=name: self._on_click(n))
            self.buttons[name] = btn
            nav_layout.addWidget(btn)
        
        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {MATERIAL_COLORS['outline_variant']}; margin: 8px 16px;")
        self._dividers.append(divider)
        nav_layout.addWidget(divider)
        
        # Section: Finance
        finance_label = QLabel("FINANZEN")
        finance_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface_variant']};
            font-size: 11px;
            font-weight: 500;
            font-family: 'Roboto';
            letter-spacing: 1px;
            padding: 8px 20px;
            background: transparent;
        """)
        self._labels.append(finance_label)
        nav_layout.addWidget(finance_label)
        
        finance_items = [
            ("📒", "Buchhaltung", "accounting"),
            ("💼", "Lohnverwaltung", "payroll"),
            ("🏦", "Finanzen", "finance"),
        ]
        
        for icon, text, name in finance_items:
            btn = SidebarButton(icon, text, name)
            btn.clicked.connect(lambda checked, n=name: self._on_click(n))
            self.buttons[name] = btn
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Divider
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet(f"background: {MATERIAL_COLORS['outline_variant']}; margin: 8px 16px;")
        self._dividers.append(divider2)
        nav_layout.addWidget(divider2)
        
        # Section: System
        system_label = QLabel("SYSTEM")
        system_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface_variant']};
            font-size: 11px;
            font-weight: 500;
            font-family: 'Roboto';
            letter-spacing: 1px;
            padding: 8px 20px;
            background: transparent;
        """)
        self._labels.append(system_label)
        nav_layout.addWidget(system_label)
        
        system_items = [
            ("🤖", "ML Insights", "ml_insights"),
            ("📈", "Telemetrie", "telemetry"),
            ("⚙️", "Einstellungen", "settings"),
            ("❓", "Hilfe & Support", "help"),
        ]
        
        for icon, text, name in system_items:
            btn = SidebarButton(icon, text, name)
            btn.clicked.connect(lambda checked, n=name: self._on_click(n))
            self.buttons[name] = btn
            nav_layout.addWidget(btn)
        
        nav_layout.addSpacing(16)
        
        scroll.setWidget(nav_widget)
        layout.addWidget(scroll)
    
    def toggle_collapse(self):
        """Toggle sidebar collapsed state"""
        self._collapsed = not self._collapsed
        self._apply_collapsed_state()
        self.collapsed_changed.emit(self._collapsed)
    
    def set_collapsed(self, collapsed: bool):
        """Set sidebar collapsed state"""
        if self._collapsed != collapsed:
            self._collapsed = collapsed
            self._apply_collapsed_state()
            self.collapsed_changed.emit(self._collapsed)
    
    def _apply_collapsed_state(self):
        """Apply collapsed/expanded styling"""
        if self._collapsed:
            self.setFixedWidth(self.COLLAPSED_WIDTH)
            self.collapse_btn.setText("▶")
            self.brand_text_container.hide()
            for label in self._labels:
                label.hide()
            for divider in self._dividers:
                divider.setStyleSheet(f"background: {MATERIAL_COLORS['outline_variant']}; margin: 8px 8px;")
        else:
            self.setFixedWidth(self.EXPANDED_WIDTH)
            self.collapse_btn.setText("◀")
            self.brand_text_container.show()
            for label in self._labels:
                label.show()
            for divider in self._dividers:
                divider.setStyleSheet(f"background: {MATERIAL_COLORS['outline_variant']}; margin: 8px 16px;")
        
        # Update buttons
        for btn in self.buttons.values():
            btn.set_collapsed(self._collapsed)
    
    @property
    def is_collapsed(self) -> bool:
        return self._collapsed
    
    def _on_click(self, name: str):
        self.navigation_clicked.emit(name)
    
    def set_active(self, name: str):
        """Set active navigation item"""
        for btn_name, btn in self.buttons.items():
            btn.setChecked(btn_name == name)
