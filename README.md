# HolzbauERP - Enterprise Resource Planning für Holzbaubetriebe

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.12+-green)

## Übersicht

HolzbauERP ist eine umfassende ERP-Software für Holzbaubetriebe - vom kleinen Handwerker bis zum etablierten KMU.

## Dokumentation

Die vollständige Dokumentation finden Sie im `docs/` Ordner:

- [📖 Benutzerhandbuch](docs/BENUTZERHANDBUCH.md)
- [🔧 Technische Dokumentation](docs/TECHNISCHE_DOKUMENTATION.md)
- [📥 Installationsanleitung](docs/INSTALLATION.md)
- [👨‍💼 Administrator-Handbuch](docs/ADMINISTRATOR.md)
- [🔌 API-Dokumentation](docs/API.md)
- [🗄️ Datenbankschema](docs/DATENBANKSCHEMA.md)

## Schnellstart

```powershell
# Anwendung starten
.\HolzbauERP.bat
```

## Funktionen

- ✅ Kundenverwaltung (CRM)
- ✅ Projektverwaltung
- ✅ Bautagebuch
- ✅ Materialwirtschaft
- ✅ Finanzverwaltung & Buchhaltung
- ✅ Personalwesen & Lohnabrechnung
- ✅ Fuhrpark & Geräteverwaltung
- ✅ Qualitätsmanagement
- ✅ Telemetrie & Monitoring

## Lizenz

Proprietäre Software - © 2025 HolzbauERP

---

# HolzbauERP (Legacy)

**Enterprise Resource Planning für Holzbaubetriebe**

Eine lokale Desktop-Anwendung für die Verwaltung von Holzbaubetrieben - vom kleinen Handwerker bis zum etablierten KMU.

## Features

- **Dashboard**: Übersicht mit wichtigen KPIs
- **Kundenverwaltung**: Privat- und Geschäftskunden, Kontakte, Adressen
- **Projektverwaltung**: Projekte mit Status-Tracking (Anfrage -> Angebot -> Beauftragt -> Planung -> Produktion -> Montage -> Fertig)
- **Materialverwaltung**: Holz-Katalog (Schnittholz, BSH, CLT, Platten, etc.)
- **Auftrags- & Angebotsverwaltung**: Angebote erstellen und Aufträge verwalten
- **Rechnungswesen**: Rechnungen mit Zahlungsstatus-Tracking
- **Mitarbeiterverwaltung**: Personalstammdaten, Abteilungen, Beschäftigungsarten

## Systemanforderungen

- Windows 10/11
- Python 3.10 oder höher
- PostgreSQL Datenbank (lokal oder remote)

## Installation & Start

### 1. Datenbank-Credentials konfigurieren

Bearbeiten Sie die Datei `dbcredentials.txt.txt` mit Ihren Datenbankzugangsdaten:

    db_host=your-db-host
    db_port=5432
    db_user=your-username
    db_password=your-password
    db_name=holzbau_erp
    db_ssl_mode=require

### 2. Anwendung starten

Doppelklick auf `HolzbauERP.bat`

Die Anwendung installiert automatisch alle Abhängigkeiten beim ersten Start.

### 3. Anmelden

Standard-Login (wird automatisch erstellt):
- E-Mail: admin@holzbau-erp.de
- Passwort: admin123

## Projektstruktur

    erp/
    ├── app/                    # Qt Desktop-Anwendung
    │   ├── main.py            # Einstiegspunkt
    │   ├── services/          # Business Logic
    │   ├── ui/
    │   │   ├── windows/       # Hauptfenster
    │   │   ├── widgets/       # Seiten-Widgets
    │   │   └── dialogs/       # Dialoge
    │   └── resources/         # Styles, Icons
    ├── shared/                 # Gemeinsame Module
    │   ├── config.py          # Konfiguration
    │   ├── models/            # Datenbankmodelle
    │   └── utils/             # Hilfsfunktionen
    ├── certs/                  # SSL-Zertifikate
    ├── HolzbauERP.bat         # Start-Script
    └── requirements.txt       # Python-Abhängigkeiten

## Technologie-Stack

- **GUI**: PyQt6
- **Datenbank**: PostgreSQL mit SQLAlchemy ORM
- **Sicherheit**: bcrypt für Passwort-Hashing

## Lizenz

(c) 2024 HolzbauERP
