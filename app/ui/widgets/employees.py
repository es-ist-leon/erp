"""
Employees Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox, 
    QMenu, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor
from sqlalchemy import select, or_

from shared.models import Employee, EmployeeStatus, EmploymentType
from app.ui.dialogs.employee_dialog import EmployeeDialog
from app.ui.styles import COLORS


class EmployeesWidget(QWidget):
    """Modern employee management page"""
    
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
        self.search_input.setPlaceholderText("Mitarbeiter suchen...")
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
        
        # Department filter
        self.dept_filter = QComboBox()
        self.dept_filter.addItem("Alle Abteilungen", None)
        self.dept_filter.addItem("Produktion", "Produktion")
        self.dept_filter.addItem("Montage", "Montage")
        self.dept_filter.addItem("Planung", "Planung")
        self.dept_filter.addItem("Verwaltung", "Verwaltung")
        self.dept_filter.setStyleSheet(f"""
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
        self.dept_filter.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.dept_filter)
        
        toolbar.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neuer Mitarbeiter")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0891b2, stop:1 #0e7490);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #22d3ee, stop:1 #0891b2);
            }}
        """)
        add_btn.clicked.connect(self.add_employee)
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
            "Personal-Nr.", "Name", "Position", "Abteilung", "E-Mail", "Telefon", "Status"
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
        self.table.doubleClicked.connect(self.edit_employee)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        
        self.status_label = QLabel("0 Mitarbeiter")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(self.status_label)
    
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
            query = select(Employee).where(Employee.is_deleted == False)
            
            search = self.search_input.text().strip()
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Employee.employee_number.ilike(search_term),
                        Employee.first_name.ilike(search_term),
                        Employee.last_name.ilike(search_term),
                        Employee.email.ilike(search_term)
                    )
                )
            
            dept = self.dept_filter.currentData()
            if dept:
                query = query.where(Employee.department == dept)
            
            query = query.order_by(Employee.last_name, Employee.first_name)
            employees = session.execute(query).scalars().all()
            
            self.table.setRowCount(len(employees))
            
            status_names = {
                EmployeeStatus.ACTIVE: "Aktiv",
                EmployeeStatus.INACTIVE: "Inaktiv",
                EmployeeStatus.ON_LEAVE: "Abwesend",
                EmployeeStatus.TERMINATED: "Ausgeschieden",
            }
            
            for row, emp in enumerate(employees):
                self.table.setItem(row, 0, QTableWidgetItem(emp.employee_number))
                self.table.setItem(row, 1, QTableWidgetItem(f"{emp.first_name} {emp.last_name}"))
                self.table.setItem(row, 2, QTableWidgetItem(emp.position or ""))
                self.table.setItem(row, 3, QTableWidgetItem(emp.department or ""))
                self.table.setItem(row, 4, QTableWidgetItem(emp.email or ""))
                self.table.setItem(row, 5, QTableWidgetItem(emp.phone or emp.mobile or ""))
                
                status_item = QTableWidgetItem(status_names.get(emp.status, ""))
                if emp.status == EmployeeStatus.ACTIVE:
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif emp.status == EmployeeStatus.TERMINATED:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 6, status_item)
                
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, str(emp.id))
            
            self.status_label.setText(f"{len(employees)} Mitarbeiter")
            
        except Exception as e:
            print(f"Error loading employees: {e}")
        finally:
            session.close()
    
    def add_employee(self):
        dialog = EmployeeDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def edit_employee(self):
        row = self.table.currentRow()
        if row < 0:
            return
        employee_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = EmployeeDialog(self.db, employee_id=employee_id, user=self.user, parent=self)
        if dialog.exec():
            self.refresh()
    
    def show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        menu = QMenu(self)
        edit_action = QAction("Bearbeiten", self)
        edit_action.triggered.connect(self.edit_employee)
        menu.addAction(edit_action)
        menu.exec(self.table.viewport().mapToGlobal(position))
