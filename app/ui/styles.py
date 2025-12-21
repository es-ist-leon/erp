"""
Modern Salesforce-inspired Design System for HolzbauERP
"""

# Color Palette - Salesforce Lightning Design System inspired
COLORS = {
    # Primary
    "primary": "#0176d3",
    "primary_dark": "#014486",
    "primary_light": "#1b96ff",
    
    # Secondary
    "secondary": "#032d60",
    "secondary_light": "#16325c",
    
    # Accents
    "success": "#2e844a",
    "success_light": "#45c65a",
    "warning": "#dd7a01",
    "warning_light": "#fe9339",
    "error": "#c23934",
    "error_light": "#ea001e",
    "danger": "#c23934",  # Alias for error
    "info": "#0070d2",
    
    # Neutrals
    "white": "#ffffff",
    "gray_50": "#f3f3f3",
    "gray_100": "#e5e5e5",
    "gray_200": "#c9c9c9",
    "gray_300": "#aeaeae",
    "gray_400": "#939393",
    "gray_500": "#706e6b",
    "gray_600": "#514f4d",
    "gray_700": "#3e3e3c",
    "gray_800": "#2b2826",
    "gray_900": "#181818",
    
    # Background
    "bg_primary": "#f3f3f3",
    "bg_secondary": "#ffffff",
    "bg_dark": "#032d60",
    
    # Text
    "text_primary": "#181818",
    "text_secondary": "#706e6b",
    "text_inverse": "#ffffff",
    "text_link": "#0176d3",
}

# Shadows
SHADOWS = {
    "small": "0 2px 4px rgba(0, 0, 0, 0.1)",
    "medium": "0 4px 8px rgba(0, 0, 0, 0.12)",
    "large": "0 8px 16px rgba(0, 0, 0, 0.15)",
    "card": "0 2px 8px rgba(0, 0, 0, 0.08)",
}

# Border Radius
RADIUS = {
    "small": "4px",
    "medium": "8px",
    "large": "12px",
    "xl": "16px",
    "round": "50%",
}

