"""
Materials Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox, 
    QMenu, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFont
from sqlalchemy import select, or_

from shared.models import Material, MaterialCategory
from app.ui.dialogs.material_dialog import MaterialDialog
from app.ui.styles import COLORS


class MaterialsWidget(QWidget):
    """Modern material management page"""
    
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
        
        # Search with icon
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
        self.search_input.setPlaceholderText("Material suchen...")
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
        
        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("Alle Kategorien", None)
        self.category_filter.addItem("Schnittholz", "schnittholz")
        self.category_filter.addItem("Brettschichtholz (BSH)", "brettschichtholz")
        self.category_filter.addItem("Brettsperrholz (CLT)", "brettsperrholz")
        self.category_filter.addItem("Platten", "platten")
        self.category_filter.addItem("Dämmung", "daemmung")
        self.category_filter.addItem("Verbindungsmittel", "verbindungsmittel")
        self.category_filter.addItem("Beschläge", "beschlaege")
        self.category_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                min-width: 150px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['gray_300']};
            }}
        """)
        self.category_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.category_filter)
        
        toolbar.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neues Material")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a78bfa, stop:1 #8b5cf6);
            }}
        """)
        add_btn.clicked.connect(self.add_material)
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
        table_layout.setSpacing(0)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Art.-Nr.", "Bezeichnung", "Kategorie", "Holzart", "Qualität", "Maße (mm)", "Einheit", "VK-Preis"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
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
        self.table.doubleClicked.connect(self.edit_material)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        
        self.status_label = QLabel("0 Materialien")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(self.status_label)
    
    def _on_search_changed(self):
        """Debounced search"""
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh)
        self._search_timer.start(300)
    
    def refresh(self):
        session = self.db.get_session()
        try:
            query = select(Material).where(
                Material.is_deleted == False,
                Material.is_active == True
            )
            
            # Filter by tenant
            if self.user and hasattr(self.user, 'tenant_id') and self.user.tenant_id:
                query = query.where(Material.tenant_id == self.user.tenant_id)
            
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
            
            query = query.order_by(Material.name)
            materials = session.execute(query).scalars().all()
            
            self.table.setRowCount(len(materials))
            
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
                self.table.setItem(row, 3, QTableWidgetItem(mat.wood_type or ""))
                self.table.setItem(row, 4, QTableWidgetItem(mat.quality_grade or ""))
                
                dims = ""
                if mat.length_mm:
                    dims = f"{mat.length_mm}x{mat.width_mm or 0}x{mat.height_mm or 0}"
                self.table.setItem(row, 5, QTableWidgetItem(dims))
                
                self.table.setItem(row, 6, QTableWidgetItem(mat.unit or ""))
                
                price = ""
                if mat.selling_price:
                    price = f"{float(mat.selling_price):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
                self.table.setItem(row, 7, QTableWidgetItem(price))
                
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(mat.id))
            
            self.status_label.setText(f"{len(materials)} Materialien")
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden: {e}")
        finally:
            session.close()
    
    def add_material(self):
        dialog = MaterialDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def edit_material(self):
        row = self.table.currentRow()
        if row < 0:
            return
        material_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = MaterialDialog(self.db, material_id=material_id, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        menu = QMenu(self)
        edit_action = QAction("Bearbeiten", self)
        edit_action.triggered.connect(self.edit_material)
        menu.addAction(edit_action)
        menu.addSeparator()
        delete_action = QAction("Löschen", self)
        delete_action.triggered.connect(lambda: self.delete_material(row))
        menu.addAction(delete_action)
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def delete_material(self, row: int):
        material_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Material löschen",
            f"Möchten Sie '{name}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.db.get_session()
            try:
                import uuid
                mat = session.get(Material, uuid.UUID(material_id))
                if mat:
                    mat.is_deleted = True
                    session.commit()
                    self.refresh()
            except Exception as e:
                session.rollback()
                QMessageBox.warning(self, "Fehler", f"Fehler: {e}")
            finally:
                session.close()
