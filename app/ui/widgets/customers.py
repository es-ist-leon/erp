"""
Customers Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QFrame, QLabel, QHeaderView,
    QMessageBox, QMenu, QSpinBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction, QColor
from sqlalchemy import select, or_, func

from shared.models import Customer, CustomerType, CustomerStatus
from app.ui.styles import COLORS, get_button_style, get_table_style


class CustomersWidget(QWidget):
    """Modern customer management page with pagination"""
    
    PAGE_SIZE = 50
    
    def __init__(self, db_service, user=None):
        super().__init__()
        self.db = db_service
        self.user = user
        self.current_page = 0
        self.total_pages = 0
        self.total_count = 0
        self._search_timer = None
        self.setStyleSheet(f"background: {COLORS['bg_primary']};")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Toolbar card
        toolbar_card = QFrame()
        toolbar_card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 15))
        toolbar_card.setGraphicsEffect(shadow)
        
        toolbar = QHBoxLayout(toolbar_card)
        toolbar.setContentsMargins(16, 12, 16, 12)
        toolbar.setSpacing(12)
        
        # Search with icon
        search_container = QFrame()
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
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kunden suchen...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                padding: 10px 0;
                font-size: 14px;
                min-width: 250px;
                color: {COLORS['text_primary']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['gray_400']};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        
        toolbar.addWidget(search_container)
        
        # Filter by type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Alle Typen", None)
        self.type_filter.addItem("Privatkunden", "private")
        self.type_filter.addItem("Geschäftskunden", "business")
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                min-width: 150px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['gray_300']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
        """)
        self.type_filter.currentIndexChanged.connect(self._reset_and_refresh)
        toolbar.addWidget(self.type_filter)
        
        toolbar.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neuer Kunde")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
            }}
        """)
        add_btn.clicked.connect(self.add_customer)
        toolbar.addWidget(add_btn)
        
        layout.addWidget(toolbar_card)
        
        # Table card
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
            }}
        """)
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(10)
        shadow2.setXOffset(0)
        shadow2.setYOffset(2)
        shadow2.setColor(QColor(0, 0, 0, 15))
        table_card.setGraphicsEffect(shadow2)
        
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Kundennr.", "Typ", "Name/Firma", "E-Mail", "Telefon", "Stadt", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: none;
                border-radius: 12px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 14px 16px;
                border-bottom: 1px solid {COLORS['gray_50']};
            }}
            QTableWidget::item:selected {{
                background: {COLORS['primary']}10;
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
                letter-spacing: 0.5px;
            }}
        """)
        self.table.doubleClicked.connect(self.edit_customer)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        
        # Pagination bar
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border-top: 1px solid {COLORS['gray_100']};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)
        
        pagination = QHBoxLayout(pagination_frame)
        pagination.setContentsMargins(16, 12, 16, 12)
        
        self.status_label = QLabel("0 Kunden")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        pagination.addWidget(self.status_label)
        
        pagination.addStretch()
        
        # Page navigation
        self.prev_btn = QPushButton("← Zurück")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                background: white;
                color: {COLORS['text_secondary']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_100']};
                border-color: {COLORS['gray_300']};
            }}
            QPushButton:disabled {{
                color: {COLORS['gray_300']};
                background: {COLORS['gray_50']};
            }}
        """)
        self.prev_btn.clicked.connect(self._prev_page)
        pagination.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Seite 1 von 1")
        self.page_label.setStyleSheet(f"margin: 0 16px; color: {COLORS['text_secondary']}; font-weight: 500;")
        pagination.addWidget(self.page_label)
        
        self.next_btn = QPushButton("Weiter →")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                background: white;
                color: {COLORS['text_secondary']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_100']};
                border-color: {COLORS['gray_300']};
            }}
            QPushButton:disabled {{
                color: {COLORS['gray_300']};
                background: {COLORS['gray_50']};
            }}
        """)
        self.next_btn.clicked.connect(self._next_page)
        pagination.addWidget(self.next_btn)
        
        table_layout.addWidget(pagination_frame)
        
        layout.addWidget(table_card)
    
    def _on_search_changed(self):
        """Debounced search - wait 300ms after typing stops"""
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._reset_and_refresh)
        self._search_timer.start(300)
    
    def _reset_and_refresh(self):
        """Reset to first page and refresh"""
        self.current_page = 0
        self.refresh()
    
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh()
    
    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.refresh()
    
    def refresh(self):
        """Load customers from database with pagination and optimized rendering"""
        session = self.db.get_session()
        try:
            # Disable updates during data load for better performance
            self.table.setUpdatesEnabled(False)
            
            # Build base query with only needed columns
            base_query = select(Customer).where(Customer.is_deleted == False)
            
            # Apply tenant filter
            if self.user and self.user.tenant_id:
                base_query = base_query.where(Customer.tenant_id == self.user.tenant_id)
            
            # Apply search filter
            search = self.search_input.text().strip()
            if search:
                search_term = f"%{search}%"
                base_query = base_query.where(
                    or_(
                        Customer.customer_number.ilike(search_term),
                        Customer.company_name.ilike(search_term),
                        Customer.first_name.ilike(search_term),
                        Customer.last_name.ilike(search_term),
                        Customer.email.ilike(search_term),
                        Customer.city.ilike(search_term)
                    )
                )
            
            # Apply type filter
            type_filter = self.type_filter.currentData()
            if type_filter:
                base_query = base_query.where(Customer.customer_type == CustomerType(type_filter))
            
            # Get total count
            count_query = select(func.count()).select_from(base_query.subquery())
            self.total_count = session.execute(count_query).scalar() or 0
            self.total_pages = max(1, (self.total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            
            # Ensure current page is valid
            if self.current_page >= self.total_pages:
                self.current_page = max(0, self.total_pages - 1)
            
            # Apply pagination and ordering
            query = base_query.order_by(Customer.created_at.desc())
            query = query.offset(self.current_page * self.PAGE_SIZE).limit(self.PAGE_SIZE)
            
            customers = session.execute(query).scalars().all()
            
            # Update table efficiently
            self.table.setRowCount(len(customers))
            
            for row, customer in enumerate(customers):
                self._set_row_data(row, customer)
            
            # Update pagination controls
            self._update_pagination()
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden: {e}")
        finally:
            # Re-enable updates
            self.table.setUpdatesEnabled(True)
            session.close()
    
    def _set_row_data(self, row: int, customer):
        """Set data for a single row with modern styling"""
        # Customer number
        item = QTableWidgetItem(customer.customer_number)
        item.setData(Qt.ItemDataRole.UserRole, str(customer.id))
        item.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.table.setItem(row, 0, item)
        
        # Type with badge style
        type_text = "Privat" if customer.customer_type == CustomerType.PRIVATE else "Geschäft"
        type_item = QTableWidgetItem(type_text)
        type_item.setForeground(QColor(COLORS['text_secondary']))
        self.table.setItem(row, 1, type_item)
        
        # Name
        if customer.company_name:
            name = customer.company_name
        else:
            name = f"{customer.first_name or ''} {customer.last_name or ''}".strip()
        name_item = QTableWidgetItem(name)
        name_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.table.setItem(row, 2, name_item)
        
        # Email, Phone, City
        self.table.setItem(row, 3, QTableWidgetItem(customer.email or ""))
        self.table.setItem(row, 4, QTableWidgetItem(customer.phone or customer.mobile or ""))
        self.table.setItem(row, 5, QTableWidgetItem(customer.city or ""))
        
        # Status with modern colors
        status_map = {
            CustomerStatus.ACTIVE: ("✓ Aktiv", COLORS['success']),
            CustomerStatus.INACTIVE: ("○ Inaktiv", COLORS['gray_400']),
            CustomerStatus.PROSPECT: ("◐ Interessent", COLORS['info']),
            CustomerStatus.BLOCKED: ("✕ Gesperrt", COLORS['error'])
        }
        status_text, color = status_map.get(customer.status, ("", COLORS['text_primary']))
        item = QTableWidgetItem(status_text)
        item.setForeground(QColor(color))
        item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.table.setItem(row, 6, item)
    
    def _update_pagination(self):
        """Update pagination controls"""
        self.status_label.setText(f"{self.total_count} Kunden")
        self.page_label.setText(f"Seite {self.current_page + 1} von {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
    
    def filter_customers(self):
        """Filter table based on search and filters"""
        self._reset_and_refresh()
    
    def add_customer(self):
        """Open dialog to add new customer"""
        from app.ui.dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.db.invalidate_cache("customer")
            self.refresh()
    
    def edit_customer(self):
        """Edit selected customer"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        customer_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        from app.ui.dialogs.customer_dialog import CustomerDialog
        dialog = CustomerDialog(self.db, customer_id=customer_id, user=self.user, parent=self)
        if dialog.exec():
            self.db.invalidate_cache("customer")
            self.refresh()
    
    def show_context_menu(self, position):
        """Show context menu for table"""
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("Bearbeiten", self)
        edit_action.triggered.connect(self.edit_customer)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Löschen", self)
        delete_action.triggered.connect(lambda: self.delete_customer(row))
        menu.addAction(delete_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def delete_customer(self, row: int):
        """Delete customer (soft delete)"""
        customer_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 2).text()
        
        reply = QMessageBox.question(
            self, "Kunde löschen",
            f"Möchten Sie den Kunden '{name}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.db.get_session()
            try:
                from datetime import datetime
                import uuid
                
                customer = session.get(Customer, uuid.UUID(customer_id))
                if customer:
                    customer.is_deleted = True
                    customer.deleted_at = datetime.utcnow()
                    session.commit()
                    self.db.invalidate_cache("customer")
                    self.refresh()
                    QMessageBox.information(self, "Erfolg", "Kunde wurde gelöscht.")
            except Exception as e:
                session.rollback()
                QMessageBox.warning(self, "Fehler", f"Fehler beim Löschen: {e}")
            finally:
                session.close()
