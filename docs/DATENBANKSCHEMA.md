# HolzbauERP - Datenbankschema

## Übersicht

Diese Dokumentation beschreibt alle Datenbanktabellen und deren Beziehungen.

---

## 1. Kernmodule

### 1.1 tenants (Mandanten)

Zentrale Tabelle für Multi-Tenant-Architektur.

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| name | VARCHAR(100) | Eindeutiger Mandantenname |
| slug | VARCHAR(100) | URL-freundlicher Name |
| company_name | VARCHAR(200) | Offizieller Firmenname |
| legal_form | VARCHAR(50) | Rechtsform (GmbH, AG, etc.) |
| founding_date | DATE | Gründungsdatum |
| tax_id | VARCHAR(50) | USt-IdNr. |
| tax_number | VARCHAR(50) | Steuernummer |
| trade_register | VARCHAR(100) | Handelsregisternummer |
| trade_register_court | VARCHAR(100) | Registergericht |
| email | VARCHAR(255) | Haupt-E-Mail |
| phone | VARCHAR(50) | Haupttelefon |
| website | VARCHAR(255) | Webseite |
| street | VARCHAR(200) | Straße |
| street_number | VARCHAR(20) | Hausnummer |
| postal_code | VARCHAR(20) | PLZ |
| city | VARCHAR(100) | Stadt |
| country | VARCHAR(100) | Land |
| latitude | NUMERIC(10,7) | Breitengrad |
| longitude | NUMERIC(10,7) | Längengrad |
| bank_name | VARCHAR(100) | Bankname |
| iban | VARCHAR(34) | IBAN |
| bic | VARCHAR(11) | BIC/SWIFT |
| subscription_plan | VARCHAR(50) | Abo-Plan |
| max_users | INTEGER | Max. Benutzer |
| is_active | BOOLEAN | Aktiv-Status |
| created_at | TIMESTAMP | Erstelldatum |
| updated_at | TIMESTAMP | Änderungsdatum |

---

### 1.2 users (Benutzer)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| email | VARCHAR(255) | E-Mail (eindeutig) |
| username | VARCHAR(100) | Benutzername |
| password_hash | VARCHAR(255) | Passwort-Hash |
| first_name | VARCHAR(100) | Vorname |
| last_name | VARCHAR(100) | Nachname |
| phone | VARCHAR(50) | Telefon |
| mobile | VARCHAR(50) | Mobil |
| avatar_url | VARCHAR(500) | Profilbild-URL |
| is_active | BOOLEAN | Aktiv-Status |
| is_superuser | BOOLEAN | Superuser-Flag |
| last_login | TIMESTAMP | Letzte Anmeldung |
| failed_login_attempts | INTEGER | Fehlversuche |
| locked_until | TIMESTAMP | Sperre bis |
| password_changed_at | TIMESTAMP | Passwort geändert am |
| must_change_password | BOOLEAN | Passwortänderung erforderlich |
| created_at | TIMESTAMP | Erstelldatum |
| updated_at | TIMESTAMP | Änderungsdatum |

---

### 1.3 roles (Rollen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| name | VARCHAR(100) | Rollenname |
| description | TEXT | Beschreibung |
| is_system | BOOLEAN | System-Rolle (nicht löschbar) |
| created_at | TIMESTAMP | Erstelldatum |

---

### 1.4 permissions (Berechtigungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| name | VARCHAR(100) | Berechtigungsname |
| code | VARCHAR(100) | Code (z.B. customer:create) |
| module | VARCHAR(50) | Modul |
| description | TEXT | Beschreibung |

---

### 1.5 user_roles (Benutzer-Rollen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| user_id | UUID | FK → users.id |
| role_id | UUID | FK → roles.id |

---

### 1.6 role_permissions (Rollen-Berechtigungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| role_id | UUID | FK → roles.id |
| permission_id | UUID | FK → permissions.id |

---

## 2. Kundenverwaltung

