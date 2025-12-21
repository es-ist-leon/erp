"""
Material Dialog - Umfassende Materialverwaltung für Holzbau
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QDoubleSpinBox, QSpinBox, QCheckBox, QScrollArea, QLabel, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
import uuid
from decimal import Decimal

from shared.models import Material, MaterialCategory


class MaterialDialog(QDialog):
    """Dialog for creating/editing materials - Vollumfängliche Erfassung"""
    
    def __init__(self, db_service, material_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.material_id = material_id
        self.user = user
        self.material = None
        self.setup_ui()
        if material_id:
            self.load_material()
    
    def _create_section_header(self, text):
        """Erstellt einen Abschnitts-Header"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #374151;
                padding: 8px 0 4px 0;
                border-bottom: 2px solid #e5e7eb;
                margin-top: 10px;
            }
        """)
        return label
    
    def _create_scrollable_tab(self, content_widget):
        """Erstellt einen scrollbaren Tab"""
        scroll = QScrollArea()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        return scroll
    
    def setup_ui(self):
        self.setWindowTitle("Neues Material" if not self.material_id else "Material bearbeiten")
        self.setMinimumSize(800, 650)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # ==================== TAB 1: GRUNDDATEN ====================
        basic_widget = QWidget()
        basic_layout = QVBoxLayout(basic_widget)
        basic_layout.setSpacing(15)
        
        # Materialinformationen
        basic_layout.addWidget(self._create_section_header("📦 Materialinformationen"))
        info_form = QFormLayout()
        info_form.setSpacing(10)
        
        self.article_number = QLineEdit()
        self.article_number.setPlaceholderText("z.B. BSH-FI-100x200")
        info_form.addRow("Artikelnummer*:", self.article_number)
        
        self.name = QLineEdit()
        self.name.setPlaceholderText("z.B. Brettschichtholz Fichte 100x200mm")
        info_form.addRow("Bezeichnung*:", self.name)
        
        self.short_name = QLineEdit()
        self.short_name.setPlaceholderText("Kurzbezeichnung für Listen")
        info_form.addRow("Kurzname:", self.short_name)
        
        self.category = QComboBox()
        self.category.addItem("Schnittholz", "schnittholz")
        self.category.addItem("Brettschichtholz (BSH)", "brettschichtholz")
        self.category.addItem("Brettsperrholz (CLT)", "brettsperrholz")
        self.category.addItem("Konstruktionsvollholz (KVH)", "kvh")
        self.category.addItem("Duobalken/Triobalken", "duobalken")
        self.category.addItem("Platten (OSB, MDF, etc.)", "platten")
        self.category.addItem("Fassadenholz", "fassade")
        self.category.addItem("Terrassendielen", "terrasse")
        self.category.addItem("Dämmung", "daemmung")
        self.category.addItem("Folien/Membranen", "folien")
        self.category.addItem("Verbindungsmittel", "verbindungsmittel")
        self.category.addItem("Beschläge", "beschlaege")
        self.category.addItem("Kleber/Leime", "kleber")
        self.category.addItem("Anstrichmittel", "anstrich")
        self.category.addItem("Sonstiges", "sonstiges")
        info_form.addRow("Kategorie:", self.category)
        
        self.subcategory = QLineEdit()
        self.subcategory.setPlaceholderText("Unterkategorie (optional)")
        info_form.addRow("Unterkategorie:", self.subcategory)
        
        self.ean = QLineEdit()
        self.ean.setPlaceholderText("EAN/GTIN Barcode")
        info_form.addRow("EAN/GTIN:", self.ean)
        
        self.manufacturer_number = QLineEdit()
        self.manufacturer_number.setPlaceholderText("Hersteller-Artikelnummer")
        info_form.addRow("Hersteller-Nr.:", self.manufacturer_number)
        
        basic_layout.addLayout(info_form)
        
        # Holzspezifikationen
        basic_layout.addWidget(self._create_section_header("🌲 Holzspezifikationen"))
        wood_form = QFormLayout()
        
        self.wood_type = QComboBox()
        self.wood_type.setEditable(True)
        self.wood_type.addItems([
            "", "Fichte", "Tanne", "Kiefer", "Lärche", "Douglasie",
            "Eiche", "Buche", "Esche", "Ahorn", "Birke", "Nussbaum",
            "Teak", "Bangkirai", "Thermoholz", "Accoya", "Kebony", "Sonstige"
        ])
        wood_form.addRow("Holzart:", self.wood_type)
        
        self.quality = QComboBox()
        self.quality.setEditable(True)
        self.quality.addItems([
            "", "GL24c", "GL24h", "GL28c", "GL28h", "GL32c", "GL32h",
            "C14", "C16", "C18", "C24", "C27", "C30", "C35", "C40",
            "S7", "S10", "S13", "MS7", "MS10", "MS13", "MS17",
            "I/III", "II/IV", "A", "B", "C", "Sichtqualität"
        ])
        wood_form.addRow("Sortierung/Klasse:", self.quality)
        
        self.moisture_content = QComboBox()
        self.moisture_content.addItems([
            "", "Technisch getrocknet (8-12%)", "Halbtrocken (15-20%)",
            "Frisch (>20%)", "Kammergetrocknet", "Luftgetrocknet"
        ])
        wood_form.addRow("Holzfeuchte:", self.moisture_content)
        
        self.treatment = QComboBox()
        self.treatment.setEditable(True)
        self.treatment.addItems([
            "", "Unbehandelt", "Gehobelt", "Sägerau", "Gefräst",
            "Keilgezinkt", "Keilgezinkt sichtbar", "Thermisch modifiziert",
            "Druckimprägniert", "Kesseldruckimprägniert", "Lasiert", "Geölt"
        ])
        wood_form.addRow("Bearbeitung:", self.treatment)
        
        self.certification = QComboBox()
        self.certification.addItems([
            "", "FSC 100%", "FSC Mix", "PEFC", "FSC/PEFC", "Keine"
        ])
        wood_form.addRow("Zertifizierung:", self.certification)
        
        self.origin_country = QLineEdit()
        self.origin_country.setPlaceholderText("z.B. Deutschland, Österreich, Skandinavien")
        wood_form.addRow("Herkunft:", self.origin_country)
        
        basic_layout.addLayout(wood_form)
        basic_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(basic_widget), "📦 Grunddaten")
        
        # ==================== TAB 2: ABMESSUNGEN ====================
        dims_widget = QWidget()
        dims_layout = QVBoxLayout(dims_widget)
        dims_layout.setSpacing(15)
        
        # Hauptmaße
        dims_layout.addWidget(self._create_section_header("📐 Abmessungen"))
        dims_form = QFormLayout()
        
        self.length = QDoubleSpinBox()
        self.length.setRange(0, 99999)
        self.length.setDecimals(1)
        self.length.setSuffix(" mm")
        dims_form.addRow("Länge:", self.length)
        
        self.width = QDoubleSpinBox()
        self.width.setRange(0, 9999)
        self.width.setDecimals(1)
        self.width.setSuffix(" mm")
        dims_form.addRow("Breite:", self.width)
        
        self.height = QDoubleSpinBox()
        self.height.setRange(0, 9999)
        self.height.setDecimals(1)
        self.height.setSuffix(" mm")
        dims_form.addRow("Höhe/Stärke:", self.height)
        
        self.diameter = QDoubleSpinBox()
        self.diameter.setRange(0, 9999)
        self.diameter.setDecimals(1)
        self.diameter.setSuffix(" mm")
        dims_form.addRow("Durchmesser:", self.diameter)
        dims_layout.addLayout(dims_form)
        
        # Toleranzen
        dims_layout.addWidget(self._create_section_header("📏 Toleranzen"))
        tol_form = QFormLayout()
        
        self.length_tolerance = QLineEdit()
        self.length_tolerance.setPlaceholderText("z.B. ±3mm")
        tol_form.addRow("Längentoleranz:", self.length_tolerance)
        
        self.width_tolerance = QLineEdit()
        self.width_tolerance.setPlaceholderText("z.B. ±1mm")
        tol_form.addRow("Breitentoleranz:", self.width_tolerance)
        
        self.height_tolerance = QLineEdit()
        self.height_tolerance.setPlaceholderText("z.B. ±1mm")
        tol_form.addRow("Höhentoleranz:", self.height_tolerance)
        dims_layout.addLayout(tol_form)
        
        # Gewicht & Volumen
        dims_layout.addWidget(self._create_section_header("⚖️ Gewicht & Volumen"))
        weight_form = QFormLayout()
        
        self.weight_per_unit = QDoubleSpinBox()
        self.weight_per_unit.setRange(0, 99999)
        self.weight_per_unit.setDecimals(3)
        self.weight_per_unit.setSuffix(" kg")
        weight_form.addRow("Gewicht/Einheit:", self.weight_per_unit)
        
        self.density = QSpinBox()
        self.density.setRange(0, 2000)
        self.density.setSuffix(" kg/m³")
        weight_form.addRow("Rohdichte:", self.density)
        
        self.volume_per_unit = QDoubleSpinBox()
        self.volume_per_unit.setRange(0, 999)
        self.volume_per_unit.setDecimals(6)
        self.volume_per_unit.setSuffix(" m³")
        weight_form.addRow("Volumen/Einheit:", self.volume_per_unit)
        
        self.area_per_unit = QDoubleSpinBox()
        self.area_per_unit.setRange(0, 999)
        self.area_per_unit.setDecimals(4)
        self.area_per_unit.setSuffix(" m²")
        weight_form.addRow("Fläche/Einheit:", self.area_per_unit)
        dims_layout.addLayout(weight_form)
        
        dims_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(dims_widget), "📐 Maße")
        
        # ==================== TAB 3: TECHNISCHE DATEN ====================
        tech_widget = QWidget()
        tech_layout = QVBoxLayout(tech_widget)
        tech_layout.setSpacing(15)
        
        # Statische Werte
        tech_layout.addWidget(self._create_section_header("⚙️ Statische Kennwerte"))
        static_form = QFormLayout()
        
        self.bending_strength = QSpinBox()
        self.bending_strength.setRange(0, 999)
        self.bending_strength.setSuffix(" N/mm²")
        static_form.addRow("Biegefestigkeit fm,k:", self.bending_strength)
        
        self.tensile_strength = QSpinBox()
        self.tensile_strength.setRange(0, 999)
        self.tensile_strength.setSuffix(" N/mm²")
        static_form.addRow("Zugfestigkeit ft,0,k:", self.tensile_strength)
        
        self.compressive_strength = QSpinBox()
        self.compressive_strength.setRange(0, 999)
        self.compressive_strength.setSuffix(" N/mm²")
        static_form.addRow("Druckfestigkeit fc,0,k:", self.compressive_strength)
        
        self.shear_strength = QSpinBox()
        self.shear_strength.setRange(0, 99)
        self.shear_strength.setSuffix(" N/mm²")
        static_form.addRow("Schubfestigkeit fv,k:", self.shear_strength)
        
        self.e_modulus = QSpinBox()
        self.e_modulus.setRange(0, 99999)
        self.e_modulus.setSuffix(" N/mm²")
        static_form.addRow("E-Modul E0,mean:", self.e_modulus)
        tech_layout.addLayout(static_form)
        
        # Brandschutz
        tech_layout.addWidget(self._create_section_header("🔥 Brandschutz"))
        fire_form = QFormLayout()
        
        self.fire_class = QComboBox()
        self.fire_class.addItems([
            "", "A1", "A2", "B", "C", "D", "E", "F",
            "B-s1,d0", "B-s2,d0", "C-s1,d0", "C-s2,d0", "D-s2,d0"
        ])
        fire_form.addRow("Brandklasse:", self.fire_class)
        
        self.fire_resistance = QLineEdit()
        self.fire_resistance.setPlaceholderText("z.B. REI 30, R 60")
        fire_form.addRow("Feuerwiderstand:", self.fire_resistance)
        
        self.charring_rate = QDoubleSpinBox()
        self.charring_rate.setRange(0, 5)
        self.charring_rate.setDecimals(2)
        self.charring_rate.setSuffix(" mm/min")
        fire_form.addRow("Abbrandrate:", self.charring_rate)
        tech_layout.addLayout(fire_form)
        
        # Wärme & Feuchte
        tech_layout.addWidget(self._create_section_header("🌡️ Wärme & Feuchte"))
        thermal_form = QFormLayout()
        
        self.lambda_value = QDoubleSpinBox()
        self.lambda_value.setRange(0, 9)
        self.lambda_value.setDecimals(3)
        self.lambda_value.setSuffix(" W/(mK)")
        thermal_form.addRow("Wärmeleitfähigkeit λ:", self.lambda_value)
        
        self.sd_value = QDoubleSpinBox()
        self.sd_value.setRange(0, 9999)
        self.sd_value.setDecimals(2)
        self.sd_value.setSuffix(" m")
        thermal_form.addRow("sd-Wert:", self.sd_value)
        
        self.water_vapor_diff = QSpinBox()
        self.water_vapor_diff.setRange(0, 999999)
        self.water_vapor_diff.setSpecialValueText("--")
        thermal_form.addRow("Diffusionswiderstand μ:", self.water_vapor_diff)
        tech_layout.addLayout(thermal_form)
        
        # Schallschutz
        tech_layout.addWidget(self._create_section_header("🔊 Schallschutz"))
        sound_form = QFormLayout()
        
        self.sound_absorption = QDoubleSpinBox()
        self.sound_absorption.setRange(0, 1)
        self.sound_absorption.setDecimals(2)
        self.sound_absorption.setSpecialValueText("--")
        sound_form.addRow("Schallabsorption αw:", self.sound_absorption)
        
        self.impact_sound = QSpinBox()
        self.impact_sound.setRange(0, 100)
        self.impact_sound.setSuffix(" dB")
        self.impact_sound.setSpecialValueText("--")
        sound_form.addRow("Trittschallverbesserung:", self.impact_sound)
        tech_layout.addLayout(sound_form)
        
        tech_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(tech_widget), "⚙️ Technik")
        
        # ==================== TAB 4: PREISE & LAGER ====================
        pricing_widget = QWidget()
        pricing_layout = QVBoxLayout(pricing_widget)
        pricing_layout.setSpacing(15)
        
        # Einheit & Preise
        pricing_layout.addWidget(self._create_section_header("💰 Preise"))
        pricing_form = QFormLayout()
        
        self.unit = QComboBox()
        self.unit.addItems(["m³", "m²", "lfm", "Stück", "kg", "Paket", "Palette", "Rolle"])
        pricing_form.addRow("Einheit:", self.unit)
        
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 999999)
        self.purchase_price.setDecimals(2)
        self.purchase_price.setSuffix(" €")
        pricing_form.addRow("Einkaufspreis (netto):", self.purchase_price)
        
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 999999)
        self.selling_price.setDecimals(2)
        self.selling_price.setSuffix(" €")
        pricing_form.addRow("Verkaufspreis (netto):", self.selling_price)
        
        self.list_price = QDoubleSpinBox()
        self.list_price.setRange(0, 999999)
        self.list_price.setDecimals(2)
        self.list_price.setSuffix(" €")
        pricing_form.addRow("Listenpreis:", self.list_price)
        
        self.discount_group = QLineEdit()
        self.discount_group.setPlaceholderText("Rabattgruppe für Kalkulation")
        pricing_form.addRow("Rabattgruppe:", self.discount_group)
        
        self.price_date = QDateEdit()
        self.price_date.setCalendarPopup(True)
        self.price_date.setDate(QDate.currentDate())
        pricing_form.addRow("Preisstand:", self.price_date)
        pricing_layout.addLayout(pricing_form)
        
        # Lagerbestand
        pricing_layout.addWidget(self._create_section_header("📦 Lagerbestand"))
        stock_form = QFormLayout()
        
        self.current_stock = QDoubleSpinBox()
        self.current_stock.setRange(0, 999999)
        self.current_stock.setDecimals(2)
        stock_form.addRow("Aktueller Bestand:", self.current_stock)
        
        self.min_stock = QDoubleSpinBox()
        self.min_stock.setRange(0, 99999)
        self.min_stock.setDecimals(2)
        stock_form.addRow("Mindestbestand:", self.min_stock)
        
        self.max_stock = QDoubleSpinBox()
        self.max_stock.setRange(0, 99999)
        self.max_stock.setDecimals(2)
        stock_form.addRow("Maximalbestand:", self.max_stock)
        
        self.reorder_quantity = QDoubleSpinBox()
        self.reorder_quantity.setRange(0, 99999)
        self.reorder_quantity.setDecimals(2)
        stock_form.addRow("Bestellmenge:", self.reorder_quantity)
        
        self.storage_location = QLineEdit()
        self.storage_location.setPlaceholderText("z.B. Halle 2, Regal A3")
        stock_form.addRow("Lagerort:", self.storage_location)
        
        self.lead_time = QSpinBox()
        self.lead_time.setRange(0, 365)
        self.lead_time.setSuffix(" Tage")
        stock_form.addRow("Lieferzeit:", self.lead_time)
        pricing_layout.addLayout(stock_form)
        
        # Status
        pricing_layout.addWidget(self._create_section_header("📊 Status"))
        status_form = QFormLayout()
        
        self.is_active = QCheckBox("Aktiv (verfügbar für Aufträge)")
        self.is_active.setChecked(True)
        status_form.addRow("", self.is_active)
        
        self.is_stocked = QCheckBox("Lagerartikel")
        status_form.addRow("", self.is_stocked)
        
        self.is_discontinued = QCheckBox("Auslaufartikel")
        status_form.addRow("", self.is_discontinued)
        pricing_layout.addLayout(status_form)
        
        pricing_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(pricing_widget), "💰 Preise/Lager")
        
        # ==================== TAB 5: LIEFERANTEN ====================
        supplier_widget = QWidget()
        supplier_layout = QVBoxLayout(supplier_widget)
        supplier_layout.setSpacing(15)
        
        # Hauptlieferant
        supplier_layout.addWidget(self._create_section_header("🏭 Hauptlieferant"))
        supplier_form = QFormLayout()
        
        self.primary_supplier = QLineEdit()
        self.primary_supplier.setPlaceholderText("Name des Hauptlieferanten")
        supplier_form.addRow("Lieferant:", self.primary_supplier)
        
        self.supplier_article_no = QLineEdit()
        self.supplier_article_no.setPlaceholderText("Artikelnummer beim Lieferanten")
        supplier_form.addRow("Lieferanten-Art.-Nr.:", self.supplier_article_no)
        
        self.supplier_unit = QLineEdit()
        self.supplier_unit.setPlaceholderText("z.B. 1 Palette = 50 Stück")
        supplier_form.addRow("Verpackungseinheit:", self.supplier_unit)
        
        self.min_order_qty = QDoubleSpinBox()
        self.min_order_qty.setRange(0, 99999)
        self.min_order_qty.setDecimals(2)
        supplier_form.addRow("Mindestbestellmenge:", self.min_order_qty)
        supplier_layout.addLayout(supplier_form)
        
        # Hersteller
        supplier_layout.addWidget(self._create_section_header("🏭 Hersteller"))
        mfr_form = QFormLayout()
        
        self.manufacturer = QLineEdit()
        self.manufacturer.setPlaceholderText("Herstellername")
        mfr_form.addRow("Hersteller:", self.manufacturer)
        
        self.product_line = QLineEdit()
        self.product_line.setPlaceholderText("Produktlinie/Serie")
        mfr_form.addRow("Produktlinie:", self.product_line)
        supplier_layout.addLayout(mfr_form)
        
        supplier_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(supplier_widget), "🏭 Lieferanten")
        
        # ==================== TAB 6: DOKUMENTE & NOTIZEN ====================
        docs_widget = QWidget()
        docs_layout = QVBoxLayout(docs_widget)
        docs_layout.setSpacing(15)
        
        # Dokumente
        docs_layout.addWidget(self._create_section_header("📄 Technische Dokumente"))
        doc_form = QFormLayout()
        
        self.datasheet_url = QLineEdit()
        self.datasheet_url.setPlaceholderText("Link zum Datenblatt")
        doc_form.addRow("Datenblatt:", self.datasheet_url)
        
        self.declaration_url = QLineEdit()
        self.declaration_url.setPlaceholderText("Link zur Leistungserklärung")
        doc_form.addRow("DoP/Leistungserklärung:", self.declaration_url)
        
        self.safety_datasheet = QLineEdit()
        self.safety_datasheet.setPlaceholderText("Link zum Sicherheitsdatenblatt")
        doc_form.addRow("Sicherheitsdatenblatt:", self.safety_datasheet)
        
        self.ce_marking = QLineEdit()
        self.ce_marking.setPlaceholderText("z.B. EN 14080, EN 13986")
        doc_form.addRow("CE-Kennzeichnung:", self.ce_marking)
        docs_layout.addLayout(doc_form)
        
        # Beschreibung
        docs_layout.addWidget(self._create_section_header("📝 Beschreibung"))
        self.description = QTextEdit()
        self.description.setPlaceholderText("Technische Beschreibung, Verarbeitungshinweise...")
        self.description.setMaximumHeight(150)
        docs_layout.addWidget(self.description)
        
        # Interne Notizen
        docs_layout.addWidget(self._create_section_header("🔒 Interne Notizen"))
        self.internal_notes = QTextEdit()
        self.internal_notes.setPlaceholderText("Interne Hinweise, Erfahrungen, Besonderheiten...")
        self.internal_notes.setMaximumHeight(100)
        docs_layout.addWidget(self.internal_notes)
        
        docs_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(docs_widget), "📄 Dokumente")
        
        layout.addWidget(tabs)
        
        # ==================== BUTTONS ====================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 40px;
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_material(self):
        session = self.db.get_session()
        try:
            self.material = session.get(Material, uuid.UUID(self.material_id))
            if not self.material:
                return
            
            m = self.material
            
            # Grunddaten
            self.article_number.setText(m.article_number or "")
            self.name.setText(m.name or "")
            
            if m.category:
                idx = self.category.findData(m.category.value)
                if idx >= 0:
                    self.category.setCurrentIndex(idx)
            
            # Holzart
            if m.wood_type:
                idx = self.wood_type.findText(m.wood_type)
                if idx >= 0:
                    self.wood_type.setCurrentIndex(idx)
                else:
                    self.wood_type.setCurrentText(m.wood_type)
            
            # Qualität
            if m.quality_grade:
                idx = self.quality.findText(m.quality_grade)
                if idx >= 0:
                    self.quality.setCurrentIndex(idx)
                else:
                    self.quality.setCurrentText(m.quality_grade)
            
            # Maße
            if m.length_mm:
                self.length.setValue(float(m.length_mm))
            if m.width_mm:
                self.width.setValue(float(m.width_mm))
            if m.height_mm:
                self.height.setValue(float(m.height_mm))
            
            # Einheit
            if m.unit:
                idx = self.unit.findText(m.unit)
                if idx >= 0:
                    self.unit.setCurrentIndex(idx)
            
            # Preise
            if m.purchase_price:
                self.purchase_price.setValue(float(m.purchase_price))
            if m.selling_price:
                self.selling_price.setValue(float(m.selling_price))
            
            # Lager
            if m.min_stock:
                self.min_stock.setValue(float(m.min_stock))
            if hasattr(m, 'current_stock') and m.current_stock:
                self.current_stock.setValue(float(m.current_stock))
            if hasattr(m, 'storage_location'):
                self.storage_location.setText(m.storage_location or "")
            
            self.is_active.setChecked(m.is_active if m.is_active is not None else True)
            self.description.setPlainText(m.description or "")
            
        finally:
            session.close()
    
    def save(self):
        if not self.article_number.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Artikelnummer eingeben.")
            return
        if not self.name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Bezeichnung eingeben.")
            return
        
        session = self.db.get_session()
        try:
            if self.material_id:
                mat = session.get(Material, uuid.UUID(self.material_id))
            else:
                mat = Material()
                if self.user:
                    mat.tenant_id = self.user.tenant_id
            
            # Grunddaten
            mat.article_number = self.article_number.text().strip()
            mat.name = self.name.text().strip()
            mat.category = MaterialCategory(self.category.currentData())
            mat.wood_type = self.wood_type.currentText() or None
            mat.quality_grade = self.quality.currentText() or None
            
            # Maße
            mat.length_mm = int(self.length.value()) if self.length.value() > 0 else None
            mat.width_mm = int(self.width.value()) if self.width.value() > 0 else None
            mat.height_mm = int(self.height.value()) if self.height.value() > 0 else None
            
            # Erweiterte Maße (falls vorhanden)
            if hasattr(mat, 'diameter_mm'):
                mat.diameter_mm = int(self.diameter.value()) if self.diameter.value() > 0 else None
            if hasattr(mat, 'density'):
                mat.density = self.density.value() or None
            if hasattr(mat, 'weight_per_unit'):
                mat.weight_per_unit = self.weight_per_unit.value() or None
            
            # Einheit & Preise
            mat.unit = self.unit.currentText()
            
            purchase = self.purchase_price.value()
            mat.purchase_price = Decimal(str(purchase)) if purchase > 0 else None
            
            selling = self.selling_price.value()
            mat.selling_price = Decimal(str(selling)) if selling > 0 else None
            
            # Lager
            mat.min_stock = int(self.min_stock.value()) if self.min_stock.value() > 0 else None
            if hasattr(mat, 'max_stock'):
                mat.max_stock = int(self.max_stock.value()) if self.max_stock.value() > 0 else None
            if hasattr(mat, 'storage_location'):
                mat.storage_location = self.storage_location.text().strip() or None
            if hasattr(mat, 'lead_time_days'):
                mat.lead_time_days = self.lead_time.value() or None
            
            # Technische Daten (falls vorhanden)
            if hasattr(mat, 'fire_class'):
                mat.fire_class = self.fire_class.currentText() or None
            if hasattr(mat, 'lambda_value'):
                mat.lambda_value = self.lambda_value.value() or None
            if hasattr(mat, 'certification'):
                mat.certification = self.certification.currentText() or None
            
            # Lieferant
            if hasattr(mat, 'primary_supplier'):
                mat.primary_supplier = self.primary_supplier.text().strip() or None
            if hasattr(mat, 'manufacturer'):
                mat.manufacturer = self.manufacturer.text().strip() or None
            
            # Status
            mat.is_active = self.is_active.isChecked()
            if hasattr(mat, 'is_stocked'):
                mat.is_stocked = self.is_stocked.isChecked()
            
            # Beschreibung
            mat.description = self.description.toPlainText().strip() or None
            if hasattr(mat, 'internal_notes'):
                mat.internal_notes = self.internal_notes.toPlainText().strip() or None
            
            if not self.material_id:
                session.add(mat)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
