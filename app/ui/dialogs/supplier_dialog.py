"""
Supplier Dialog - Lieferantenverwaltung
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTextEdit, QMessageBox, QSpinBox, QScrollArea,
    QFrame, QLabel, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import uuid
from datetime import datetime

from shared.models import Supplier
from sqlalchemy import select, func

# Colors
COLORS = {
    "primary": "#0176d3",
    "primary_dark": "#014486",
    "text_primary": "#181818",
    "text_secondary": "#706e6b",
    "gray_50": "#f3f3f3",
    "gray_100": "#e5e5e5",
    "gray_200": "#c9c9c9",
    "white": "#ffffff",
}


class SupplierDialog(QDialog):
    """Dialog for creating/editing suppliers"""
    
    def __init__(self, db_service, supplier_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.supplier_id = supplier_id
        self.user = user
        self.supplier = None
        self.setup_ui()
        if supplier_id:
            self.load_supplier()
    
    def setup_ui(self):
        self.setWindowTitle("Neuer Lieferant" if not self.supplier_id else "Lieferant bearbeiten")
        self.setMinimumSize(650, 600)
        self.setStyleSheet(f"background: {COLORS['gray_50']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #032d60, stop:1 {COLORS['primary']});
                padding: 20px;
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        
        title = QLabel("Neuer Lieferant" if not self.supplier_id else "Lieferant bearbeiten")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Lieferantendaten erfassen und verwalten")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent; font-size: 13px;")
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QFrame()
        scroll_content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Basic Info
        info_group = self._create_section("Lieferanteninformationen")
        info_form = QFormLayout()
        info_form.setSpacing(12)
        info_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.company_name = self._create_input("Firmenname eingeben")
        info_form.addRow(self._create_label("Firma*:"), self.company_name)
        
        self.contact_person = self._create_input("Ansprechpartner eingeben")
        info_form.addRow(self._create_label("Ansprechpartner:"), self.contact_person)
        
        self.tax_id = self._create_input("DE123456789")
        info_form.addRow(self._create_label("USt-IdNr.:"), self.tax_id)
        
        info_group.layout().addLayout(info_form)
        layout.addWidget(info_group)
        
        # Contact
        contact_group = self._create_section("Kontaktdaten")
        contact_form = QFormLayout()
        contact_form.setSpacing(12)
        contact_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.email = self._create_input("email@firma.de")
        contact_form.addRow(self._create_label("E-Mail:"), self.email)
        
        self.phone = self._create_input("+49 123 456789")
        contact_form.addRow(self._create_label("Telefon:"), self.phone)
        
        self.fax = self._create_input("+49 123 456780")
        contact_form.addRow(self._create_label("Fax:"), self.fax)
        
        self.website = self._create_input("www.firma.de")
        contact_form.addRow(self._create_label("Website:"), self.website)
        
        contact_group.layout().addLayout(contact_form)
        layout.addWidget(contact_group)
        
        # Address
        address_group = self._create_section("Adresse")
        address_form = QFormLayout()
        address_form.setSpacing(12)
        address_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        street_layout = QHBoxLayout()
        street_layout.setSpacing(8)
        self.street = self._create_input("Straßenname")
        street_layout.addWidget(self.street, 4)
        self.street_number = self._create_input("Nr.")
        self.street_number.setMaximumWidth(80)
        street_layout.addWidget(self.street_number, 1)
        address_form.addRow(self._create_label("Straße:"), street_layout)
        
        city_layout = QHBoxLayout()
        city_layout.setSpacing(8)
        self.postal_code = self._create_input("PLZ")
        self.postal_code.setMaximumWidth(100)
        city_layout.addWidget(self.postal_code)
        self.city = self._create_input("Stadt")
        city_layout.addWidget(self.city)
        address_form.addRow(self._create_label("PLZ / Stadt:"), city_layout)
        
        self.country = self._create_input("Land")
        self.country.setText("Deutschland")
        address_form.addRow(self._create_label("Land:"), self.country)
        
        address_group.layout().addLayout(address_form)
        layout.addWidget(address_group)
        
        # Payment & Banking
        payment_group = self._create_section("Zahlungsinformationen")
        payment_form = QFormLayout()
        payment_form.setSpacing(12)
        payment_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.payment_terms = QSpinBox()
        self.payment_terms.setRange(0, 365)
        self.payment_terms.setValue(30)
        self.payment_terms.setSuffix(" Tage")
        self.payment_terms.setStyleSheet(self._get_input_style())
        payment_form.addRow(self._create_label("Zahlungsziel:"), self.payment_terms)
        
        self.iban = self._create_input("DE89 3704 0044 0532 0130 00")
        payment_form.addRow(self._create_label("IBAN:"), self.iban)
        
        self.bic = self._create_input("COBADEFFXXX")
        payment_form.addRow(self._create_label("BIC:"), self.bic)
        
        payment_group.layout().addLayout(payment_form)
        layout.addWidget(payment_group)
        
        # Notes
        notes_group = self._create_section("Notizen")
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(100)
        self.notes.setPlaceholderText("Zusätzliche Informationen zum Lieferanten...")
        self.notes.setStyleSheet(f"""
            QTextEdit {{
                padding: 12px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: {COLORS['white']};
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QTextEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        notes_group.layout().addWidget(self.notes)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Footer with buttons
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border-top: 1px solid {COLORS['gray_100']};
            }}
        """)
        btn_layout = QHBoxLayout(footer)
        btn_layout.setContentsMargins(24, 16, 24, 16)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                background: {COLORS['white']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_50']};
                border-color: {COLORS['gray_200']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 32px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_dark']});
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1b96ff, stop:1 {COLORS['primary']});
            }}
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        main_layout.addWidget(footer)
    
    def _create_section(self, title: str) -> QFrame:
        """Create a modern section card"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['white']};
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 15))
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        layout.addWidget(title_label)
        
        return frame
    
    def _create_label(self, text: str) -> QLabel:
        """Create a styled form label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-weight: 500;
            background: transparent;
        """)
        label.setMinimumWidth(100)
        return label
    
    def _create_input(self, placeholder: str) -> QLineEdit:
        """Create a styled input field"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet(self._get_input_style())
        return input_field
    
    def _get_input_style(self) -> str:
        """Get input field stylesheet"""
        return f"""
            QLineEdit, QSpinBox {{
                padding: 12px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: {COLORS['white']};
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 2px solid {COLORS['primary']};
                padding: 11px 15px;
            }}
            QLineEdit:hover, QSpinBox:hover {{
                border-color: #aeaeae;
            }}
            QLineEdit::placeholder {{
                color: #939393;
            }}
        """
    
    def load_supplier(self):
        """Load existing supplier for editing"""
        session = self.db.get_session()
        try:
            self.supplier = session.get(Supplier, uuid.UUID(self.supplier_id))
            if not self.supplier:
                return
            
            self.company_name.setText(self.supplier.company_name or "")
            self.contact_person.setText(self.supplier.contact_person or "")
            self.tax_id.setText(self.supplier.tax_id or "")
            self.email.setText(self.supplier.email or "")
            self.phone.setText(self.supplier.phone or "")
            self.fax.setText(self.supplier.fax or "")
            self.website.setText(self.supplier.website or "")
            self.street.setText(self.supplier.street or "")
            self.street_number.setText(self.supplier.street_number or "")
            self.postal_code.setText(self.supplier.postal_code or "")
            self.city.setText(self.supplier.city or "")
            self.country.setText(self.supplier.country or "Deutschland")
            
            if self.supplier.payment_terms:
                self.payment_terms.setValue(int(self.supplier.payment_terms))
            
            self.iban.setText(self.supplier.iban or "")
            self.bic.setText(self.supplier.bic or "")
            self.notes.setPlainText(self.supplier.notes or "")
            
        finally:
            session.close()
    
    def save(self):
        """Save supplier"""
        if not self.company_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Firmennamen ein.")
            return
        
        session = self.db.get_session()
        try:
            if self.supplier_id:
                supplier = session.get(Supplier, uuid.UUID(self.supplier_id))
            else:
                supplier = Supplier()
                count = session.execute(select(func.count(Supplier.id))).scalar() or 0
                supplier.supplier_number = f"L{count + 1:04d}"
                
                # Set tenant_id from current user
                if self.user:
                    supplier.tenant_id = self.user.tenant_id
            
            supplier.company_name = self.company_name.text().strip()
            supplier.contact_person = self.contact_person.text().strip() or None
            supplier.tax_id = self.tax_id.text().strip() or None
            supplier.email = self.email.text().strip() or None
            supplier.phone = self.phone.text().strip() or None
            supplier.fax = self.fax.text().strip() or None
            supplier.website = self.website.text().strip() or None
            supplier.street = self.street.text().strip() or None
            supplier.street_number = self.street_number.text().strip() or None
            supplier.postal_code = self.postal_code.text().strip() or None
            supplier.city = self.city.text().strip() or None
            supplier.country = self.country.text().strip() or "Deutschland"
            supplier.payment_terms = str(self.payment_terms.value())
            supplier.iban = self.iban.text().strip() or None
            supplier.bic = self.bic.text().strip() or None
            supplier.notes = self.notes.toPlainText().strip() or None
            
            if not self.supplier_id:
                session.add(supplier)
            
            session.commit()
            QMessageBox.information(self, "Erfolg", f"Lieferant {supplier.supplier_number} wurde gespeichert.")
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
