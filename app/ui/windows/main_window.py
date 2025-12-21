"""
Main Application Window - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QPushButton, QLabel, QSizePolicy, QMessageBox, QSpacerItem,
    QApplication, QLineEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction, QColor

from app.ui.widgets.sidebar import Sidebar
from app.ui.styles import COLORS, GLOBAL_STYLE, get_button_style


class PageLoader(QThread):
    """Background thread for loading pages"""
    finished = pyqtSignal(str, object)
    
    def __init__(self, page_name, db_service, user):
        super().__init__()
        self.page_name = page_name
        self.db_service = db_service
        self.user = user
    
    def run(self):
        widget = self._create_widget()
        self.finished.emit(self.page_name, widget)
    
    def _create_widget(self):
        # Import only when needed
        if self.page_name == "dashboard":
            from app.ui.widgets.dashboard import DashboardWidget
            return DashboardWidget(self.db_service, self.user)
        elif self.page_name == "customers":
            from app.ui.widgets.customers import CustomersWidget
            return CustomersWidget(self.db_service, self.user)
        elif self.page_name == "projects":
            from app.ui.widgets.projects import ProjectsWidget
            return ProjectsWidget(self.db_service, self.user)
        elif self.page_name == "materials":
            from app.ui.widgets.materials import MaterialsWidget
            return MaterialsWidget(self.db_service, self.user)
        elif self.page_name == "suppliers":
            from app.ui.widgets.suppliers import SuppliersWidget
            return SuppliersWidget(self.db_service, self.user)
        elif self.page_name == "orders":
            from app.ui.widgets.orders import OrdersWidget
            return OrdersWidget(self.db_service, self.user)
        elif self.page_name == "invoices":
            from app.ui.widgets.invoices import InvoicesWidget
            return InvoicesWidget(self.db_service, self.user)
        elif self.page_name == "employees":
            from app.ui.widgets.employees import EmployeesWidget
            return EmployeesWidget(self.db_service, self.user)
        elif self.page_name == "settings":
            from app.ui.widgets.settings import SettingsWidget
            return SettingsWidget(self.db_service, self.user)
        elif self.page_name == "telemetry":
            from app.ui.widgets.telemetry_dashboard import TelemetryDashboard
            return TelemetryDashboard(self.db_service, self.user)
        return None



class MainWindow(QMainWindow):
    """Main application window with lazy loading optimization"""
    
    def __init__(self, db_service, user):
        super().__init__()
        self.db_service = db_service
        self.user = user
        self.pages = {}
        self._loading_pages = set()
        self._page_loaders = []
        self.setup_ui()
        self.setup_menu()
        
        # Preload dashboard immediately, others on-demand
        QTimer.singleShot(100, self._preload_dashboard)
    
    def _preload_dashboard(self):
        """Preload dashboard widget"""
        from app.ui.widgets.dashboard import DashboardWidget
        self.pages["dashboard"] = DashboardWidget(self.db_service, self.user)
        self.stack.addWidget(self.pages["dashboard"])
        self.navigate_to("dashboard")
    
    def setup_ui(self):
        # Apply global stylesheet
        self.setStyleSheet(GLOBAL_STYLE)
        
        # Safely get company name from UserData
        company_name = self.user.company_name or 'HolzbauERP'
        self.setWindowTitle(f"HolzbauERP - {company_name}")
        self.setMinimumSize(1400, 900)
        self.showMaximized()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.navigation_clicked.connect(self.navigate_to)
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setStyleSheet(f"""
            #contentFrame {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Stacked widget for pages (lazy loaded)
        self.stack = QStackedWidget()
        
        # Modern loading placeholder
        self.loading_widget = QWidget()
        self.loading_widget.setStyleSheet(f"background: {COLORS['bg_primary']};")
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        loading_container = QFrame()
        loading_container.setFixedSize(200, 100)
        loading_container.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid {COLORS['gray_100']};
            }}
        """)
        loading_inner = QVBoxLayout(loading_container)
        
        loading_label = QLabel("⏳")
        loading_label.setFont(QFont("Segoe UI", 24))
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_inner.addWidget(loading_label)
        
        loading_text = QLabel("Lädt...")
        loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_text.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        loading_inner.addWidget(loading_text)
        
        loading_layout.addWidget(loading_container)
        self.stack.addWidget(self.loading_widget)
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame, 1)
    
    def _create_header(self) -> QFrame:
        """Create modern top header bar with search and user info"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame#header {{
                background-color: white;
                border-bottom: 1px solid {COLORS['gray_100']};
            }}
        """)
        
        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        header.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # Page title with icon
        title_container = QHBoxLayout()
        title_container.setSpacing(12)
        
        self.page_icon = QLabel("📊")
        self.page_icon.setFont(QFont("Segoe UI", 20))
        title_container.addWidget(self.page_icon)
        
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.page_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_container.addWidget(self.page_title)
        
        layout.addLayout(title_container)
        
        # Global search bar
        search_container = QFrame()
        search_container.setFixedWidth(400)
        search_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border: 1px solid {COLORS['gray_100']};
                border-radius: 8px;
            }}
            QFrame:focus-within {{
                border-color: {COLORS['primary']};
                background: white;
            }}
        """)
        
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_layout.setSpacing(8)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("Suchen... (Strg+K)")
        self.global_search.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                padding: 10px 0;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['gray_400']};
            }}
        """)
        search_layout.addWidget(self.global_search)
        
        layout.addWidget(search_container)
        layout.addStretch()
        
        # Notifications button
        notif_btn = QPushButton("🔔")
        notif_btn.setFixedSize(40, 40)
        notif_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 8px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_50']};
            }}
        """)
        layout.addWidget(notif_btn)
        
        # User info dropdown
        user_container = QFrame()
        user_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border-radius: 8px;
                padding: 4px;
            }}
            QFrame:hover {{
                background: {COLORS['gray_100']};
            }}
        """)
        user_container.setCursor(Qt.CursorShape.PointingHandCursor)
        
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(8, 6, 12, 6)
        user_layout.setSpacing(10)
        
        # User avatar
        avatar = QLabel("👤")
        avatar.setFont(QFont("Segoe UI", 16))
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {COLORS['primary']};
            border-radius: 16px;
            color: white;
        """)
        user_layout.addWidget(avatar)
        
        # User name
        user_name = f"{self.user.first_name or ''} {self.user.last_name or self.user.username}".strip()
        user_label = QLabel(user_name)
        user_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-weight: 600;
            font-size: 13px;
            background: transparent;
        """)
        user_layout.addWidget(user_label)
        
        # Dropdown arrow
        arrow = QLabel("▼")
        arrow.setStyleSheet(f"color: {COLORS['gray_400']}; font-size: 8px; background: transparent;")
        user_layout.addWidget(arrow)
        
        layout.addWidget(user_container)
        
        # Logout button
        logout_btn = QPushButton("Abmelden")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                background: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_50']};
                border-color: {COLORS['gray_300']};
                color: {COLORS['text_primary']};
            }}
        """)
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)
        
        return header
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&Datei")
        
        new_action = QAction("&Neu", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&Ansicht")
        
        for name, title in [
            ("dashboard", "Dashboard"),
            ("customers", "Kunden"),
            ("projects", "Projekte"),
            ("materials", "Material"),
            ("suppliers", "Lieferanten"),
            ("orders", "Aufträge"),
            ("invoices", "Rechnungen"),
            ("employees", "Mitarbeiter"),
        ]:
            action = QAction(title, self)
            action.triggered.connect(lambda checked, n=name: self.navigate_to(n))
            view_menu.addAction(action)
        
        # Help menu
        help_menu = menubar.addMenu("&Hilfe")
        
        about_action = QAction("Über HolzbauERP", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def navigate_to(self, page_name: str):
        """Navigate to a specific page with lazy loading"""
        page_info = {
            "dashboard": ("Dashboard", "📊"),
            "customers": ("Kundenverwaltung", "👥"),
            "projects": ("Projektverwaltung", "🏗️"),
            "construction_diary": ("Bautagebuch", "📋"),
            "materials": ("Materialverwaltung", "📦"),
            "suppliers": ("Lieferantenverwaltung", "🚚"),
            "orders": ("Aufträge & Angebote", "📋"),
            "invoices": ("Rechnungen", "💰"),
            "employees": ("Mitarbeiterverwaltung", "👷"),
            "fleet": ("Fuhrpark & Geräte", "🚗"),
            "crm": ("CRM", "🤝"),
            "quality": ("Qualitätskontrolle", "✅"),
            "accounting": ("Buchhaltung", "📒"),
            "payroll": ("Lohnverwaltung", "💼"),
            "finance": ("Finanzverwaltung", "🏦"),
            "telemetry": ("Telemetrie", "📈"),
            "settings": ("Einstellungen", "⚙️"),
            "help": ("Hilfe & Support", "❓"),
        }
        
        title, icon = page_info.get(page_name, (page_name.title(), "📄"))
        self.page_title.setText(title)
        self.page_icon.setText(icon)
        self.sidebar.set_active(page_name)
        
        if page_name in self.pages:
            # Page already loaded
            self.stack.setCurrentWidget(self.pages[page_name])
            # Refresh page data using QTimer to avoid blocking
            if hasattr(self.pages[page_name], 'refresh'):
                QTimer.singleShot(0, self.pages[page_name].refresh)
        elif page_name not in self._loading_pages:
            # Load page lazily
            self._loading_pages.add(page_name)
            self.stack.setCurrentWidget(self.loading_widget)
            self._load_page_sync(page_name)
    
    def _load_page_sync(self, page_name: str):
        """Load page synchronously (in main thread for Qt widgets)"""
        widget = None
        
        if page_name == "dashboard":
            from app.ui.widgets.dashboard import DashboardWidget
            widget = DashboardWidget(self.db_service, self.user)
        elif page_name == "customers":
            from app.ui.widgets.customers import CustomersWidget
            widget = CustomersWidget(self.db_service, self.user)
        elif page_name == "projects":
            from app.ui.widgets.projects import ProjectsWidget
            widget = ProjectsWidget(self.db_service, self.user)
        elif page_name == "construction_diary":
            from app.ui.widgets.construction_diary import ConstructionDiaryWidget
            widget = ConstructionDiaryWidget(self.db_service, self.user)
        elif page_name == "materials":
            from app.ui.widgets.materials import MaterialsWidget
            widget = MaterialsWidget(self.db_service, self.user)
        elif page_name == "suppliers":
            from app.ui.widgets.suppliers import SuppliersWidget
            widget = SuppliersWidget(self.db_service, self.user)
        elif page_name == "orders":
            from app.ui.widgets.orders import OrdersWidget
            widget = OrdersWidget(self.db_service, self.user)
        elif page_name == "invoices":
            from app.ui.widgets.invoices import InvoicesWidget
            widget = InvoicesWidget(self.db_service, self.user)
        elif page_name == "employees":
            from app.ui.widgets.employees import EmployeesWidget
            widget = EmployeesWidget(self.db_service, self.user)
        elif page_name == "fleet":
            from app.ui.widgets.fleet import FleetWidget
            widget = FleetWidget(self.db_service, self.user)
        elif page_name == "crm":
            from app.ui.widgets.crm import CRMWidget
            widget = CRMWidget(self.db_service, self.user)
        elif page_name == "quality":
            from app.ui.widgets.quality import QualityWidget
            widget = QualityWidget(self.db_service, self.user)
        elif page_name == "accounting":
            from app.ui.widgets.accounting import AccountingWidget
            widget = AccountingWidget(self.db_service, self.user)
        elif page_name == "payroll":
            from app.ui.widgets.payroll import PayrollWidget
            widget = PayrollWidget(self.db_service, self.user)
        elif page_name == "finance":
            from app.ui.widgets.finance import FinanceWidget
            widget = FinanceWidget(self.db_service, self.user)
        elif page_name == "telemetry":
            from app.ui.widgets.telemetry_dashboard import TelemetryDashboard
            widget = TelemetryDashboard(self.db_service, self.user)
        elif page_name == "settings":
            from app.ui.widgets.settings import SettingsWidget
            widget = SettingsWidget(self.db_service, self.user)
        
        if widget:
            self.pages[page_name] = widget
            self.stack.addWidget(widget)
            self.stack.setCurrentWidget(widget)
            self._loading_pages.discard(page_name)
            
            if hasattr(widget, 'refresh'):
                QTimer.singleShot(0, widget.refresh)
    
    def handle_logout(self):
        reply = QMessageBox.question(
            self, "Abmelden",
            "Möchten Sie sich wirklich abmelden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    def show_about(self):
        QMessageBox.about(
            self, "Über HolzbauERP",
            "<h2>HolzbauERP</h2>"
            "<p>Version 1.0.0</p>"
            "<p>Enterprise Resource Planning für Holzbaubetriebe</p>"
            "<p>© 2024 HolzbauERP</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close"""
        self.db_service.close_session()
        event.accept()
