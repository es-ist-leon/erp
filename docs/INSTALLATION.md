# HolzbauERP - Installationsanleitung

## Inhaltsverzeichnis

1. [Systemvoraussetzungen](#1-systemvoraussetzungen)
2. [Python-Installation](#2-python-installation)
3. [HolzbauERP-Installation](#3-holzbauerp-installation)
4. [Datenbank-Konfiguration](#4-datenbank-konfiguration)
5. [Erster Start](#5-erster-start)
6. [Fehlerbehebung](#6-fehlerbehebung)

---

## 1. Systemvoraussetzungen

### Hardware

| Anforderung | Minimum | Empfohlen |
|-------------|---------|-----------|
| Prozessor | Intel Core i3 / AMD Ryzen 3 | Intel Core i5 / AMD Ryzen 5 |
| Arbeitsspeicher | 4 GB RAM | 8 GB RAM |
| Festplatte | 500 MB frei | 1 GB SSD |
| Bildschirm | 1366 × 768 | 1920 × 1080 |

### Software

- **Betriebssystem:** Windows 10/11 (64-bit)
- **Python:** 3.12 oder höher
- **Internetverbindung:** Für Datenbankzugriff erforderlich

---

## 2. Python-Installation

### 2.1 Python herunterladen

1. Besuchen Sie [python.org/downloads](https://www.python.org/downloads/)
2. Laden Sie Python 3.12.x (oder höher) für Windows herunter
3. Wählen Sie die 64-bit Version

### 2.2 Python installieren

1. Starten Sie den Installer
2. **WICHTIG:** Aktivieren Sie "Add Python to PATH"
3. Klicken Sie auf "Customize installation"
4. Aktivieren Sie alle Optionen
5. Wählen Sie "Install for all users"
6. Klicken Sie auf "Install"

### 2.3 Installation überprüfen

Öffnen Sie PowerShell und führen Sie aus:

```powershell
python --version
# Erwartete Ausgabe: Python 3.12.x

pip --version
# Erwartete Ausgabe: pip 23.x.x
```

Falls `python` nicht gefunden wird:

```powershell
# Alternativer Pfad prüfen
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" --version
```

---

## 3. HolzbauERP-Installation

### 3.1 Dateien entpacken

1. Entpacken Sie das HolzbauERP-Archiv in einen Ordner Ihrer Wahl
2. Empfohlener Pfad: `C:\HolzbauERP` oder `C:\Users\[Benutzername]\Desktop\erp`

### 3.2 Automatische Installation

**Option A: Batch-Datei (empfohlen)**

1. Navigieren Sie zum HolzbauERP-Ordner
2. Doppelklicken Sie auf `HolzbauERP.bat`
3. Die Installation erfolgt automatisch beim ersten Start

**Option B: PowerShell-Script**

1. Öffnen Sie PowerShell als Administrator
2. Navigieren Sie zum HolzbauERP-Ordner:
   ```powershell
   cd C:\Users\[Benutzername]\Desktop\erp
   ```
3. Führen Sie das Script aus:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\HolzbauERP.ps1
   ```

### 3.3 Manuelle Installation

Falls die automatische Installation fehlschlägt:

```powershell
# 1. Zum Ordner navigieren
cd C:\Users\[Benutzername]\Desktop\erp

# 2. Virtuelle Umgebung erstellen
python -m venv venv

# 3. Virtuelle Umgebung aktivieren
.\venv\Scripts\Activate.ps1

# 4. Abhängigkeiten installieren
pip install -r requirements.txt

# 5. Anwendung starten
python -m app.main
```

---

## 4. Datenbank-Konfiguration

### 4.1 Cloud-Datenbank (Standard)

Die Datenbankverbindung ist bereits in `dbcredentials.txt.txt` konfiguriert.

**Struktur der Credentials-Datei:**
```
host=server.db.example.com
port=5432
database=holzbauerp
user=app_user
password=secure_password
```

### 4.2 Lokale Datenbank (Optional)

Falls Sie eine lokale PostgreSQL-Datenbank verwenden möchten:

1. Installieren Sie PostgreSQL von [postgresql.org](https://www.postgresql.org/download/)
2. Erstellen Sie eine neue Datenbank:
   ```sql
   CREATE DATABASE holzbauerp;
   CREATE USER erp_user WITH PASSWORD 'ihr_passwort';
   GRANT ALL PRIVILEGES ON DATABASE holzbauerp TO erp_user;
   ```
3. Aktualisieren Sie `dbcredentials.txt.txt`:
   ```
   host=localhost
   port=5432
   database=holzbauerp
   user=erp_user
   password=ihr_passwort
   ```

### 4.3 SSL-Zertifikate

Für sichere Verbindungen zur Cloud-Datenbank:

1. Legen Sie das CA-Zertifikat in `certs/ca.crt` ab
2. Das Zertifikat wird automatisch verwendet

---

## 5. Erster Start

### 5.1 Anwendung starten

1. Doppelklicken Sie auf `HolzbauERP.bat`
2. Warten Sie, bis die Anwendung geladen ist

### 5.2 Erstanmeldung

**Standard-Anmeldedaten:**
- E-Mail: `admin@demo.de`
- Passwort: `admin123`

⚠️ **WICHTIG:** Ändern Sie das Passwort nach der ersten Anmeldung!

### 5.3 Initiale Einrichtung

Nach der ersten Anmeldung:

1. **Firmendaten konfigurieren**
   - Einstellungen → Firmendaten
   - Füllen Sie alle Pflichtfelder aus

2. **Benutzer anlegen**
   - Einstellungen → Benutzer
   - Erstellen Sie Konten für Ihre Mitarbeiter

3. **Grundeinstellungen**
   - Nummernkreise konfigurieren
   - Standardwerte festlegen

---

## 6. Fehlerbehebung

### 6.1 Python nicht gefunden

**Problem:**
```
Python wurde nicht gefunden
```

**Lösung:**
1. Öffnen Sie Windows-Einstellungen → Apps → Apps & Features
2. Suchen Sie nach "App-Ausführungsaliase"
3. Deaktivieren Sie "python.exe" und "python3.exe"
4. Installieren Sie Python neu mit "Add to PATH"

### 6.2 Datenbankverbindung fehlgeschlagen

**Problem:**
```
connection to server failed: server closed the connection unexpectedly
```

**Lösungen:**
1. Prüfen Sie Ihre Internetverbindung
2. Überprüfen Sie die Credentials in `dbcredentials.txt.txt`
3. Stellen Sie sicher, dass Ihre IP-Adresse freigegeben ist
4. Prüfen Sie, ob eine Firewall die Verbindung blockiert

### 6.3 Module nicht gefunden

**Problem:**
```
ModuleNotFoundError: No module named 'PyQt6'
```

**Lösung:**
```powershell
# Virtuelle Umgebung aktivieren
.\venv\Scripts\Activate.ps1

# Abhängigkeiten neu installieren
pip install --force-reinstall -r requirements.txt
```

### 6.4 SSL-Fehler

**Problem:**
```
SSL certificate verify failed
```

**Lösung:**
1. Stellen Sie sicher, dass `certs/ca.crt` vorhanden ist
2. Oder deaktivieren Sie SSL-Verifizierung (nicht empfohlen für Produktion):
   ```python
   # In shared/config.py
   SSL_VERIFY = False
   ```

### 6.5 Berechtigungsfehler

**Problem:**
```
PermissionError: [Errno 13] Permission denied
```

**Lösung:**
1. Führen Sie PowerShell als Administrator aus
2. Oder verschieben Sie den Ordner in ein Verzeichnis mit Schreibrechten

### 6.6 UI-Darstellungsprobleme

**Problem:**
Unscharfe oder verzerrte Darstellung

**Lösung:**
1. Rechtsklick auf `HolzbauERP.bat` → Eigenschaften
2. Kompatibilität → Hohe DPI-Einstellungen ändern
3. Aktivieren Sie "Hohe DPI-Skalierung überschreiben"

---

## Kontakt & Support

Bei weiteren Problemen:

- **E-Mail:** support@holzbauerp.de
- **Telefon:** +49 (0) 123 456789
- **Geschäftszeiten:** Mo-Fr 8:00-17:00 Uhr

---

© 2025 HolzbauERP. Alle Rechte vorbehalten.