### 2.1 customers (Kunden)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| customer_number | VARCHAR(50) | Kundennummer |
| customer_type | ENUM | PRIVATE, BUSINESS |
| status | ENUM | ACTIVE, INACTIVE, BLOCKED |
| company_name | VARCHAR(200) | Firmenname |
| tax_id | VARCHAR(50) | USt-IdNr. |
| trade_register | VARCHAR(100) | Handelsregister |
| salutation | VARCHAR(20) | Anrede |
| title | VARCHAR(50) | Titel |
| first_name | VARCHAR(100) | Vorname |
| last_name | VARCHAR(100) | Nachname |
| email | VARCHAR(255) | E-Mail |
| phone | VARCHAR(50) | Telefon |
| mobile | VARCHAR(50) | Mobil |
| fax | VARCHAR(50) | Fax |
| website | VARCHAR(255) | Webseite |
| street | VARCHAR(200) | Straße |
| street_number | VARCHAR(20) | Hausnummer |
| postal_code | VARCHAR(20) | PLZ |
| city | VARCHAR(100) | Stadt |
| state | VARCHAR(100) | Bundesland |
| country | VARCHAR(100) | Land |
| latitude | NUMERIC(10,7) | Breitengrad |
| longitude | NUMERIC(10,7) | Längengrad |
| payment_terms | INTEGER | Zahlungsziel (Tage) |
| credit_limit | NUMERIC(15,2) | Kreditlimit |
| discount_percent | NUMERIC(5,2) | Rabatt % |
| bank_name | VARCHAR(100) | Bank |
| iban | VARCHAR(34) | IBAN |
| bic | VARCHAR(11) | BIC |
| notes | TEXT | Notizen |
| created_at | TIMESTAMP | Erstelldatum |
| updated_at | TIMESTAMP | Änderungsdatum |
| created_by | UUID | FK → users.id |
| updated_by | UUID | FK → users.id |
| is_deleted | BOOLEAN | Soft-Delete |
| deleted_at | TIMESTAMP | Löschdatum |

---

## 3. Projektverwaltung

### 3.1 projects (Projekte)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| customer_id | UUID | FK → customers.id |
| project_number | VARCHAR(50) | Projektnummer |
| name | VARCHAR(200) | Projektname |
| description | TEXT | Beschreibung |
| project_type | ENUM | Projekttyp |
| status | ENUM | Status |
| priority | ENUM | Priorität |
| street | VARCHAR(200) | Baustellenadresse |
| postal_code | VARCHAR(20) | PLZ |
| city | VARCHAR(100) | Stadt |
| latitude | NUMERIC(10,7) | Breitengrad |
| longitude | NUMERIC(10,7) | Längengrad |
| altitude | NUMERIC(8,2) | Höhe über NN |
| plot_number | VARCHAR(50) | Flurstück |
| land_registry | VARCHAR(100) | Gemarkung |
| building_permit_number | VARCHAR(100) | Baugenehmigungsnummer |
| building_permit_date | DATE | Baugenehmigung Datum |
| planned_start | DATE | Geplanter Start |
| planned_end | DATE | Geplantes Ende |
| actual_start | DATE | Tatsächlicher Start |
| actual_end | DATE | Tatsächliches Ende |
| budget_total | NUMERIC(15,2) | Gesamtbudget |
| budget_spent | NUMERIC(15,2) | Verbrauchtes Budget |
| progress_percent | NUMERIC(5,2) | Fortschritt % |
| created_at | TIMESTAMP | Erstelldatum |
| updated_at | TIMESTAMP | Änderungsdatum |
| created_by | UUID | FK → users.id |
| is_deleted | BOOLEAN | Soft-Delete |

**Indizes:**
- `idx_projects_tenant` (tenant_id)
- `idx_projects_customer` (customer_id)
- `idx_projects_status` (status)
- `idx_projects_number` (project_number)

---

### 3.2 project_milestones (Meilensteine)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| project_id | UUID | FK → projects.id |
| name | VARCHAR(200) | Bezeichnung |
| description | TEXT | Beschreibung |
| planned_date | DATE | Geplantes Datum |
| actual_date | DATE | Tatsächliches Datum |
| status | ENUM | Status |
| is_critical | BOOLEAN | Kritischer Pfad |

---

