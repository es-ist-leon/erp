"""
HolzbauERP - Main Application Entry Point
Optimized for fast startup
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    # Lazy import Qt - only when needed
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    
    # High DPI support is enabled by default in PyQt6
    app = QApplication(sys.argv)
    app.setApplicationName("HolzbauERP")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("HolzbauERP")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Load stylesheet (minimal blocking)
    style_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "main.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    
    # Import database service only when needed
    from app.services.database_service import DatabaseService
    
    # Initialize database with connection pooling
    db_service = DatabaseService()
    if not db_service.connect():
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Datenbankfehler", 
                           "Konnte keine Verbindung zur Datenbank herstellen.\n"
                           "Bitte prüfen Sie die Verbindungseinstellungen.")
        sys.exit(1)
    
    # Initialize telemetry system
    try:
        from app.services.telemetry_service import init_telemetry
        telemetry = init_telemetry(db_service)
        telemetry.track_event("app_started", data={"version": "1.0.0"})
    except Exception as e:
        print(f"Telemetry initialization failed: {e}")
    
    # Initialize tables (optimized - skips if already exists)
    db_service.create_tables()
    
    # Import auth service only when needed
    from app.services.auth_service import AuthService
    from app.ui.windows.login_window import LoginWindow
    
    # Show login window
    auth_service = AuthService(db_service)
    login = LoginWindow(auth_service)
    
    if login.exec() == 1:  # Login successful
        # Import main window only after successful login
        from app.ui.windows.main_window import MainWindow
        
        # Track login in telemetry
        try:
            telemetry.set_context(
                user_id=str(auth_service.current_user.id),
                tenant_id=str(auth_service.current_user.tenant_id) if auth_service.current_user.tenant_id else None
            )
            telemetry.track_event("user_login", data={"username": auth_service.current_user.username})
        except Exception:
            pass
        
        # Show main window
        main_window = MainWindow(db_service, auth_service.current_user)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
