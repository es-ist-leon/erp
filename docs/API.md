# HolzbauERP - API-Dokumentation

## Übersicht

Diese Dokumentation beschreibt die internen Service-APIs von HolzbauERP.

---

## 1. DatabaseService

Zentraler Service für Datenbankoperationen.

### 1.1 Initialisierung

```python
from app.services.database_service import DatabaseService

db_service = DatabaseService(connection_string)
```

### 1.2 Methoden

#### get_session()

Context Manager für Datenbank-Sessions.

```python
with db_service.get_session() as session:
    customers = session.query(Customer).all()
```

**Returns:** SQLAlchemy Session

---

#### create(model_class, **data)

Erstellt einen neuen Datensatz.

```python
customer = db_service.create(Customer,
    last_name="Mustermann",
    first_name="Max",
    email="max@example.de",
    tenant_id=tenant_id
)
```

**Parameters:**
- `model_class`: SQLAlchemy Model-Klasse
- `**data`: Felddaten

**Returns:** Erstelltes Objekt

---

#### get_by_id(model_class, id, tenant_id=None)

Lädt einen Datensatz per ID.

```python
customer = db_service.get_by_id(Customer, customer_id, tenant_id)
```

**Parameters:**
- `model_class`: SQLAlchemy Model-Klasse
- `id`: UUID des Datensatzes
- `tenant_id`: Optional, für Tenant-Filterung

**Returns:** Objekt oder None

---

#### get_all(model_class, tenant_id, **filters)

Lädt alle Datensätze mit optionalen Filtern.

```python
customers = db_service.get_all(Customer, tenant_id, status="ACTIVE")
```

**Parameters:**
- `model_class`: SQLAlchemy Model-Klasse
- `tenant_id`: Mandanten-ID
- `**filters`: Optionale Filterkriterien

**Returns:** Liste von Objekten

---

#### update(model_class, id, tenant_id, **data)

Aktualisiert einen Datensatz.

```python
db_service.update(Customer, customer_id, tenant_id,
    email="neu@example.de",
    phone="+49 123 456789"
)
```

**Parameters:**
- `model_class`: SQLAlchemy Model-Klasse
- `id`: UUID des Datensatzes
- `tenant_id`: Mandanten-ID
- `**data`: Zu aktualisierende Felder

**Returns:** Aktualisiertes Objekt

---

#### delete(model_class, id, tenant_id, soft=True)

Löscht einen Datensatz (standardmäßig Soft-Delete).

```python
# Soft Delete (Standard)
db_service.delete(Customer, customer_id, tenant_id)

# Hard Delete
db_service.delete(Customer, customer_id, tenant_id, soft=False)
```

**Parameters:**
- `model_class`: SQLAlchemy Model-Klasse
- `id`: UUID des Datensatzes
- `tenant_id`: Mandanten-ID
- `soft`: True = Soft-Delete, False = permanentes Löschen

**Returns:** Boolean (Erfolg)

---

#### search(model_class, tenant_id, search_term, fields)

Volltextsuche über mehrere Felder.

```python
results = db_service.search(Customer, tenant_id, "Mustermann", 
    ["last_name", "first_name", "company_name", "email"]
)
```

**Parameters:**
- `model_class`: SQLAlchemy Model-Klasse
- `tenant_id`: Mandanten-ID
- `search_term`: Suchbegriff
- `fields`: Liste der zu durchsuchenden Felder

**Returns:** Liste von Objekten

---

## 2. AuthService

Service für Authentifizierung und Autorisierung.

### 2.1 Initialisierung

```python
from app.services.auth_service import AuthService

auth_service = AuthService(db_service)
```

### 2.2 Methoden

#### authenticate(email, password)

Authentifiziert einen Benutzer.

```python
user = auth_service.authenticate("admin@demo.de", "password123")
if user:
    print(f"Angemeldet als {user.username}")
else:
    print("Anmeldung fehlgeschlagen")
```

**Parameters:**
- `email`: E-Mail-Adresse
- `password`: Passwort (Klartext)

**Returns:** User-Objekt oder None

---

#### logout()

Meldet den aktuellen Benutzer ab.

```python
auth_service.logout()
```

---

#### get_current_user()

Gibt den aktuell angemeldeten Benutzer zurück.

```python
user = auth_service.get_current_user()
```

**Returns:** User-Objekt oder None

---

#### has_permission(permission)