# Global Application Stylesheet
GLOBAL_STYLE = """
/* ============================================
   GLOBAL STYLES - Salesforce Lightning Design
   ============================================ */

* {
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}

QMainWindow, QDialog {
    background-color: #f3f3f3;
}

/* ============================================
   BUTTONS
   ============================================ */

QPushButton {
    font-size: 13px;
    font-weight: 600;
    padding: 10px 16px;
    border-radius: 4px;
    border: none;
    min-height: 32px;
}

QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0176d3, stop:1 #014486);
    color: white;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1b96ff, stop:1 #0176d3);
}

QPushButton#primaryButton:pressed {
    background: #014486;
}

QPushButton#secondaryButton {
    background: white;
    color: #0176d3;
    border: 1px solid #0176d3;
}

QPushButton#secondaryButton:hover {
    background: #f3f3f3;
}

QPushButton#destructiveButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #c23934, stop:1 #8e2622);
    color: white;
}

QPushButton#destructiveButton:hover {
    background: #ea001e;
}

QPushButton#neutralButton {
    background: white;
    color: #706e6b;
    border: 1px solid #c9c9c9;
}

QPushButton#neutralButton:hover {
    background: #f3f3f3;
    border-color: #aeaeae;
}

/* ============================================
   INPUT FIELDS
   ============================================ */

QLineEdit, QTextEdit, QPlainTextEdit {
    padding: 10px 12px;
    border: 1px solid #c9c9c9;
    border-radius: 4px;
    background: white;
    font-size: 13px;
    color: #181818;
    selection-background-color: #0176d3;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #0176d3;
    padding: 9px 11px;
    outline: none;
}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {
    border-color: #aeaeae;
}

QLineEdit:disabled, QTextEdit:disabled {
    background: #f3f3f3;
    color: #aeaeae;
}

QLineEdit::placeholder {
    color: #706e6b;
}

/* ============================================
   COMBO BOX
   ============================================ */

QComboBox {
    padding: 10px 12px;
    border: 1px solid #c9c9c9;
    border-radius: 4px;
    background: white;
    font-size: 13px;
    color: #181818;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #aeaeae;
}

QComboBox:focus {
    border: 2px solid #0176d3;
    padding: 9px 11px;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #706e6b;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: white;
    border: 1px solid #c9c9c9;
    border-radius: 4px;
    selection-background-color: #0176d3;
    selection-color: white;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:hover {
    background: #f3f3f3;
}

/* ============================================
   SPIN BOX
   ============================================ */

QSpinBox, QDoubleSpinBox {
    padding: 10px 12px;
    border: 1px solid #c9c9c9;
    border-radius: 4px;
    background: white;
    font-size: 13px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #0176d3;
}

/* ============================================
   DATE EDIT
   ============================================ */

QDateEdit, QDateTimeEdit {
    padding: 10px 12px;
    border: 1px solid #c9c9c9;
    border-radius: 4px;
    background: white;
    font-size: 13px;
}

QDateEdit:focus, QDateTimeEdit:focus {
    border: 2px solid #0176d3;
}

QDateEdit::drop-down, QDateTimeEdit::drop-down {
    border: none;
    padding-right: 10px;
}

/* ============================================
   CHECK BOX & RADIO BUTTON
   ============================================ */

QCheckBox {
    font-size: 13px;
    color: #181818;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #c9c9c9;
    border-radius: 4px;
    background: white;
}

QCheckBox::indicator:hover {
    border-color: #0176d3;
}

QCheckBox::indicator:checked {
    background: #0176d3;
    border-color: #0176d3;
}

QRadioButton {
    font-size: 13px;
    color: #181818;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #c9c9c9;
    border-radius: 9px;
    background: white;
}

QRadioButton::indicator:checked {
    background: white;
    border: 6px solid #0176d3;
}

/* ============================================
   TABLES
   ============================================ */

QTableWidget, QTableView {
    background-color: white;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    gridline-color: #f3f3f3;
    selection-background-color: #e5f1fb;
    selection-color: #181818;
    font-size: 13px;
}

QTableWidget::item, QTableView::item {
    padding: 12px 16px;
    border-bottom: 1px solid #f3f3f3;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #e5f1fb;
    color: #181818;
}

QTableWidget::item:hover, QTableView::item:hover {
    background-color: #f3f3f3;
}

QHeaderView::section {
    background: #fafbfc;
    padding: 12px 16px;
    border: none;
    border-bottom: 2px solid #e5e5e5;
    font-weight: 700;
    font-size: 11px;
    color: #706e6b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QHeaderView::section:hover {
    background: #f3f3f3;
}

/* ============================================
   SCROLL BARS
   ============================================ */

QScrollBar:vertical {
    background: #f3f3f3;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #c9c9c9;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #aeaeae;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #f3f3f3;
    height: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #c9c9c9;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #aeaeae;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ============================================
   TAB WIDGET
   ============================================ */

QTabWidget::pane {
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    background: white;
    margin-top: -1px;
}

QTabBar::tab {
    background: #f3f3f3;
    border: 1px solid #e5e5e5;
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    color: #706e6b;
}

QTabBar::tab:selected {
    background: white;
    color: #0176d3;
    border-bottom: 2px solid #0176d3;
}

QTabBar::tab:hover:!selected {
    background: #e5e5e5;
}

/* ============================================
   GROUP BOX
   ============================================ */

QGroupBox {
    font-weight: 700;
    font-size: 14px;
    color: #181818;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    background: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0 8px;
    background: white;
}

/* ============================================
   LABELS
   ============================================ */

QLabel {
    color: #181818;
    font-size: 13px;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
    color: #181818;
    padding: 8px 0;
}

QLabel#fieldLabel {
    font-size: 12px;
    font-weight: 600;
    color: #706e6b;
    margin-bottom: 4px;
}

QLabel#errorLabel {
    color: #c23934;
    font-size: 12px;
}

QLabel#successLabel {
    color: #2e844a;
    font-size: 12px;
}

/* ============================================
   MESSAGE BOX
   ============================================ */

QMessageBox {
    background: white;
}

QMessageBox QLabel {
    color: #181818;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ============================================
   TOOLTIPS
   ============================================ */

QToolTip {
    background: #181818;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 12px;
}

/* ============================================
   MENU
   ============================================ */

QMenu {
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 4px 0;
}

QMenu::item {
    padding: 8px 16px;
    color: #181818;
}

QMenu::item:selected {
    background: #e5f1fb;
    color: #0176d3;
}

QMenu::separator {
    height: 1px;
    background: #e5e5e5;
    margin: 4px 0;
}

QMenuBar {
    background: white;
    border-bottom: 1px solid #e5e5e5;
    padding: 4px;
}

QMenuBar::item {
    padding: 8px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: #e5f1fb;
}

/* ============================================
   PROGRESS BAR
   ============================================ */

QProgressBar {
    background: #e5e5e5;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0176d3, stop:1 #1b96ff);
    border-radius: 4px;
}

/* ============================================
   SPLITTER
   ============================================ */

QSplitter::handle {
    background: #e5e5e5;
}

QSplitter::handle:hover {
    background: #0176d3;
}

/* ============================================
   STATUS BAR
   ============================================ */

QStatusBar {
    background: white;
    border-top: 1px solid #e5e5e5;
    color: #706e6b;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}
"""