### 3.3 project_tasks (Aufgaben)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| project_id | UUID | FK → projects.id |
| milestone_id | UUID | FK → project_milestones.id |
| parent_task_id | UUID | FK → project_tasks.id |
| name | VARCHAR(200) | Aufgabenname |
| description | TEXT | Beschreibung |
| status | ENUM | Status |
| priority | ENUM | Priorität |
| assigned_to | UUID | FK → users.id |
| planned_start | DATE | Geplanter Start |
| planned_end | DATE | Geplantes Ende |
| actual_start | DATE | Tatsächlicher Start |
| actual_end | DATE | Tatsächliches Ende |
| estimated_hours | NUMERIC(8,2) | Geschätzte Stunden |
| actual_hours | NUMERIC(8,2) | Tatsächliche Stunden |

---

## 4. Bautagebuch

### 4.1 construction_diary_entries (Bautagebuch-Einträge)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| project_id | UUID | FK → projects.id |
| entry_date | DATE | Eintragsdatum |
| entry_number | INTEGER | Laufende Nummer |
| weather_morning | VARCHAR(50) | Wetter morgens |
| weather_noon | VARCHAR(50) | Wetter mittags |
| weather_evening | VARCHAR(50) | Wetter abends |
| temperature_morning | NUMERIC(4,1) | Temperatur morgens °C |
| temperature_noon | NUMERIC(4,1) | Temperatur mittags °C |
| temperature_evening | NUMERIC(4,1) | Temperatur abends °C |
| precipitation | VARCHAR(100) | Niederschlag |
| wind_speed | VARCHAR(50) | Windstärke |
| work_description | TEXT | Ausgeführte Arbeiten |
| special_events | TEXT | Besondere Vorkommnisse |
| delays | TEXT | Verzögerungen |
| visitors | TEXT | Besucher |
| notes | TEXT | Notizen |
| signature | TEXT | Digitale Unterschrift |
| signed_at | TIMESTAMP | Unterschrift Zeitpunkt |
| signed_by | UUID | FK → users.id |
| created_at | TIMESTAMP | Erstelldatum |
| created_by | UUID | FK → users.id |

---

### 4.2 diary_personnel (Personal pro Tagebucheintrag)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| diary_entry_id | UUID | FK → construction_diary_entries.id |
| employee_id | UUID | FK → employees.id (nullable) |
| name | VARCHAR(200) | Name (bei externen) |
| company | VARCHAR(200) | Firma (bei Subunternehmern) |
| hours_worked | NUMERIC(4,2) | Arbeitsstunden |
| activity | TEXT | Tätigkeit |

---

### 4.3 diary_deliveries (Lieferungen pro Tagebucheintrag)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| diary_entry_id | UUID | FK → construction_diary_entries.id |
| delivery_time | TIME | Lieferzeit |
| supplier | VARCHAR(200) | Lieferant |
| material | VARCHAR(200) | Material |
| quantity | NUMERIC(12,3) | Menge |
| unit | VARCHAR(20) | Einheit |
| delivery_note_number | VARCHAR(100) | Lieferschein-Nr. |

---

## 5. Materialwirtschaft

### 5.1 materials (Materialstamm)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| article_number | VARCHAR(50) | Artikelnummer |
| ean | VARCHAR(20) | EAN-Code |
| name | VARCHAR(200) | Artikelname |
| description | TEXT | Beschreibung |
| category | VARCHAR(100) | Kategorie |
| subcategory | VARCHAR(100) | Unterkategorie |
| unit | VARCHAR(20) | Einheit |
| length_mm | NUMERIC(10,2) | Länge mm |
| width_mm | NUMERIC(10,2) | Breite mm |
| height_mm | NUMERIC(10,2) | Höhe mm |
| weight_kg | NUMERIC(10,3) | Gewicht kg |
| volume_m3 | NUMERIC(10,6) | Volumen m³ |
| wood_type | VARCHAR(50) | Holzart |
| wood_quality | VARCHAR(50) | Holzqualität |
| moisture_content | NUMERIC(5,2) | Feuchtigkeit % |
| strength_class | VARCHAR(20) | Festigkeitsklasse |
| fire_rating | VARCHAR(20) | Brandschutzklasse |
| fsc_certified | BOOLEAN | FSC-zertifiziert |
| pefc_certified | BOOLEAN | PEFC-zertifiziert |
| purchase_price | NUMERIC(12,4) | Einkaufspreis |
| selling_price | NUMERIC(12,4) | Verkaufspreis |
| tax_rate | NUMERIC(5,2) | MwSt-Satz |
| stock_quantity | NUMERIC(12,3) | Lagerbestand |
| min_stock | NUMERIC(12,3) | Mindestbestand |
| max_stock | NUMERIC(12,3) | Maximalbestand |
| reorder_quantity | NUMERIC(12,3) | Bestellmenge |
| storage_location | VARCHAR(100) | Lagerort |
| supplier_id | UUID | FK → suppliers.id |
| is_active | BOOLEAN | Aktiv |
| created_at | TIMESTAMP | Erstelldatum |
| is_deleted | BOOLEAN | Soft-Delete |

