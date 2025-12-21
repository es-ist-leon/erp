"""
Telemetrie-Dashboard Widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QProgressBar, QGroupBox, QSplitter, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPainter
try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QPieSeries, QValueAxis, QBarCategoryAxis
    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json


class MetricCard(QFrame):
    """Karte für einzelne Metrik"""
    
    def __init__(self, title: str, value: str = "0", subtitle: str = "", icon: str = "📊", color: str = "#3498db"):
        super().__init__()
        self.setObjectName("metricCard")
        self.color = color
        self.setup_ui(title, value, subtitle, icon)
    
    def setup_ui(self, title: str, value: str, subtitle: str, icon: str):
        self.setStyleSheet(f"""
            #metricCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color}, stop:1 {self._darken_color(self.color)});
                border-radius: 12px;
                padding: 20px;
                min-height: 120px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header mit Icon
        header = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        header.addWidget(icon_label)
        
        header.addStretch()
        
        layout.addLayout(header)
        
        # Wert
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        layout.addWidget(self.value_label)
        
        # Titel
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet("color: rgba(255,255,255,0.9);")
        layout.addWidget(title_label)
        
        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setFont(QFont("Segoe UI", 10))
            self.subtitle_label.setStyleSheet("color: rgba(255,255,255,0.7);")
            layout.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None
    
    def update_value(self, value: str, subtitle: str = None):
        """Aktualisiert den Wert"""
        self.value_label.setText(value)
        if subtitle and self.subtitle_label:
            self.subtitle_label.setText(subtitle)
    
    def _darken_color(self, color: str) -> str:
        """Dunkelt eine Farbe ab"""
        # Einfache Abdunkelung
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 40)
            g = max(0, g - 40)
            b = max(0, b - 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color


class HealthIndicator(QFrame):
    """System-Health-Indikator"""
    
    def __init__(self, name: str, status: str = "healthy"):
        super().__init__()
        self.name = name
        self.setup_ui()
        self.set_status(status)
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: #2d3748;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Status-Punkt
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Segoe UI", 14))
        layout.addWidget(self.status_dot)
        
        # Name
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Segoe UI", 11))
        name_label.setStyleSheet("color: white;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Status-Text
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.status_label)
        
        # Wert
        self.value_label = QLabel()
        self.value_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: white;")
        layout.addWidget(self.value_label)
    
    def set_status(self, status: str, value: str = ""):
        """Setzt den Status"""
        colors = {
            'healthy': '#10b981',
            'degraded': '#f59e0b',
            'unhealthy': '#ef4444',
            'unknown': '#6b7280'
        }
        color = colors.get(status, colors['unknown'])
        
        self.status_dot.setStyleSheet(f"color: {color};")
        self.status_label.setText(status.capitalize())
        self.status_label.setStyleSheet(f"color: {color};")
        
        if value:
            self.value_label.setText(value)


class ErrorListWidget(QFrame):
    """Widget für Fehler-Liste"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: #1e2530;
                border-radius: 12px;
            }
            QTableWidget {
                background: transparent;
                border: none;
                color: white;
                gridline-color: #374151;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #374151;
            }
            QTableWidget::item:selected {
                background: #3b82f6;
            }
            QHeaderView::section {
                background: #374151;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background: #374151; border-radius: 12px 12px 0 0;")
        header_layout = QHBoxLayout(header)
        
        title = QLabel("🐛 Aktuelle Fehler")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Aktualisieren")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addWidget(header)
        
        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Typ", "Nachricht", "Modul", "Anzahl", "Zuletzt"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
    
    def set_errors(self, errors: List[Dict[str, Any]]):
        """Setzt die Fehler-Liste"""
        self.table.setRowCount(len(errors))
        
        for row, error in enumerate(errors):
            # Typ
            type_item = QTableWidgetItem(error.get('error_type', ''))
            type_item.setForeground(QColor('#ef4444'))
            self.table.setItem(row, 0, type_item)
            
            # Nachricht
            msg = error.get('error_message', '')[:100]
            self.table.setItem(row, 1, QTableWidgetItem(msg))
            
            # Modul
            self.table.setItem(row, 2, QTableWidgetItem(error.get('module', '')))
            
            # Anzahl
            count_item = QTableWidgetItem(str(error.get('occurrence_count', 1)))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if error.get('occurrence_count', 0) > 10:
                count_item.setForeground(QColor('#ef4444'))
            self.table.setItem(row, 3, count_item)
            
            # Zuletzt
            last_seen = error.get('last_seen', '')
            if last_seen:
                try:
                    dt = datetime.fromisoformat(last_seen)
                    last_seen = dt.strftime("%d.%m. %H:%M")
                except:
                    pass
            self.table.setItem(row, 4, QTableWidgetItem(last_seen))


class PerformanceChart(QFrame):
    """Performance-Chart Widget"""
    
    def __init__(self, title: str = "Performance"):
        super().__init__()
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: #1e2530;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Titel
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        # Chart (nur wenn PyQt6-Charts verfügbar)
        if HAS_CHARTS:
            self.chart = QChart()
            self.chart.setBackgroundVisible(False)
            self.chart.setTitle("")
            self.chart.legend().setVisible(True)
            self.chart.legend().setLabelColor(QColor("white"))
            
            self.chart_view = QChartView(self.chart)
            self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.chart_view.setStyleSheet("background: transparent;")
            
            layout.addWidget(self.chart_view)
        else:
            # Fallback ohne Charts
            placeholder = QLabel("📊 Charts nicht verfügbar\n(PyQt6-Charts installieren)")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #6b7280; font-size: 14px;")
            layout.addWidget(placeholder)
    
    def set_line_data(self, data: List[Dict[str, Any]], x_key: str, y_key: str, name: str = "Data"):
        """Setzt Liniendaten"""
        if not HAS_CHARTS:
            return
            
        self.chart.removeAllSeries()
        
        series = QLineSeries()
        series.setName(name)
        series.setColor(QColor("#3b82f6"))
        
        for i, point in enumerate(data):
            series.append(i, point.get(y_key, 0))
        
        self.chart.addSeries(series)
        self.chart.createDefaultAxes()
        
        # Achsen stylen
        for axis in self.chart.axes():
            axis.setLabelsColor(QColor("white"))
            axis.setGridLineColor(QColor("#374151"))
    
    def set_bar_data(self, categories: List[str], values: List[float], name: str = "Data"):
        """Setzt Balkendaten"""
        if not HAS_CHARTS:
            return
            
        self.chart.removeAllSeries()
        
        bar_set = QBarSet(name)
        bar_set.setColor(QColor("#3b82f6"))
        
        for value in values:
            bar_set.append(value)
        
        series = QBarSeries()
        series.append(bar_set)
        
        self.chart.addSeries(series)
        
        # X-Achse
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_x.setLabelsColor(QColor("white"))
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        # Y-Achse
        axis_y = QValueAxis()
        axis_y.setLabelsColor(QColor("white"))
        axis_y.setGridLineColor(QColor("#374151"))
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)


class TelemetryDashboard(QWidget):
    """Hauptwidget für das Telemetrie-Dashboard"""
    
    def __init__(self, db_service, user=None):
        super().__init__()
        self.db_service = db_service
        self.user = user
        self.telemetry_service = None
        
        self.setup_ui()
        self.setup_refresh_timer()
        self.load_data()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #111827;
                color: white;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #374151;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px 8px 0 0;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
            }
            QTabBar::tab:hover:!selected {
                background: #4b5563;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_overview_tab(), "📊 Übersicht")
        tabs.addTab(self._create_performance_tab(), "⚡ Performance")
        tabs.addTab(self._create_errors_tab(), "🐛 Fehler")
        tabs.addTab(self._create_health_tab(), "💚 System-Health")
        tabs.addTab(self._create_activity_tab(), "👥 Aktivität")
        tabs.addTab(self._create_audit_tab(), "📋 Audit-Log")
        
        layout.addWidget(tabs)
    
    def _create_header(self) -> QWidget:
        """Erstellt den Header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titel
        title = QLabel("📈 Telemetrie Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Zeitraum-Auswahl
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Letzte 24 Stunden", "Letzte 7 Tage", "Letzte 30 Tage", "Letzte 90 Tage"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                background: #374151;
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
                border: none;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #374151;
                color: white;
                selection-background-color: #3b82f6;
            }
        """)
        self.period_combo.currentIndexChanged.connect(self.load_data)
        layout.addWidget(self.period_combo)
        
        # Refresh-Button
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        return header
    
    def _create_overview_tab(self) -> QWidget:
        """Erstellt die Übersicht-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        
        # Metric Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        self.events_card = MetricCard("Events (gesamt)", "0", "Letzte 7 Tage", "📊", "#3b82f6")
        cards_layout.addWidget(self.events_card)
        
        self.errors_card = MetricCard("Fehler", "0", "Ungelöst", "🐛", "#ef4444")
        cards_layout.addWidget(self.errors_card)
        
        self.sessions_card = MetricCard("Aktive Sessions", "0", "Jetzt", "👥", "#10b981")
        cards_layout.addWidget(self.sessions_card)
        
        self.performance_card = MetricCard("Ø Antwortzeit", "0 ms", "", "⚡", "#f59e0b")
        cards_layout.addWidget(self.performance_card)
        
        layout.addLayout(cards_layout)
        
        # Charts
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)
        
        self.events_chart = PerformanceChart("Events über Zeit")
        charts_layout.addWidget(self.events_chart, 2)
        
        self.features_chart = PerformanceChart("Top Features")
        charts_layout.addWidget(self.features_chart, 1)
        
        layout.addLayout(charts_layout)
        
        return widget
    
    def _create_performance_tab(self) -> QWidget:
        """Erstellt die Performance-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        
        # Performance-Metriken
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        
        self.avg_response_card = MetricCard("Ø Antwortzeit", "0 ms", "", "⏱️", "#3b82f6")
        metrics_layout.addWidget(self.avg_response_card)
        
        self.max_response_card = MetricCard("Max. Antwortzeit", "0 ms", "", "📈", "#ef4444")
        metrics_layout.addWidget(self.max_response_card)
        
        self.request_count_card = MetricCard("Requests", "0", "Gesamt", "📊", "#10b981")
        metrics_layout.addWidget(self.request_count_card)
        
        self.db_time_card = MetricCard("Ø DB-Zeit", "0 ms", "", "🗄️", "#f59e0b")
        metrics_layout.addWidget(self.db_time_card)
        
        layout.addLayout(metrics_layout)
        
        # Performance-Chart
        self.perf_chart = PerformanceChart("Antwortzeiten")
        layout.addWidget(self.perf_chart)
        
        # Slow Queries Tabelle
        slow_group = QGroupBox("🐢 Langsame Operationen (> 500ms)")
        slow_group.setStyleSheet("""
            QGroupBox {
                background: #1e2530;
                border-radius: 12px;
                padding: 16px;
                margin-top: 12px;
                font-weight: bold;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        slow_layout = QVBoxLayout(slow_group)
        
        self.slow_table = QTableWidget()
        self.slow_table.setColumnCount(4)
        self.slow_table.setHorizontalHeaderLabels(["Operation", "Typ", "Dauer (ms)", "Zeitpunkt"])
        self.slow_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.slow_table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background: #374151;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        slow_layout.addWidget(self.slow_table)
        
        layout.addWidget(slow_group)
        
        return widget
    
    def _create_errors_tab(self) -> QWidget:
        """Erstellt die Fehler-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        
        # Error-Statistiken
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.total_errors_card = MetricCard("Fehler gesamt", "0", "", "🐛", "#ef4444")
        stats_layout.addWidget(self.total_errors_card)
        
        self.unresolved_errors_card = MetricCard("Ungelöst", "0", "", "⚠️", "#f59e0b")
        stats_layout.addWidget(self.unresolved_errors_card)
        
        self.critical_errors_card = MetricCard("Kritisch", "0", "", "🔴", "#dc2626")
        stats_layout.addWidget(self.critical_errors_card)
        
        self.error_rate_card = MetricCard("Fehlerrate", "0%", "", "📉", "#6366f1")
        stats_layout.addWidget(self.error_rate_card)
        
        layout.addLayout(stats_layout)
        
        # Error-Liste
        self.error_list = ErrorListWidget()
        self.error_list.refresh_btn.clicked.connect(self.load_errors)
        layout.addWidget(self.error_list)
        
        return widget
    
    def _create_health_tab(self) -> QWidget:
        """Erstellt die System-Health-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        
        # System-Status
        status_group = QGroupBox("System-Status")
        status_group.setStyleSheet("""
            QGroupBox {
                background: #1e2530;
                border-radius: 12px;
                padding: 20px;
                margin-top: 12px;
                font-weight: bold;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
        """)
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(12)
        
        # Health-Indikatoren
        self.cpu_health = HealthIndicator("CPU")
        status_layout.addWidget(self.cpu_health)
        
        self.memory_health = HealthIndicator("Arbeitsspeicher")
        status_layout.addWidget(self.memory_health)
        
        self.disk_health = HealthIndicator("Festplatte")
        status_layout.addWidget(self.disk_health)
        
        self.db_health = HealthIndicator("Datenbank")
        status_layout.addWidget(self.db_health)
        
        layout.addWidget(status_group)
        
        # Resource-Nutzung
        resources_layout = QHBoxLayout()
        resources_layout.setSpacing(16)
        
        self.cpu_card = MetricCard("CPU-Auslastung", "0%", "", "🖥️", "#3b82f6")
        resources_layout.addWidget(self.cpu_card)
        
        self.memory_card = MetricCard("RAM-Nutzung", "0%", "", "💾", "#10b981")
        resources_layout.addWidget(self.memory_card)
        
        self.disk_card = MetricCard("Speicher", "0%", "", "💿", "#f59e0b")
        resources_layout.addWidget(self.disk_card)
        
        self.uptime_card = MetricCard("Uptime", "0h", "", "⏰", "#6366f1")
        resources_layout.addWidget(self.uptime_card)
        
        layout.addLayout(resources_layout)
        
        layout.addStretch()
        
        return widget
    
    def _create_activity_tab(self) -> QWidget:
        """Erstellt die Aktivität-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        
        # Aktivitäts-Metriken
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        
        self.active_users_card = MetricCard("Aktive Nutzer", "0", "Heute", "👥", "#3b82f6")
        metrics_layout.addWidget(self.active_users_card)
        
        self.page_views_card = MetricCard("Seitenaufrufe", "0", "Heute", "📄", "#10b981")
        metrics_layout.addWidget(self.page_views_card)
        
        self.actions_card = MetricCard("Aktionen", "0", "Heute", "🖱️", "#f59e0b")
        metrics_layout.addWidget(self.actions_card)
        
        self.avg_session_card = MetricCard("Ø Session-Dauer", "0 min", "", "⏱️", "#6366f1")
        metrics_layout.addWidget(self.avg_session_card)
        
        layout.addLayout(metrics_layout)
        
        # Aktivitäts-Tabelle
        activity_group = QGroupBox("📋 Letzte Aktivitäten")
        activity_group.setStyleSheet("""
            QGroupBox {
                background: #1e2530;
                border-radius: 12px;
                padding: 16px;
                margin-top: 12px;
                font-weight: bold;
                color: white;
            }
        """)
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(5)
        self.activity_table.setHorizontalHeaderLabels(["Benutzer", "Aktion", "Modul", "Ziel", "Zeit"])
        self.activity_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.activity_table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background: #374151;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        activity_layout.addWidget(self.activity_table)
        
        layout.addWidget(activity_group)
        
        return widget
    
    def _create_audit_tab(self) -> QWidget:
        """Erstellt die Audit-Log-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        
        # Filter
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Aktion:"))
        self.action_filter = QComboBox()
        self.action_filter.addItems(["Alle", "create", "update", "delete", "login", "logout"])
        self.action_filter.setStyleSheet("""
            QComboBox {
                background: #374151;
                color: white;
                padding: 8px;
                border-radius: 6px;
                border: none;
                min-width: 100px;
            }
        """)
        filter_layout.addWidget(self.action_filter)
        
        filter_layout.addWidget(QLabel("Resource:"))
        self.resource_filter = QComboBox()
        self.resource_filter.addItems(["Alle", "customer", "project", "invoice", "material", "user"])
        self.resource_filter.setStyleSheet("""
            QComboBox {
                background: #374151;
                color: white;
                padding: 8px;
                border-radius: 6px;
                border: none;
                min-width: 100px;
            }
        """)
        filter_layout.addWidget(self.resource_filter)
        
        filter_layout.addStretch()
        
        search_btn = QPushButton("🔍 Filtern")
        search_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
        """)
        search_btn.clicked.connect(self.load_audit_logs)
        filter_layout.addWidget(search_btn)
        
        layout.addLayout(filter_layout)
        
        # Audit-Tabelle
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(7)
        self.audit_table.setHorizontalHeaderLabels([
            "Zeitpunkt", "Benutzer", "Aktion", "Resource", "ID", "Änderungen", "IP"
        ])
        self.audit_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.audit_table.setStyleSheet("""
            QTableWidget {
                background: #1e2530;
                border: none;
                color: white;
                border-radius: 12px;
            }
            QHeaderView::section {
                background: #374151;
                color: white;
                padding: 10px;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        layout.addWidget(self.audit_table)
        
        return widget
    
    def setup_refresh_timer(self):
        """Setzt den Auto-Refresh-Timer"""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(60000)  # Alle 60 Sekunden
    
    def get_selected_days(self) -> int:
        """Gibt die ausgewählten Tage zurück"""
        index = self.period_combo.currentIndex()
        days_map = {0: 1, 1: 7, 2: 30, 3: 90}
        return days_map.get(index, 7)
    
    def load_data(self):
        """Lädt alle Dashboard-Daten"""
        try:
            self.load_overview_data()
            self.load_performance_data()
            self.load_errors()
            self.load_health_data()
            self.load_activity_data()
        except Exception as e:
            print(f"Fehler beim Laden der Telemetrie-Daten: {e}")
    
    def load_overview_data(self):
        """Lädt Übersichtsdaten"""
        try:
            from app.services.telemetry_service import get_telemetry
            telemetry = get_telemetry()
            
            days = self.get_selected_days()
            metrics = telemetry.get_dashboard_metrics(days=days)
            
            # Cards aktualisieren
            event_total = sum(metrics.get('event_counts', {}).values())
            self.events_card.update_value(str(event_total))
            self.errors_card.update_value(str(metrics.get('error_count', 0)))
            self.sessions_card.update_value(str(metrics.get('active_sessions', 0)))
            
            # Top Features Chart
            features = metrics.get('top_features', [])
            if features:
                categories = [f['name'][:15] for f in features[:5]]
                values = [f['count'] for f in features[:5]]
                self.features_chart.set_bar_data(categories, values, "Nutzung")
                
        except Exception as e:
            print(f"Fehler beim Laden der Übersichtsdaten: {e}")
    
    def load_performance_data(self):
        """Lädt Performance-Daten"""
        try:
            from app.services.telemetry_service import get_telemetry
            telemetry = get_telemetry()
            
            days = self.get_selected_days()
            stats = telemetry.get_performance_stats(days=days)
            
            self.avg_response_card.update_value(f"{stats.get('avg_duration_ms', 0):.0f} ms")
            self.max_response_card.update_value(f"{stats.get('max_duration_ms', 0):.0f} ms")
            self.request_count_card.update_value(str(stats.get('request_count', 0)))
            self.performance_card.update_value(f"{stats.get('avg_duration_ms', 0):.0f} ms")
            
        except Exception as e:
            print(f"Fehler beim Laden der Performance-Daten: {e}")
    
    def load_errors(self):
        """Lädt Fehler-Daten"""
        try:
            from app.services.telemetry_service import get_telemetry
            telemetry = get_telemetry()
            
            days = self.get_selected_days()
            errors = telemetry.get_error_summary(days=days)
            
            self.error_list.set_errors(errors)
            self.total_errors_card.update_value(str(len(errors)))
            
            unresolved = sum(1 for e in errors if not e.get('is_resolved'))
            self.unresolved_errors_card.update_value(str(unresolved))
            
        except Exception as e:
            print(f"Fehler beim Laden der Fehler: {e}")
    
    def load_health_data(self):
        """Lädt System-Health-Daten"""
        try:
            from app.services.telemetry_service import get_telemetry
            telemetry = get_telemetry()
            
            health = telemetry.check_system_health()
            
            # Health-Indikatoren aktualisieren
            cpu_data = health.get('checks', {}).get('cpu', {})
            self.cpu_health.set_status(
                cpu_data.get('status', 'unknown'),
                f"{cpu_data.get('value', 0):.1f}%"
            )
            self.cpu_card.update_value(f"{cpu_data.get('value', 0):.1f}%")
            
            memory_data = health.get('checks', {}).get('memory', {})
            self.memory_health.set_status(
                memory_data.get('status', 'unknown'),
                f"{memory_data.get('value', 0):.1f}%"
            )
            self.memory_card.update_value(f"{memory_data.get('value', 0):.1f}%")
            
            disk_data = health.get('checks', {}).get('disk', {})
            self.disk_health.set_status(
                disk_data.get('status', 'unknown'),
                f"{disk_data.get('value', 0):.1f}%"
            )
            self.disk_card.update_value(f"{disk_data.get('value', 0):.1f}%")
            
            db_data = health.get('checks', {}).get('database', {})
            self.db_health.set_status(
                db_data.get('status', 'unknown'),
                f"{db_data.get('latency_ms', 0):.0f}ms" if db_data.get('latency_ms') else ""
            )
            
        except Exception as e:
            print(f"Fehler beim Laden der Health-Daten: {e}")
    
    def load_activity_data(self):
        """Lädt Aktivitätsdaten"""
        # Placeholder - würde echte Daten aus der DB laden
        pass
    
    def load_audit_logs(self):
        """Lädt Audit-Logs"""
        # Placeholder - würde echte Daten aus der DB laden
        pass
