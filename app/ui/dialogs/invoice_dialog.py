"""
Invoice Dialog - Rechnungserstellung
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QDateEdit, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QSpinBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

from shared.models import Invoice, InvoiceItem, InvoiceStatus, InvoiceType, Customer, Project, Order
from sqlalchemy import select, func


class InvoiceDialog(QDialog):
    """Dialog for creating/editing invoices"""
    
    def __init__(self, db_service, invoice_id=None, order_id=None, customer_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.invoice_id = invoice_id
        self.initial_order_id = order_id
        self.initial_customer_id = customer_id
        self.user = user
        self.invoice = None
        self.setup_ui()
        self.load_data()
        if invoice_id:
            self.load_invoice()
        elif order_id:
            self.load_from_order(order_id)
    
    def setup_ui(self):
        self.setWindowTitle("Neue Rechnung" if not self.invoice_id else "Rechnung bearbeiten")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # === Basic Info Tab ===
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Header info
        header_group = QGroupBox("Rechnungsinformationen")
        header_form = QFormLayout(header_group)
        
        self.customer_combo = QComboBox()
        header_form.addRow("Kunde*:", self.customer_combo)
        
        self.order_combo = QComboBox()
        self.order_combo.currentIndexChanged.connect(self.on_order_selected)
        header_form.addRow("Auftrag:", self.order_combo)
        
        self.invoice_type = QComboBox()
        self.invoice_type.addItem("Rechnung", "invoice")
        self.invoice_type.addItem("Teilrechnung", "partial_invoice")
        self.invoice_type.addItem("Schlussrechnung", "final_invoice")
        self.invoice_type.addItem("Anzahlungsrechnung", "advance")
        self.invoice_type.addItem("Gutschrift", "credit_note")
        header_form.addRow("Rechnungstyp:", self.invoice_type)
        
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("z.B. Rechnung Dachstuhl Projekt Müller")
        header_form.addRow("Betreff:", self.subject)
        
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Referenz / Auftragsnummer")
        header_form.addRow("Referenz:", self.reference)
        
        dates_layout = QHBoxLayout()
        self.invoice_date = QDateEdit()
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.dateChanged.connect(self.update_due_date)
        dates_layout.addWidget(QLabel("Rechnungsdatum:"))
        dates_layout.addWidget(self.invoice_date)
        dates_layout.addSpacing(20)
        
        self.payment_days = QSpinBox()
        self.payment_days.setRange(0, 365)
        self.payment_days.setValue(30)
        self.payment_days.setSuffix(" Tage")
        self.payment_days.valueChanged.connect(self.update_due_date)
        dates_layout.addWidget(QLabel("Zahlungsziel:"))
        dates_layout.addWidget(self.payment_days)
        dates_layout.addSpacing(20)
        
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate().addDays(30))
        dates_layout.addWidget(QLabel("Fällig am:"))
        dates_layout.addWidget(self.due_date)
        dates_layout.addStretch()
        header_form.addRow("", dates_layout)
        
        basic_layout.addWidget(header_group)
        
        # Billing Address
        billing_group = QGroupBox("Rechnungsadresse")
        billing_form = QFormLayout(billing_group)
        
        self.billing_company = QLineEdit()
        billing_form.addRow("Firma:", self.billing_company)
        
        self.billing_name = QLineEdit()
        billing_form.addRow("Name:", self.billing_name)
        
        self.billing_street = QLineEdit()
        billing_form.addRow("Straße:", self.billing_street)
        
        addr_layout = QHBoxLayout()
        self.billing_postal = QLineEdit()
        self.billing_postal.setMaximumWidth(100)
        addr_layout.addWidget(self.billing_postal)
        self.billing_city = QLineEdit()
        addr_layout.addWidget(self.billing_city)
        billing_form.addRow("PLZ / Stadt:", addr_layout)
        
        basic_layout.addWidget(billing_group)
        
        # Intro text
        intro_group = QGroupBox("Einleitungstext")
        intro_layout = QVBoxLayout(intro_group)
        self.intro_text = QTextEdit()
        self.intro_text.setMaximumHeight(60)
        self.intro_text.setPlaceholderText("Sehr geehrte Damen und Herren,\n\nfür die erbrachten Leistungen erlauben wir uns wie folgt zu berechnen:")
        intro_layout.addWidget(self.intro_text)
        basic_layout.addWidget(intro_group)
        
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
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #b91c1c; }
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
        totals_form.addRow("MwSt. (19%):", self.tax_label)
        
        self.total_label = QLabel("0,00 €")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #dc2626;")
        totals_form.addRow("Gesamtbetrag (brutto):", self.total_label)
        
        totals_layout.addWidget(totals_group)
        items_layout.addLayout(totals_layout)
        
        tabs.addTab(items_tab, "Positionen")
        
        # === Payment Tab ===
        payment_tab = QWidget()
        payment_layout = QVBoxLayout(payment_tab)
        
        # Bank details
        bank_group = QGroupBox("Bankverbindung")
        bank_form = QFormLayout(bank_group)
        
        self.bank_name = QLineEdit()
        bank_form.addRow("Bank:", self.bank_name)
        
        self.iban = QLineEdit()
        self.iban.setPlaceholderText("DE89 3704 0044 0532 0130 00")
        bank_form.addRow("IBAN:", self.iban)
        
        self.bic = QLineEdit()
        bank_form.addRow("BIC:", self.bic)
        
        payment_layout.addWidget(bank_group)
        
        # Skonto
        skonto_group = QGroupBox("Skonto")
        skonto_form = QFormLayout(skonto_group)
        
        skonto_layout = QHBoxLayout()
        self.skonto_days = QSpinBox()
        self.skonto_days.setRange(0, 30)
        self.skonto_days.setValue(0)
        self.skonto_days.setSuffix(" Tage")
        skonto_layout.addWidget(self.skonto_days)
        
        self.skonto_percent = QDoubleSpinBox()
        self.skonto_percent.setRange(0, 10)
        self.skonto_percent.setSuffix(" %")
        skonto_layout.addWidget(self.skonto_percent)
        skonto_layout.addStretch()
        skonto_form.addRow("Bei Zahlung innerhalb:", skonto_layout)
        
        payment_layout.addWidget(skonto_group)
        
        # Closing text
        closing_group = QGroupBox("Schlusstext")
        closing_layout = QVBoxLayout(closing_group)
        self.closing_text = QTextEdit()
        self.closing_text.setMaximumHeight(80)
        self.closing_text.setPlaceholderText("Vielen Dank für Ihren Auftrag!\n\nMit freundlichen Grüßen")
        closing_layout.addWidget(self.closing_text)
        payment_layout.addWidget(closing_group)
        
        payment_layout.addStretch()
        tabs.addTab(payment_tab, "Zahlung")
        
        # === Notes Tab ===
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        
        notes_group = QGroupBox("Interne Notizen")
        notes_form = QVBoxLayout(notes_group)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Interne Notizen (werden nicht auf der Rechnung gedruckt)")
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
        
        save_draft_btn = QPushButton("Als Entwurf speichern")
        save_draft_btn.clicked.connect(lambda: self.save(InvoiceStatus.DRAFT))
        btn_layout.addWidget(save_draft_btn)
        
        save_btn = QPushButton("Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b91c1c; }
        """)
        save_btn.clicked.connect(lambda: self.save(None))
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def update_due_date(self):
        """Update due date based on invoice date and payment days"""
        inv_date = self.invoice_date.date()
        days = self.payment_days.value()
        self.due_date.setDate(inv_date.addDays(days))
    
    def load_data(self):
        """Load customers and orders"""
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
            
            # Load orders
            orders = session.execute(
                select(Order).where(Order.is_deleted == False).order_by(Order.created_at.desc())
            ).scalars().all()
            
            self.order_combo.addItem("-- Kein Auftrag --", None)
            for order in orders:
                self.order_combo.addItem(f"{order.order_number} - {order.subject or 'Ohne Betreff'}", str(order.id))
                if self.initial_order_id and str(order.id) == self.initial_order_id:
                    self.order_combo.setCurrentIndex(self.order_combo.count() - 1)
                    
        finally:
            session.close()
    
    def on_order_selected(self):
        """Handle order selection"""
        order_id = self.order_combo.currentData()
        if order_id and not self.invoice_id:
            reply = QMessageBox.question(
                self, "Daten übernehmen",
                "Möchten Sie die Daten aus dem Auftrag übernehmen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.load_from_order(order_id)
    
    def load_from_order(self, order_id):
        """Load data from order"""
        session = self.db.get_session()
        try:
            order = session.get(Order, uuid.UUID(order_id))
            if not order:
                return
            
            # Set customer
            if order.customer_id:
                idx = self.customer_combo.findData(str(order.customer_id))
                if idx >= 0:
                    self.customer_combo.setCurrentIndex(idx)
                
                # Load customer address
                customer = session.get(Customer, order.customer_id)
                if customer:
                    self.billing_company.setText(customer.company_name or "")
                    name = f"{customer.first_name or ''} {customer.last_name or ''}".strip()
                    self.billing_name.setText(name)
                    self.billing_street.setText(customer.street or "")
                    self.billing_postal.setText(customer.postal_code or "")
                    self.billing_city.setText(customer.city or "")
            
            self.subject.setText(f"Rechnung {order.order_number} - {order.subject or ''}")
            self.reference.setText(order.order_number or "")
            
            if order.discount_percent:
                self.discount_percent.setValue(float(order.discount_percent))
            
            # Clear and load items
            self.items_table.setRowCount(0)
            for item in sorted(order.items, key=lambda x: x.position):
                self.add_item_row(item.title, item.quantity, item.unit, item.unit_price, item.tax_rate)
            
            self.calculate_totals()
            
        finally:
            session.close()
    
    def load_invoice(self):
        """Load existing invoice for editing"""
        session = self.db.get_session()
        try:
            self.invoice = session.get(Invoice, uuid.UUID(self.invoice_id))
            if not self.invoice:
                return
            
            # Set customer
            if self.invoice.customer_id:
                idx = self.customer_combo.findData(str(self.invoice.customer_id))
                if idx >= 0:
                    self.customer_combo.setCurrentIndex(idx)
            
            # Set order
            if self.invoice.order_id:
                idx = self.order_combo.findData(str(self.invoice.order_id))
                if idx >= 0:
                    self.order_combo.setCurrentIndex(idx)
            
            # Type
            if self.invoice.invoice_type:
                idx = self.invoice_type.findData(self.invoice.invoice_type.value)
                if idx >= 0:
                    self.invoice_type.setCurrentIndex(idx)
            
            self.subject.setText(self.invoice.subject or "")
            self.reference.setText(self.invoice.reference or "")
            
            # Dates
            if self.invoice.invoice_date:
                self.invoice_date.setDate(QDate(self.invoice.invoice_date.year, self.invoice.invoice_date.month, self.invoice.invoice_date.day))
            if self.invoice.due_date:
                self.due_date.setDate(QDate(self.invoice.due_date.year, self.invoice.due_date.month, self.invoice.due_date.day))
            if self.invoice.payment_terms_days:
                self.payment_days.setValue(self.invoice.payment_terms_days)
            
            # Billing address
            self.billing_company.setText(self.invoice.billing_company or "")
            self.billing_name.setText(self.invoice.billing_name or "")
            self.billing_street.setText(self.invoice.billing_street or "")
            self.billing_postal.setText(self.invoice.billing_postal_code or "")
            self.billing_city.setText(self.invoice.billing_city or "")
            
            self.intro_text.setPlainText(self.invoice.intro_text or "")
            self.closing_text.setPlainText(self.invoice.closing_text or "")
            
            # Bank
            self.bank_name.setText(self.invoice.bank_name or "")
            self.iban.setText(self.invoice.iban or "")
            self.bic.setText(self.invoice.bic or "")
            
            # Skonto
            if self.invoice.early_payment_discount_days:
                self.skonto_days.setValue(self.invoice.early_payment_discount_days)
            if self.invoice.early_payment_discount_percent:
                self.skonto_percent.setValue(float(self.invoice.early_payment_discount_percent))
            
            self.notes.setPlainText(self.invoice.internal_notes or "")
            
            if self.invoice.discount_percent:
                self.discount_percent.setValue(float(self.invoice.discount_percent))
            
            # Load items
            for item in sorted(self.invoice.items, key=lambda x: x.position):
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
    
    def save(self, status=None):
        """Save invoice"""
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen Kunden.")
            return
        
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "Fehler", "Bitte fügen Sie mindestens eine Position hinzu.")
            return
        
        session = self.db.get_session()
        try:
            if self.invoice_id:
                invoice = session.get(Invoice, uuid.UUID(self.invoice_id))
                for item in invoice.items:
                    session.delete(item)
            else:
                invoice = Invoice()
                count = session.execute(select(func.count(Invoice.id))).scalar() or 0
                invoice.invoice_number = f"R{datetime.now().year}{count + 1:04d}"
                
                # Set tenant_id from current user
                if self.user:
                    invoice.tenant_id = self.user.tenant_id
                    invoice.created_by = self.user.id
            
            invoice.customer_id = uuid.UUID(customer_id)
            
            order_id = self.order_combo.currentData()
            invoice.order_id = uuid.UUID(order_id) if order_id else None
            
            invoice.invoice_type = InvoiceType(self.invoice_type.currentData())
            
            invoice.subject = self.subject.text().strip() or None
            invoice.reference = self.reference.text().strip() or None
            
            invoice.invoice_date = self.invoice_date.date().toPyDate()
            invoice.due_date = self.due_date.date().toPyDate()
            invoice.payment_terms_days = self.payment_days.value()
            
            # Billing address
            invoice.billing_company = self.billing_company.text().strip() or None
            invoice.billing_name = self.billing_name.text().strip() or None
            invoice.billing_street = self.billing_street.text().strip() or None
            invoice.billing_postal_code = self.billing_postal.text().strip() or None
            invoice.billing_city = self.billing_city.text().strip() or None
            
            invoice.intro_text = self.intro_text.toPlainText().strip() or None
            invoice.closing_text = self.closing_text.toPlainText().strip() or None
            
            # Bank
            invoice.bank_name = self.bank_name.text().strip() or None
            invoice.iban = self.iban.text().strip() or None
            invoice.bic = self.bic.text().strip() or None
            
            # Skonto
            skonto_days = self.skonto_days.value()
            invoice.early_payment_discount_days = skonto_days if skonto_days > 0 else None
            skonto_pct = self.skonto_percent.value()
            invoice.early_payment_discount_percent = str(skonto_pct) if skonto_pct > 0 else None
            
            invoice.internal_notes = self.notes.toPlainText().strip() or None
            
            if status:
                invoice.status = status
            
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
                    
                    item = InvoiceItem(
                        invoice_id=invoice.id,
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
                    invoice.items.append(item)
                    
                    subtotal += line_subtotal
                    total_tax += line_tax
                    
                except (ValueError, AttributeError) as e:
                    print(f"Error processing row {row}: {e}")
            
            discount_pct = Decimal(str(self.discount_percent.value()))
            discount_amount = subtotal * discount_pct / Decimal("100")
            total = subtotal - discount_amount + total_tax
            
            invoice.subtotal = str(subtotal)
            invoice.discount_percent = str(discount_pct)
            invoice.discount_amount = str(discount_amount)
            invoice.total_tax = str(total_tax)
            invoice.total = str(total)
            invoice.remaining_amount = str(total)  # Full amount is remaining initially
            
            if not self.invoice_id:
                session.add(invoice)
            
            session.commit()
            QMessageBox.information(self, "Erfolg", f"Rechnung {invoice.invoice_number} wurde gespeichert.")
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