---

### 5.2 inventory_movements (Lagerbewegungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| material_id | UUID | FK → materials.id |
| movement_type | ENUM | IN, OUT, ADJUSTMENT |
| quantity | NUMERIC(12,3) | Menge |
| unit_price | NUMERIC(12,4) | Stückpreis |
| reference_type | VARCHAR(50) | Referenztyp |
| reference_id | UUID | Referenz-ID |
| project_id | UUID | FK → projects.id |
| notes | TEXT | Notizen |
| movement_date | TIMESTAMP | Bewegungsdatum |
| created_by | UUID | FK → users.id |

---

## 6. Finanzverwaltung

### 6.1 accounts (Kontenplan)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| account_number | VARCHAR(10) | Kontonummer |
| name | VARCHAR(200) | Kontoname |
| account_type | ENUM | Kontotyp |
| parent_account_id | UUID | FK → accounts.id |
| is_active | BOOLEAN | Aktiv |
| balance | NUMERIC(15,2) | Saldo |

---

### 6.2 journal_entries (Buchungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| entry_number | VARCHAR(50) | Buchungsnummer |
| entry_date | DATE | Buchungsdatum |
| description | TEXT | Buchungstext |
| debit_account_id | UUID | FK → accounts.id |
| credit_account_id | UUID | FK → accounts.id |
| amount | NUMERIC(15,2) | Betrag |
| document_number | VARCHAR(100) | Belegnummer |
| document_date | DATE | Belegdatum |
| is_posted | BOOLEAN | Gebucht |
| created_by | UUID | FK → users.id |

---

### 6.3 invoices (Rechnungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| customer_id | UUID | FK → customers.id |
| project_id | UUID | FK → projects.id |
| invoice_number | VARCHAR(50) | Rechnungsnummer |
| invoice_type | ENUM | INVOICE, CREDIT_NOTE |
| status | ENUM | Status |
| invoice_date | DATE | Rechnungsdatum |
| due_date | DATE | Fälligkeitsdatum |
| delivery_date | DATE | Lieferdatum |
| net_amount | NUMERIC(15,2) | Nettobetrag |
| tax_amount | NUMERIC(15,2) | MwSt-Betrag |
| gross_amount | NUMERIC(15,2) | Bruttobetrag |
| discount_percent | NUMERIC(5,2) | Rabatt % |
| discount_amount | NUMERIC(15,2) | Rabattbetrag |
| paid_amount | NUMERIC(15,2) | Bezahlter Betrag |
| payment_terms | INTEGER | Zahlungsziel (Tage) |
| notes | TEXT | Notizen |
| internal_notes | TEXT | Interne Notizen |
| created_at | TIMESTAMP | Erstelldatum |
| created_by | UUID | FK → users.id |
| is_deleted | BOOLEAN | Soft-Delete |

---

### 6.4 invoice_items (Rechnungspositionen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| invoice_id | UUID | FK → invoices.id |
| position | INTEGER | Position |
| material_id | UUID | FK → materials.id |
| description | TEXT | Beschreibung |
| quantity | NUMERIC(12,3) | Menge |
| unit | VARCHAR(20) | Einheit |
| unit_price | NUMERIC(12,4) | Einzelpreis |
| discount_percent | NUMERIC(5,2) | Rabatt % |
| net_amount | NUMERIC(15,2) | Nettobetrag |
| tax_rate | NUMERIC(5,2) | MwSt-Satz |
| tax_amount | NUMERIC(15,2) | MwSt-Betrag |

---

