"""
Main Application Window - Material Design 3 with Responsive Support
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QFrame, QPushButton, QLabel, QSizePolicy, QMessageBox, QSpacerItem,
    QApplication, QLineEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction, QColor, QResizeEvent

from app.ui.widgets.sidebar import Sidebar
from app.ui.material_theme import MATERIAL_COLORS, CORNER_RADIUS, get_material_stylesheet
from app.ui.responsive import ResponsiveManager, Breakpoint


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
    """Main application window with lazy loading and responsive design"""
    
    def __init__(self, db_service, user):
        super().__init__()
        self.db_service = db_service
        self.user = user
        self.pages = {}
        self._loading_pages = set()
        self._page_loaders = []
        
        # Initialize responsive manager
        self._responsive_manager = ResponsiveManager.instance()
        self._responsive_manager.breakpoint_changed.connect(self._on_breakpoint_changed)
        
        self.setup_ui()
        self.setup_menu()
        
        # Preload dashboard immediately, others on-demand
        QTimer.singleShot(100, self._preload_dashboard)
    
    def _on_breakpoint_changed(self, breakpoint: Breakpoint):
        """Handle responsive breakpoint changes"""
        # Auto-collapse sidebar on smaller screens
        if breakpoint.value < Breakpoint.LG.value:
            self.sidebar.set_collapsed(True)
        else:
            self.sidebar.set_collapsed(False)
        
        # Update header visibility
        self._update_header_for_breakpoint(breakpoint)
    
    def _update_header_for_breakpoint(self, breakpoint: Breakpoint):
        """Update header elements based on screen size"""
        is_small = breakpoint.value < Breakpoint.MD.value
        is_medium = breakpoint.value < Breakpoint.LG.value
        
        # Hide search on very small screens
        if hasattr(self, 'search_container'):
            self.search_container.setVisible(not is_small)
        
        # Compact user info on medium screens
        if hasattr(self, 'user_label'):
            self.user_label.setVisible(not is_medium)
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize"""
        super().resizeEvent(event)
        self._responsive_manager.update_size(event.size().width(), event.size().height())
    
    def _preload_dashboard(self):
        """Preload dashboard widget"""
        from app.ui.widgets.dashboard import DashboardWidget
        self.pages["dashboard"] = DashboardWidget(self.db_service, self.user)
        self.stack.addWidget(self.pages["dashboard"])
        self.navigate_to("dashboard")
    
    def setup_ui(self):
        # Apply Material stylesheet
        
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
        
        # Content area with Material Design
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setStyleSheet(f"""
            #contentFrame {{
                background-color: {MATERIAL_COLORS['background']};
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
        
        # Material Design loading placeholder
        self.loading_widget = QWidget()
        self.loading_widget.setStyleSheet(f"background: {MATERIAL_COLORS['background']};")
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        loading_container = QFrame()
        loading_container.setFixedSize(200, 100)
        loading_container.setStyleSheet(f"""
            QFrame {{
                background: {MATERIAL_COLORS['surface']};
                border-radius: {CORNER_RADIUS['medium']};
                border: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        loading_inner = QVBoxLayout(loading_container)
        
        loading_label = QLabel("⏳")
        loading_label.setFont(QFont("Segoe UI Emoji", 24))
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_inner.addWidget(loading_label)
        
        loading_text = QLabel("Lädt...")
        loading_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_text.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface_variant']}; font-size: 14px; font-family: 'Roboto';")
        loading_inner.addWidget(loading_text)
        
        loading_layout.addWidget(loading_container)
        self.stack.addWidget(self.loading_widget)
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame, 1)
    
    def _create_header(self) -> QFrame:
        """Create Material Design top header bar with responsive elements"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QFrame#header {{
                background-color: {MATERIAL_COLORS['surface']};
                border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)
        
        # Page title with Material Typography
        title_container = QHBoxLayout()
        title_container.setSpacing(10)
        
        self.page_icon = QLabel("📊")
        self.page_icon.setFont(QFont("Segoe UI Emoji", 20))
        title_container.addWidget(self.page_icon)
        
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Roboto", 20, QFont.Weight.Normal))
        self.page_title.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface']};")
        title_container.addWidget(self.page_title)
        
        layout.addLayout(title_container)
        
        # Material Design Search Bar (responsive)
        self.search_container = QFrame()
        self.search_container.setMinimumWidth(200)
        self.search_container.setMaximumWidth(400)
        self.search_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_container.setStyleSheet(f"""
            QFrame {{
                background: {MATERIAL_COLORS['surface_container_highest']};
                border: none;
                border-radius: 24px;
            }}
        """)
        
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(16, 0, 16, 0)
        search_layout.setSpacing(10)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("Suchen... (Strg+K)")
        self.global_search.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                padding: 12px 0;
                font-size: 16px;
                font-family: 'Roboto';
                color: {MATERIAL_COLORS['on_surface']};
            }}
            QLineEdit::placeholder {{
                color: {MATERIAL_COLORS['on_surface_variant']};
            }}
        """)
        search_layout.addWidget(self.global_search)
        
        layout.addWidget(self.search_container)
        layout.addStretch()
        
        # Material Icon Buttons
        notif_btn = QPushButton("🔔")
        notif_btn.setFixedSize(40, 40)
        notif_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: {MATERIAL_COLORS['surface_container_highest']};
            }}
        """)
        layout.addWidget(notif_btn)
        
        # User info with Material Design (responsive)
        user_container = QFrame()
        user_container.setStyleSheet(f"""
            QFrame {{
                background: {MATERIAL_COLORS['surface_container_low']};
                border-radius: 22px;
                padding: 2px;
            }}
            QFrame:hover {{
                background: {MATERIAL_COLORS['surface_container_highest']};
            }}
        """)
        user_container.setCursor(Qt.CursorShape.PointingHandCursor)
        
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(6, 4, 12, 4)
        user_layout.setSpacing(10)
        
        # User avatar
        avatar = QLabel("👤")
        avatar.setFont(QFont("Segoe UI Emoji", 12))
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {MATERIAL_COLORS['primary']};
            border-radius: 16px;
            color: white;
        """)
        user_layout.addWidget(avatar)
        
        # User name (hidden on small screens)
        user_name = f"{self.user.first_name or ''} {self.user.last_name or self.user.username}".strip()
        self.user_label = QLabel(user_name)
        self.user_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface']};
            font-weight: 500;
            font-size: 13px;
            font-family: 'Roboto';
            background: transparent;
        """)
        user_layout.addWidget(self.user_label)
        
        # Dropdown arrow
        arrow = QLabel("▼")
        arrow.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface_variant']}; font-size: 8px; background: transparent;")
        user_layout.addWidget(arrow)
        
        layout.addWidget(user_container)
        
        # Logout button with Material Design
        logout_btn = QPushButton("Abmelden")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: transparent;
                color: {MATERIAL_COLORS['on_surface_variant']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 20px;
                font-weight: 500;
                font-size: 14px;
                font-family: 'Roboto';
            }}
            QPushButton:hover {{
                background: {MATERIAL_COLORS['surface_container_highest']};
                border-color: {MATERIAL_COLORS['outline']};
                color: {MATERIAL_COLORS['on_surface']};
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
