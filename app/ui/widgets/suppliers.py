"""
Suppliers Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QMenu,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor
from sqlalchemy import select, or_

from shared.models import Supplier
from app.ui.dialogs.supplier_dialog import SupplierDialog
from app.ui.styles import COLORS


class SuppliersWidget(QWidget):
    """Modern supplier management page"""
    
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
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Lieferanten suchen...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background: transparent;
                padding: 10px 0;
                font-size: 14px;
                min-width: 250px;
                color: {COLORS['text_primary']};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)
        
        toolbar.addWidget(search_container)
        toolbar.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neuer Lieferant")
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
        add_btn.clicked.connect(self.add_supplier)
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
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Nr.", "Firma", "Ansprechpartner", "E-Mail", "Telefon", "Stadt", "Zahlung"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
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
        self.table.doubleClicked.connect(self.edit_supplier)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        
        self.status_label = QLabel("0 Lieferanten")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(self.status_label)
    
    def _on_search_changed(self):
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh)
        self._search_timer.start(300)
    
    def refresh(self):
        """Load suppliers from database"""
        session = self.db.get_session()
        try:
            query = select(Supplier).where(
                Supplier.is_deleted == False,
                Supplier.is_active == True
            )
            
            search = self.search_input.text().strip()
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Supplier.supplier_number.ilike(search_term),
                        Supplier.company_name.ilike(search_term),
                        Supplier.contact_person.ilike(search_term),
                        Supplier.city.ilike(search_term)
                    )
                )
            
            query = query.order_by(Supplier.company_name)
            suppliers = session.execute(query).scalars().all()
            
            self.table.setRowCount(len(suppliers))
            
            for row, supp in enumerate(suppliers):
                self.table.setItem(row, 0, QTableWidgetItem(supp.supplier_number))
                self.table.setItem(row, 1, QTableWidgetItem(supp.company_name))
                self.table.setItem(row, 2, QTableWidgetItem(supp.contact_person or ""))
                self.table.setItem(row, 3, QTableWidgetItem(supp.email or ""))
                self.table.setItem(row, 4, QTableWidgetItem(supp.phone or ""))
                self.table.setItem(row, 5, QTableWidgetItem(supp.city or ""))
                self.table.setItem(row, 6, QTableWidgetItem(f"{supp.payment_terms or 30}d"))
                
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(supp.id))
            
            self.status_label.setText(f"{len(suppliers)} Lieferanten")
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden: {e}")
        finally:
            session.close()
    
    def add_supplier(self):
        dialog = SupplierDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def edit_supplier(self):
        row = self.table.currentRow()
        if row < 0:
            return
        supplier_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = SupplierDialog(self.db, supplier_id=supplier_id, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("Bearbeiten", self)
        edit_action.triggered.connect(self.edit_supplier)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Löschen", self)
        delete_action.triggered.connect(lambda: self.delete_supplier(row))
        menu.addAction(delete_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def delete_supplier(self, row: int):
        supplier_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Lieferant löschen",
            f"Möchten Sie den Lieferanten '{name}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.db.get_session()
            try:
                import uuid
                from datetime import datetime
                
                supp = session.get(Supplier, uuid.UUID(supplier_id))
                if supp:
                    supp.is_deleted = True
                    supp.deleted_at = datetime.utcnow()
                    session.commit()
                    self.refresh()
            except Exception as e:
                session.rollback()
                QMessageBox.warning(self, "Fehler", f"Fehler: {e}")
            finally:
                session.close()