### 6.5 payments (Zahlungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| invoice_id | UUID | FK → invoices.id |
| payment_date | DATE | Zahlungsdatum |
| amount | NUMERIC(15,2) | Betrag |
| payment_method | ENUM | Zahlungsart |
| reference | VARCHAR(200) | Referenz/Verwendungszweck |
| bank_account_id | UUID | FK → bank_accounts.id |
| notes | TEXT | Notizen |
| created_by | UUID | FK → users.id |

---

### 6.6 bank_accounts (Bankkonten)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| name | VARCHAR(200) | Kontobezeichnung |
| bank_name | VARCHAR(100) | Bankname |
| bank_code | VARCHAR(20) | Bankleitzahl |
| iban | VARCHAR(34) | IBAN |
| bic | VARCHAR(11) | BIC/SWIFT |
| account_holder | VARCHAR(200) | Kontoinhaber |
| account_type | ENUM | Kontotyp |
| currency | VARCHAR(3) | Währung (EUR) |
| current_balance | NUMERIC(15,2) | Aktueller Kontostand |
| balance_date | TIMESTAMP | Stand vom |
| provider | VARCHAR(50) | Banking-Provider (FinTS) |
| credentials_encrypted | TEXT | Verschlüsselte Zugangsdaten |
| online_banking_enabled | BOOLEAN | Online-Banking aktiv |
| last_sync | TIMESTAMP | Letzte Synchronisation |
| is_active | BOOLEAN | Aktiv |
| is_default | BOOLEAN | Standardkonto |
| created_at | TIMESTAMP | Erstelldatum |
| is_deleted | BOOLEAN | Soft-Delete |

---

### 6.7 bank_transactions (Banktransaktionen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| bank_account_id | UUID | FK → bank_accounts.id |
| transaction_id | VARCHAR(100) | Externe Transaktions-ID |
| booking_date | DATE | Buchungsdatum |
| value_date | DATE | Wertstellung |
| amount | NUMERIC(15,2) | Betrag |
| currency | VARCHAR(3) | Währung |
| purpose | TEXT | Verwendungszweck |
| counterparty_name | VARCHAR(200) | Name Gegenkonto |
| counterparty_iban | VARCHAR(34) | IBAN Gegenkonto |
| counterparty_bic | VARCHAR(11) | BIC Gegenkonto |
| transaction_type | VARCHAR(50) | Transaktionsart |
| is_matched | BOOLEAN | Mit Rechnung verknüpft |
| matched_invoice_id | UUID | FK → invoices.id |
| created_at | TIMESTAMP | Importdatum |

---

## 7. Personalverwaltung

### 7.1 employees (Mitarbeiter)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| user_id | UUID | FK → users.id |
| employee_number | VARCHAR(50) | Personalnummer |
| salutation | VARCHAR(20) | Anrede |
| first_name | VARCHAR(100) | Vorname |
| last_name | VARCHAR(100) | Nachname |
| birth_date | DATE | Geburtsdatum |
| birth_place | VARCHAR(100) | Geburtsort |
| nationality | VARCHAR(50) | Staatsangehörigkeit |
| social_security_number | VARCHAR(50) | Sozialversicherungsnummer |
| tax_id | VARCHAR(50) | Steuer-ID |
| tax_class | VARCHAR(10) | Steuerklasse |
| health_insurance | VARCHAR(100) | Krankenkasse |
| street | VARCHAR(200) | Straße |
| postal_code | VARCHAR(20) | PLZ |
| city | VARCHAR(100) | Stadt |
| phone | VARCHAR(50) | Telefon |
| mobile | VARCHAR(50) | Mobil |
| email | VARCHAR(255) | E-Mail |
| emergency_contact | VARCHAR(200) | Notfallkontakt |
| emergency_phone | VARCHAR(50) | Notfall-Telefon |
| entry_date | DATE | Eintrittsdatum |
| exit_date | DATE | Austrittsdatum |
| department | VARCHAR(100) | Abteilung |
| position | VARCHAR(100) | Position |
| employment_type | ENUM | Beschäftigungsart |
| weekly_hours | NUMERIC(4,2) | Wochenstunden |
| vacation_days | INTEGER | Urlaubstage |
| salary_type | ENUM | Gehaltsart |
| hourly_rate | NUMERIC(10,2) | Stundenlohn |
| monthly_salary | NUMERIC(10,2) | Monatsgehalt |
| bank_name | VARCHAR(100) | Bank |
| iban | VARCHAR(34) | IBAN |
| is_active | BOOLEAN | Aktiv |
| created_at | TIMESTAMP | Erstelldatum |
| is_deleted | BOOLEAN | Soft-Delete |