Prüft, ob der aktuelle Benutzer eine Berechtigung hat.

```python
if auth_service.has_permission("customer:create"):
    # Kunde anlegen erlaubt
    pass
```

**Parameters:**
- `permission`: Berechtigungs-String

**Returns:** Boolean

---

#### change_password(user_id, old_password, new_password)

Ändert das Passwort eines Benutzers.

```python
success = auth_service.change_password(
    user_id,
    "altes_passwort",
    "neues_sicheres_passwort"
)
```

**Parameters:**
- `user_id`: UUID des Benutzers
- `old_password`: Aktuelles Passwort
- `new_password`: Neues Passwort

**Returns:** Boolean (Erfolg)

---

#### reset_password(user_id, new_password)

Setzt das Passwort zurück (Admin-Funktion).

```python
auth_service.reset_password(user_id, "neues_passwort")
```

**Parameters:**
- `user_id`: UUID des Benutzers
- `new_password`: Neues Passwort

**Returns:** Boolean (Erfolg)

---

## 3. TelemetryService

Service für Telemetrie und Monitoring.

### 3.1 Initialisierung

```python
from app.services.telemetry_service import TelemetryService

telemetry = TelemetryService(db_service, user_id, tenant_id)
```

### 3.2 Methoden

#### track_event(event_type, data)

Erfasst ein Ereignis.

```python
telemetry.track_event("customer_created", {
    "customer_id": str(customer.id),
    "customer_type": customer.customer_type
})
```

**Parameters:**
- `event_type`: Ereignistyp als String
- `data`: Dictionary mit Ereignisdaten

---

#### track_performance(operation, duration_ms)

Erfasst eine Performance-Metrik.

```python
import time

start = time.time()
# Operation durchführen
duration_ms = (time.time() - start) * 1000

telemetry.track_performance("load_customers", duration_ms)
```

**Parameters:**
- `operation`: Name der Operation
- `duration_ms`: Dauer in Millisekunden

---

#### track_error(exception, context=None)

Erfasst einen Fehler.

```python
try:
    risky_operation()
except Exception as e:
    telemetry.track_error(e, {
        "module": "customer",
        "action": "save"
    })
```

**Parameters:**
- `exception`: Exception-Objekt
- `context`: Optionales Dictionary mit Kontext

---

#### track_navigation(module_name)

Erfasst einen Modulwechsel.

```python
telemetry.track_navigation("customers")
```

**Parameters:**
- `module_name`: Name des Moduls

---

#### get_metrics(start_date, end_date, metric_type=None)

Lädt Metriken für einen Zeitraum.

```python
metrics = telemetry.get_metrics(
    datetime(2025, 12, 1),
    datetime(2025, 12, 31),
    metric_type="performance"
)
```

**Parameters:**
- `start_date`: Startdatum
- `end_date`: Enddatum
- `metric_type`: Optional, Filterung nach Typ

**Returns:** Liste von Metriken

---

## 4. FileStorageService

Service für Datei-Upload und -Download mit MongoDB GridFS.

### 4.1 Initialisierung

```python
from app.services.file_storage_service import FileStorageService

file_service = FileStorageService(tenant_id)
```

### 4.2 Methoden

#### upload_file(file_path, entity_type, entity_id)

Lädt eine Datei hoch.

```python
file_id = file_service.upload_file(
    file_path="C:/temp/foto.jpg",
    entity_type="defect",
    entity_id=defect_id
)
```

**Parameters:**
- `file_path`: Pfad zur Datei
- `entity_type`: Verknüpfter Typ (defect, project, etc.)
- `entity_id`: UUID der verknüpften Entität

**Returns:** MongoDB ObjectId der Datei

---

#### get_file(file_id)

Lädt eine Datei herunter.

```python
file_data, filename, content_type = file_service.get_file(file_id)
```

**Parameters:**
- `file_id`: MongoDB ObjectId

**Returns:** Tuple (bytes, filename, content_type)

---

#### delete_file(file_id)

Löscht eine Datei.

```python
file_service.delete_file(file_id)
```

---

#### get_files_for_entity(entity_type, entity_id)

Lädt alle Dateien einer Entität.

```python
files = file_service.get_files_for_entity("defect", defect_id)
for f in files:
    print(f['filename'], f['file_size'])
```

**Returns:** Liste von Datei-Metadaten

---

## 5. BankingService

Service für FinTS/HBCI Banking-Integration.

### 5.1 Initialisierung

