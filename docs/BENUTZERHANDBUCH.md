# HolzbauERP - Benutzerhandbuch

## Inhaltsverzeichnis

1. [Erste Schritte](#1-erste-schritte)
2. [Dashboard](#2-dashboard)
3. [Kundenverwaltung](#3-kundenverwaltung)
4. [Projektverwaltung](#4-projektverwaltung)
5. [Bautagebuch](#5-bautagebuch)
6. [Materialwirtschaft](#6-materialwirtschaft)
7. [Finanzverwaltung](#7-finanzverwaltung)
8. [Personalwesen](#8-personalwesen)
9. [Fuhrpark & Geräte](#9-fuhrpark--geräte)
10. [Qualitätsmanagement](#10-qualitätsmanagement)
11. [Banking-Integration](#11-banking-integration)
12. [Machine Learning](#12-machine-learning)
13. [Einstellungen](#13-einstellungen)

---

## 1. Erste Schritte

### 1.1 Anmeldung

1. Starten Sie HolzbauERP über die Desktop-Verknüpfung oder `HolzbauERP.bat`
2. Geben Sie Ihre E-Mail-Adresse ein
3. Geben Sie Ihr Passwort ein
4. Optional: Aktivieren Sie "Angemeldet bleiben"
5. Klicken Sie auf "Anmelden"

### 1.2 Erstmalige Einrichtung

Bei der ersten Anmeldung als Administrator:
1. Richten Sie Ihre Firmendaten ein
2. Erstellen Sie Benutzerkonten für Ihre Mitarbeiter
3. Konfigurieren Sie die Grundeinstellungen

### 1.3 Navigation

Die Hauptnavigation befindet sich auf der linken Seite:

| Symbol | Modul | Beschreibung |
|--------|-------|--------------|
| 🏠 | Dashboard | Übersicht und Kennzahlen |
| 👥 | Kunden | Kundenverwaltung |
| 🏗️ | Projekte | Projektverwaltung |
| 📋 | Bautagebuch | Tägliche Dokumentation |
| 📦 | Material | Lagerverwaltung |
| 💰 | Finanzen | Buchhaltung und Rechnungen |
| 👷 | Personal | Mitarbeiterverwaltung |
| 🚛 | Fuhrpark | Fahrzeuge und Geräte |
| ✅ | Qualität | Qualitätsmanagement |
| ⚙️ | Einstellungen | Systemkonfiguration |

---

## 2. Dashboard

Das Dashboard bietet eine Übersicht über die wichtigsten Kennzahlen:

### 2.1 KPI-Karten

- **Aktive Projekte:** Anzahl laufender Projekte
- **Offene Angebote:** Wert offener Angebote in Euro
- **Umsatz (Monat):** Aktueller Monatsumsatz
- **Offene Rechnungen:** Summe unbezahlter Rechnungen

### 2.2 Diagramme

- **Umsatzentwicklung:** Monatliche Umsatzübersicht
- **Projektfortschritt:** Status aller aktiven Projekte
- **Top-Kunden:** Umsatzstärkste Kunden

### 2.3 Schnellaktionen

- Neuen Kunden anlegen
- Neues Projekt erstellen
- Rechnung erstellen
- Material bestellen

---

## 3. Kundenverwaltung

### 3.1 Kundenübersicht

Die Kundenübersicht zeigt alle Kunden in einer Tabelle:

| Spalte | Beschreibung |
|--------|--------------|
| Kundennummer | Eindeutige Identifikation |
| Typ | Privat/Geschäftskunde |
| Name/Firma | Kundenname oder Firmenbezeichnung |
| Ort | Standort des Kunden |
| Telefon | Hauptkontaktnummer |
| Status | Aktiv/Inaktiv/Gesperrt |

### 3.2 Neuen Kunden anlegen

1. Klicken Sie auf "Neuer Kunde"
2. Wählen Sie den Kundentyp (Privat/Geschäftlich)
3. Füllen Sie die Pflichtfelder aus:
   - Bei Privatkunden: Nachname
   - Bei Geschäftskunden: Firmenname
4. Ergänzen Sie weitere Informationen:

#### Stammdaten
- Anrede, Vorname, Nachname
- Firmenname (bei Geschäftskunden)
- USt-IdNr., Handelsregister

#### Kontaktdaten
- E-Mail, Telefon, Mobil, Fax
- Website
- Bevorzugte Kontaktmethode
- Erreichbarkeitszeiten

#### Adressdaten
- Straße, Hausnummer
- PLZ, Ort, Bundesland, Land
- Geo-Koordinaten (optional)
- Lieferadresse (falls abweichend)

#### Zahlungsinformationen
- Zahlungsziel (Tage)
- Kreditlimit
- Skonto
- Bankverbindung

5. Klicken Sie auf "Speichern"

### 3.3 Kunden bearbeiten

1. Wählen Sie einen Kunden in der Liste
2. Klicken Sie auf "Bearbeiten" oder Doppelklick
3. Ändern Sie die gewünschten Daten
4. Klicken Sie auf "Speichern"

### 3.4 Kunden suchen

- **Schnellsuche:** Geben Sie einen Suchbegriff in das Suchfeld ein
- **Filter:** Verwenden Sie die Filteroptionen für erweiterte Suche
  - Nach Kundentyp
  - Nach Status
  - Nach PLZ/Ort
  - Nach Erstelldatum

### 3.5 Kundenakte

Die Kundenakte enthält alle Informationen zu einem Kunden:

- **Übersicht:** Stammdaten und Kontaktinformationen
- **Projekte:** Alle Projekte des Kunden
- **Angebote:** Erstellte Angebote
- **Rechnungen:** Rechnungshistorie
- **Aktivitäten:** Kommunikationshistorie
- **Dokumente:** Angehängte Dateien
- **Notizen:** Interne Vermerke

---

## 4. Projektverwaltung

### 4.1 Projektübersicht

Zeigt alle Projekte mit Status und Fortschritt:

| Spalte | Beschreibung |
|--------|--------------|
| Projektnummer | Eindeutige Kennung |
| Projektname | Bezeichnung des Projekts |
| Kunde | Zugeordneter Kunde |
| Status | Planung/Aktiv/Abgeschlossen |
| Fortschritt | Prozentuale Fertigstellung |
| Fällig | Geplantes Enddatum |

### 4.2 Neues Projekt anlegen

1. Klicken Sie auf "Neues Projekt"
2. Füllen Sie die Projektdaten aus:

#### Grunddaten
- Projektname
- Projektnummer (wird automatisch generiert)
- Projekttyp (Neubau, Anbau, Sanierung, etc.)
- Beschreibung

#### Kunde & Kontakt
- Kunde auswählen
- Ansprechpartner
- Bauleiter

#### Standort
- Adresse der Baustelle
- Geo-Koordinaten
- Höhe über NN
- Flurstück, Gemarkung

#### Zeitplanung
- Geplanter Start
- Geplantes Ende
- Meilensteine

#### Budget
- Gesamtbudget
- Kostenrahmen
- Zahlungsplan

3. Klicken Sie auf "Speichern"

### 4.3 Projektdetails

In der Projektansicht finden Sie:

#### Tabs
- **Übersicht:** Projektdaten und KPIs
- **Zeitplan:** Gantt-Diagramm und Meilensteine
- **Kosten:** Budget und Ist-Kosten
- **Material:** Materialbedarf und Bestellungen
- **Personal:** Zugewiesene Mitarbeiter
- **Dokumente:** Pläne, Genehmigungen, Verträge
- **Bautagebuch:** Tägliche Einträge
- **Mängel:** Erfasste Mängel
- **Fotos:** Baudokumentation

### 4.4 Meilensteine

Meilensteine markieren wichtige Projektphasen:

1. Klicken Sie auf "Meilenstein hinzufügen"
2. Geben Sie Bezeichnung und Datum ein
3. Optional: Fügen Sie Abhängigkeiten hinzu
4. Speichern Sie den Meilenstein

### 4.5 Projektfortschritt

Der Fortschritt wird berechnet aus:
- Abgeschlossenen Meilensteinen
- Erfassten Arbeitsstunden
- Verbrauchtem Material

---

## 5. Bautagebuch

### 5.1 Übersicht

Das Bautagebuch dokumentiert den täglichen Baufortschritt:

- Wetterdaten
- Anwesendes Personal
- Durchgeführte Arbeiten
- Materialverbrauch
- Besondere Vorkommnisse

### 5.2 Neuen Eintrag erstellen

1. Wählen Sie das Projekt aus
2. Klicken Sie auf "Neuer Eintrag"
3. Das aktuelle Datum wird automatisch eingetragen

#### Wetterdaten
| Feld | Beschreibung |
|------|--------------|
| Temperatur | Morgens/Mittags/Abends in °C |
| Niederschlag | Regen, Schnee, etc. |
| Wind | Windstärke und -richtung |
| Witterung | Sonnig, bewölkt, etc. |

#### Personal
- Eigene Mitarbeiter (Name, Stunden, Tätigkeit)
- Subunternehmer (Firma, Anzahl, Tätigkeit)
- Besucher (Name, Firma, Grund)

#### Arbeiten
- Durchgeführte Tätigkeiten
- Verwendete Materialien
- Eingesetzte Geräte/Maschinen

#### Lieferungen
- Datum/Uhrzeit
- Lieferant
- Material und Menge
- Lieferschein-Nr.

#### Vorkommnisse
- Unterbrechungen
- Unfälle
- Mängel
- Abweichungen vom Plan

#### Fotos
- Fortschrittsfotos
- Detailaufnahmen
- Problembereiche

4. Klicken Sie auf "Speichern"

### 5.3 Einträge exportieren

- **PDF:** Einzelner Eintrag oder Zeitraum
- **Excel:** Für weitere Verarbeitung
- **Druck:** Direktausdruck

---

## 6. Materialwirtschaft

### 6.1 Artikelstamm

#### Neuen Artikel anlegen
1. Klicken Sie auf "Neuer Artikel"
2. Füllen Sie die Artikeldaten aus:

**Grunddaten:**
- Artikelnummer (automatisch oder manuell)
- Bezeichnung
- Kategorie
- Einheit

**Technische Daten:**
- Abmessungen (Länge, Breite, Höhe)
- Gewicht
- Material
- Holzart und Qualität

**Preise:**
- Einkaufspreis
- Verkaufspreis
- Staffelpreise

**Lager:**
- Lagerort
- Mindestbestand
- Bestellmenge

### 6.2 Lagerübersicht

Zeigt alle Artikel mit aktuellem Bestand:

| Spalte | Bedeutung |
|--------|-----------|
| 🟢 | Bestand ausreichend |
| 🟡 | Bestand knapp |
| 🔴 | Bestand unterschritten |

### 6.3 Wareneingang

1. Klicken Sie auf "Wareneingang"
2. Wählen Sie die Bestellung oder geben Sie manuell ein
3. Erfassen Sie:
   - Artikel
   - Menge
   - Lieferschein-Nr.
   - Qualitätsprüfung
4. Bestätigen Sie den Eingang

### 6.4 Warenausgang

1. Wählen Sie das Projekt/die Kostenstelle
2. Erfassen Sie die entnommenen Artikel
3. Optional: Scannen Sie Barcodes
4. Bestätigen Sie den Ausgang

### 6.5 Inventur

1. Starten Sie eine neue Inventur
2. Zählen Sie die Bestände
3. Erfassen Sie die Zählmengen
4. Prüfen Sie Differenzen
5. Buchen Sie die Inventur

---

## 7. Finanzverwaltung

### 7.1 Buchhaltung

#### Kontenplan
Basierend auf SKR03 oder SKR04 (konfigurierbar):

| Klasse | Bezeichnung |
|--------|-------------|
| 0 | Anlage- und Kapitalkonten |
| 1 | Finanz- und Privatkonten |
| 2 | Abgrenzungskonten |
| 3 | Wareneingangskonten |
| 4 | Betriebliche Aufwendungen |
| 5-6 | (nicht belegt in SKR03) |
| 7 | Bestände |
| 8 | Erlöskonten |
| 9 | Vortrags- und Kapitalkonten |

#### Buchungen erfassen
1. Klicken Sie auf "Neue Buchung"
2. Wählen Sie die Buchungsart
3. Geben Sie ein:
   - Datum
   - Sollkonto
   - Habenkonto
   - Betrag
   - Belegnummer
   - Buchungstext
4. Speichern Sie die Buchung

### 7.2 Rechnungen

#### Rechnung erstellen
1. Klicken Sie auf "Neue Rechnung"
2. Wählen Sie den Kunden
3. Optional: Verknüpfen Sie ein Projekt
4. Fügen Sie Positionen hinzu:
   - Artikel aus Katalog
   - Freie Positionen
   - Arbeitszeiten
5. Prüfen Sie die Summen
6. Speichern oder direkt versenden

#### Rechnungsstatus
| Status | Bedeutung |
|--------|-----------|
| Entwurf | Noch nicht versendet |
| Versendet | An Kunden übermittelt |
| Bezahlt | Vollständig beglichen |
| Teilbezahlt | Teilzahlung eingegangen |
| Überfällig | Zahlungsziel überschritten |
| Storniert | Rechnung ungültig |

### 7.3 Mahnwesen

1. Überfällige Rechnungen werden automatisch markiert
2. Wählen Sie Rechnungen für Mahnlauf
3. Erstellen Sie Mahnungen (1., 2., 3. Mahnung)
4. Versenden Sie per E-Mail oder Post

### 7.4 Zahlungen

#### Zahlungseingang erfassen
1. Öffnen Sie die Rechnung
2. Klicken Sie auf "Zahlung erfassen"
3. Geben Sie ein:
   - Datum
   - Betrag
   - Zahlungsart
   - Referenz
4. Speichern Sie die Zahlung

### 7.5 Auswertungen

- **BWA:** Betriebswirtschaftliche Auswertung
- **USt-VA:** Umsatzsteuer-Voranmeldung
- **Offene Posten:** Debitoren/Kreditoren
- **Cashflow:** Liquiditätsübersicht

---

## 8. Personalwesen

### 8.1 Mitarbeiterverwaltung

#### Neuen Mitarbeiter anlegen
1. Klicken Sie auf "Neuer Mitarbeiter"
2. Erfassen Sie:

**Persönliche Daten:**
- Name, Vorname
- Geburtsdatum
- Adresse
- Kontaktdaten
- Bankverbindung

**Beschäftigung:**
- Personalnummer
- Eintrittsdatum
- Abteilung
- Position
- Vorgesetzter

**Vertrag:**
- Vertragsart
- Arbeitszeit
- Urlaubsanspruch
- Gehalt/Stundenlohn

**Qualifikationen:**
- Ausbildung
- Zertifikate
- Führerscheine
- Schulungen

### 8.2 Zeiterfassung

1. Mitarbeiter meldet sich an
2. Projekt/Tätigkeit auswählen
3. Start-/Endzeit wird erfasst
4. Pausen werden abgezogen
5. Zeiten werden freigegeben

### 8.3 Lohnabrechnung

#### Monatliche Abrechnung
1. Prüfen Sie die Zeitdaten
2. Erfassen Sie Zulagen/Abzüge
3. Berechnen Sie die Abrechnung
4. Erstellen Sie die Abrechnungen
5. Exportieren Sie für DATEV

### 8.4 Urlaubsverwaltung

- Anträge stellen
- Genehmigung durch Vorgesetzten
- Kalenderübersicht
- Resturlaub-Anzeige

---

## 9. Fuhrpark & Geräte

### 9.1 Fahrzeugverwaltung

#### Neues Fahrzeug anlegen
1. Klicken Sie auf "Neues Fahrzeug"
2. Erfassen Sie:
   - Kennzeichen
   - Fahrzeugtyp
   - Hersteller/Modell
   - Erstzulassung
   - Fahrgestellnummer

**Termine:**
- TÜV/HU
- AU
- UVV-Prüfung
- Wartung

**Kosten:**
- Versicherung
- Steuer
- Leasing/Finanzierung

### 9.2 Tankprotokoll

1. Öffnen Sie das Fahrzeug
2. Klicken Sie auf "Tanken"
3. Erfassen Sie:
   - Datum
   - Kilometerstand
   - Liter
   - Kosten
   - Tankstelle

### 9.3 Fahrtenbuch

Für jede Fahrt:
- Datum
- Start/Ziel
- Kilometerstand
- Zweck (Geschäftlich/Privat)
- Fahrer

### 9.4 Geräteverwaltung

- Betriebsstunden erfassen
- Wartungen planen
- Prüfungen dokumentieren
- Reservierungen verwalten

---

## 10. Qualitätsmanagement

### 10.1 Mängelverwaltung

#### Mangel erfassen
1. Klicken Sie auf "Neuer Mangel"
2. Wählen Sie das Projekt
3. Erfassen Sie:
   - Bezeichnung
   - Beschreibung
   - Ort (Bauteil/Raum)
   - Schweregrad
   - Fotos hochladen (Vorher-Bilder)
4. Weisen Sie Verantwortlichen zu
5. Setzen Sie Frist

#### Fotos hochladen
1. Klicken Sie auf "Fotos hinzufügen"
2. Wählen Sie Bilder aus (JPG, PNG, max. 10 MB)
3. Fotos werden in MongoDB GridFS gespeichert
4. Miniaturansichten werden im Detailbereich angezeigt
5. Klicken Sie auf ein Foto für Vollbildansicht

#### Mangel beheben
1. Dokumentieren Sie die Behebung
2. Fügen Sie Fotos (nachher) hinzu
3. Erfassen Sie Kosten
4. Markieren Sie als behoben

### 10.2 Qualitätsprüfungen

1. Wählen Sie Prüfplan
2. Führen Sie Prüfungen durch
3. Erfassen Sie Messwerte
4. Dokumentieren Sie Ergebnisse
5. Erstellen Sie Prüfbericht

### 10.3 Zertifikate

Verwalten Sie:
- CE-Kennzeichnungen
- Statik-Nachweise
- FSC/PEFC-Zertifikate
- Brandschutz-Nachweise
- Energieausweise

### 10.4 Gewährleistung

- Gewährleistungsfristen überwachen
- Einbehalte verwalten
- Bürgschaften dokumentieren

---

## 11. Banking-Integration

### 11.1 Bankkonto verbinden

HolzbauERP unterstützt über 2.000 deutsche Banken via FinTS/HBCI.

#### Neue Bankverbindung hinzufügen
1. Navigieren Sie zu Finanzen → Banking
2. Klicken Sie auf "Konto verbinden"
3. Suchen Sie Ihre Bank (Sparkasse, Volksbank, Deutsche Bank, etc.)
4. Geben Sie Ihre Online-Banking-Zugangsdaten ein
5. Bestätigen Sie mit Ihrer TAN

#### Unterstützte Banken
- Alle Sparkassen
- Alle Volks- und Raiffeisenbanken
- Deutsche Bank
- Commerzbank
- Postbank
- ING
- DKB
- HypoVereinsbank
- Und viele weitere...

### 11.2 Kontosynchronisation

- **Automatische Synchronisation:** Täglich um 6:00 Uhr
- **Manuelle Synchronisation:** Jederzeit per Klick
- **Transaktionsimport:** Umsätze werden automatisch importiert

### 11.3 Zahlungsabgleich

1. Öffnen Sie Banking → Transaktionen
2. Wählen Sie nicht zugeordnete Transaktionen
3. System schlägt passende Rechnungen vor
4. Bestätigen Sie die Zuordnung

### 11.4 SEPA-Zahlungen

- SEPA-Überweisungen erstellen
- SEPA-Lastschriften (mit Gläubiger-ID)
- Sammelaufträge für mehrere Zahlungen

---

## 12. Machine Learning

### 12.1 Verfügbare ML-Services

HolzbauERP bietet intelligente Automatisierung:

| Service | Beschreibung |
|---------|--------------|
| Kostenprognose | Projektkosten basierend auf historischen Daten vorhersagen |
| Qualitätsvorhersage | Wahrscheinlichkeit für Mängel berechnen |
| Lieferzeitoptimierung | Optimale Bestellzeitpunkte ermitteln |
| Kundenanalyse | Kundenwert und Zahlungsverhalten analysieren |

### 12.2 Kostenprognose

1. Öffnen Sie ein Projekt
2. Klicken Sie auf "KI-Prognose"
3. Das System analysiert:
   - Ähnliche vergangene Projekte
   - Materialpreise
   - Lohnkosten
   - Saisonale Faktoren
4. Ergebnis: Geschätzte Kosten mit Konfidenzintervall

### 12.3 Qualitätsvorhersage

Basierend auf Projektparametern:
- Projekttyp und -größe
- Wetterbedingungen
- Subunternehmer-Bewertungen
- Materialqualität

Das System warnt vor erhöhtem Mängelrisiko.

### 12.4 Empfehlungen aktivieren

1. Einstellungen → ML-Services
2. Aktivieren Sie gewünschte Services
3. Konfigurieren Sie Schwellenwerte für Benachrichtigungen

---

## 13. Einstellungen

### 11.1 Firmendaten

- Firmenname und Rechtsform
- Adresse
- Kontaktdaten
- Bankverbindungen
- Logo

### 11.2 Benutzerverwaltung

- Benutzer anlegen/bearbeiten
- Rollen und Rechte zuweisen
- Passwörter zurücksetzen

### 11.3 Systemeinstellungen

- Nummernkreise
- Standardwerte
- E-Mail-Vorlagen
- Druckformulare

### 11.4 Datenexport

- DATEV-Export
- Excel-Export
- PDF-Berichte
- Backup erstellen

---

## Tastenkürzel

| Kürzel | Funktion |
|--------|----------|
| Strg+N | Neu anlegen |
| Strg+S | Speichern |
| Strg+P | Drucken |
| Strg+F | Suchen |
| F1 | Hilfe |
| F5 | Aktualisieren |
| Esc | Abbrechen/Schließen |

---

## Hilfe & Support

Bei Fragen oder Problemen:

1. **In-App-Hilfe:** Drücken Sie F1
2. **E-Mail:** support@holzbauerp.de
3. **Telefon:** +49 (0) 123 456789
4. **Fernwartung:** TeamViewer ID auf Anfrage

---

© 2025 HolzbauERP. Alle Rechte vorbehalten.
