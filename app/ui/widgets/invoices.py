"""
Invoices Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox, 
    QMenu, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from shared.models import Invoice, InvoiceStatus, InvoiceType
from app.ui.styles import COLORS


class InvoicesWidget(QWidget):
    """Modern invoice management page"""
    
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
        self.search_input.setPlaceholderText("Rechnungen suchen...")
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
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("Alle Status", None)
        self.status_filter.addItem("Entwurf", "draft")
        self.status_filter.addItem("Gesendet", "sent")
        self.status_filter.addItem("Teilbezahlt", "partial_paid")
        self.status_filter.addItem("Bezahlt", "paid")
        self.status_filter.addItem("Überfällig", "overdue")
        self.status_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                min-width: 120px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['gray_300']};
            }}
        """)
        self.status_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.status_filter)
        
        toolbar.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neue Rechnung")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['error']}, stop:1 #8e2622);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['error_light']}, stop:1 {COLORS['error']});
            }}
        """)
        add_btn.clicked.connect(self.add_invoice)
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
            "Rechnungs-Nr.", "Kunde", "Betreff", "Betrag", "Offen", "Status", "Fällig am"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
                background: {COLORS['error']}10;
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
        self.table.doubleClicked.connect(self.edit_invoice)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        self.status_label = QLabel("0 Rechnungen")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        summary_layout.addWidget(self.status_label)
        
        summary_layout.addStretch()
        
        self.total_label = QLabel("Gesamt offen: 0,00 €")
        self.total_label.setStyleSheet(f"font-weight: bold; color: {COLORS['error']}; font-size: 14px;")
        summary_layout.addWidget(self.total_label)
        
        layout.addLayout(summary_layout)
    
    def _on_search_changed(self):
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh)
        self._search_timer.start(300)
    
    def refresh(self):
        session = self.db.get_session()
        try:
            query = select(Invoice).options(
                selectinload(Invoice.customer)
            ).where(Invoice.is_deleted == False)
            
            status = self.status_filter.currentData()
            if status:
                query = query.where(Invoice.status == InvoiceStatus(status))
            
            query = query.order_by(Invoice.created_at.desc())
            invoices = session.execute(query).scalars().all()
            
            self.table.setRowCount(len(invoices))
            
            status_names = {
                InvoiceStatus.DRAFT: "Entwurf",
                InvoiceStatus.SENT: "Gesendet",
                InvoiceStatus.PARTIAL_PAID: "Teilbezahlt",
                InvoiceStatus.PAID: "Bezahlt",
                InvoiceStatus.OVERDUE: "Überfällig",
                InvoiceStatus.CANCELLED: "Storniert",
            }
            
            total_open = 0.0
            
            for row, inv in enumerate(invoices):
                self.table.setItem(row, 0, QTableWidgetItem(inv.invoice_number))
                
                customer_name = ""
                if inv.customer:
                    customer_name = inv.customer.company_name or \
                                  f"{inv.customer.first_name or ''} {inv.customer.last_name or ''}".strip()
                self.table.setItem(row, 1, QTableWidgetItem(customer_name))
                self.table.setItem(row, 2, QTableWidgetItem(inv.subject or ""))
                
                total = float(inv.total or 0)
                total_str = f"{total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.table.setItem(row, 3, QTableWidgetItem(total_str))
                
                remaining = float(inv.remaining_amount or 0)
                remaining_str = f"{remaining:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                remaining_item = QTableWidgetItem(remaining_str)
                if remaining > 0:
                    remaining_item.setForeground(Qt.GlobalColor.red)
                    total_open += remaining
                self.table.setItem(row, 4, remaining_item)
                
                status_item = QTableWidgetItem(status_names.get(inv.status, ""))
                if inv.status == InvoiceStatus.PAID:
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif inv.status == InvoiceStatus.OVERDUE:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 5, status_item)
                
                due = inv.due_date.strftime("%d.%m.%Y") if inv.due_date else ""
                self.table.setItem(row, 6, QTableWidgetItem(due))
                
                # Store invoice ID
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(inv.id))
            
            self.status_label.setText(f"{len(invoices)} Rechnungen")
            total_open_str = f"{total_open:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
            self.total_label.setText(f"Gesamt offen: {total_open_str}")
            
        except Exception as e:
            print(f"Error loading invoices: {e}")
        finally:
            session.close()
    
    def add_invoice(self):
        from app.ui.dialogs.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def edit_invoice(self):
        """Edit selected invoice"""
        row = self.table.currentRow()
        if row < 0:
            return
        invoice_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        from app.ui.dialogs.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog(self.db, invoice_id=invoice_id, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def show_context_menu(self, position):
        """Show context menu for invoice actions"""
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        invoice_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        edit_action = QAction("Bearbeiten", self)
        edit_action.triggered.connect(self.edit_invoice)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        payment_action = QAction("💰 Zahlung erfassen", self)
        payment_action.triggered.connect(lambda: self.record_payment(invoice_id))
        menu.addAction(payment_action)
        
        menu.addSeparator()
        
        mark_sent_action = QAction("Als versendet markieren", self)
        mark_sent_action.triggered.connect(lambda: self.mark_as_sent(invoice_id))
        menu.addAction(mark_sent_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def record_payment(self, invoice_id):
        """Open payment dialog"""
        from app.ui.dialogs.payment_dialog import PaymentDialog
        dialog = PaymentDialog(self.db, invoice_id=invoice_id, parent=self)
        if dialog.exec():
            self.refresh()
    
    def mark_as_sent(self, invoice_id):
        """Mark invoice as sent"""
        import uuid
        from datetime import datetime
        
        session = self.db.get_session()
        try:
            invoice = session.get(Invoice, uuid.UUID(invoice_id))
            if invoice and invoice.status == InvoiceStatus.DRAFT:
                invoice.status = InvoiceStatus.SENT
                invoice.sent_at = datetime.utcnow()
                session.commit()
                self.refresh()
                QMessageBox.information(self, "Erfolg", "Rechnung wurde als versendet markiert.")
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler: {e}")
        finally:
            session.close()
