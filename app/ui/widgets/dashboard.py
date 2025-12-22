"""
Dashboard Widget - Material Design 3
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from sqlalchemy import select, func
from datetime import date, timedelta, datetime

from shared.models import Customer, Project, Quote, Order, Invoice, Employee
from shared.models.project import ProjectStatus
from shared.models.invoice import InvoiceStatus
from shared.models.order import QuoteStatus
from app.ui.material_theme import MATERIAL_COLORS, CORNER_RADIUS


class StatCard(QFrame):
    """Material Design Statistics Card"""
    
    def __init__(self, title: str, value: str, icon: str, color: str = None, trend: str = None):
        super().__init__()
        self.color = color or MATERIAL_COLORS['primary']
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background: {MATERIAL_COLORS['surface']};
                border: 1px solid {MATERIAL_COLORS['outline_variant']};
                border-radius: {CORNER_RADIUS['medium']};
            }}
            QFrame#statCard:hover {{
                border-color: {self.color};
            }}
        """)
        self.setMinimumHeight(140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Material elevation shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # Top row with icon and trend
        top_row = QHBoxLayout()
        
        # Icon container with Material Design
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            background: rgba({self._hex_to_rgb(self.color)}, 0.12);
            border-radius: 12px;
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        icon_layout.addWidget(icon_label)
        
        top_row.addWidget(icon_container)
        top_row.addStretch()
        
        # Trend indicator
        if trend:
            trend_label = QLabel(trend)
            is_positive = "+" in trend or "↑" in trend
            trend_color = MATERIAL_COLORS['success'] if is_positive else MATERIAL_COLORS['error']
            trend_label.setStyleSheet(f"""
                color: {trend_color};
                font-size: 12px;
                font-weight: 500;
                font-family: 'Roboto';
                background: transparent;
            """)
            top_row.addWidget(trend_label)
        
        layout.addLayout(top_row)
        
        # Value with Material Typography
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Roboto", 32, QFont.Weight.Normal))
        self.value_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface']}; background: transparent;")
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface_variant']};
            font-size: 14px;
            font-weight: 500;
            font-family: 'Roboto';
            background: transparent;
        """)
        layout.addWidget(title_label)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{r}, {g}, {b}"
    
    def set_value(self, value: str):
        self.value_label.setText(value)


class DashboardWidget(QWidget):
    """Material Design Dashboard"""
    
    def __init__(self, db_service, user=None):
        super().__init__()
        self.db = db_service
        self.user = user
        self.setStyleSheet(f"background: {MATERIAL_COLORS['background']};")
        self.setup_ui()
    
    def setup_ui(self):
        # Scroll area for responsive layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Welcome section with Material Design
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {MATERIAL_COLORS['primary']}, 
                    stop:1 {MATERIAL_COLORS['primary_light']});
                border-radius: {CORNER_RADIUS['large']};
            }}
        """)
        welcome_frame.setMinimumHeight(160)
        
        # Material elevation shadow
        welcome_shadow = QGraphicsDropShadowEffect()
        welcome_shadow.setBlurRadius(16)
        welcome_shadow.setXOffset(0)
        welcome_shadow.setYOffset(4)
        welcome_shadow.setColor(QColor(25, 118, 210, 80))
        welcome_frame.setGraphicsEffect(welcome_shadow)
        
        welcome_layout = QHBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(40, 32, 40, 32)
        
        # Left side - text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(12)
        
        # Get current time for greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting_text = "Guten Morgen! ☀️"
        elif hour < 18:
            greeting_text = "Guten Tag! 👋"
        else:
            greeting_text = "Guten Abend! 🌙"
        
        greeting = QLabel(greeting_text)
        greeting.setFont(QFont("Roboto", 28, QFont.Weight.Normal))
        greeting.setStyleSheet(f"color: {MATERIAL_COLORS['on_primary']}; background: transparent;")
        text_layout.addWidget(greeting)
        
        subtitle = QLabel("Hier ist Ihre Übersicht für heute")
        subtitle.setStyleSheet(f"color: rgba(255,255,255,0.85); font-size: 16px; font-family: 'Roboto'; background: transparent;")
        text_layout.addWidget(subtitle)
        
        # Date
        date_label = QLabel(datetime.now().strftime("%A, %d. %B %Y"))
        date_label.setStyleSheet(f"color: rgba(255,255,255,0.7); font-size: 14px; font-family: 'Roboto'; background: transparent; margin-top: 8px;")
        text_layout.addWidget(date_label)
        
        welcome_layout.addLayout(text_layout)
        welcome_layout.addStretch()
        
        # Right side - decorative icon
        icon_label = QLabel("🏗️")
        icon_label.setFont(QFont("Segoe UI Emoji", 56))
        icon_label.setStyleSheet("background: transparent;")
        welcome_layout.addWidget(icon_label)
        
        layout.addWidget(welcome_frame)
        
        # Section title with Material Typography
        stats_label = QLabel("Übersicht")
        stats_label.setFont(QFont("Roboto", 22, QFont.Weight.Normal))
        stats_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface']}; margin-top: 8px;")
        layout.addWidget(stats_label)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        # Create stat cards with Material colors
        self.stat_cards = {}
        stats = [
            ("Kunden", "0", "👥", MATERIAL_COLORS['primary'], "customers"),
            ("Aktive Projekte", "0", "🏗️", MATERIAL_COLORS['secondary'], "projects"),
            ("Offene Angebote", "0", "📄", MATERIAL_COLORS['tertiary'], "quotes"),
            ("Offene Aufträge", "0", "📋", MATERIAL_COLORS['warning'], "orders"),
            ("Offene Rechnungen", "0", "💰", MATERIAL_COLORS['success'], "invoices"),
            ("Mitarbeiter", "0", "👷", MATERIAL_COLORS['primary_light'], "employees"),
        ]
        
        for i, (title, value, icon, color, key) in enumerate(stats):
            card = StatCard(title, value, icon, color)
            self.stat_cards[key] = card
            stats_layout.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(stats_layout)
        
        # Quick Actions section
        actions_label = QLabel("Schnellaktionen")
        actions_label.setFont(QFont("Roboto", 22, QFont.Weight.Normal))
        actions_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface']}; margin-top: 16px;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)
        
        quick_actions = [
            ("➕ Neuer Kunde", MATERIAL_COLORS['primary']),
            ("📝 Neues Projekt", MATERIAL_COLORS['secondary']),
            ("📄 Neues Angebot", MATERIAL_COLORS['tertiary']),
            ("📋 Neue Rechnung", MATERIAL_COLORS['success']),
        ]
        
        for text, color in quick_actions:
            btn_frame = QFrame()
            btn_frame.setStyleSheet(f"""
                QFrame {{
                    background: {MATERIAL_COLORS['surface']};
                    border: 1px solid {MATERIAL_COLORS['outline_variant']};
                    border-radius: {CORNER_RADIUS['medium']};
                    padding: 16px 24px;
                }}
                QFrame:hover {{
                    background: {MATERIAL_COLORS['surface_container_low']};
                    border-color: {color};
                }}
            """)
            btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn_layout = QVBoxLayout(btn_frame)
            btn_layout.setContentsMargins(16, 12, 16, 12)
            
            btn_label = QLabel(text)
            btn_label.setStyleSheet(f"""
                color: {color};
                font-size: 14px;
                font-weight: 500;
                font-family: 'Roboto';
                background: transparent;
            """)
            btn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(btn_label)
            
            actions_layout.addWidget(btn_frame)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Load actual data
        self.load_statistics()
    
    def load_statistics(self):
        """Load statistics from database"""
        try:
            with self.db.session_scope() as session:
                tenant_id = self.user.tenant_id if self.user and hasattr(self.user, 'tenant_id') else None
                
                # Count customers
                customer_count = session.query(func.count(Customer.id)).filter(
                    Customer.is_deleted == False
                ).scalar() or 0
                self.stat_cards["customers"].set_value(str(customer_count))
                
                # Count active projects
                try:
                    project_count = session.query(func.count(Project.id)).filter(
                        Project.is_deleted == False,
                        Project.status.in_([ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS])
                    ).scalar() or 0
                    self.stat_cards["projects"].set_value(str(project_count))
                except:
                    self.stat_cards["projects"].set_value("0")
                
                # Count open quotes
                try:
                    quote_count = session.query(func.count(Quote.id)).filter(
                        Quote.is_deleted == False,
                        Quote.status.in_([QuoteStatus.DRAFT, QuoteStatus.SENT])
                    ).scalar() or 0
                    self.stat_cards["quotes"].set_value(str(quote_count))
                except:
                    self.stat_cards["quotes"].set_value("0")
                
                # Count open orders
                try:
                    order_count = session.query(func.count(Order.id)).filter(
                        Order.is_deleted == False
                    ).scalar() or 0
                    self.stat_cards["orders"].set_value(str(order_count))
                except:
                    self.stat_cards["orders"].set_value("0")
                
                # Count open invoices
                try:
                    invoice_count = session.query(func.count(Invoice.id)).filter(
                        Invoice.is_deleted == False,
                        Invoice.status.in_([InvoiceStatus.DRAFT, InvoiceStatus.SENT])
                    ).scalar() or 0
                    self.stat_cards["invoices"].set_value(str(invoice_count))
                except:
                    self.stat_cards["invoices"].set_value("0")
                
                # Count employees
                try:
                    employee_count = session.query(func.count(Employee.id)).filter(
                        Employee.is_deleted == False
                    ).scalar() or 0
                    self.stat_cards["employees"].set_value(str(employee_count))
                except:
                    self.stat_cards["employees"].set_value("0")
                    
        except Exception as e:
            print(f"Error loading dashboard statistics: {e}")
