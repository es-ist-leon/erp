"""
Projects Management Widget - Modern Salesforce-inspired Design
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox, 
    QMenu, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFont
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from shared.models import Project, ProjectType, ProjectStatus, Customer
from app.ui.styles import COLORS


class ProjectsWidget(QWidget):
    """Modern project management page with pagination"""
    
    PAGE_SIZE = 50
    
    def __init__(self, db_service, user=None):
        super().__init__()
        self.db = db_service
        self.user = user
        self.current_page = 0
        self.total_pages = 0
        self.total_count = 0
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
        self.search_input.setPlaceholderText("Projekte suchen...")
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
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("Alle Status", None)
        self.status_filter.addItem("Anfrage", "anfrage")
        self.status_filter.addItem("Angebot", "angebot")
        self.status_filter.addItem("Beauftragt", "beauftragt")
        self.status_filter.addItem("In Planung", "planung")
        self.status_filter.addItem("Produktion", "produktion")
        self.status_filter.addItem("Montage", "montage")
        self.status_filter.addItem("Fertig", "fertig")
        self.status_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                min-width: 120px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['gray_300']};
            }}
        """)
        self.status_filter.currentIndexChanged.connect(self._reset_and_refresh)
        toolbar.addWidget(self.status_filter)
        
        # Type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("Alle Projekttypen", None)
        self.type_filter.addItem("Neubau", "neubau")
        self.type_filter.addItem("Anbau", "anbau")
        self.type_filter.addItem("Dachstuhl", "dachstuhl")
        self.type_filter.addItem("Carport", "carport")
        self.type_filter.addItem("Fassade", "fassade")
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 8px;
                background: white;
                min-width: 140px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['gray_300']};
            }}
        """)
        self.type_filter.currentIndexChanged.connect(self._reset_and_refresh)
        toolbar.addWidget(self.type_filter)
        
        toolbar.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neues Projekt")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['success']}, stop:1 #1c5a2f);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['success_light']}, stop:1 {COLORS['success']});
            }}
        """)
        add_btn.clicked.connect(self.add_project)
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
            "Projektnr.", "Name", "Kunde", "Typ", "Status", "Bauort", "Geplant", "Auftragswert"
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
                background: {COLORS['success']}10;
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
        self.table.doubleClicked.connect(self.edit_project)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        
        # Pagination bar
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['gray_50']};
                border-top: 1px solid {COLORS['gray_100']};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)
        
        pagination = QHBoxLayout(pagination_frame)
        pagination.setContentsMargins(16, 12, 16, 12)
        
        self.status_label = QLabel("0 Projekte")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        pagination.addWidget(self.status_label)
        
        pagination.addStretch()
        
        self.prev_btn = QPushButton("← Zurück")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                background: white;
                color: {COLORS['text_secondary']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_100']};
            }}
            QPushButton:disabled {{
                color: {COLORS['gray_300']};
                background: {COLORS['gray_50']};
            }}
        """)
        self.prev_btn.clicked.connect(self._prev_page)
        pagination.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Seite 1 von 1")
        self.page_label.setStyleSheet(f"margin: 0 16px; color: {COLORS['text_secondary']}; font-weight: 500;")
        pagination.addWidget(self.page_label)
        
        self.next_btn = QPushButton("Weiter →")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                background: white;
                color: {COLORS['text_secondary']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {COLORS['gray_100']};
            }}
            QPushButton:disabled {{
                color: {COLORS['gray_300']};
                background: {COLORS['gray_50']};
            }}
        """)
        self.next_btn.clicked.connect(self._next_page)
        pagination.addWidget(self.next_btn)
        
        table_layout.addWidget(pagination_frame)
        layout.addWidget(table_card)
    
    def _on_search_changed(self):
        if self._search_timer:
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._reset_and_refresh)
        self._search_timer.start(300)
    
    def _reset_and_refresh(self):
        self.current_page = 0
        self.refresh()
    
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh()
    
    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.refresh()
    
    def refresh(self):
        """Load projects from database with pagination and optimized rendering"""
        session = self.db.get_session()
        try:
            # Disable updates during data load for better performance
            self.table.setUpdatesEnabled(False)
            
            base_query = select(Project).options(
                selectinload(Project.customer)
            ).where(Project.is_deleted == False)
            
            # Apply tenant filter
            if self.user and self.user.tenant_id:
                base_query = base_query.where(Project.tenant_id == self.user.tenant_id)
            
            search = self.search_input.text().strip()
            if search:
                search_term = f"%{search}%"
                base_query = base_query.where(
                    or_(
                        Project.project_number.ilike(search_term),
                        Project.name.ilike(search_term),
                        Project.site_city.ilike(search_term)
                    )
                )
            
            status_filter = self.status_filter.currentData()
            if status_filter:
                base_query = base_query.where(Project.status == ProjectStatus(status_filter))
            
            type_filter = self.type_filter.currentData()
            if type_filter:
                base_query = base_query.where(Project.project_type == ProjectType(type_filter))
            
            # Count total
            count_query = select(func.count()).select_from(
                select(Project.id).where(Project.is_deleted == False).subquery()
            )
            self.total_count = session.execute(count_query).scalar() or 0
            self.total_pages = max(1, (self.total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            
            if self.current_page >= self.total_pages:
                self.current_page = max(0, self.total_pages - 1)
            
            query = base_query.order_by(Project.created_at.desc())
            query = query.offset(self.current_page * self.PAGE_SIZE).limit(self.PAGE_SIZE)
            projects = session.execute(query).scalars().all()
            
            self.table.setRowCount(len(projects))
            
            for row, project in enumerate(projects):
                self._set_row_data(row, project)
            
            self._update_pagination()
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden: {e}")
        finally:
            # Re-enable updates
            self.table.setUpdatesEnabled(True)
            session.close()
    
    def _set_row_data(self, row: int, project):
        item = QTableWidgetItem(project.project_number)
        item.setData(Qt.ItemDataRole.UserRole, str(project.id))
        self.table.setItem(row, 0, item)
        
        self.table.setItem(row, 1, QTableWidgetItem(project.name))
        
        customer_name = ""
        if project.customer:
            customer_name = project.customer.company_name or \
                          f"{project.customer.first_name or ''} {project.customer.last_name or ''}".strip()
        self.table.setItem(row, 2, QTableWidgetItem(customer_name))
        
        type_names = {
            ProjectType.NEUBAU: "Neubau",
            ProjectType.ANBAU: "Anbau",
            ProjectType.DACHSTUHL: "Dachstuhl",
            ProjectType.CARPORT: "Carport",
            ProjectType.FASSADE: "Fassade",
        }
        self.table.setItem(row, 3, QTableWidgetItem(type_names.get(project.project_type, "")))
        
        status_names = {
            ProjectStatus.ANFRAGE: "Anfrage",
            ProjectStatus.ANGEBOT: "Angebot",
            ProjectStatus.BEAUFTRAGT: "Beauftragt",
            ProjectStatus.PLANUNG: "Planung",
            ProjectStatus.PRODUKTION: "Produktion",
            ProjectStatus.MONTAGE: "Montage",
            ProjectStatus.FERTIG: "Fertig",
        }
        self.table.setItem(row, 4, QTableWidgetItem(status_names.get(project.status, "")))
        self.table.setItem(row, 5, QTableWidgetItem(project.site_city or ""))
        
        planned = ""
        if project.planned_start:
            planned = project.planned_start.strftime("%d.%m.%Y")
        self.table.setItem(row, 6, QTableWidgetItem(planned))
        
        value = project.contract_value or project.quoted_value or ""
        if value:
            value = f"{float(value):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        self.table.setItem(row, 7, QTableWidgetItem(value))
    
    def _update_pagination(self):
        self.status_label.setText(f"{self.total_count} Projekte")
        self.page_label.setText(f"Seite {self.current_page + 1} von {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
    
    def add_project(self):
        from app.ui.dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self.db, user=self.user, parent=self)
        if dialog.exec():
            self.db.invalidate_cache("project")
            self.refresh()
    
    def edit_project(self):
        row = self.table.currentRow()
        if row < 0:
            return
        project_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        from app.ui.dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self.db, project_id=project_id, user=self.user, parent=self)
        if dialog.exec():
            self.db.invalidate_cache("project")
            self.refresh()
    
    def show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("Bearbeiten", self)
        edit_action.triggered.connect(self.edit_project)
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Löschen", self)
        delete_action.triggered.connect(lambda: self.delete_project(row))
        menu.addAction(delete_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def delete_project(self, row: int):
        project_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Projekt löschen",
            f"Möchten Sie das Projekt '{name}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            session = self.db.get_session()
            try:
                from datetime import datetime
                import uuid
                
                project = session.get(Project, uuid.UUID(project_id))
                if project:
                    project.is_deleted = True
                    project.deleted_at = datetime.utcnow()
                    session.commit()
                    self.db.invalidate_cache("project")
                    self.refresh()
            except Exception as e:
                session.rollback()
                QMessageBox.warning(self, "Fehler", f"Fehler beim Löschen: {e}")
            finally:
                session.close()