```python
from app.services.banking_service import BankingService

banking_service = BankingService(tenant_id)
```

### 5.2 Methoden

#### connect_bank(blz, username, pin)

Verbindet ein Bankkonto.

```python
account = banking_service.connect_bank(
    blz="70150000",
    username="max.mustermann",
    pin="secure_pin"
)
```

**Parameters:**
- `blz`: Bankleitzahl
- `username`: Online-Banking Benutzername
- `pin`: PIN

**Returns:** BankAccount-Objekt

---

#### sync_transactions(account_id)

Synchronisiert Transaktionen.

```python
transactions = banking_service.sync_transactions(account_id)
```

**Returns:** Liste neuer Transaktionen

---

#### get_balance(account_id)

Ruft aktuellen Kontostand ab.

```python
balance = banking_service.get_balance(account_id)
print(f"Kontostand: {balance} EUR")
```

**Returns:** Decimal

---

## 6. MLService

Service für Machine Learning Vorhersagen.

### 6.1 Initialisierung

```python
from app.services.ml_service import MLService

ml_service = MLService(db_service, tenant_id)
```

### 6.2 Methoden

#### predict_project_cost(project_data)

Prognostiziert Projektkosten.

```python
prediction = ml_service.predict_project_cost({
    'project_type': 'NEUBAU',
    'gross_floor_area': 250,
    'floors_above_ground': 2,
    'wood_volume_m3': 80
})
print(f"Geschätzte Kosten: {prediction['cost']} EUR")
print(f"Konfidenz: {prediction['confidence']*100}%")
```

**Returns:** Dict mit cost, confidence, range_min, range_max

---

#### predict_defect_probability(project_id)

Berechnet Mängelwahrscheinlichkeit.

```python
risk = ml_service.predict_defect_probability(project_id)
if risk['probability'] > 0.7:
    print("Hohes Mängelrisiko!")
```

**Returns:** Dict mit probability, factors

---

#### analyze_customer_value(customer_id)

Analysiert Kundenwert.

```python
analysis = ml_service.analyze_customer_value(customer_id)
print(f"Lifetime Value: {analysis['ltv']} EUR")
print(f"Zahlungsmoral: {analysis['payment_score']}")
```

**Returns:** Dict mit ltv, payment_score, churn_risk

---

## 7. Datenmodelle

### 4.1 Customer (Kunde)

```python
class Customer:
    # Identifikation
    id: UUID
    customer_number: str           # z.B. "K000001"
    tenant_id: UUID
    
    # Typ und Status
    customer_type: CustomerType    # PRIVATE, BUSINESS
    status: CustomerStatus         # ACTIVE, INACTIVE, BLOCKED
    
    # Firmendaten (bei Geschäftskunden)
    company_name: str
    tax_id: str                    # USt-IdNr.
    trade_register: str
    
    # Kontaktperson
    salutation: str
    first_name: str
    last_name: str
    
    # Kontakt
    email: str
    phone: str
    mobile: str
    website: str
    
    # Adresse
    street: str
    street_number: str
    postal_code: str
    city: str
    country: str
    latitude: Decimal
    longitude: Decimal
    
    # Zahlungsdaten
    payment_terms: int             # Zahlungsziel in Tagen
    credit_limit: Decimal
    discount_percent: Decimal
    bank_name: str
    iban: str
    bic: str
    
    # Metadaten
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
```

### 4.2 Project (Projekt)

```python
class Project:
    # Identifikation
    id: UUID
    project_number: str            # z.B. "P2025-0001"
    tenant_id: UUID
    customer_id: UUID
    
    # Grunddaten
    name: str
    description: str
    project_type: ProjectType      # NEWBUILD, EXTENSION, RENOVATION
    status: ProjectStatus          # PLANNING, ACTIVE, COMPLETED
    priority: ProjectPriority      # LOW, MEDIUM, HIGH, CRITICAL
    
    # Standort
    street: str
    postal_code: str
    city: str
    latitude: Decimal
    longitude: Decimal
    altitude: Decimal              # Höhe über NN
    
    # Baurechtliche Daten
    plot_number: str               # Flurstück
    land_registry: str             # Gemarkung
    building_permit_number: str
    building_permit_date: date
    
    # Zeitplanung
    planned_start: date
    planned_end: date
    actual_start: date
    actual_end: date
    
    # Budget
    budget_total: Decimal
    budget_spent: Decimal
    
    # Beziehungen
    customer: Customer
    tasks: List[Task]
    milestones: List[Milestone]
    documents: List[Document]
```

