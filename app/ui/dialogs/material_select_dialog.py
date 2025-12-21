"""
Material Select Dialog - Auswahl von Material aus dem Katalog
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PyQt6.QtCore import Qt
from sqlalchemy import select, or_

from shared.models import Material, MaterialCategory


class MaterialSelectDialog(QDialog):
    """Dialog for selecting material from catalog"""
    
    def __init__(self, db_service, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.selected_material = None
        self.setup_ui()
        self.load_materials()
    
    def setup_ui(self):
        self.setWindowTitle("Material auswählen")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Material suchen...")
        self.search_input.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 6px;")
        self.search_input.textChanged.connect(self.load_materials)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("Alle Kategorien", None)
        self.category_filter.addItem("Schnittholz", "schnittholz")
        self.category_filter.addItem("Brettschichtholz (BSH)", "brettschichtholz")
        self.category_filter.addItem("Brettsperrholz (CLT)", "brettsperrholz")
        self.category_filter.addItem("Platten", "platten")
        self.category_filter.addItem("Dämmung", "daemmung")
        self.category_filter.addItem("Verbindungsmittel", "verbindungsmittel")
        self.category_filter.addItem("Beschläge", "beschlaege")
        self.category_filter.setStyleSheet("padding: 10px; border: 1px solid #ddd; border-radius: 6px;")
        self.category_filter.currentIndexChanged.connect(self.load_materials)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Art.-Nr.", "Bezeichnung", "Kategorie", "Einheit", "VK-Preis"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.accept_selection)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Auswählen")
        select_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7c3aed; }
        """)
        select_btn.clicked.connect(self.accept_selection)
        btn_layout.addWidget(select_btn)
        
        layout.addLayout(btn_layout)
    
    def load_materials(self):
        """Load materials from database"""
        session = self.db.get_session()
        try:
            query = select(Material).where(
                Material.is_deleted == False,
                Material.is_active == True
            )
            
            search = self.search_input.text().strip()
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Material.article_number.ilike(search_term),
                        Material.name.ilike(search_term),
                        Material.wood_type.ilike(search_term)
                    )
                )
            
            category = self.category_filter.currentData()
            if category:
                query = query.where(Material.category == MaterialCategory(category))
            
            query = query.order_by(Material.name).limit(100)
            materials = session.execute(query).scalars().all()
            
            self.table.setRowCount(len(materials))
            self.materials_data = {}
            
            category_names = {
                MaterialCategory.SCHNITTHOLZ: "Schnittholz",
                MaterialCategory.BRETTSCHICHTHOLZ: "BSH",
                MaterialCategory.BRETTSPERRHOLZ: "CLT",
                MaterialCategory.PLATTEN: "Platten",
                MaterialCategory.DAEMMUNG: "Dämmung",
                MaterialCategory.VERBINDUNGSMITTEL: "Verbindungsmittel",
                MaterialCategory.BESCHLAEGE: "Beschläge",
            }
            
            for row, mat in enumerate(materials):
                self.table.setItem(row, 0, QTableWidgetItem(mat.article_number))
                self.table.setItem(row, 1, QTableWidgetItem(mat.name))
                self.table.setItem(row, 2, QTableWidgetItem(category_names.get(mat.category, "")))
                self.table.setItem(row, 3, QTableWidgetItem(mat.unit or "STK"))
                
                price = ""
                if mat.selling_price:
                    price = f"{float(mat.selling_price):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.table.setItem(row, 4, QTableWidgetItem(price))
                
                # Store material data
                self.materials_data[row] = mat
                
        finally:
            session.close()
    
    def accept_selection(self):
        """Accept selected material"""
        row = self.table.currentRow()
        if row >= 0 and row in self.materials_data:
            # Get fresh copy from database
            session = self.db.get_session()
            try:
                mat = self.materials_data[row]
                self.selected_material = session.get(Material, mat.id)
                # Detach and copy essential data
                if self.selected_material:
                    # Create simple object with needed data
                    class MaterialData:
                        pass
                    
                    data = MaterialData()
                    data.id = self.selected_material.id
                    data.name = self.selected_material.name
                    data.article_number = self.selected_material.article_number
                    data.unit = self.selected_material.unit
                    data.selling_price = self.selected_material.selling_price
                    
                    self.selected_material = data
                    self.accept()
            finally:
                session.close()
        else:
            self.reject()
