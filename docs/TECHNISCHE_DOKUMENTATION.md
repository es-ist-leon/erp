# HolzbauERP - Technische Dokumentation

## Inhaltsverzeichnis

1. [Architekturübersicht](#1-architekturübersicht)
2. [Projektstruktur](#2-projektstruktur)
3. [Datenmodelle](#3-datenmodelle)
4. [Services](#4-services)
5. [UI-Komponenten](#5-ui-komponenten)
6. [Sicherheit](#6-sicherheit)
7. [Performance](#7-performance)
8. [Telemetrie](#8-telemetrie)

---

## 1. Architekturübersicht

### 1.1 Systemarchitektur

```
┌─────────────────────────────────────────────────────────────┐
│                    HolzbauERP Client                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   PyQt6 UI Layer                      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │
│  │  │Dashboard│ │ Kunden  │ │Projekte │ │Material │    │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │
│  │  │Finanzen │ │Personal │ │Fuhrpark │ │Qualität │    │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Service Layer                       │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │  │
│  │  │ AuthService│ │ DBService  │ │TelemetryS. │        │  │
│  │  └────────────┘ └────────────┘ └────────────┘        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Data Access Layer (SQLAlchemy)           │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │          Connection Pooling & Caching           │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SSL/TLS
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Tenants │ │  Users  │ │Projects │ │Materials│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Customers│ │Invoices │ │Employees│ │ Vehicles│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Design-Prinzipien

- **Multi-Tenant-Architektur:** Datenisolierung auf Datenbankebene
- **Soft-Delete:** Daten werden nicht physisch gelöscht
- **Audit-Trail:** Alle Änderungen werden protokolliert
- **Lazy Loading:** Daten werden bei Bedarf geladen
- **Connection Pooling:** Effiziente Datenbankverbindungen
- **Caching:** LRU-Cache für häufig verwendete Daten

### 1.3 Technologie-Stack

| Komponente | Technologie | Version |
|------------|-------------|---------|
| Programmiersprache | Python | 3.12+ |
| UI-Framework | PyQt6 | 6.6+ |
| ORM | SQLAlchemy | 2.0+ |
| Datenbank | PostgreSQL | 15+ |
| Passwort-Hashing | passlib (bcrypt) | 1.7+ |
| Telemetrie | Custom Implementation | 1.0 |

---

## 2. Projektstruktur

```
erp/
├── app/                          # Anwendungscode
│   ├── main.py                   # Einstiegspunkt
│   ├── controllers/              # Business Logic
│   ├── services/                 # Service Layer
│   │   ├── auth_service.py       # Authentifizierung
│   │   ├── database_service.py   # Datenbankzugriff
│   │   └── telemetry_service.py  # Telemetrie
│   ├── ui/                       # User Interface
│   │   ├── dialogs/              # Dialogfenster
│   │   ├── widgets/              # Wiederverwendbare Widgets
│   │   ├── windows/              # Hauptfenster
│   │   └── styles.py             # Stylesheet-Definitionen
│   └── resources/                # Statische Ressourcen
│
├── shared/                       # Gemeinsam genutzte Module
│   ├── config.py                 # Konfiguration
│   ├── database/                 # Datenbankverbindung
│   │   └── connection.py         # Connection Management
│   ├── models/                   # SQLAlchemy Models
│   │   ├── base.py               # Basis-Mixins
│   │   ├── auth.py               # User, Role, Permission
│   │   ├── customer.py           # Kundenverwaltung
│   │   ├── project.py            # Projektverwaltung
│   │   ├── construction.py       # Bautagebuch
│   │   ├── inventory.py          # Materialwirtschaft
│   │   ├── finance.py            # Finanzverwaltung
│   │   ├── accounting.py         # Buchhaltung
│   │   ├── payroll.py            # Lohnabrechnung
│   │   ├── employee.py           # Personal
│   │   ├── fleet.py              # Fuhrpark
│   │   ├── quality.py            # Qualität
│   │   ├── crm.py                # CRM
│   │   └── telemetry.py          # Telemetrie
│   └── utils/                    # Hilfsfunktionen
│
├── docs/                         # Dokumentation
├── certs/                        # SSL-Zertifikate
├── venv/                         # Virtuelle Umgebung
├── requirements.txt              # Python-Abhängigkeiten
├── HolzbauERP.bat               # Windows Starter
└── HolzbauERP.ps1               # PowerShell Starter
```

---

## 3. Datenmodelle

### 3.1 Basis-Mixins

```python
# shared/models/base.py

class TimestampMixin:
    """Automatische Zeitstempel für created_at und updated_at"""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SoftDeleteMixin:
    """Soft-Delete Funktionalität"""
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

class TenantMixin:
    """Multi-Tenant Unterstützung"""
    tenant_id = Column(UUID, ForeignKey('tenants.id'), nullable=False)

class AuditMixin:
    """Audit-Trail für Änderungen"""
    created_by = Column(UUID, ForeignKey('users.id'))
    updated_by = Column(UUID, ForeignKey('users.id'))
```

### 3.2 Kernmodelle

#### Tenant (Mandant)
```python
class Tenant(Base):
    __tablename__ = 'tenants'
    
    # Identifikation
    id = Column(UUID, primary_key=True)
    name = Column(String(100), unique=True)
    slug = Column(String(100), unique=True)
    
    # Firmendaten
    company_name = Column(String(200))
    legal_form = Column(String(50))
    tax_id = Column(String(50))
    trade_register = Column(String(100))
    
    # Kontakt
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(255))
    
    # Adresse
    street = Column(String(200))
    postal_code = Column(String(20))
    city = Column(String(100))
    country = Column(String(100))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    
    # Bank
    bank_name = Column(String(100))
    iban = Column(String(34))
    bic = Column(String(11))
    
    # Subscription
    subscription_plan = Column(String(50))
    max_users = Column(Integer)
    is_active = Column(Boolean, default=True)
```

#### User (Benutzer)
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey('tenants.id'))
    
    # Anmeldedaten
    email = Column(String(255), unique=True)
    username = Column(String(100))
    password_hash = Column(String(255))
    
    # Profil
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Beziehungen
    roles = relationship('Role', secondary='user_roles')
```

#### Project (Projekt)
```python
class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey('tenants.id'))
    customer_id = Column(UUID, ForeignKey('customers.id'))
    
    # Grunddaten
    project_number = Column(String(50))
    name = Column(String(200))
    description = Column(Text)
    project_type = Column(Enum(ProjectType))
    status = Column(Enum(ProjectStatus))
    
    # Standort mit vollständigen Geodaten
    street = Column(String(200))
    postal_code = Column(String(20))
    city = Column(String(100))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    altitude = Column(Numeric(8, 2))  # Höhe über NN
    
    # Zeitplanung
    planned_start = Column(Date)
    planned_end = Column(Date)
    actual_start = Column(Date)
    actual_end = Column(Date)
    
    # Budget
    budget_total = Column(Numeric(15, 2))
    budget_spent = Column(Numeric(15, 2))
```

### 3.3 Entity-Relationship-Diagramm

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Tenant  │────<│   User   │     │   Role   │
└──────────┘     └──────────┘>────└──────────┘
      │                │
      │                │
      ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Customer │────<│ Project  │────<│  Task    │
└──────────┘     └──────────┘     └──────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │Bautageb. │  │ Invoice  │  │ Material │
   └──────────┘  └──────────┘  └──────────┘
```

---

## 4. Services

### 4.1 DatabaseService

Zentraler Service für alle Datenbankoperationen:

```python
class DatabaseService:
    def __init__(self, connection_string: str):
        self.engine = create_engine(
            connection_string,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True
        )
        self.Session = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Thread-safe Session Context Manager"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_by_tenant(self, model, tenant_id, **filters):
        """Tenant-gefilterte Abfrage"""
        with self.get_session() as session:
            query = session.query(model).filter(
                model.tenant_id == tenant_id,
                model.is_deleted == False
            )
            for key, value in filters.items():
                query = query.filter(getattr(model, key) == value)
            return query.all()
```

### 4.2 AuthService

Authentifizierung und Autorisierung:

```python
class AuthService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        self.current_user = None
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Benutzer authentifizieren"""
        with self.db_service.get_session() as session:
            user = session.query(User).filter(
                User.email == email,
                User.is_active == True
            ).first()
            
            if user and self.pwd_context.verify(password, user.password_hash):
                user.last_login = datetime.utcnow()
                session.commit()
                
                # Eager load für UI
                session.refresh(user, ['tenant', 'roles'])
                self.current_user = self._detach_user(user)
                return self.current_user
        return None
    
    def has_permission(self, permission: str) -> bool:
        """Berechtigungsprüfung"""
        if not self.current_user:
            return False
        if self.current_user.is_superuser:
            return True
        return permission in self.current_user.permissions
```

### 4.3 TelemetryService

Performance-Monitoring und Fehlererfassung:

```python
class TelemetryService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.metrics_buffer = []
        self.buffer_lock = threading.Lock()
    
    def track_event(self, event_type: str, data: dict):
        """Event erfassen"""
        event = {
            'timestamp': datetime.utcnow(),
            'type': event_type,
            'data': data,
            'session_id': self.session_id
        }
        with self.buffer_lock:
            self.metrics_buffer.append(event)
    
    def track_performance(self, operation: str, duration_ms: float):
        """Performance-Metrik erfassen"""
        self.track_event('performance', {
            'operation': operation,
            'duration_ms': duration_ms
        })
    
    def track_error(self, error: Exception, context: dict = None):
        """Fehler erfassen"""
        self.track_event('error', {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context
        })
```

---

## 5. UI-Komponenten

### 5.1 Architektur

```
UI Layer
├── MainWindow              # Hauptfenster mit Navigation
│   ├── Sidebar             # Navigationsleiste
│   ├── Header              # Kopfzeile mit User-Info
│   └── ContentStack        # Wechselnde Inhalte
│
├── Module (QWidget)
│   ├── DashboardWidget     # Dashboard
│   ├── CustomerWidget      # Kundenverwaltung
│   ├── ProjectWidget       # Projektverwaltung
│   ├── MaterialWidget      # Materialwirtschaft
│   ├── FinanceWidget       # Finanzen
│   └── ...
│
├── Dialogs (QDialog)
│   ├── LoginDialog         # Anmeldung
│   ├── CustomerDialog      # Kunde bearbeiten
│   ├── ProjectDialog       # Projekt bearbeiten
│   └── ...
│
└── Widgets (Wiederverwendbar)
    ├── DataTable           # Tabelle mit Sortierung/Filter
    ├── SearchBar           # Suchfeld
    ├── StatCard            # KPI-Karte
    └── FormFields          # Formular-Elemente
```

### 5.2 Styling

Modernes Salesforce-inspiriertes Design:

```python
# app/ui/styles.py

SALESFORCE_STYLE = """
/* Hauptfarben */
QMainWindow {
    background-color: #f3f3f3;
}

/* Sidebar */
#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a365d, stop:1 #0d1b2a);
    border-right: 1px solid #2d4a6f;
}

/* Karten */
.stat-card {
    background-color: white;
    border-radius: 8px;
    border: 1px solid #e5e5e5;
    padding: 20px;
}

.stat-card:hover {
    border-color: #0176d3;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Buttons */
QPushButton[class="primary"] {
    background-color: #0176d3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton[class="primary"]:hover {
    background-color: #014486;
}

/* Tabellen */
QTableWidget {
    background-color: white;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    gridline-color: #f0f0f0;
}

QTableWidget::item:selected {
    background-color: #e5f2ff;
    color: #0176d3;
}
"""
```

### 5.3 DataTable Widget

Wiederverwendbare Tabelle mit erweiterten Features:

```python
class DataTable(QTableWidget):
    def __init__(self, columns: list, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.setup_table()
    
    def setup_table(self):
        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels([c['label'] for c in self.columns])
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # Header-Styling
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
    
    def load_data(self, data: list):
        """Daten laden mit Batch-Processing"""
        self.setRowCount(0)
        self.setUpdatesEnabled(False)
        
        for row_idx, item in enumerate(data):
            self.insertRow(row_idx)
            for col_idx, col in enumerate(self.columns):
                value = getattr(item, col['field'], '')
                cell = QTableWidgetItem(str(value) if value else '')
                self.setItem(row_idx, col_idx, cell)
        
        self.setUpdatesEnabled(True)
```

---

## 6. Sicherheit

### 6.1 Authentifizierung

- **Passwort-Hashing:** bcrypt mit automatischem Salt
- **Session-Management:** Token-basierte Sessions
- **Brute-Force-Schutz:** Rate-Limiting bei Login

### 6.2 Autorisierung

- **Role-Based Access Control (RBAC)**
- **Tenant-Isolation:** Strenge Datentrennung
- **Permission-System:** Granulare Berechtigungen

```python
# Berechtigungsprüfung
class Permissions:
    # Kunden
    CUSTOMER_VIEW = "customer:view"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_EDIT = "customer:edit"
    CUSTOMER_DELETE = "customer:delete"
    
    # Projekte
    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_EDIT = "project:edit"
    PROJECT_DELETE = "project:delete"
    
    # Finanzen
    FINANCE_VIEW = "finance:view"
    FINANCE_CREATE = "finance:create"
    INVOICE_CREATE = "invoice:create"
```

### 6.3 Datenbankverbindung

- **SSL/TLS:** Verschlüsselte Verbindung
- **Connection Pooling:** Sichere Verbindungsverwaltung
- **Parameterisierte Queries:** SQL-Injection-Schutz

```python
# Sichere Datenbankverbindung
engine = create_engine(
    connection_string,
    connect_args={
        'sslmode': 'require',
        'sslrootcert': 'certs/ca.crt'
    }
)
```

---

## 7. Performance

### 7.1 Datenbankoptimierungen

```python
# Connection Pooling
engine = create_engine(
    connection_string,
    pool_size=10,          # Basis-Poolbröße
    max_overflow=20,       # Zusätzliche Verbindungen bei Bedarf
    pool_timeout=30,       # Timeout für Pool-Akquise
    pool_recycle=1800,     # Verbindungs-Recycling (30 min)
    pool_pre_ping=True     # Verbindungscheck vor Nutzung
)

# Query-Optimierung
session.query(Project).options(
    joinedload(Project.customer),      # Eager Loading
    selectinload(Project.tasks)        # Batch Loading
).filter(...)
```

### 7.2 Caching

```python
from functools import lru_cache

class CachedDataService:
    @lru_cache(maxsize=1000)
    def get_customer(self, customer_id: str):
        """Cached Customer Lookup"""
        return self._fetch_customer(customer_id)
    
    def invalidate_customer_cache(self, customer_id: str):
        """Cache invalidieren"""
        self.get_customer.cache_clear()
```

### 7.3 UI-Performance

- **Lazy Loading:** Daten bei Bedarf laden
- **Virtual Scrolling:** Große Listen effizient anzeigen
- **Batch Updates:** UI-Updates gruppieren

```python
# Batch UI Update
self.setUpdatesEnabled(False)
for item in large_dataset:
    self.add_item(item)
self.setUpdatesEnabled(True)
```

---

## 8. Telemetrie

### 8.1 Erfasste Metriken

| Metrik | Beschreibung |
|--------|--------------|
| `app.startup` | Anwendungsstart |
| `app.login` | Benutzeranmeldung |
| `app.navigation` | Modulwechsel |
| `db.query` | Datenbankabfragen |
| `ui.render` | UI-Renderzeiten |
| `error.exception` | Fehler und Ausnahmen |

### 8.2 Performance-Tracking

```python
@track_performance("load_customers")
def load_customers(self):
    # Automatisch gemessene Ausführungszeit
    return self.db_service.get_all(Customer)
```

### 8.3 Fehlerberichterstattung

```python
try:
    risky_operation()
except Exception as e:
    telemetry.track_error(e, {
        'module': 'customer',
        'action': 'save',
        'user_id': current_user.id
    })
    raise
```

---

## Anhang

### A. Abhängigkeiten

```
# requirements.txt
PyQt6>=6.6.0
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.0
passlib>=1.7.0
bcrypt>=4.0.0
python-dateutil>=2.8.0
```

### B. Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `DATABASE_URL` | Datenbankverbindung | - |
| `DEBUG` | Debug-Modus | `false` |
| `LOG_LEVEL` | Log-Level | `INFO` |

### C. Fehlerbehandlung

```python
class HolzbauERPError(Exception):
    """Basis-Exception für alle Anwendungsfehler"""
    pass

class DatabaseError(HolzbauERPError):
    """Datenbankfehler"""
    pass

class AuthenticationError(HolzbauERPError):
    """Authentifizierungsfehler"""
    pass

class ValidationError(HolzbauERPError):
    """Validierungsfehler"""
    pass
```

---

© 2025 HolzbauERP. Alle Rechte vorbehalten.
