"""
Orders Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox,
    QTabWidget, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from shared.models import Quote, Order, QuoteStatus, OrderStatus
from app.ui.styles import COLORS


class OrdersWidget(QWidget):
    """Modern Orders and Quotes management page"""
    
    def __init__(self, db_service, user=None):
        super().__init__()
        self.db = db_service
        self.user = user
        self._search_timer = None
        self.setStyleSheet(f"background: {COLORS['bg_primary']};")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Tabs for Quotes and Orders
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
                background: white;
                margin-top: -1px;
            }}
            QTabBar::tab {{
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                background: {COLORS['gray_100']};
                color: {COLORS['text_secondary']};
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: white;
                color: {COLORS['primary']};
                border: 1px solid {COLORS['gray_100']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {COLORS['gray_50']};
            }}
        """)
        
        # ===== QUOTES TAB =====
        quotes_widget = QWidget()
        quotes_widget.setStyleSheet("background: white;")
        quotes_layout = QVBoxLayout(quotes_widget)
        quotes_layout.setContentsMargins(16, 16, 16, 16)
        quotes_layout.setSpacing(12)
        
        # Quotes toolbar
        quotes_toolbar = QHBoxLayout()
        
        # Search
        search_container = QFrame()
        search_container.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border: 1px solid {COLORS['gray_100']};
                border-radius: 8px;
            }}
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_layout.setSpacing(8)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("background: transparent;")
        search_layout.addWidget(search_icon)
        
        self.quotes_search = QLineEdit()
        self.quotes_search.setPlaceholderText("Angebote suchen...")
        self.quotes_search.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                padding: 10px 0;
                font-size: 14px;
                min-width: 200px;
                color: {COLORS['text_primary']};
            }}
        """)
        self.quotes_search.textChanged.connect(self._on_quotes_search)
        search_layout.addWidget(self.quotes_search)
        
        quotes_toolbar.addWidget(search_container)
        quotes_toolbar.addStretch()
        
        new_quote_btn = QPushButton("+ Neues Angebot")
        new_quote_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_quote_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['warning']}, stop:1 #a16207);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['warning_light']}, stop:1 {COLORS['warning']});
            }}
        """)
        new_quote_btn.clicked.connect(self.add_quote)
        quotes_toolbar.addWidget(new_quote_btn)
        quotes_layout.addLayout(quotes_toolbar)
        
        # Quotes table
        self.quotes_table = QTableWidget()
        self.quotes_table.setColumnCount(6)
        self.quotes_table.setHorizontalHeaderLabels([
            "Angebots-Nr.", "Kunde", "Betreff", "Betrag", "Status", "Gültig bis"
        ])
        self.quotes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.quotes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.quotes_table.setAlternatingRowColors(False)
        self.quotes_table.verticalHeader().setVisible(False)
        self.quotes_table.setShowGrid(False)
        self.quotes_table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: none;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 14px 16px;
                border-bottom: 1px solid {COLORS['gray_50']};
            }}
            QTableWidget::item:selected {{
                background: {COLORS['warning']}10;
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:hover {{
                background: {COLORS['gray_50']};
            }}
            QHeaderView::section {{
                background: {COLORS['gray_50']};
                padding: 14px 16px;
                border: none;
                border-bottom: 2px solid {COLORS['gray_100']};
                font-weight: 700;
                font-size: 11px;
                color: {COLORS['text_secondary']};
                text-transform: uppercase;
            }}
        """)
        quotes_layout.addWidget(self.quotes_table)
        
        self.tabs.addTab(quotes_widget, "📋 Angebote")
        
        # ===== ORDERS TAB =====
        orders_widget = QWidget()
        orders_widget.setStyleSheet("background: white;")
        orders_layout = QVBoxLayout(orders_widget)
        orders_layout.setContentsMargins(16, 16, 16, 16)
        orders_layout.setSpacing(12)
        
        # Orders toolbar
        orders_toolbar = QHBoxLayout()
        
        # Search
        search_container2 = QFrame()
        search_container2.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border: 1px solid {COLORS['gray_100']};
                border-radius: 8px;
            }}
        """)
        search_layout2 = QHBoxLayout(search_container2)
        search_layout2.setContentsMargins(12, 0, 12, 0)
        search_layout2.setSpacing(8)
        
        search_icon2 = QLabel("🔍")
        search_icon2.setStyleSheet("background: transparent;")
        search_layout2.addWidget(search_icon2)
        
        self.orders_search = QLineEdit()
        self.orders_search.setPlaceholderText("Aufträge suchen...")
        self.orders_search.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                padding: 10px 0;
                font-size: 14px;
                min-width: 200px;
                color: {COLORS['text_primary']};
            }}
        """)
        self.orders_search.textChanged.connect(self._on_orders_search)
        search_layout2.addWidget(self.orders_search)
        
        orders_toolbar.addWidget(search_container2)
        orders_toolbar.addStretch()
        
        new_order_btn = QPushButton("+ Neuer Auftrag")
        new_order_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_order_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['success']}, stop:1 #1c5a2f);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['success_light']}, stop:1 {COLORS['success']});
            }}
        """)
        new_order_btn.clicked.connect(self.add_order)
        orders_toolbar.addWidget(new_order_btn)
        orders_layout.addLayout(orders_toolbar)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels([
            "Auftrags-Nr.", "Kunde", "Betreff", "Betrag", "Status", "Auftragsdatum"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setAlternatingRowColors(False)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setShowGrid(False)
        self.orders_table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: none;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 14px 16px;
                border-bottom: 1px solid {COLORS['gray_50']};
            }}
            QTableWidget::item:selected {{
                background: {COLORS['success']}10;
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:hover {{
                background: {COLORS['gray_50']};
            }}
            QHeaderView::section {{
                background: {COLORS['gray_50']};
                padding: 14px 16px;
                border: none;
                border-bottom: 2px solid {COLORS['gray_100']};
                font-weight: 700;
                font-size: 11px;
                color: {COLORS['text_secondary']};
                text-transform: uppercase;
            }}
        """)
        orders_layout.addWidget(self.orders_table)
        
        self.tabs.addTab(orders_widget, "📦 Aufträge")
        
        layout.addWidget(self.tabs)
    
    def _on_quotes_search(self):
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh_quotes)
        self._search_timer.start(300)
    
    def _on_orders_search(self):
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh_orders)
        self._search_timer.start(300)
    
    def refresh(self):
        self.refresh_quotes()
        self.refresh_orders()
    
    def refresh_quotes(self):
        session = self.db.get_session()
        try:
            # Disable updates during data load for better performance
            self.quotes_table.setUpdatesEnabled(False)
            
            query = select(Quote).options(
                selectinload(Quote.customer)
            ).where(Quote.is_deleted == False).order_by(Quote.created_at.desc())
            
            quotes = session.execute(query).scalars().all()
            self.quotes_table.setRowCount(len(quotes))
            
            status_names = {
                QuoteStatus.DRAFT: "Entwurf",
                QuoteStatus.SENT: "Gesendet",
                QuoteStatus.ACCEPTED: "Angenommen",
                QuoteStatus.REJECTED: "Abgelehnt",
            }
            
            for row, quote in enumerate(quotes):
                self.quotes_table.setItem(row, 0, QTableWidgetItem(quote.quote_number))
                
                customer_name = ""
                if quote.customer:
                    customer_name = quote.customer.company_name or \
                                  f"{quote.customer.first_name or ''} {quote.customer.last_name or ''}".strip()
                self.quotes_table.setItem(row, 1, QTableWidgetItem(customer_name))
                self.quotes_table.setItem(row, 2, QTableWidgetItem(quote.subject or ""))
                
                total = ""
                if quote.total:
                    total = f"{float(quote.total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.quotes_table.setItem(row, 3, QTableWidgetItem(total))
                
                self.quotes_table.setItem(row, 4, QTableWidgetItem(status_names.get(quote.status, "")))
                
                valid = quote.valid_until.strftime("%d.%m.%Y") if quote.valid_until else ""
                self.quotes_table.setItem(row, 5, QTableWidgetItem(valid))
                
        except Exception as e:
            print(f"Error loading quotes: {e}")
        finally:
            # Re-enable updates
            self.quotes_table.setUpdatesEnabled(True)
            session.close()
    
    def refresh_orders(self):
        session = self.db.get_session()
        try:
            # Disable updates during data load for better performance
            self.orders_table.setUpdatesEnabled(False)
            
            query = select(Order).options(
                selectinload(Order.customer)
            ).where(Order.is_deleted == False).order_by(Order.created_at.desc())
            
            orders = session.execute(query).scalars().all()
            self.orders_table.setRowCount(len(orders))
            
            status_names = {
                OrderStatus.DRAFT: "Entwurf",
                OrderStatus.CONFIRMED: "Bestätigt",
                OrderStatus.IN_PROGRESS: "In Bearbeitung",
                OrderStatus.COMPLETED: "Abgeschlossen",
            }
            
            for row, order in enumerate(orders):
                self.orders_table.setItem(row, 0, QTableWidgetItem(order.order_number))
                
                customer_name = ""
                if order.customer:
                    customer_name = order.customer.company_name or \
                                  f"{order.customer.first_name or ''} {order.customer.last_name or ''}".strip()
                self.orders_table.setItem(row, 1, QTableWidgetItem(customer_name))
                self.orders_table.setItem(row, 2, QTableWidgetItem(order.subject or ""))
                
                total = ""
                if order.total:
                    total = f"{float(order.total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.orders_table.setItem(row, 3, QTableWidgetItem(total))
                
                self.orders_table.setItem(row, 4, QTableWidgetItem(status_names.get(order.status, "")))
                
                order_date = order.order_date.strftime("%d.%m.%Y") if order.order_date else ""
                self.orders_table.setItem(row, 5, QTableWidgetItem(order_date))
                
        except Exception as e:
            print(f"Error loading orders: {e}")
        finally:
            # Re-enable updates
            self.orders_table.setUpdatesEnabled(True)
            session.close()
    
    def add_quote(self):
        from app.ui.dialogs.quote_dialog import QuoteDialog
        dialog = QuoteDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.refresh_quotes()
    
    def add_order(self):
        from app.ui.dialogs.order_dialog import OrderDialog
        dialog = OrderDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.refresh_orders()
