"""
Order Dialog - Auftragserstellung
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QDateEdit, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import uuid
from datetime import datetime, date
from decimal import Decimal

from shared.models import Order, OrderItem, OrderStatus, Customer, Project, Quote
from sqlalchemy import select, func


class OrderDialog(QDialog):
    """Dialog for creating/editing orders"""
    
    def __init__(self, db_service, order_id=None, quote_id=None, customer_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.order_id = order_id
        self.initial_quote_id = quote_id
        self.initial_customer_id = customer_id
        self.user = user
        self.order = None
        self.setup_ui()
        self.load_data()
        if order_id:
            self.load_order()
        elif quote_id:
            self.load_from_quote(quote_id)
    
    def setup_ui(self):
        self.setWindowTitle("Neuer Auftrag" if not self.order_id else "Auftrag bearbeiten")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # === Basic Info Tab ===
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Header info
        header_group = QGroupBox("Auftragsinformationen")
        header_form = QFormLayout(header_group)
        
        self.customer_combo = QComboBox()
        header_form.addRow("Kunde*:", self.customer_combo)
        
        self.project_combo = QComboBox()
        header_form.addRow("Projekt:", self.project_combo)
        
        self.quote_combo = QComboBox()
        self.quote_combo.currentIndexChanged.connect(self.on_quote_selected)
        header_form.addRow("Angebot:", self.quote_combo)
        
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("z.B. Dachstuhl Einfamilienhaus")
        header_form.addRow("Betreff*:", self.subject)
        
        self.customer_order_number = QLineEdit()
        self.customer_order_number.setPlaceholderText("Kunden-Auftragsnummer (optional)")
        header_form.addRow("Kunden-Auftr.-Nr.:", self.customer_order_number)
        
        self.status = QComboBox()
        self.status.addItem("Entwurf", "draft")
        self.status.addItem("Bestätigt", "confirmed")
        self.status.addItem("In Bearbeitung", "in_progress")
        self.status.addItem("Teilgeliefert", "partial_delivered")
        self.status.addItem("Geliefert", "delivered")
        self.status.addItem("Abgeschlossen", "completed")
        header_form.addRow("Status:", self.status)
        
        dates_layout = QHBoxLayout()
        self.order_date = QDateEdit()
        self.order_date.setCalendarPopup(True)
        self.order_date.setDate(QDate.currentDate())
        dates_layout.addWidget(QLabel("Auftragsdatum:"))
        dates_layout.addWidget(self.order_date)
        dates_layout.addSpacing(20)
        
        self.planned_start = QDateEdit()
        self.planned_start.setCalendarPopup(True)
        self.planned_start.setDate(QDate.currentDate().addDays(14))
        dates_layout.addWidget(QLabel("Geplanter Start:"))
        dates_layout.addWidget(self.planned_start)
        dates_layout.addSpacing(20)
        
        self.planned_end = QDateEdit()
        self.planned_end.setCalendarPopup(True)
        self.planned_end.setDate(QDate.currentDate().addMonths(2))
        dates_layout.addWidget(QLabel("Geplantes Ende:"))
        dates_layout.addWidget(self.planned_end)
        dates_layout.addStretch()
        header_form.addRow("", dates_layout)
        
        basic_layout.addWidget(header_group)
        
        # Delivery Address
        delivery_group = QGroupBox("Lieferadresse")
        delivery_form = QFormLayout(delivery_group)
        
        self.delivery_street = QLineEdit()
        delivery_form.addRow("Straße:", self.delivery_street)
        
        addr_layout = QHBoxLayout()
        self.delivery_postal = QLineEdit()
        self.delivery_postal.setMaximumWidth(100)
        addr_layout.addWidget(self.delivery_postal)
        self.delivery_city = QLineEdit()
        addr_layout.addWidget(self.delivery_city)
        delivery_form.addRow("PLZ / Stadt:", addr_layout)
        
        basic_layout.addWidget(delivery_group)
        basic_layout.addStretch()
        tabs.addTab(basic_tab, "Grunddaten")
        
        # === Items Tab ===
        items_tab = QWidget()
        items_layout = QVBoxLayout(items_tab)
        
        # Toolbar
        items_toolbar = QHBoxLayout()
        
        add_item_btn = QPushButton("+ Position hinzufügen")
        add_item_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #15803d; }
        """)
        add_item_btn.clicked.connect(self.add_item)
        items_toolbar.addWidget(add_item_btn)
        
        items_toolbar.addStretch()
        
        remove_btn = QPushButton("Position entfernen")
        remove_btn.clicked.connect(self.remove_item)
        items_toolbar.addWidget(remove_btn)
        
        items_layout.addLayout(items_toolbar)
        
        # Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "Pos", "Bezeichnung", "Menge", "Einheit", "Einzelpreis", "MwSt %", "Gesamt"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.cellChanged.connect(self.calculate_totals)
        items_layout.addWidget(self.items_table)
        
        # Totals
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        totals_group = QGroupBox("Summen")
        totals_form = QFormLayout(totals_group)
        
        self.subtotal_label = QLabel("0,00 €")
        self.subtotal_label.setFont(QFont("Segoe UI", 11))
        totals_form.addRow("Zwischensumme (netto):", self.subtotal_label)
        
        discount_layout = QHBoxLayout()
        self.discount_percent = QDoubleSpinBox()
        self.discount_percent.setRange(0, 100)
        self.discount_percent.setSuffix(" %")
        self.discount_percent.valueChanged.connect(self.calculate_totals)
        discount_layout.addWidget(self.discount_percent)
        self.discount_label = QLabel("- 0,00 €")
        discount_layout.addWidget(self.discount_label)
        totals_form.addRow("Rabatt:", discount_layout)
        
        self.tax_label = QLabel("0,00 €")
        totals_form.addRow("MwSt.:", self.tax_label)
        
        self.total_label = QLabel("0,00 €")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #16a34a;")
        totals_form.addRow("Gesamtbetrag (brutto):", self.total_label)
        
        totals_layout.addWidget(totals_group)
        items_layout.addLayout(totals_layout)
        
        tabs.addTab(items_tab, "Positionen")
        
        # === Notes Tab ===
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        
        terms_group = QGroupBox("Zahlungs- und Lieferbedingungen")
        terms_form = QVBoxLayout(terms_group)
        self.payment_terms = QTextEdit()
        self.payment_terms.setMaximumHeight(80)
        self.payment_terms.setPlaceholderText("Zahlungsbedingungen...")
        terms_form.addWidget(QLabel("Zahlungsbedingungen:"))
        terms_form.addWidget(self.payment_terms)
        self.delivery_terms = QTextEdit()
        self.delivery_terms.setMaximumHeight(80)
        self.delivery_terms.setPlaceholderText("Lieferbedingungen...")
        terms_form.addWidget(QLabel("Lieferbedingungen:"))
        terms_form.addWidget(self.delivery_terms)
        notes_layout.addWidget(terms_group)
        
        notes_group = QGroupBox("Notizen")
        notes_form = QVBoxLayout(notes_group)
        self.notes = QTextEdit()
        notes_form.addWidget(self.notes)
        notes_layout.addWidget(notes_group)
        
        tabs.addTab(notes_tab, "Notizen")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #15803d; }
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Load customers, projects, and quotes"""
        session = self.db.get_session()
        try:
            # Load customers
            customers = session.execute(
                select(Customer).where(Customer.is_deleted == False).order_by(Customer.company_name, Customer.last_name)
            ).scalars().all()
            
            self.customer_combo.addItem("-- Kunde wählen --", None)
            for cust in customers:
                name = cust.company_name or f"{cust.first_name or ''} {cust.last_name or ''}".strip()
                self.customer_combo.addItem(f"{cust.customer_number} - {name}", str(cust.id))
                if self.initial_customer_id and str(cust.id) == self.initial_customer_id:
                    self.customer_combo.setCurrentIndex(self.customer_combo.count() - 1)
            
            # Load projects
            projects = session.execute(
                select(Project).where(Project.is_deleted == False).order_by(Project.created_at.desc())
            ).scalars().all()
            
            self.project_combo.addItem("-- Kein Projekt --", None)
            for proj in projects:
                self.project_combo.addItem(f"{proj.project_number} - {proj.name}", str(proj.id))
            
            # Load accepted quotes
            quotes = session.execute(
                select(Quote).where(
                    Quote.is_deleted == False
                ).order_by(Quote.created_at.desc())
            ).scalars().all()
            
            self.quote_combo.addItem("-- Kein Angebot --", None)
            for quote in quotes:
                status = "✓" if quote.status.value == "accepted" else ""
                self.quote_combo.addItem(f"{status} {quote.quote_number} - {quote.subject or 'Ohne Betreff'}", str(quote.id))
                if self.initial_quote_id and str(quote.id) == self.initial_quote_id:
                    self.quote_combo.setCurrentIndex(self.quote_combo.count() - 1)
                    
        finally:
            session.close()
    
    def on_quote_selected(self):
        """Handle quote selection"""
        quote_id = self.quote_combo.currentData()
        if quote_id and not self.order_id:
            reply = QMessageBox.question(
                self, "Daten übernehmen",
                "Möchten Sie die Daten aus dem Angebot übernehmen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.load_from_quote(quote_id)
    
    def load_from_quote(self, quote_id):
        """Load data from quote"""
        session = self.db.get_session()
        try:
            quote = session.get(Quote, uuid.UUID(quote_id))
            if not quote:
                return
            
            # Set customer
            if quote.customer_id:
                idx = self.customer_combo.findData(str(quote.customer_id))
                if idx >= 0:
                    self.customer_combo.setCurrentIndex(idx)
            
            # Set project
            if quote.project_id:
                idx = self.project_combo.findData(str(quote.project_id))
                if idx >= 0:
                    self.project_combo.setCurrentIndex(idx)
            
            self.subject.setText(quote.subject or "")
            self.payment_terms.setPlainText(quote.payment_terms or "")
            self.delivery_terms.setPlainText(quote.delivery_terms or "")
            
            if quote.discount_percent:
                self.discount_percent.setValue(float(quote.discount_percent))
            
            # Clear and load items
            self.items_table.setRowCount(0)
            for item in sorted(quote.items, key=lambda x: x.position):
                self.add_item_row(item.title, item.quantity, item.unit, item.unit_price, item.tax_rate)
            
            self.calculate_totals()
            
        finally:
            session.close()
    
    def load_order(self):
        """Load existing order for editing"""
        session = self.db.get_session()
        try:
            self.order = session.get(Order, uuid.UUID(self.order_id))
            if not self.order:
                return
            
            # Set customer
            if self.order.customer_id:
                idx = self.customer_combo.findData(str(self.order.customer_id))
                if idx >= 0:
                    self.customer_combo.setCurrentIndex(idx)
            
            # Set project
            if self.order.project_id:
                idx = self.project_combo.findData(str(self.order.project_id))
                if idx >= 0:
                    self.project_combo.setCurrentIndex(idx)
            
            # Set quote
            if self.order.quote_id:
                idx = self.quote_combo.findData(str(self.order.quote_id))
                if idx >= 0:
                    self.quote_combo.setCurrentIndex(idx)
            
            self.subject.setText(self.order.subject or "")
            self.customer_order_number.setText(self.order.customer_order_number or "")
            
            # Status
            if self.order.status:
                idx = self.status.findData(self.order.status.value)
                if idx >= 0:
                    self.status.setCurrentIndex(idx)
            
            # Dates
            if self.order.order_date:
                self.order_date.setDate(QDate(self.order.order_date.year, self.order.order_date.month, self.order.order_date.day))
            if self.order.planned_start:
                self.planned_start.setDate(QDate(self.order.planned_start.year, self.order.planned_start.month, self.order.planned_start.day))
            if self.order.planned_end:
                self.planned_end.setDate(QDate(self.order.planned_end.year, self.order.planned_end.month, self.order.planned_end.day))
            
            # Delivery address
            self.delivery_street.setText(self.order.delivery_street or "")
            self.delivery_postal.setText(self.order.delivery_postal_code or "")
            self.delivery_city.setText(self.order.delivery_city or "")
            
            self.payment_terms.setPlainText(self.order.payment_terms or "")
            self.delivery_terms.setPlainText(self.order.delivery_terms or "")
            self.notes.setPlainText(self.order.internal_notes or "")
            
            if self.order.discount_percent:
                self.discount_percent.setValue(float(self.order.discount_percent))
            
            # Load items
            for item in sorted(self.order.items, key=lambda x: x.position):
                self.add_item_row(item.title, item.quantity, item.unit, item.unit_price, item.tax_rate)
            
            self.calculate_totals()
            
        finally:
            session.close()
    
    def add_item(self):
        """Add empty item row"""
        self.add_item_row("", "1", "STK", "0", "19")
    
    def add_item_row(self, title="", quantity="1", unit="STK", price="0", tax="19"):
        """Add item row to table"""
        row = self.items_table.rowCount()
        self.items_table.setRowCount(row + 1)
        
        # Position
        pos_item = QTableWidgetItem(str(row + 1))
        pos_item.setFlags(pos_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 0, pos_item)
        
        # Title
        self.items_table.setItem(row, 1, QTableWidgetItem(title))
        
        # Quantity
        self.items_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
        
        # Unit
        unit_combo = QComboBox()
        unit_combo.addItems(["STK", "m", "m²", "m³", "kg", "Std", "Pausch."])
        unit_combo.setCurrentText(unit)
        unit_combo.currentTextChanged.connect(self.calculate_totals)
        self.items_table.setCellWidget(row, 3, unit_combo)
        
        # Price
        self.items_table.setItem(row, 4, QTableWidgetItem(str(price)))
        
        # Tax
        tax_combo = QComboBox()
        tax_combo.addItems(["19", "7", "0"])
        tax_combo.setCurrentText(str(tax))
        tax_combo.currentTextChanged.connect(self.calculate_totals)
        self.items_table.setCellWidget(row, 5, tax_combo)
        
        # Total
        total_item = QTableWidgetItem("0,00 €")
        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 6, total_item)
        
        self.calculate_totals()
    
    def remove_item(self):
        """Remove selected item"""
        row = self.items_table.currentRow()
        if row >= 0:
            self.items_table.removeRow(row)
            self.renumber_positions()
            self.calculate_totals()
    
    def renumber_positions(self):
        """Renumber positions after delete"""
        for row in range(self.items_table.rowCount()):
            self.items_table.item(row, 0).setText(str(row + 1))
    
    def calculate_totals(self):
        """Calculate all totals"""
        subtotal = Decimal("0")
        total_tax = Decimal("0")
        
        for row in range(self.items_table.rowCount()):
            try:
                qty_text = self.items_table.item(row, 2).text().replace(",", ".")
                price_text = self.items_table.item(row, 4).text().replace(",", ".")
                
                qty = Decimal(qty_text) if qty_text else Decimal("0")
                price = Decimal(price_text) if price_text else Decimal("0")
                
                tax_widget = self.items_table.cellWidget(row, 5)
                tax_rate = Decimal(tax_widget.currentText()) if tax_widget else Decimal("19")
                
                line_total = qty * price
                line_tax = line_total * tax_rate / Decimal("100")
                
                subtotal += line_total
                total_tax += line_tax
                
                total_str = f"{float(line_total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.items_table.item(row, 6).setText(total_str)
                
            except (ValueError, AttributeError):
                pass
        
        discount_pct = Decimal(str(self.discount_percent.value()))
        discount_amount = subtotal * discount_pct / Decimal("100")
        total = subtotal - discount_amount + total_tax
        
        self.subtotal_label.setText(f"{float(subtotal):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
        self.discount_label.setText(f"- {float(discount_amount):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
        self.tax_label.setText(f"{float(total_tax):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
        self.total_label.setText(f"{float(total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def save(self):
        """Save order"""
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen Kunden.")
            return
        
        if not self.subject.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Betreff ein.")
            return
        
        session = self.db.get_session()
        try:
            if self.order_id:
                order = session.get(Order, uuid.UUID(self.order_id))
                for item in order.items:
                    session.delete(item)
            else:
                order = Order()
                count = session.execute(select(func.count(Order.id))).scalar() or 0
                order.order_number = f"B{datetime.now().year}{count + 1:04d}"
                
                # Set tenant_id from current user
                if self.user:
                    order.tenant_id = self.user.tenant_id
                    order.created_by = self.user.id
            
            order.customer_id = uuid.UUID(customer_id)
            
            project_id = self.project_combo.currentData()
            order.project_id = uuid.UUID(project_id) if project_id else None
            
            quote_id = self.quote_combo.currentData()
            order.quote_id = uuid.UUID(quote_id) if quote_id else None
            
            order.subject = self.subject.text().strip()
            order.customer_order_number = self.customer_order_number.text().strip() or None
            order.status = OrderStatus(self.status.currentData())
            
            order.order_date = self.order_date.date().toPyDate()
            order.planned_start = self.planned_start.date().toPyDate()
            order.planned_end = self.planned_end.date().toPyDate()
            
            order.delivery_street = self.delivery_street.text().strip() or None
            order.delivery_postal_code = self.delivery_postal.text().strip() or None
            order.delivery_city = self.delivery_city.text().strip() or None
            
            order.payment_terms = self.payment_terms.toPlainText().strip() or None
            order.delivery_terms = self.delivery_terms.toPlainText().strip() or None
            order.internal_notes = self.notes.toPlainText().strip() or None
            
            # Calculate and save items
            subtotal = Decimal("0")
            total_tax = Decimal("0")
            
            for row in range(self.items_table.rowCount()):
                try:
                    title = self.items_table.item(row, 1).text().strip()
                    if not title:
                        continue
                    
                    qty = self.items_table.item(row, 2).text().replace(",", ".")
                    unit_widget = self.items_table.cellWidget(row, 3)
                    unit = unit_widget.currentText() if unit_widget else "STK"
                    price = self.items_table.item(row, 4).text().replace(",", ".")
                    tax_widget = self.items_table.cellWidget(row, 5)
                    tax_rate = tax_widget.currentText() if tax_widget else "19"
                    
                    line_subtotal = Decimal(qty) * Decimal(price)
                    line_tax = line_subtotal * Decimal(tax_rate) / Decimal("100")
                    
                    item = OrderItem(
                        order_id=order.id,
                        position=row + 1,
                        title=title,
                        quantity=qty,
                        unit=unit,
                        unit_price=price,
                        tax_rate=tax_rate,
                        subtotal=str(line_subtotal),
                        tax_amount=str(line_tax),
                        total=str(line_subtotal + line_tax)
                    )
                    order.items.append(item)
                    
                    subtotal += line_subtotal
                    total_tax += line_tax
                    
                except (ValueError, AttributeError) as e:
                    print(f"Error processing row {row}: {e}")
            
            discount_pct = Decimal(str(self.discount_percent.value()))
            discount_amount = subtotal * discount_pct / Decimal("100")
            
            order.subtotal = str(subtotal)
            order.discount_percent = str(discount_pct)
            order.discount_amount = str(discount_amount)
            order.tax_amount = str(total_tax)
            order.total = str(subtotal - discount_amount + total_tax)
            
            if not self.order_id:
                session.add(order)
            
            session.commit()
            QMessageBox.information(self, "Erfolg", f"Auftrag {order.order_number} wurde gespeichert.")
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
