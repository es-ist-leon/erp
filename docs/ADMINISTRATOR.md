# HolzbauERP - Administrator-Handbuch

## Inhaltsverzeichnis

1. [Systemverwaltung](#1-systemverwaltung)
2. [Benutzerverwaltung](#2-benutzerverwaltung)
3. [Rollen und Berechtigungen](#3-rollen-und-berechtigungen)
4. [Mandantenverwaltung](#4-mandantenverwaltung)
5. [Datensicherung](#5-datensicherung)
6. [Wartung](#6-wartung)
7. [Monitoring](#7-monitoring)
8. [Sicherheit](#8-sicherheit)
9. [Banking-Administration](#9-banking-administration)
10. [Machine Learning](#10-machine-learning)

---

## 1. Systemverwaltung

### 1.1 Systemübersicht

Als Administrator haben Sie Zugriff auf:

- Benutzer- und Rechteverwaltung
- Systemkonfiguration
- Datenbankwartung
- Protokolle und Auswertungen
- Backup und Restore

### 1.2 Administrator-Dashboard

Das Admin-Dashboard zeigt:

| KPI | Beschreibung |
|-----|--------------|
| Aktive Benutzer | Aktuell angemeldete User |
| Datenbankgröße | Speicherverbrauch |
| Fehlerrate | Fehler der letzten 24h |
| Performance | Durchschnittliche Antwortzeit |

### 1.3 Systemeinstellungen

Pfad: `Einstellungen → System`

#### Nummernkreise

Konfigurieren Sie automatische Nummernvergabe:

| Bereich | Präfix | Format | Beispiel |
|---------|--------|--------|----------|
| Kunden | K | K{NNNNNN} | K000001 |
| Projekte | P | P{YYYY}-{NNNN} | P2025-0001 |
| Rechnungen | RE | RE{YYYY}{NNNNN} | RE202500001 |
| Angebote | AN | AN{YYYY}{NNNNN} | AN202500001 |
| Material | M | M{NNNNNN} | M000001 |

#### Standardwerte

- Standard-Zahlungsziel (Tage)
- Standard-Skonto (%)
- Standard-MwSt-Satz (%)
- Standardwährung
- Standardland

#### E-Mail-Konfiguration

```
SMTP-Server: smtp.example.com
Port: 587
Verschlüsselung: TLS
Benutzername: erp@firma.de
Absender: HolzbauERP <erp@firma.de>
```

---

## 2. Benutzerverwaltung

### 2.1 Benutzer anlegen

Pfad: `Einstellungen → Benutzer → Neuer Benutzer`

**Pflichtfelder:**
- E-Mail-Adresse (eindeutig)
- Benutzername
- Passwort (mind. 8 Zeichen)
- Vorname, Nachname
- Rolle

**Optionale Felder:**
- Telefon
- Abteilung
- Vorgesetzter
- Profilbild

### 2.2 Benutzer bearbeiten

1. Wählen Sie den Benutzer aus der Liste
2. Klicken Sie auf "Bearbeiten"
3. Ändern Sie die gewünschten Daten
4. Speichern Sie die Änderungen

### 2.3 Benutzer deaktivieren

Statt Benutzer zu löschen, deaktivieren Sie sie:

1. Benutzer auswählen
2. "Bearbeiten" klicken
3. "Aktiv" deaktivieren
4. Speichern

Deaktivierte Benutzer:
- Können sich nicht anmelden
- Behalten ihre Datenhistorie
- Können reaktiviert werden

### 2.4 Passwort zurücksetzen

1. Benutzer auswählen
2. "Passwort zurücksetzen" klicken
3. Neues Passwort eingeben
4. Option: "Passwortänderung bei nächster Anmeldung erzwingen"

### 2.5 Massen-Import

Importieren Sie mehrere Benutzer per CSV:

```csv
email,username,first_name,last_name,role
max.mustermann@firma.de,mmustermann,Max,Mustermann,Mitarbeiter
anna.schmidt@firma.de,aschmidt,Anna,Schmidt,Projektleiter
```

---

## 3. Rollen und Berechtigungen

### 3.1 Vordefinierte Rollen

| Rolle | Beschreibung |
|-------|--------------|
| Administrator | Vollzugriff auf alle Funktionen |
| Geschäftsführer | Voller Lesezugriff, Finanzen |
| Projektleiter | Projekt- und Mitarbeiterverwaltung |
| Bauleiter | Baustellendokumentation |
| Sachbearbeiter | Kunden, Angebote, Rechnungen |
| Lager | Materialwirtschaft |
| Mitarbeiter | Zeiterfassung, eigene Daten |

### 3.2 Berechtigungsmatrix

| Modul | Admin | GF | PL | BL | SB | Lager | MA |
|-------|-------|----|----|----|----|-------|-----|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Kunden | ✅ | 👁️ | 👁️ | 👁️ | ✅ | ❌ | ❌ |
| Projekte | ✅ | ✅ | ✅ | ✅ | 👁️ | 👁️ | 👁️ |
| Bautagebuch | ✅ | 👁️ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Material | ✅ | 👁️ | 👁️ | 👁️ | 👁️ | ✅ | ❌ |
| Finanzen | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Personal | ✅ | ✅ | 👁️ | ❌ | ❌ | ❌ | ❌ |
| Einstellungen | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

Legende: ✅ Vollzugriff | 👁️ Nur Lesen | ❌ Kein Zugriff

### 3.3 Eigene Rollen erstellen

1. Einstellungen → Rollen → Neue Rolle
2. Name und Beschreibung eingeben
3. Berechtigungen auswählen:

```
☑ customer:view      ☑ customer:create
☐ customer:edit      ☐ customer:delete

☑ project:view       ☑ project:create
☑ project:edit       ☐ project:delete

☐ finance:view       ☐ finance:create
☐ invoice:view       ☐ invoice:create
```

4. Speichern

### 3.4 Berechtigungen im Detail

**Kunden-Berechtigungen:**
- `customer:view` - Kunden anzeigen
- `customer:create` - Kunden anlegen
- `customer:edit` - Kunden bearbeiten
- `customer:delete` - Kunden löschen

**Projekt-Berechtigungen:**
- `project:view` - Projekte anzeigen
- `project:create` - Projekte anlegen
- `project:edit` - Projekte bearbeiten
- `project:delete` - Projekte löschen
- `project:budget` - Budget einsehen/ändern

**Finanz-Berechtigungen:**
- `finance:view` - Finanzdaten einsehen
- `finance:create` - Buchungen erstellen
- `invoice:view` - Rechnungen einsehen
- `invoice:create` - Rechnungen erstellen
- `invoice:approve` - Rechnungen freigeben
- `payment:view` - Zahlungen einsehen
- `payment:create` - Zahlungen erfassen

---

## 4. Mandantenverwaltung

### 4.1 Multi-Tenant-Konzept

HolzbauERP unterstützt mehrere Mandanten (Firmen) in einer Installation.

Jeder Mandant hat:
- Eigene Daten (komplett isoliert)
- Eigene Benutzer
- Eigene Einstellungen
- Eigenes Branding

### 4.2 Mandant anlegen

Als Super-Administrator:

1. System → Mandanten → Neu
2. Firmendaten eingeben:
   - Firmenname
   - Slug (URL-freundlicher Name)
   - Kontaktdaten
   - Bankverbindung
3. Subscription festlegen:
   - Plan (Basic/Professional/Enterprise)
   - Max. Benutzer
   - Gültig bis
4. Speichern

### 4.3 Mandant verwalten

- **Aktivieren/Deaktivieren:** Zugang sperren
- **Benutzer verwalten:** Admins für Mandant festlegen
- **Limits anpassen:** Benutzer, Speicher, etc.
- **Daten exportieren:** Kompletter Datenexport

---

## 5. Datensicherung

### 5.1 Automatische Backups

Die Cloud-Datenbank erstellt automatisch:
- Stündliche Snapshots (24h aufbewahrt)
- Tägliche Backups (30 Tage aufbewahrt)
- Wöchentliche Backups (52 Wochen aufbewahrt)

### 5.2 Manuelles Backup

**Datenbank-Export:**
```powershell
# PostgreSQL Backup
pg_dump -h server.db.example.com -U user -d holzbauerp > backup_$(Get-Date -Format "yyyyMMdd").sql
```

**Innerhalb der Anwendung:**
1. Einstellungen → System → Backup
2. "Backup erstellen" klicken
3. Speicherort wählen
4. Backup wird erstellt (JSON/SQL)

### 5.3 Datenwiederherstellung

⚠️ **ACHTUNG:** Restore überschreibt vorhandene Daten!

1. Einstellungen → System → Backup
2. "Wiederherstellen" klicken
3. Backup-Datei auswählen
4. Bestätigen Sie die Wiederherstellung

### 5.4 Datenexport

Für DATEV, Steuerberater oder Archivierung:

**DATEV-Export:**
- Buchungen im DATEV-Format
- Für Import in DATEV-Software

**Excel-Export:**
- Alle Daten als Excel-Dateien
- Pro Modul separate Dateien

**PDF-Archiv:**
- Rechnungen und Dokumente als PDF
- Mit digitaler Signatur

---

## 6. Wartung

### 6.1 Datenbank-Optimierung

Führen Sie regelmäßig aus:

**Innerhalb der Anwendung:**
1. Einstellungen → System → Wartung
2. "Datenbank optimieren" klicken

**Manuell (SQL):**
```sql
-- Statistiken aktualisieren
ANALYZE;

-- Tabellen bereinigen
VACUUM ANALYZE;

-- Index-Wartung
REINDEX DATABASE holzbauerp;
```

### 6.2 Cache leeren

Bei Performance-Problemen:
1. Einstellungen → System → Cache
2. "Cache leeren" klicken

### 6.3 Protokolle bereinigen

Alte Telemetrie-Daten löschen:
1. Einstellungen → System → Protokolle
2. Zeitraum wählen (älter als X Tage)
3. "Bereinigen" klicken

### 6.4 Updates einspielen

1. Neue Version herunterladen
2. Anwendung beenden
3. Dateien überschreiben (außer Konfiguration)
4. Anwendung starten
5. Datenbank-Migration wird automatisch ausgeführt

---

## 7. Monitoring

### 7.1 System-Dashboard

Überwachen Sie in Echtzeit:

- **CPU-Auslastung:** Lokale Ressourcen
- **Speicher:** RAM-Verbrauch
- **Datenbankverbindungen:** Aktive Connections
- **Antwortzeiten:** Query-Performance

### 7.2 Benutzer-Aktivität

Protokolliert werden:
- Anmeldungen (erfolgreich/fehlgeschlagen)
- Datenänderungen (wer, was, wann)
- Modulzugriffe

**Bericht generieren:**
1. Einstellungen → Berichte → Benutzeraktivität
2. Zeitraum und Benutzer wählen
3. Bericht erstellen

### 7.3 Fehlerprotokoll

Alle Fehler werden erfasst:

| Feld | Beschreibung |
|------|--------------|
| Zeitstempel | Wann trat der Fehler auf |
| Benutzer | Wer war betroffen |
| Modul | Wo trat der Fehler auf |
| Fehlertyp | Art des Fehlers |
| Stacktrace | Technische Details |

### 7.4 Performance-Metriken

Gemessene Werte:
- Seitenladezeiten
- Datenbankabfrage-Dauer
- API-Antwortzeiten

---

## 8. Sicherheit

### 8.1 Passwortrichtlinien

Konfigurieren Sie unter Einstellungen → Sicherheit:

- **Mindestlänge:** 8-32 Zeichen
- **Komplexität:** Groß-/Kleinbuchstaben, Zahlen, Sonderzeichen
- **Ablauf:** Nach X Tagen Passwortänderung erzwingen
- **Historie:** Letzte X Passwörter nicht wiederverwendbar

### 8.2 Anmeldeschutz

- **Fehlgeschlagene Versuche:** Nach X Versuchen Account sperren
- **Sperrzeit:** Automatische Entsperrung nach X Minuten
- **IP-Whitelist:** Nur bestimmte IPs zulassen

### 8.3 Session-Management

- **Timeout:** Automatische Abmeldung nach X Minuten Inaktivität
- **Concurrent Sessions:** Mehrfach-Anmeldung erlauben/verbieten
- **Session-Protokoll:** Aktive Sitzungen anzeigen und beenden

### 8.4 Audit-Trail

Alle sicherheitsrelevanten Ereignisse:

```
2025-12-21 10:15:32 | LOGIN_SUCCESS | admin@demo.de | IP: 192.168.1.100
2025-12-21 10:16:45 | DATA_CREATE | admin@demo.de | Customer #K000042
2025-12-21 10:18:03 | DATA_UPDATE | admin@demo.de | Project #P2025-0015
2025-12-21 11:30:00 | LOGOUT | admin@demo.de
```

### 8.5 Datenverschlüsselung

- **Transport:** TLS 1.3 für alle Verbindungen
- **Passwörter:** bcrypt-Hashing
- **Sensible Daten:** AES-256 Verschlüsselung

### 8.6 Compliance

HolzbauERP unterstützt:
- **DSGVO:** Datenschutz-Grundverordnung
- **GoBD:** Grundsätze ordnungsmäßiger Buchführung
- **Revisionssicherheit:** Unveränderbare Protokolle
- **PSD2:** Payment Services Directive für Banking

---

## 9. Banking-Administration

### 9.1 FinTS/HBCI-Konfiguration

Die Banking-Integration nutzt FinTS 3.0 für sichere Bankverbindungen.

#### Unterstützte TAN-Verfahren
- PushTAN / AppTAN
- SMS-TAN
- ChipTAN (manuell)
- PhotoTAN

#### Bank-Credentials
Zugangsdaten werden verschlüsselt in der Datenbank gespeichert (AES-256).

### 9.2 Bankkonten verwalten

Pfad: `Finanzen → Banking → Konten`

**Konto hinzufügen:**
1. Bank aus Liste wählen (2.000+ deutsche Banken)
2. Zugangsdaten eingeben
3. TAN-Verfahren auswählen
4. Verbindung testen

**Konto synchronisieren:**
- Automatisch: Täglich um 6:00 Uhr
- Manuell: "Jetzt synchronisieren" klicken

### 9.3 Transaktionsabgleich

Automatischer Abgleich von Transaktionen mit offenen Rechnungen:
1. System prüft Verwendungszweck
2. Matching-Score wird berechnet
3. Transaktionen werden vorgeschlagen
4. Administrator bestätigt Zuordnung

### 9.4 Sicherheitshinweise

- Zugangsdaten werden nie im Klartext gespeichert
- TLS 1.3 für alle Bankverbindungen
- Session-Tokens verfallen nach 5 Minuten
- Audit-Log für alle Banking-Aktionen

---

## 10. Machine Learning

### 10.1 ML-Services verwalten

Pfad: `Einstellungen → ML-Services`

#### Verfügbare Modelle

| Modell | Beschreibung | Datenvoraussetzung |
|--------|--------------|-------------------|
| Kostenprognose | Projektkosten vorhersagen | Mind. 20 abgeschlossene Projekte |
| Mängelrisiko | Qualitätsprobleme erkennen | Mind. 50 Mängeldatensätze |
| Kundenwert | Customer Lifetime Value | Mind. 30 Kunden mit Historie |
| Lieferzeit | Optimale Bestellzeitpunkte | Mind. 100 Lieferungen |

### 10.2 Modelle trainieren

1. Einstellungen → ML-Services → Training
2. Modell auswählen
3. Trainingsdaten prüfen
4. "Training starten" klicken
5. Nach Abschluss: Modell-Performance anzeigen

### 10.3 Empfehlungen konfigurieren

| Einstellung | Beschreibung | Standard |
|-------------|--------------|----------|
| Auto-Empfehlungen | Automatische Vorschläge | Ein |
| Konfidenz-Schwelle | Min. Konfidenz für Anzeige | 70% |
| Benachrichtigungen | Bei hohem Risiko warnen | Ein |

### 10.4 Datenschutz

- ML-Modelle laufen lokal
- Keine Daten an externe Server
- Mandantentrennung bei Training
- Modelle können gelöscht werden

---

## Anhang

### A. Administrator-Checkliste

**Täglich:**
- [ ] Fehlerprotokoll prüfen
- [ ] Systemstatus überprüfen

**Wöchentlich:**
- [ ] Benutzeraktivität prüfen
- [ ] Performance-Metriken analysieren
- [ ] Backup-Status prüfen

**Monatlich:**
- [ ] Benutzerkonten überprüfen (inaktive deaktivieren)
- [ ] Berechtigungen auditieren
- [ ] Datenbank optimieren
- [ ] ML-Modelle überprüfen
- [ ] Banking-Synchronisation prüfen

**Jährlich:**
- [ ] Passwörter zurücksetzen lassen
- [ ] Rollen und Berechtigungen überprüfen
- [ ] Compliance-Check durchführen

### B. Notfall-Kontakte

| Situation | Kontakt |
|-----------|---------|
| Technischer Support | support@holzbauerp.de |
| Datenbank-Notfall | db-support@holzbauerp.de |
| Sicherheitsvorfall | security@holzbauerp.de |
| Telefon-Hotline | +49 (0) 123 456789 |

---

© 2025 HolzbauERP. Alle Rechte vorbehalten.
