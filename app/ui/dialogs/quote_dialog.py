"""
Quote Dialog - Angebotserstellung
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QDateEdit, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QSpinBox, QLabel
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

from shared.models import Quote, QuoteItem, QuoteStatus, Customer, Project, Material
from sqlalchemy import select, func


class QuoteDialog(QDialog):
    """Dialog for creating/editing quotes"""
    
    def __init__(self, db_service, quote_id=None, customer_id=None, project_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.quote_id = quote_id
        self.initial_customer_id = customer_id
        self.initial_project_id = project_id
        self.user = user
        self.quote = None
        self.items = []
        self.setup_ui()
        self.load_data()
        if quote_id:
            self.load_quote()
    
    def setup_ui(self):
        self.setWindowTitle("Neues Angebot" if not self.quote_id else "Angebot bearbeiten")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # === Basic Info Tab ===
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Header info
        header_group = QGroupBox("Angebotsinformationen")
        header_form = QFormLayout(header_group)
        
        self.customer_combo = QComboBox()
        header_form.addRow("Kunde*:", self.customer_combo)
        
        self.project_combo = QComboBox()
        header_form.addRow("Projekt:", self.project_combo)
        
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("z.B. Angebot Dachstuhl Neubau")
        header_form.addRow("Betreff*:", self.subject)
        
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Kunden-Referenz (optional)")
        header_form.addRow("Referenz:", self.reference)
        
        dates_layout = QHBoxLayout()
        self.quote_date = QDateEdit()
        self.quote_date.setCalendarPopup(True)
        self.quote_date.setDate(QDate.currentDate())
        dates_layout.addWidget(QLabel("Angebotsdatum:"))
        dates_layout.addWidget(self.quote_date)
        dates_layout.addSpacing(20)
        
        self.valid_until = QDateEdit()
        self.valid_until.setCalendarPopup(True)
        self.valid_until.setDate(QDate.currentDate().addDays(30))
        dates_layout.addWidget(QLabel("Gültig bis:"))
        dates_layout.addWidget(self.valid_until)
        dates_layout.addStretch()
        header_form.addRow("", dates_layout)
        
        basic_layout.addWidget(header_group)
        
        # Intro Text
        intro_group = QGroupBox("Einleitungstext")
        intro_layout = QVBoxLayout(intro_group)
        self.intro_text = QTextEdit()
        self.intro_text.setMaximumHeight(80)
        self.intro_text.setPlaceholderText("Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihre Anfrage...")
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
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #15803d; }
        """)
        add_item_btn.clicked.connect(self.add_item)
        items_toolbar.addWidget(add_item_btn)
        
        add_material_btn = QPushButton("+ Material aus Katalog")
        add_material_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        add_material_btn.clicked.connect(self.add_material_item)
        items_toolbar.addWidget(add_material_btn)
        
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
        self.tax_label.setFont(QFont("Segoe UI", 11))
        totals_form.addRow("MwSt.:", self.tax_label)
        
        self.total_label = QLabel("0,00 €")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #16a34a;")
        totals_form.addRow("Gesamtbetrag (brutto):", self.total_label)
        
        totals_layout.addWidget(totals_group)
        items_layout.addLayout(totals_layout)
        
        tabs.addTab(items_tab, "Positionen")
        
        # === Terms Tab ===
        terms_tab = QWidget()
        terms_layout = QVBoxLayout(terms_tab)
        
        # Closing Text
        closing_group = QGroupBox("Schlusstext")
        closing_layout = QVBoxLayout(closing_group)
        self.closing_text = QTextEdit()
        self.closing_text.setMaximumHeight(100)
        self.closing_text.setPlaceholderText("Wir würden uns freuen, den Auftrag für Sie ausführen zu dürfen...")
        closing_layout.addWidget(self.closing_text)
        terms_layout.addWidget(closing_group)
        
        # Payment Terms
        payment_group = QGroupBox("Zahlungsbedingungen")
        payment_layout = QVBoxLayout(payment_group)
        self.payment_terms = QTextEdit()
        self.payment_terms.setMaximumHeight(80)
        self.payment_terms.setPlaceholderText("Zahlbar innerhalb von 14 Tagen nach Rechnungsstellung ohne Abzug.")
        payment_layout.addWidget(self.payment_terms)
        terms_layout.addWidget(payment_group)
        
        # Delivery Terms
        delivery_group = QGroupBox("Lieferbedingungen")
        delivery_layout = QVBoxLayout(delivery_group)
        self.delivery_terms = QTextEdit()
        self.delivery_terms.setMaximumHeight(80)
        self.delivery_terms.setPlaceholderText("Lieferzeit ca. 4-6 Wochen nach Auftragserteilung.")
        delivery_layout.addWidget(self.delivery_terms)
        terms_layout.addWidget(delivery_group)
        
        terms_layout.addStretch()
        tabs.addTab(terms_tab, "Konditionen")
        
        # === Notes Tab ===
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        
        notes_group = QGroupBox("Interne Notizen")
        notes_form = QVBoxLayout(notes_group)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Interne Notizen (werden nicht auf dem Angebot gedruckt)")
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
        save_draft_btn.clicked.connect(lambda: self.save(QuoteStatus.DRAFT))
        btn_layout.addWidget(save_draft_btn)
        
        save_btn = QPushButton("Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #ca8a04;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a16207; }
        """)
        save_btn.clicked.connect(lambda: self.save(None))
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_data(self):
        """Load customers and projects"""
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
                if self.initial_project_id and str(proj.id) == self.initial_project_id:
                    self.project_combo.setCurrentIndex(self.project_combo.count() - 1)
                    
        finally:
            session.close()
    
    def load_quote(self):
        """Load existing quote for editing"""
        session = self.db.get_session()
        try:
            self.quote = session.get(Quote, uuid.UUID(self.quote_id))
            if not self.quote:
                return
            
            # Set customer
            if self.quote.customer_id:
                idx = self.customer_combo.findData(str(self.quote.customer_id))
                if idx >= 0:
                    self.customer_combo.setCurrentIndex(idx)
            
            # Set project
            if self.quote.project_id:
                idx = self.project_combo.findData(str(self.quote.project_id))
                if idx >= 0:
                    self.project_combo.setCurrentIndex(idx)
            
            self.subject.setText(self.quote.subject or "")
            self.reference.setText(self.quote.reference or "")
            
            if self.quote.quote_date:
                self.quote_date.setDate(QDate(self.quote.quote_date.year, self.quote.quote_date.month, self.quote.quote_date.day))
            if self.quote.valid_until:
                self.valid_until.setDate(QDate(self.quote.valid_until.year, self.quote.valid_until.month, self.quote.valid_until.day))
            
            self.intro_text.setPlainText(self.quote.intro_text or "")
            self.closing_text.setPlainText(self.quote.closing_text or "")
            self.payment_terms.setPlainText(self.quote.payment_terms or "")
            self.delivery_terms.setPlainText(self.quote.delivery_terms or "")
            self.notes.setPlainText(self.quote.internal_notes or "")
            
            if self.quote.discount_percent:
                self.discount_percent.setValue(float(self.quote.discount_percent))
            
            # Load items
            for item in sorted(self.quote.items, key=lambda x: x.position):
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
        
        # Total (calculated)
        total_item = QTableWidgetItem("0,00 €")
        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 6, total_item)
        
        self.calculate_totals()
    
    def add_material_item(self):
        """Add material from catalog"""
        from app.ui.dialogs.material_select_dialog import MaterialSelectDialog
        
        dialog = MaterialSelectDialog(self.db, parent=self)
        if dialog.exec():
            material = dialog.selected_material
            if material:
                price = str(material.selling_price) if material.selling_price else "0"
                self.add_item_row(material.name, "1", material.unit or "STK", price, "19")
    
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
                
                # Update line total
                total_str = f"{float(line_total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.items_table.item(row, 6).setText(total_str)
                
            except (ValueError, AttributeError):
                pass
        
        # Apply discount
        discount_pct = Decimal(str(self.discount_percent.value()))
        discount_amount = subtotal * discount_pct / Decimal("100")
        
        # Recalculate tax on discounted amount
        discounted_subtotal = subtotal - discount_amount
        
        # Final total
        total = discounted_subtotal + total_tax
        
        # Update labels
        self.subtotal_label.setText(f"{float(subtotal):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
        self.discount_label.setText(f"- {float(discount_amount):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
        self.tax_label.setText(f"{float(total_tax):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
        self.total_label.setText(f"{float(total):,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def save(self, status=None):
        """Save quote"""
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie einen Kunden.")
            return
        
        if not self.subject.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Betreff ein.")
            return
        
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "Fehler", "Bitte fügen Sie mindestens eine Position hinzu.")
            return
        
        session = self.db.get_session()
        try:
            if self.quote_id:
                quote = session.get(Quote, uuid.UUID(self.quote_id))
                # Remove old items
                for item in quote.items:
                    session.delete(item)
            else:
                quote = Quote()
                # Generate quote number
                count = session.execute(select(func.count(Quote.id))).scalar() or 0
                quote.quote_number = f"A{datetime.now().year}{count + 1:04d}"
                
                # Set tenant_id from current user
                if self.user:
                    quote.tenant_id = self.user.tenant_id
                    quote.created_by = self.user.id
            
            quote.customer_id = uuid.UUID(customer_id)
            
            project_id = self.project_combo.currentData()
            quote.project_id = uuid.UUID(project_id) if project_id else None
            
            quote.subject = self.subject.text().strip()
            quote.reference = self.reference.text().strip() or None
            quote.quote_date = self.quote_date.date().toPyDate()
            quote.valid_until = self.valid_until.date().toPyDate()
            
            quote.intro_text = self.intro_text.toPlainText().strip() or None
            quote.closing_text = self.closing_text.toPlainText().strip() or None
            quote.payment_terms = self.payment_terms.toPlainText().strip() or None
            quote.delivery_terms = self.delivery_terms.toPlainText().strip() or None
            quote.internal_notes = self.notes.toPlainText().strip() or None
            
            if status:
                quote.status = status
            
            # Calculate and save totals
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
                    
                    item = QuoteItem(
                        quote_id=quote.id,
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
                    quote.items.append(item)
                    
                    subtotal += line_subtotal
                    total_tax += line_tax
                    
                except (ValueError, AttributeError) as e:
                    print(f"Error processing row {row}: {e}")
            
            discount_pct = Decimal(str(self.discount_percent.value()))
            discount_amount = subtotal * discount_pct / Decimal("100")
            
            quote.subtotal = str(subtotal)
            quote.discount_percent = str(discount_pct)
            quote.discount_amount = str(discount_amount)
            quote.tax_amount = str(total_tax)
            quote.total = str(subtotal - discount_amount + total_tax)
            
            if not self.quote_id:
                session.add(quote)
            
            session.commit()
            QMessageBox.information(self, "Erfolg", f"Angebot {quote.quote_number} wurde gespeichert.")
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
