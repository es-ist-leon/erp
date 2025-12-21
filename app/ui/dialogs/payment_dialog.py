"""
Payment Dialog - Zahlungseingänge verbuchen
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QLabel, QMessageBox, QDateEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import uuid
from datetime import datetime, date
from decimal import Decimal

from shared.models import Invoice, Payment, PaymentMethod, InvoiceStatus
from sqlalchemy import select, func


class PaymentDialog(QDialog):
    """Dialog for recording payments"""
    
    def __init__(self, db_service, invoice_id=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.invoice_id = invoice_id
        self.invoice = None
        self.setup_ui()
        if invoice_id:
            self.load_invoice()
    
    def setup_ui(self):
        self.setWindowTitle("Zahlung erfassen")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Invoice info
        invoice_group = QGroupBox("Rechnungsinformationen")
        invoice_layout = QFormLayout(invoice_group)
        
        self.invoice_number_label = QLabel("-")
        self.invoice_number_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        invoice_layout.addRow("Rechnungs-Nr.:", self.invoice_number_label)
        
        self.customer_label = QLabel("-")
        invoice_layout.addRow("Kunde:", self.customer_label)
        
        self.total_label = QLabel("-")
        invoice_layout.addRow("Rechnungsbetrag:", self.total_label)
        
        self.paid_label = QLabel("-")
        invoice_layout.addRow("Bereits bezahlt:", self.paid_label)
        
        self.remaining_label = QLabel("-")
        self.remaining_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        invoice_layout.addRow("Offener Betrag:", self.remaining_label)
        
        layout.addWidget(invoice_group)
        
        # Payment info
        payment_group = QGroupBox("Zahlungsdetails")
        payment_layout = QFormLayout(payment_group)
        
        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        payment_layout.addRow("Zahlungsdatum:", self.payment_date)
        
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, 9999999.99)
        self.amount.setDecimals(2)
        self.amount.setSuffix(" €")
        self.amount.setGroupSeparatorShown(True)
        payment_layout.addRow("Betrag:", self.amount)
        
        self.payment_method = QComboBox()
        self.payment_method.addItem("Überweisung", "bank_transfer")
        self.payment_method.addItem("Bar", "cash")
        self.payment_method.addItem("Scheck", "check")
        self.payment_method.addItem("Kreditkarte", "credit_card")
        self.payment_method.addItem("Lastschrift", "direct_debit")
        self.payment_method.addItem("PayPal", "paypal")
        self.payment_method.addItem("Sonstige", "other")
        payment_layout.addRow("Zahlungsart:", self.payment_method)
        
        self.reference = QLineEdit()
        self.reference.setPlaceholderText("z.B. Überweisungs-Referenz, Transaktions-ID")
        payment_layout.addRow("Referenz:", self.reference)
        
        self.notes = QLineEdit()
        self.notes.setPlaceholderText("Optionale Notizen zur Zahlung")
        payment_layout.addRow("Notizen:", self.notes)
        
        layout.addWidget(payment_group)
        
        # Full payment button
        full_payment_btn = QPushButton("Gesamten offenen Betrag übernehmen")
        full_payment_btn.clicked.connect(self.set_full_amount)
        layout.addWidget(full_payment_btn)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Zahlung erfassen")
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
    
    def load_invoice(self):
        """Load invoice data"""
        session = self.db.get_session()
        try:
            from sqlalchemy.orm import selectinload
            result = session.execute(
                select(Invoice)
                .options(selectinload(Invoice.customer))
                .where(Invoice.id == uuid.UUID(self.invoice_id))
            )
            self.invoice = result.scalar_one_or_none()
            
            if not self.invoice:
                QMessageBox.warning(self, "Fehler", "Rechnung nicht gefunden.")
                self.reject()
                return
            
            self.invoice_number_label.setText(self.invoice.invoice_number)
            
            customer_name = ""
            if self.invoice.customer:
                customer_name = self.invoice.customer.company_name or \
                               f"{self.invoice.customer.first_name or ''} {self.invoice.customer.last_name or ''}".strip()
            self.customer_label.setText(customer_name)
            
            total = float(self.invoice.total or 0)
            self.total_label.setText(f"{total:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
            
            paid = float(self.invoice.paid_amount or 0)
            self.paid_label.setText(f"{paid:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
            
            remaining = float(self.invoice.remaining_amount or 0)
            self.remaining_label.setText(f"{remaining:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
            
            # Set default amount to remaining
            self.amount.setValue(remaining)
            
        finally:
            session.close()
    
    def set_full_amount(self):
        """Set amount to full remaining balance"""
        if self.invoice:
            remaining = float(self.invoice.remaining_amount or 0)
            self.amount.setValue(remaining)
    
    def save(self):
        """Save payment"""
        if not self.invoice_id:
            QMessageBox.warning(self, "Fehler", "Keine Rechnung ausgewählt.")
            return
        
        amount = Decimal(str(self.amount.value()))
        if amount <= 0:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Betrag ein.")
            return
        
        session = self.db.get_session()
        try:
            invoice = session.get(Invoice, uuid.UUID(self.invoice_id))
            if not invoice:
                QMessageBox.warning(self, "Fehler", "Rechnung nicht gefunden.")
                return
            
            remaining = Decimal(invoice.remaining_amount or "0")
            if amount > remaining:
                reply = QMessageBox.question(
                    self, "Überzahlung",
                    f"Der Betrag übersteigt den offenen Betrag ({float(remaining):,.2f} €). Fortfahren?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Create payment record
            count = session.execute(select(func.count(Payment.id))).scalar() or 0
            payment = Payment(
                payment_number=f"Z{datetime.now().year}{count + 1:04d}",
                invoice_id=invoice.id,
                payment_date=self.payment_date.date().toPyDate(),
                amount=str(amount),
                payment_method=PaymentMethod(self.payment_method.currentData()),
                reference=self.reference.text().strip() or None,
                notes=self.notes.text().strip() or None,
                tenant_id=invoice.tenant_id
            )
            session.add(payment)
            
            # Update invoice amounts
            paid = Decimal(invoice.paid_amount or "0") + amount
            new_remaining = Decimal(invoice.total or "0") - paid
            
            invoice.paid_amount = str(paid)
            invoice.remaining_amount = str(max(Decimal("0"), new_remaining))
            
            # Update status
            if new_remaining <= 0:
                invoice.status = InvoiceStatus.PAID
                invoice.paid_at = datetime.utcnow()
            elif paid > 0:
                invoice.status = InvoiceStatus.PARTIAL_PAID
            
            session.commit()
            
            QMessageBox.information(
                self, "Erfolg", 
                f"Zahlung über {float(amount):,.2f} € wurde erfasst.".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