---

### 7.2 time_entries (Zeiterfassung)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| employee_id | UUID | FK → employees.id |
| project_id | UUID | FK → projects.id |
| task_id | UUID | FK → project_tasks.id |
| entry_date | DATE | Datum |
| start_time | TIME | Startzeit |
| end_time | TIME | Endzeit |
| break_minutes | INTEGER | Pause (Minuten) |
| hours_worked | NUMERIC(5,2) | Arbeitsstunden |
| activity | TEXT | Tätigkeit |
| is_approved | BOOLEAN | Genehmigt |
| approved_by | UUID | FK → users.id |
| approved_at | TIMESTAMP | Genehmigt am |

---

## 8. Fuhrpark & Geräte

### 8.1 vehicles (Fahrzeuge)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| license_plate | VARCHAR(20) | Kennzeichen |
| vehicle_type | ENUM | Fahrzeugtyp |
| manufacturer | VARCHAR(100) | Hersteller |
| model | VARCHAR(100) | Modell |
| vin | VARCHAR(50) | Fahrgestellnummer |
| year | INTEGER | Baujahr |
| first_registration | DATE | Erstzulassung |
| fuel_type | ENUM | Kraftstoffart |
| mileage | INTEGER | Kilometerstand |
| next_inspection | DATE | Nächster TÜV |
| next_service | DATE | Nächste Wartung |
| insurance_company | VARCHAR(100) | Versicherung |
| insurance_number | VARCHAR(100) | Versicherungsnummer |
| status | ENUM | Status |
| assigned_employee_id | UUID | FK → employees.id |
| notes | TEXT | Notizen |
| is_active | BOOLEAN | Aktiv |
| created_at | TIMESTAMP | Erstelldatum |
| is_deleted | BOOLEAN | Soft-Delete |

---

### 8.2 equipment (Geräte/Maschinen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| equipment_number | VARCHAR(50) | Gerätenummer |
| name | VARCHAR(200) | Bezeichnung |
| category | VARCHAR(100) | Kategorie |
| manufacturer | VARCHAR(100) | Hersteller |
| model | VARCHAR(100) | Modell |
| serial_number | VARCHAR(100) | Seriennummer |
| purchase_date | DATE | Kaufdatum |
| purchase_price | NUMERIC(12,2) | Kaufpreis |
| operating_hours | NUMERIC(10,2) | Betriebsstunden |
| next_inspection | DATE | Nächste Prüfung |
| next_service | DATE | Nächste Wartung |
| status | ENUM | Status |
| storage_location | VARCHAR(100) | Lagerort |
| current_project_id | UUID | FK → projects.id |
| notes | TEXT | Notizen |
| is_active | BOOLEAN | Aktiv |
| created_at | TIMESTAMP | Erstelldatum |
| is_deleted | BOOLEAN | Soft-Delete |

---

## 9. Qualitätsmanagement

### 9.1 defects (Mängel)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| project_id | UUID | FK → projects.id |
| defect_number | VARCHAR(50) | Mangelnummer |
| title | VARCHAR(200) | Bezeichnung |
| description | TEXT | Beschreibung |
| location | VARCHAR(200) | Ort/Bauteil |
| severity | ENUM | Schweregrad |
| status | ENUM | Status |
| detected_date | DATE | Erkannt am |
| detected_by | UUID | FK → users.id |
| responsible_party | VARCHAR(200) | Verantwortlicher |
| deadline | DATE | Frist |
| fixed_date | DATE | Behoben am |
| fixed_by | VARCHAR(200) | Behoben durch |
| cost_estimate | NUMERIC(12,2) | Geschätzte Kosten |
| actual_cost | NUMERIC(12,2) | Tatsächliche Kosten |
| photos_before | JSON | Fotos vorher (MongoDB GridFS IDs) |
| photos_after | JSON | Fotos nachher (MongoDB GridFS IDs) |
| notes | TEXT | Notizen |
| created_at | TIMESTAMP | Erstelldatum |
| is_deleted | BOOLEAN | Soft-Delete |

