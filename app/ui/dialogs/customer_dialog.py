"""
Customer Dialog - Modern Salesforce-inspired Design mit vollständiger Datenerfassung
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QFrame, QLabel, QGraphicsDropShadowEffect, QScrollArea, QSpinBox,
    QDoubleSpinBox, QCheckBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import uuid
from datetime import datetime

from shared.models import Customer, CustomerType, CustomerStatus
from app.ui.styles import COLORS, get_button_style


class CustomerDialog(QDialog):
    """Modern dialog for creating/editing customers"""
    
    def __init__(self, db_service, customer_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.customer_id = customer_id
        self.user = user
        self.customer = None
        self.setup_ui()
        if customer_id:
            self.load_customer()
    
    def setup_ui(self):
        self.setWindowTitle("Neuer Kunde" if not self.customer_id else "Kunde bearbeiten")
        self.setMinimumSize(700, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background: {COLORS['bg_primary']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("👤 " + ("Neuer Kunde" if not self.customer_id else "Kunde bearbeiten"))
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        # Main card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {COLORS['gray_100']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: white;
                border-radius: 0 0 12px 12px;
            }}
            QTabBar::tab {{
                background: {COLORS['gray_50']};
                border: none;
                padding: 12px 24px;
                margin-right: 2px;
                font-weight: 600;
                color: {COLORS['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background: white;
                color: {COLORS['primary']};
                border-bottom: 3px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {COLORS['gray_100']};
            }}
        """)
        
        # Basic Info Tab
        basic_tab = QWidget()
        basic_tab.setStyleSheet("background: white;")
        basic_layout = QVBoxLayout(basic_tab)
        basic_layout.setContentsMargins(24, 24, 24, 24)
        basic_layout.setSpacing(20)
        
        # Type selection
        type_section = self._create_section("Kundentyp")
        type_content = QHBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("Privatkunde", "private")
        self.type_combo.addItem("Geschäftskunde", "business")
        self.type_combo.setStyleSheet(self._combo_style())
        self.type_combo.setMinimumWidth(200)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_content.addWidget(self.type_combo)
        type_content.addStretch()
        
        type_section.layout().addLayout(type_content)
        basic_layout.addWidget(type_section)
        
        # Company fields (for business)
        self.company_section = self._create_section("Firmendaten")
        company_form = QFormLayout()
        company_form.setSpacing(12)
        company_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.company_name = QLineEdit()
        self.company_name.setStyleSheet(self._input_style())
        self.company_name.setPlaceholderText("Firmenname eingeben...")
        company_form.addRow(self._label("Firmenname *"), self.company_name)
        
        self.tax_id = QLineEdit()
        self.tax_id.setStyleSheet(self._input_style())
        self.tax_id.setPlaceholderText("DE123456789")
        company_form.addRow(self._label("USt-IdNr."), self.tax_id)
        
        self.company_section.layout().addLayout(company_form)
        basic_layout.addWidget(self.company_section)
        
        # Person fields
        person_section = self._create_section("Kontaktperson")
        person_form = QFormLayout()
        person_form.setSpacing(12)
        person_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.salutation = QComboBox()
        self.salutation.addItems(["", "Herr", "Frau", "Divers"])
        self.salutation.setStyleSheet(self._combo_style())
        person_form.addRow(self._label("Anrede"), self.salutation)
        
        # Name row
        name_layout = QHBoxLayout()
        name_layout.setSpacing(12)
        
        self.first_name = QLineEdit()
        self.first_name.setStyleSheet(self._input_style())
        self.first_name.setPlaceholderText("Vorname")
        name_layout.addWidget(self.first_name)
        
        self.last_name = QLineEdit()
        self.last_name.setStyleSheet(self._input_style())
        self.last_name.setPlaceholderText("Nachname *")
        name_layout.addWidget(self.last_name)
        
        person_form.addRow(self._label("Name"), name_layout)
        
        person_section.layout().addLayout(person_form)
        basic_layout.addWidget(person_section)
        basic_layout.addStretch()
        
        tabs.addTab(basic_tab, "  Grunddaten  ")
        
        # Contact Tab
        contact_tab = QWidget()
        contact_tab.setStyleSheet("background: white;")
        contact_layout = QVBoxLayout(contact_tab)
        contact_layout.setContentsMargins(24, 24, 24, 24)
        contact_layout.setSpacing(20)
        
        contact_section = self._create_section("Kontaktdaten")
        contact_form = QFormLayout()
        contact_form.setSpacing(12)
        contact_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.email = QLineEdit()
        self.email.setStyleSheet(self._input_style())
        self.email.setPlaceholderText("email@example.com")
        contact_form.addRow(self._label("E-Mail"), self.email)
        
        self.phone = QLineEdit()
        self.phone.setStyleSheet(self._input_style())
        self.phone.setPlaceholderText("+49 123 456789")
        contact_form.addRow(self._label("Telefon"), self.phone)
        
        self.mobile = QLineEdit()
        self.mobile.setStyleSheet(self._input_style())
        self.mobile.setPlaceholderText("+49 171 1234567")
        contact_form.addRow(self._label("Mobil"), self.mobile)
        
        self.fax = QLineEdit()
        self.fax.setStyleSheet(self._input_style())
        contact_form.addRow(self._label("Fax"), self.fax)
        
        self.website = QLineEdit()
        self.website.setStyleSheet(self._input_style())
        self.website.setPlaceholderText("https://www.example.com")
        contact_form.addRow(self._label("Webseite"), self.website)
        
        contact_section.layout().addLayout(contact_form)
        contact_layout.addWidget(contact_section)
        contact_layout.addStretch()
        
        tabs.addTab(contact_tab, "  Kontakt  ")
        
        # Address Tab
        address_tab = QWidget()
        address_tab.setStyleSheet("background: white;")
        address_layout = QVBoxLayout(address_tab)
        address_layout.setContentsMargins(24, 24, 24, 24)
        address_layout.setSpacing(20)
        
        address_section = self._create_section("Adresse")
        address_form = QFormLayout()
        address_form.setSpacing(12)
        address_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Street row
        street_layout = QHBoxLayout()
        street_layout.setSpacing(12)
        
        self.street = QLineEdit()
        self.street.setStyleSheet(self._input_style())
        self.street.setPlaceholderText("Straße")
        street_layout.addWidget(self.street, 3)
        
        self.street_number = QLineEdit()
        self.street_number.setStyleSheet(self._input_style())
        self.street_number.setPlaceholderText("Nr.")
        self.street_number.setMaximumWidth(80)
        street_layout.addWidget(self.street_number, 1)
        
        address_form.addRow(self._label("Straße"), street_layout)
        
        # City row
        city_layout = QHBoxLayout()
        city_layout.setSpacing(12)
        
        self.postal_code = QLineEdit()
        self.postal_code.setStyleSheet(self._input_style())
        self.postal_code.setPlaceholderText("PLZ")
        self.postal_code.setMaximumWidth(100)
        city_layout.addWidget(self.postal_code, 1)
        
        self.city = QLineEdit()
        self.city.setStyleSheet(self._input_style())
        self.city.setPlaceholderText("Stadt")
        city_layout.addWidget(self.city, 3)
        
        address_form.addRow(self._label("PLZ / Stadt"), city_layout)
        
        self.country = QComboBox()
        self.country.addItems(["Deutschland", "Österreich", "Schweiz"])
        self.country.setStyleSheet(self._combo_style())
        address_form.addRow(self._label("Land"), self.country)
        
        address_section.layout().addLayout(address_form)
        address_layout.addWidget(address_section)
        address_layout.addStretch()
        
        tabs.addTab(address_tab, "  Adresse  ")
        
        # ==================== BANK & FINANZEN TAB ====================
        finance_tab = QWidget()
        finance_tab.setStyleSheet("background: white;")
        finance_layout = QVBoxLayout(finance_tab)
        finance_layout.setContentsMargins(24, 24, 24, 24)
        finance_layout.setSpacing(20)
        
        # Bankdaten
        bank_section = self._create_section("Bankverbindung")
        bank_form = QFormLayout()
        bank_form.setSpacing(12)
        bank_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.bank_name = QLineEdit()
        self.bank_name.setStyleSheet(self._input_style())
        self.bank_name.setPlaceholderText("Name der Bank")
        bank_form.addRow(self._label("Bank"), self.bank_name)
        
        self.iban = QLineEdit()
        self.iban.setStyleSheet(self._input_style())
        self.iban.setPlaceholderText("DE89 3704 0044 0532 0130 00")
        bank_form.addRow(self._label("IBAN"), self.iban)
        
        self.bic = QLineEdit()
        self.bic.setStyleSheet(self._input_style())
        self.bic.setPlaceholderText("COBADEFFXXX")
        bank_form.addRow(self._label("BIC"), self.bic)
        
        self.account_holder = QLineEdit()
        self.account_holder.setStyleSheet(self._input_style())
        self.account_holder.setPlaceholderText("Kontoinhaber (falls abweichend)")
        bank_form.addRow(self._label("Kontoinhaber"), self.account_holder)
        
        bank_section.layout().addLayout(bank_form)
        finance_layout.addWidget(bank_section)
        
        # Zahlungskonditionen
        payment_section = self._create_section("Zahlungskonditionen")
        payment_form = QFormLayout()
        payment_form.setSpacing(12)
        payment_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.payment_terms = QSpinBox()
        self.payment_terms.setRange(0, 365)
        self.payment_terms.setValue(30)
        self.payment_terms.setSuffix(" Tage")
        self.payment_terms.setStyleSheet(self._input_style())
        payment_form.addRow(self._label("Zahlungsziel"), self.payment_terms)
        
        self.discount_percent = QDoubleSpinBox()
        self.discount_percent.setRange(0, 100)
        self.discount_percent.setDecimals(2)
        self.discount_percent.setSuffix(" %")
        self.discount_percent.setStyleSheet(self._input_style())
        payment_form.addRow(self._label("Skonto"), self.discount_percent)
        
        self.discount_days = QSpinBox()
        self.discount_days.setRange(0, 60)
        self.discount_days.setValue(14)
        self.discount_days.setSuffix(" Tage")
        self.discount_days.setStyleSheet(self._input_style())
        payment_form.addRow(self._label("Skonto-Frist"), self.discount_days)
        
        self.credit_limit = QDoubleSpinBox()
        self.credit_limit.setRange(0, 9999999)
        self.credit_limit.setDecimals(2)
        self.credit_limit.setSuffix(" €")
        self.credit_limit.setStyleSheet(self._input_style())
        payment_form.addRow(self._label("Kreditlimit"), self.credit_limit)
        
        self.payment_method = QComboBox()
        self.payment_method.addItems([
            "Überweisung", "SEPA-Lastschrift", "Kreditkarte", 
            "PayPal", "Vorkasse", "Barzahlung", "Sonstiges"
        ])
        self.payment_method.setStyleSheet(self._combo_style())
        payment_form.addRow(self._label("Zahlungsart"), self.payment_method)
        
        self.sepa_mandate = QLineEdit()
        self.sepa_mandate.setStyleSheet(self._input_style())
        self.sepa_mandate.setPlaceholderText("SEPA-Mandatsreferenz")
        payment_form.addRow(self._label("SEPA-Mandat"), self.sepa_mandate)
        
        self.sepa_mandate_date = QDateEdit()
        self.sepa_mandate_date.setCalendarPopup(True)
        self.sepa_mandate_date.setStyleSheet(self._input_style())
        self.sepa_mandate_date.setSpecialValueText("Nicht erteilt")
        payment_form.addRow(self._label("Mandatsdatum"), self.sepa_mandate_date)
        
        payment_section.layout().addLayout(payment_form)
        finance_layout.addWidget(payment_section)
        finance_layout.addStretch()
        
        tabs.addTab(finance_tab, "  Finanzen  ")
        
        # ==================== LIEFERADRESSE TAB ====================
        delivery_tab = QWidget()
        delivery_tab.setStyleSheet("background: white;")
        delivery_layout = QVBoxLayout(delivery_tab)
        delivery_layout.setContentsMargins(24, 24, 24, 24)
        delivery_layout.setSpacing(20)
        
        self.same_as_billing = QCheckBox("Lieferadresse = Rechnungsadresse")
        self.same_as_billing.setChecked(True)
        self.same_as_billing.setStyleSheet("font-weight: 600;")
        self.same_as_billing.stateChanged.connect(self._toggle_delivery_address)
        delivery_layout.addWidget(self.same_as_billing)
        
        self.delivery_section = self._create_section("Lieferadresse")
        delivery_form = QFormLayout()
        delivery_form.setSpacing(12)
        delivery_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.delivery_company = QLineEdit()
        self.delivery_company.setStyleSheet(self._input_style())
        self.delivery_company.setPlaceholderText("Firma/Name")
        delivery_form.addRow(self._label("Empfänger"), self.delivery_company)
        
        delivery_street_layout = QHBoxLayout()
        self.delivery_street = QLineEdit()
        self.delivery_street.setStyleSheet(self._input_style())
        self.delivery_street.setPlaceholderText("Straße")
        delivery_street_layout.addWidget(self.delivery_street, 3)
        
        self.delivery_street_number = QLineEdit()
        self.delivery_street_number.setStyleSheet(self._input_style())
        self.delivery_street_number.setPlaceholderText("Nr.")
        self.delivery_street_number.setMaximumWidth(80)
        delivery_street_layout.addWidget(self.delivery_street_number, 1)
        delivery_form.addRow(self._label("Straße"), delivery_street_layout)
        
        delivery_city_layout = QHBoxLayout()
        self.delivery_postal_code = QLineEdit()
        self.delivery_postal_code.setStyleSheet(self._input_style())
        self.delivery_postal_code.setPlaceholderText("PLZ")
        self.delivery_postal_code.setMaximumWidth(100)
        delivery_city_layout.addWidget(self.delivery_postal_code, 1)
        
        self.delivery_city = QLineEdit()
        self.delivery_city.setStyleSheet(self._input_style())
        self.delivery_city.setPlaceholderText("Stadt")
        delivery_city_layout.addWidget(self.delivery_city, 3)
        delivery_form.addRow(self._label("PLZ / Stadt"), delivery_city_layout)
        
        self.delivery_country = QComboBox()
        self.delivery_country.addItems(["Deutschland", "Österreich", "Schweiz"])
        self.delivery_country.setStyleSheet(self._combo_style())
        delivery_form.addRow(self._label("Land"), self.delivery_country)
        
        self.delivery_notes = QTextEdit()
        self.delivery_notes.setStyleSheet(self._input_style())
        self.delivery_notes.setPlaceholderText("Besondere Lieferhinweise (Anfahrt, Öffnungszeiten...)")
        self.delivery_notes.setMaximumHeight(80)
        delivery_form.addRow(self._label("Hinweise"), self.delivery_notes)
        
        self.delivery_section.layout().addLayout(delivery_form)
        delivery_layout.addWidget(self.delivery_section)
        self.delivery_section.setVisible(False)
        delivery_layout.addStretch()
        
        tabs.addTab(delivery_tab, "  Lieferung  ")
        
        # ==================== KLASSIFIZIERUNG TAB ====================
        class_tab = QWidget()
        class_tab.setStyleSheet("background: white;")
        class_layout = QVBoxLayout(class_tab)
        class_layout.setContentsMargins(24, 24, 24, 24)
        class_layout.setSpacing(20)
        
        category_section = self._create_section("Kategorisierung")
        category_form = QFormLayout()
        category_form.setSpacing(12)
        category_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.category = QComboBox()
        self.category.addItems([
            "", "A - Premiumkunde", "B - Standardkunde", "C - Gelegenheitskunde",
            "Neukunde", "Interessent", "Inaktiv"
        ])
        self.category.setStyleSheet(self._combo_style())
        category_form.addRow(self._label("Kategorie"), self.category)
        
        self.source = QComboBox()
        self.source.addItems([
            "", "Empfehlung", "Website", "Messe", "Werbung", 
            "Social Media", "Bestandskunde", "Kaltakquise", "Sonstiges"
        ])
        self.source.setStyleSheet(self._combo_style())
        category_form.addRow(self._label("Akquisequelle"), self.source)
        
        self.assigned_rep = QLineEdit()
        self.assigned_rep.setStyleSheet(self._input_style())
        self.assigned_rep.setPlaceholderText("Name des Kundenbetreuers")
        category_form.addRow(self._label("Betreuer"), self.assigned_rep)
        
        self.tags = QLineEdit()
        self.tags.setStyleSheet(self._input_style())
        self.tags.setPlaceholderText("z.B. VIP, Holzhaus, Gewerbe (kommagetrennt)")
        category_form.addRow(self._label("Tags"), self.tags)
        
        self.customer_since = QDateEdit()
        self.customer_since.setCalendarPopup(True)
        self.customer_since.setDate(QDate.currentDate())
        self.customer_since.setStyleSheet(self._input_style())
        category_form.addRow(self._label("Kunde seit"), self.customer_since)
        
        category_section.layout().addLayout(category_form)
        class_layout.addWidget(category_section)
        
        # Präferenzen
        pref_section = self._create_section("Präferenzen")
        pref_form = QFormLayout()
        pref_form.setSpacing(12)
        
        self.preferred_contact = QComboBox()
        self.preferred_contact.addItems([
            "Keine Präferenz", "E-Mail", "Telefon", "Brief", "Persönlich"
        ])
        self.preferred_contact.setStyleSheet(self._combo_style())
        pref_form.addRow(self._label("Kontaktweg"), self.preferred_contact)
        
        self.newsletter = QCheckBox("Newsletter abonniert")
        pref_form.addRow(self._label(""), self.newsletter)
        
        self.gdpr_consent = QCheckBox("DSGVO-Einwilligung erteilt")
        pref_form.addRow(self._label(""), self.gdpr_consent)
        
        self.gdpr_consent_date = QDateEdit()
        self.gdpr_consent_date.setCalendarPopup(True)
        self.gdpr_consent_date.setStyleSheet(self._input_style())
        self.gdpr_consent_date.setSpecialValueText("Nicht dokumentiert")
        pref_form.addRow(self._label("Einwilligung am"), self.gdpr_consent_date)
        
        pref_section.layout().addLayout(pref_form)
        class_layout.addWidget(pref_section)
        class_layout.addStretch()
        
        tabs.addTab(class_tab, "  Klassifizierung  ")
        
        # Notes Tab
        notes_tab = QWidget()
        notes_tab.setStyleSheet("background: white;")
        notes_layout = QVBoxLayout(notes_tab)
        notes_layout.setContentsMargins(24, 24, 24, 24)
        notes_layout.setSpacing(20)
        
        notes_section = self._create_section("Interne Notizen")
        
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notizen zum Kunden eingeben...")
        self.notes.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background: white;
                min-height: 200px;
            }}
            QTextEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        notes_section.layout().addWidget(self.notes)
        notes_layout.addWidget(notes_section)
        
        tabs.addTab(notes_tab, "  Notizen  ")
        
        card_layout.addWidget(tabs)
        layout.addWidget(card)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                background: white;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_50']};
                border-color: {COLORS['gray_300']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾  Speichern")
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
                    stop:0 {COLORS['primary_light']}, stop:1 {COLORS['primary']});
            }}
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Initial state
        self.on_type_changed()
    
    def _create_section(self, title: str) -> QFrame:
        """Create a styled section with title"""
        section = QFrame()
        section.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(label)
        
        return section
    
    def _label(self, text: str) -> QLabel:
        """Create a styled form label"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-weight: 500;
            font-size: 13px;
        """)
        label.setMinimumWidth(100)
        return label
    
    def _input_style(self) -> str:
        """Get input field style"""
        return f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                font-size: 14px;
                background: white;
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                padding: 9px 13px;
            }}
            QLineEdit:hover {{
                border-color: {COLORS['gray_300']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['gray_400']};
            }}
        """
    
    def _combo_style(self) -> str:
        """Get combo box style"""
        return f"""
            QComboBox {{
                padding: 10px 14px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                font-size: 14px;
                background: white;
                min-width: 150px;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox:hover {{
                border-color: {COLORS['gray_300']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
        """
    
    def on_type_changed(self):
        is_business = self.type_combo.currentData() == "business"
        self.company_section.setVisible(is_business)
    
    def _toggle_delivery_address(self, state):
        """Toggle visibility of delivery address fields"""
        self.delivery_section.setVisible(not self.same_as_billing.isChecked())
    
    def load_customer(self):
        session = self.db.get_session()
        try:
            self.customer = session.get(Customer, uuid.UUID(self.customer_id))
            if not self.customer:
                return
            
            c = self.customer
            
            # Type
            idx = 0 if c.customer_type == CustomerType.PRIVATE else 1
            self.type_combo.setCurrentIndex(idx)
            
            # Company
            self.company_name.setText(c.company_name or "")
            self.tax_id.setText(c.tax_id or "")
            
            # Person
            if c.salutation:
                idx = self.salutation.findText(c.salutation)
                if idx >= 0:
                    self.salutation.setCurrentIndex(idx)
            self.first_name.setText(c.first_name or "")
            self.last_name.setText(c.last_name or "")
            
            # Contact
            self.email.setText(c.email or "")
            self.phone.setText(c.phone or "")
            self.mobile.setText(c.mobile or "")
            self.fax.setText(c.fax or "")
            self.website.setText(c.website or "")
            
            # Address
            self.street.setText(c.street or "")
            self.street_number.setText(c.street_number or "")
            self.postal_code.setText(c.postal_code or "")
            self.city.setText(c.city or "")
            if c.country:
                idx = self.country.findText(c.country)
                if idx >= 0:
                    self.country.setCurrentIndex(idx)
            
            # Bank & Finanzen
            self.bank_name.setText(getattr(c, 'bank_name', "") or "")
            self.iban.setText(getattr(c, 'iban', "") or "")
            self.bic.setText(getattr(c, 'bic', "") or "")
            
            if hasattr(c, 'payment_terms') and c.payment_terms:
                self.payment_terms.setValue(int(c.payment_terms))
            if hasattr(c, 'discount_percent') and c.discount_percent:
                self.discount_percent.setValue(float(c.discount_percent))
            if hasattr(c, 'credit_limit') and c.credit_limit:
                self.credit_limit.setValue(float(c.credit_limit))
            
            # Lieferadresse
            if hasattr(c, 'delivery_street') and c.delivery_street:
                self.same_as_billing.setChecked(False)
                self.delivery_street.setText(c.delivery_street or "")
                self.delivery_street_number.setText(getattr(c, 'delivery_street_number', "") or "")
                self.delivery_postal_code.setText(getattr(c, 'delivery_postal_code', "") or "")
                self.delivery_city.setText(getattr(c, 'delivery_city', "") or "")
            
            # Klassifizierung
            if hasattr(c, 'category') and c.category:
                idx = self.category.findText(c.category)
                if idx >= 0:
                    self.category.setCurrentIndex(idx)
            if hasattr(c, 'source') and c.source:
                idx = self.source.findText(c.source)
                if idx >= 0:
                    self.source.setCurrentIndex(idx)
            self.tags.setText(getattr(c, 'tags', "") or "")
            
            # Notes
            self.notes.setPlainText(c.notes or "")
            
        finally:
            session.close()
    
    def save(self):
        # Validate
        if self.type_combo.currentData() == "business" and not self.company_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Firmennamen eingeben.")
            return
        
        if self.type_combo.currentData() == "private" and not self.last_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Nachnamen eingeben.")
            return
        
        session = self.db.get_session()
        try:
            if self.customer_id:
                customer = session.get(Customer, uuid.UUID(self.customer_id))
            else:
                customer = Customer()
                # Generate customer number
                from sqlalchemy import select, func
                count = session.execute(select(func.count(Customer.id))).scalar() or 0
                customer.customer_number = f"K{count + 1:06d}"
                
                # Set tenant_id and created_by from current user
                if self.user:
                    customer.tenant_id = self.user.tenant_id
                    customer.created_by = self.user.id
            
            # Type
            customer.customer_type = CustomerType.BUSINESS if self.type_combo.currentData() == "business" else CustomerType.PRIVATE
            
            # Company
            customer.company_name = self.company_name.text().strip() or None
            customer.tax_id = self.tax_id.text().strip() or None
            
            # Person
            customer.salutation = self.salutation.currentText() or None
            customer.first_name = self.first_name.text().strip() or None
            customer.last_name = self.last_name.text().strip() or None
            
            # Contact
            customer.email = self.email.text().strip() or None
            customer.phone = self.phone.text().strip() or None
            customer.mobile = self.mobile.text().strip() or None
            customer.fax = self.fax.text().strip() or None
            customer.website = self.website.text().strip() or None
            
            # Address
            customer.street = self.street.text().strip() or None
            customer.street_number = self.street_number.text().strip() or None
            customer.postal_code = self.postal_code.text().strip() or None
            customer.city = self.city.text().strip() or None
            customer.country = self.country.currentText()
            
            # Bank & Finanzen
            if hasattr(customer, 'bank_name'):
                customer.bank_name = self.bank_name.text().strip() or None
            if hasattr(customer, 'iban'):
                customer.iban = self.iban.text().strip() or None
            if hasattr(customer, 'bic'):
                customer.bic = self.bic.text().strip() or None
            if hasattr(customer, 'account_holder'):
                customer.account_holder = self.account_holder.text().strip() or None
            
            # Zahlungskonditionen
            if hasattr(customer, 'payment_terms'):
                customer.payment_terms = str(self.payment_terms.value())
            if hasattr(customer, 'discount_percent'):
                customer.discount_percent = str(self.discount_percent.value())
            if hasattr(customer, 'credit_limit'):
                val = self.credit_limit.value()
                customer.credit_limit = val if val > 0 else None
            if hasattr(customer, 'payment_method'):
                customer.payment_method = self.payment_method.currentText()
            if hasattr(customer, 'sepa_mandate'):
                customer.sepa_mandate = self.sepa_mandate.text().strip() or None
            
            # Lieferadresse
            if not self.same_as_billing.isChecked():
                if hasattr(customer, 'delivery_company'):
                    customer.delivery_company = self.delivery_company.text().strip() or None
                if hasattr(customer, 'delivery_street'):
                    customer.delivery_street = self.delivery_street.text().strip() or None
                if hasattr(customer, 'delivery_street_number'):
                    customer.delivery_street_number = self.delivery_street_number.text().strip() or None
                if hasattr(customer, 'delivery_postal_code'):
                    customer.delivery_postal_code = self.delivery_postal_code.text().strip() or None
                if hasattr(customer, 'delivery_city'):
                    customer.delivery_city = self.delivery_city.text().strip() or None
                if hasattr(customer, 'delivery_country'):
                    customer.delivery_country = self.delivery_country.currentText()
                if hasattr(customer, 'delivery_notes'):
                    customer.delivery_notes = self.delivery_notes.toPlainText().strip() or None
            
            # Klassifizierung
            if hasattr(customer, 'category'):
                customer.category = self.category.currentText() or None
            if hasattr(customer, 'source'):
                customer.source = self.source.currentText() or None
            if hasattr(customer, 'tags'):
                customer.tags = self.tags.text().strip() or None
            if hasattr(customer, 'assigned_rep'):
                customer.assigned_rep = self.assigned_rep.text().strip() or None
            if hasattr(customer, 'preferred_contact'):
                customer.preferred_contact = self.preferred_contact.currentText()
            if hasattr(customer, 'newsletter'):
                customer.newsletter = self.newsletter.isChecked()
            if hasattr(customer, 'gdpr_consent'):
                customer.gdpr_consent = self.gdpr_consent.isChecked()
            
            # Notes
            customer.notes = self.notes.toPlainText().strip() or None
            
            # Set updated_by
            if self.user:
                customer.updated_by = self.user.id
            
            # Status
            if not self.customer_id:
                customer.status = CustomerStatus.ACTIVE
            
            if not self.customer_id:
                session.add(customer)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