### 4.3 Material

```python
class Material:
    # Identifikation
    id: UUID
    article_number: str
    tenant_id: UUID
    
    # Grunddaten
    name: str
    description: str
    category: str
    unit: str                      # Stück, m, m², m³, kg
    
    # Technische Daten
    length_mm: Decimal
    width_mm: Decimal
    height_mm: Decimal
    weight_kg: Decimal
    
    # Holzspezifisch
    wood_type: str                 # Fichte, Tanne, Eiche, etc.
    wood_quality: str              # SI, SII, SIII
    moisture_content: Decimal      # Feuchtigkeit in %
    
    # Preise
    purchase_price: Decimal
    selling_price: Decimal
    
    # Lager
    stock_quantity: Decimal
    min_stock: Decimal
    storage_location: str
    
    # Lieferant
    supplier_id: UUID
    supplier_article_number: str
```

### 4.4 Invoice (Rechnung)

```python
class Invoice:
    # Identifikation
    id: UUID
    invoice_number: str            # z.B. "RE202500001"
    tenant_id: UUID
    customer_id: UUID
    project_id: UUID               # Optional
    
    # Status
    status: InvoiceStatus          # DRAFT, SENT, PAID, OVERDUE
    
    # Daten
    invoice_date: date
    due_date: date
    
    # Beträge
    net_amount: Decimal
    tax_amount: Decimal
    gross_amount: Decimal
    discount_amount: Decimal
    
    # Zahlung
    paid_amount: Decimal
    payment_date: date
    payment_method: str
    
    # Positionen
    items: List[InvoiceItem]
```

---

## 8. Enumerationen

### CustomerType
```python
class CustomerType(enum.Enum):
    PRIVATE = "PRIVATE"           # Privatkunde
    BUSINESS = "BUSINESS"         # Geschäftskunde
```

### ProjectStatus
```python
class ProjectStatus(enum.Enum):
    PLANNING = "PLANNING"         # In Planung
    PREPARATION = "PREPARATION"   # In Vorbereitung
    ACTIVE = "ACTIVE"             # Aktiv/Laufend
    ON_HOLD = "ON_HOLD"           # Pausiert
    COMPLETED = "COMPLETED"       # Abgeschlossen
    CANCELLED = "CANCELLED"       # Abgebrochen
```

### InvoiceStatus
```python
class InvoiceStatus(enum.Enum):
    DRAFT = "DRAFT"               # Entwurf
    SENT = "SENT"                 # Versendet
    PARTIALLY_PAID = "PARTIALLY_PAID"  # Teilbezahlt
    PAID = "PAID"                 # Bezahlt
    OVERDUE = "OVERDUE"           # Überfällig
    CANCELLED = "CANCELLED"       # Storniert
```

---

## 9. Fehlerbehandlung

### Exceptions

```python
class HolzbauERPError(Exception):
    """Basis-Exception"""
    pass

class DatabaseError(HolzbauERPError):
    """Datenbankfehler"""
    pass

class AuthenticationError(HolzbauERPError):
    """Authentifizierungsfehler"""
    pass

class AuthorizationError(HolzbauERPError):
    """Autorisierungsfehler (keine Berechtigung)"""
    pass

class ValidationError(HolzbauERPError):
    """Validierungsfehler"""
    pass

class NotFoundError(HolzbauERPError):
    """Datensatz nicht gefunden"""
    pass
```

### Fehlerbehandlung Beispiel

```python
from app.exceptions import *

try:
    customer = db_service.get_by_id(Customer, customer_id, tenant_id)
    if not customer:
        raise NotFoundError(f"Kunde {customer_id} nicht gefunden")
    
    if not auth_service.has_permission("customer:edit"):
        raise AuthorizationError("Keine Berechtigung zum Bearbeiten")
    
    db_service.update(Customer, customer_id, tenant_id, **data)
    
except NotFoundError as e:
    show_error_message(str(e))
except AuthorizationError as e:
    show_error_message("Zugriff verweigert")
except DatabaseError as e:
    telemetry.track_error(e)
    show_error_message("Datenbankfehler")
except Exception as e:
    telemetry.track_error(e)
    show_error_message("Unbekannter Fehler")
```

---

© 2025 HolzbauERP. Alle Rechte vorbehalten.