# Component-specific styles
SIDEBAR_STYLE = """
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #032d60, stop:1 #014486);
}

QFrame#sidebarBrand {
    background: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

QPushButton#sidebarButton {
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 0;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    background: transparent;
    margin: 2px 8px;
    border-radius: 8px;
}

QPushButton#sidebarButton:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

QPushButton#sidebarButton:checked {
    background: rgba(255, 255, 255, 0.15);
    color: white;
    font-weight: bold;
    border-left: 3px solid #1b96ff;
}
"""

CARD_STYLE = """
QFrame#card {
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
}

QFrame#card:hover {
    border-color: #0176d3;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
"""

STAT_CARD_STYLE = """
QFrame#statCard {
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 12px;
    padding: 20px;
}

QFrame#statCard:hover {
    border-color: #0176d3;
}
"""

HEADER_STYLE = """
QFrame#header {
    background: white;
    border-bottom: 1px solid #e5e5e5;
}
"""

LOGIN_STYLE = """
QFrame#loginCard {
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e5e5;
}

QFrame#loginHeader {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #032d60, stop:1 #0176d3);
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}
"""

DIALOG_STYLE = """
QDialog {
    background: #f3f3f3;
}

QDialog QFrame#dialogContent {
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
}
"""

# Badge/Tag styles for status indicators
def get_status_badge_style(status_type: str) -> str:
    """Get style for status badges"""
    colors = {
        "success": ("#2e844a", "#e3f3e8"),
        "warning": ("#dd7a01", "#fef3e0"),
        "error": ("#c23934", "#fce4e4"),
        "info": ("#0176d3", "#e5f1fb"),
        "neutral": ("#706e6b", "#f3f3f3"),
    }
    
    fg, bg = colors.get(status_type, colors["neutral"])
    
    return f"""
        QLabel {{
            background: {bg};
            color: {fg};
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }}
    """


def get_button_style(button_type: str = "primary") -> str:
    """Get button style by type"""
    styles = {
        "primary": """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0176d3, stop:1 #014486);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1b96ff, stop:1 #0176d3);
            }
            QPushButton:pressed {
                background: #014486;
            }
            QPushButton:disabled {
                background: #c9c9c9;
                color: #706e6b;
            }
        """,
        "secondary": """
            QPushButton {
                background: white;
                color: #0176d3;
                border: 1px solid #0176d3;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #e5f1fb;
            }
            QPushButton:pressed {
                background: #cce4f7;
            }
        """,
        "destructive": """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c23934, stop:1 #8e2622);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #ea001e;
            }
        """,
        "success": """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e844a, stop:1 #1c5a2f);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #45c65a;
            }
        """,
        "neutral": """
            QPushButton {
                background: white;
                color: #706e6b;
                border: 1px solid #c9c9c9;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #f3f3f3;
                border-color: #aeaeae;
            }
        """,
        "icon": """
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                color: #706e6b;
            }
            QPushButton:hover {
                background: #f3f3f3;
                color: #181818;
            }
        """,
    }
    return styles.get(button_type, styles["primary"])


def get_input_style() -> str:
    """Get input field style"""
    return """
        QLineEdit {
            padding: 12px 16px;
            border: 1px solid #c9c9c9;
            border-radius: 4px;
            background: white;
            font-size: 14px;
            color: #181818;
        }
        QLineEdit:focus {
            border: 2px solid #0176d3;
            padding: 11px 15px;
        }
        QLineEdit:hover {
            border-color: #aeaeae;
        }
        QLineEdit::placeholder {
            color: #aeaeae;
        }
    """


def get_table_style() -> str:
    """Get modern table style"""
    return """
        QTableWidget {
            background-color: white;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            gridline-color: transparent;
            selection-background-color: #e5f1fb;
            selection-color: #181818;
            outline: none;
        }
        QTableWidget::item {
            padding: 12px 16px;
            border-bottom: 1px solid #f3f3f3;
        }
        QTableWidget::item:selected {
            background-color: #e5f1fb;
            color: #181818;
        }
        QTableWidget::item:hover {
            background-color: #fafbfc;
        }
        QHeaderView::section {
            background: #fafbfc;
            padding: 14px 16px;
            border: none;
            border-bottom: 2px solid #e5e5e5;
            font-weight: 700;
            font-size: 11px;
            color: #706e6b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        QHeaderView::section:first {
            border-top-left-radius: 8px;
        }
        QHeaderView::section:last {
            border-top-right-radius: 8px;
        }
    """