---

### 9.2 quality_checks (Qualitätsprüfungen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| project_id | UUID | FK → projects.id |
| check_type | VARCHAR(100) | Prüfungsart |
| check_date | DATE | Prüfungsdatum |
| inspector_id | UUID | FK → users.id |
| result | ENUM | Ergebnis |
| measurements | JSON | Messwerte |
| notes | TEXT | Notizen |
| signature | TEXT | Unterschrift |
| created_at | TIMESTAMP | Erstelldatum |

---

## 10. Telemetrie

### 10.1 telemetry_events (Ereignisse)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| user_id | UUID | FK → users.id |
| session_id | VARCHAR(100) | Session-ID |
| event_type | VARCHAR(50) | Ereignistyp |
| event_name | VARCHAR(100) | Ereignisname |
| event_data | JSON | Ereignisdaten |
| timestamp | TIMESTAMP | Zeitstempel |
| client_info | JSON | Client-Informationen |

---

### 10.2 telemetry_metrics (Metriken)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| metric_name | VARCHAR(100) | Metrikname |
| metric_value | NUMERIC(15,4) | Metrikwert |
| metric_unit | VARCHAR(20) | Einheit |
| tags | JSON | Tags |
| timestamp | TIMESTAMP | Zeitstempel |

---

## 11. Dateispeicher (MongoDB GridFS)

Dateien werden in MongoDB GridFS gespeichert für:
- Skalierbarkeit
- Mandantentrennung
- Große Dateien (bis 16 MB)

### 11.1 file_storage (MongoDB Collection)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| _id | ObjectId | Primärschlüssel |
| tenant_id | String | Mandanten-ID |
| filename | String | Dateiname |
| content_type | String | MIME-Type |
| file_id | ObjectId | GridFS File ID |
| entity_type | String | Verknüpfter Entitätstyp |
| entity_id | String | Verknüpfte Entitäts-ID |
| uploaded_by | String | Hochgeladen von (User-ID) |
| uploaded_at | DateTime | Hochladedatum |
| file_size | Integer | Dateigröße in Bytes |

---

## 12. Machine Learning

### 12.1 ml_predictions (ML-Vorhersagen)

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | UUID | Primärschlüssel |
| tenant_id | UUID | FK → tenants.id |
| model_type | VARCHAR(50) | Modelltyp |
| entity_type | VARCHAR(50) | Bezogene Entität |
| entity_id | UUID | Entitäts-ID |
| prediction_data | JSONB | Vorhersagedaten |
| confidence | NUMERIC(5,4) | Konfidenz (0-1) |
| created_at | TIMESTAMP | Erstelldatum |

---

## Entity-Relationship-Diagramm

```
                                    ┌──────────────┐
                                    │   tenants    │
                                    └──────┬───────┘
                                           │
           ┌───────────────┬───────────────┼───────────────┬───────────────┐
           │               │               │               │               │
           ▼               ▼               ▼               ▼               ▼
     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
     │  users  │     │customers│     │projects │     │materials│     │employees│
     └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
          │               │               │               │               │
          │               │      ┌────────┼────────┐      │               │
          │               │      ▼        ▼        ▼      │               │
          │               │ ┌────────┐┌───────┐┌───────┐  │               │
          │               │ │ tasks  ││diary  ││defects│  │               │
          │               │ └────────┘└───────┘└───────┘  │               │
          │               │                               │               │
          │               └───────────────┬───────────────┘               │
          │                               ▼                               │
          │                         ┌─────────┐                           │
          │                         │invoices │                           │
          │                         └────┬────┘                           │
          │                              │                                │
          │                              ▼                                │
          │                         ┌─────────┐                           │
          │                         │payments │                           │
          │                         └─────────┘                           │
          │                                                               │
          └───────────────────────────────┬───────────────────────────────┘
                                          ▼
                                    ┌───────────┐
                                    │time_entries│
                                    └───────────┘
```

---

© 2025 HolzbauERP. Alle Rechte vorbehalten.
