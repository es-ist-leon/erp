"""
Dashboard Widget - Modern Salesforce-inspired Design
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
from app.ui.styles import COLORS


class StatCard(QFrame):
    """Modern statistics card with gradient accent"""
    
    def __init__(self, title: str, value: str, icon: str, color: str = "#0176d3", trend: str = None):
        super().__init__()
        self.color = color
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background: white;
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
            QFrame#statCard:hover {{
                border-color: {color};
            }}
        """)
        self.setMinimumHeight(130)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        # Top row with icon and trend
        top_row = QHBoxLayout()
        
        # Icon in colored circle
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"""
            background: {color}20;
            border-radius: 12px;
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")
        icon_layout.addWidget(icon_label)
        
        top_row.addWidget(icon_container)
        top_row.addStretch()
        
        # Trend indicator
        if trend:
            trend_label = QLabel(trend)
            trend_color = COLORS['success'] if "+" in trend else COLORS['error']
            trend_label.setStyleSheet(f"""
                color: {trend_color};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            """)
            top_row.addWidget(trend_label)
        
        layout.addLayout(top_row)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
        """)
        layout.addWidget(title_label)
    
    def set_value(self, value: str):
        self.value_label.setText(value)


class DashboardWidget(QWidget):
    """Modern dashboard with overview statistics"""
    
    def __init__(self, db_service, user=None):
        super().__init__()
        self.db = db_service
        self.user = user
        self.setStyleSheet(f"background: {COLORS['bg_primary']};")
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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Welcome section with modern design
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #032d60, stop:0.5 #0176d3, stop:1 #1b96ff);
                border-radius: 16px;
            }}
        """)
        welcome_frame.setMinimumHeight(140)
        
        # Add shadow to welcome frame
        welcome_shadow = QGraphicsDropShadowEffect()
        welcome_shadow.setBlurRadius(20)
        welcome_shadow.setXOffset(0)
        welcome_shadow.setYOffset(8)
        welcome_shadow.setColor(QColor(1, 118, 211, 80))
        welcome_frame.setGraphicsEffect(welcome_shadow)
        
        welcome_layout = QHBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(32, 28, 32, 28)
        
        # Left side - text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        
        # Get current time for greeting
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:
            greeting_text = "Guten Morgen! ☀️"
        elif hour < 18:
            greeting_text = "Guten Tag! 👋"
        else:
            greeting_text = "Guten Abend! 🌙"
        
        greeting = QLabel(greeting_text)
        greeting.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        greeting.setStyleSheet("color: white; background: transparent;")
        text_layout.addWidget(greeting)
        
        subtitle = QLabel("Hier ist Ihre Übersicht für heute")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 15px; background: transparent;")
        text_layout.addWidget(subtitle)
        
        # Quick stats in welcome banner
        stats_row = QHBoxLayout()
        stats_row.setSpacing(24)
        
        welcome_layout.addLayout(text_layout)
        welcome_layout.addStretch()
        
        # Right side - decorative icon
        icon_label = QLabel("🏗️")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setStyleSheet("background: transparent;")
        welcome_layout.addWidget(icon_label)
        
        layout.addWidget(welcome_frame)
        
        # Stats grid
        stats_label = QLabel("Übersicht")
        stats_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        stats_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(stats_label)
        
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        
        self.stat_cards = {
            "customers": StatCard("Kunden", "0", "👥", COLORS['primary']),
            "projects": StatCard("Aktive Projekte", "0", "🏗️", COLORS['success']),
            "quotes": StatCard("Offene Angebote", "0", "📋", COLORS['warning']),
            "invoices": StatCard("Offene Rechnungen", "0", "💰", COLORS['error']),
        }
        
        stats_layout.addWidget(self.stat_cards["customers"], 0, 0)
        stats_layout.addWidget(self.stat_cards["projects"], 0, 1)
        stats_layout.addWidget(self.stat_cards["quotes"], 0, 2)
        stats_layout.addWidget(self.stat_cards["invoices"], 0, 3)
        
        layout.addLayout(stats_layout)
        
        # Financial section
        finance_label = QLabel("Finanzen")
        finance_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        finance_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(finance_label)
        
        financial_layout = QHBoxLayout()
        financial_layout.setSpacing(16)
        
        # Revenue card
        self.revenue_frame = self._create_finance_card("💵", "Umsatz (aktuelles Jahr)", COLORS['success'])
        self.revenue_label = self.revenue_frame.findChild(QLabel, "mainValue")
        self.revenue_paid = self.revenue_frame.findChild(QLabel, "subValue")
        financial_layout.addWidget(self.revenue_frame)
        
        # Open amounts card
        self.open_frame = self._create_finance_card("📊", "Offene Posten", COLORS['error'])
        self.open_total = self.open_frame.findChild(QLabel, "mainValue")
        self.overdue_label = self.open_frame.findChild(QLabel, "subValue")
        financial_layout.addWidget(self.open_frame)
        
        layout.addLayout(financial_layout)
        
        # Recent activity
        activity_label = QLabel("Letzte Aktivitäten")
        activity_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        activity_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(activity_label)
        
        activity_frame = QFrame()
        activity_frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        activity_frame.setGraphicsEffect(shadow)
        
        activity_inner = QVBoxLayout(activity_frame)
        activity_inner.setContentsMargins(24, 20, 24, 20)
        activity_inner.setSpacing(0)
        
        self.activity_list = QVBoxLayout()
        self.activity_list.setSpacing(0)
        activity_inner.addLayout(self.activity_list)
        
        layout.addWidget(activity_frame)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_finance_card(self, icon: str, title: str, color: str) -> QFrame:
        """Create a modern finance card"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        header.addWidget(title_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Main value
        main_value = QLabel("0,00 €")
        main_value.setObjectName("mainValue")
        main_value.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        main_value.setStyleSheet(f"color: {color};")
        layout.addWidget(main_value)
        
        # Sub value
        sub_value = QLabel("Davon bezahlt: 0,00 €")
        sub_value.setObjectName("subValue")
        sub_value.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(sub_value)
        
        return frame
    
    def refresh(self):
        """Refresh dashboard data"""
        session = self.db.get_session()
        try:
            # Count customers
            count = session.execute(
                select(func.count(Customer.id)).where(Customer.is_deleted == False)
            ).scalar() or 0
            self.stat_cards["customers"].set_value(str(count))
            
            # Count active projects
            count = session.execute(
                select(func.count(Project.id)).where(
                    Project.is_deleted == False,
                    Project.status.in_([
                        ProjectStatus.BEAUFTRAGT,
                        ProjectStatus.PLANUNG,
                        ProjectStatus.PRODUKTION,
                        ProjectStatus.MONTAGE
                    ])
                )
            ).scalar() or 0
            self.stat_cards["projects"].set_value(str(count))
            
            # Count open quotes
            count = session.execute(
                select(func.count(Quote.id)).where(
                    Quote.is_deleted == False,
                    Quote.status.in_([QuoteStatus.DRAFT, QuoteStatus.SENT])
                )
            ).scalar() or 0
            self.stat_cards["quotes"].set_value(str(count))
            
            # Count open invoices
            count = session.execute(
                select(func.count(Invoice.id)).where(
                    Invoice.is_deleted == False,
                    Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID, InvoiceStatus.OVERDUE])
                )
            ).scalar() or 0
            self.stat_cards["invoices"].set_value(str(count))
            
            # Calculate year revenue
            current_year = datetime.now().year
            start_of_year = date(current_year, 1, 1)
            
            invoices = session.execute(
                select(Invoice).where(
                    Invoice.is_deleted == False,
                    Invoice.invoice_date >= start_of_year
                )
            ).scalars().all()
            
            total_revenue = 0.0
            total_paid = 0.0
            total_open = 0.0
            total_overdue = 0.0
            
            for inv in invoices:
                try:
                    inv_total = float(inv.total or 0)
                    inv_paid = float(inv.paid_amount or 0)
                    inv_remaining = float(inv.remaining_amount or 0)
                    
                    total_revenue += inv_total
                    total_paid += inv_paid
                    
                    if inv.status in [InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID, InvoiceStatus.OVERDUE]:
                        total_open += inv_remaining
                    
                    if inv.status == InvoiceStatus.OVERDUE:
                        total_overdue += inv_remaining
                except:
                    pass
            
            # Format amounts
            def fmt_currency(amount):
                return f"{amount:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.revenue_label.setText(fmt_currency(total_revenue))
            self.revenue_paid.setText(f"Davon bezahlt: {fmt_currency(total_paid)}")
            self.open_total.setText(fmt_currency(total_open))
            self.overdue_label.setText(f"Davon überfällig: {fmt_currency(total_overdue)}")
            
            # Clear and update activity list
            while self.activity_list.count():
                item = self.activity_list.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Get recent projects
            projects = session.execute(
                select(Project)
                .where(Project.is_deleted == False)
                .order_by(Project.created_at.desc())
                .limit(5)
            ).scalars().all()
            
            if projects:
                for i, project in enumerate(projects):
                    created = project.created_at.strftime("%d.%m.%Y") if project.created_at else ""
                    
                    # Activity item container
                    item_frame = QFrame()
                    item_frame.setStyleSheet(f"""
                        QFrame {{
                            background: transparent;
                            border-bottom: 1px solid {COLORS['gray_100']};
                            padding: 12px 0;
                        }}
                    """)
                    
                    item_layout = QHBoxLayout(item_frame)
                    item_layout.setContentsMargins(0, 12, 0, 12)
                    item_layout.setSpacing(12)
                    
                    # Icon
                    icon = QLabel("🏗️")
                    icon.setFont(QFont("Segoe UI", 16))
                    icon.setFixedSize(36, 36)
                    icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    icon.setStyleSheet(f"""
                        background: {COLORS['primary']}15;
                        border-radius: 8px;
                    """)
                    item_layout.addWidget(icon)
                    
                    # Text
                    text_layout = QVBoxLayout()
                    text_layout.setSpacing(2)
                    
                    title = QLabel(f"Projekt '{project.name}' erstellt")
                    title.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
                    text_layout.addWidget(title)
                    
                    date_label = QLabel(created)
                    date_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
                    text_layout.addWidget(date_label)
                    
                    item_layout.addLayout(text_layout)
                    item_layout.addStretch()
                    
                    self.activity_list.addWidget(item_frame)
            else:
                empty = QLabel("Keine Aktivitäten vorhanden")
                empty.setStyleSheet(f"color: {COLORS['text_secondary']}; padding: 20px; text-align: center;")
                empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.activity_list.addWidget(empty)
                
        except Exception as e:
            print(f"Dashboard refresh error: {e}")
        finally:
            session.close()
