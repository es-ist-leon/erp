"""
Employee Dialog - Umfassende Mitarbeiterverwaltung für Holzbau
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QTabWidget, QWidget, QTextEdit, QMessageBox,
    QDateEdit, QScrollArea, QLabel, QDoubleSpinBox, QSpinBox, QCheckBox,
    QTimeEdit
)
from PyQt6.QtCore import Qt, QDate, QTime
import uuid
from datetime import datetime

from shared.models import Employee, EmployeeStatus, EmploymentType


class EmployeeDialog(QDialog):
    """Dialog for creating/editing employees - Vollumfängliche Erfassung"""
    
    def __init__(self, db_service, employee_id=None, user=None, parent=None):
        super().__init__(parent)
        self.db = db_service
        self.employee_id = employee_id
        self.user = user
        self.employee = None
        self.setup_ui()
        if employee_id:
            self.load_employee()
    
    def _create_section_header(self, text):
        """Erstellt einen Abschnitts-Header"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #374151;
                padding: 8px 0 4px 0;
                border-bottom: 2px solid #e5e7eb;
                margin-top: 10px;
            }
        """)
        return label
    
    def _create_scrollable_tab(self, content_widget):
        """Erstellt einen scrollbaren Tab"""
        scroll = QScrollArea()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        return scroll
    
    def setup_ui(self):
        self.setWindowTitle("Neuer Mitarbeiter" if not self.employee_id else "Mitarbeiter bearbeiten")
        self.setMinimumSize(800, 650)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # ==================== TAB 1: PERSÖNLICHE DATEN ====================
        personal_widget = QWidget()
        personal_layout = QVBoxLayout(personal_widget)
        personal_layout.setSpacing(15)
        
        # Grunddaten
        personal_layout.addWidget(self._create_section_header("👤 Persönliche Daten"))
        info_form = QFormLayout()
        info_form.setSpacing(10)
        
        self.salutation = QComboBox()
        self.salutation.addItems(["", "Herr", "Frau", "Divers"])
        info_form.addRow("Anrede:", self.salutation)
        
        self.title = QLineEdit()
        self.title.setPlaceholderText("z.B. Dr., Dipl.-Ing.")
        info_form.addRow("Titel:", self.title)
        
        self.first_name = QLineEdit()
        info_form.addRow("Vorname*:", self.first_name)
        
        self.last_name = QLineEdit()
        info_form.addRow("Nachname*:", self.last_name)
        
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setSpecialValueText("Nicht angegeben")
        info_form.addRow("Geburtsdatum:", self.birth_date)
        
        self.birth_place = QLineEdit()
        self.birth_place.setPlaceholderText("Geburtsort")
        info_form.addRow("Geburtsort:", self.birth_place)
        
        self.nationality = QLineEdit()
        self.nationality.setText("Deutsch")
        info_form.addRow("Staatsangehörigkeit:", self.nationality)
        
        self.marital_status = QComboBox()
        self.marital_status.addItems(["", "Ledig", "Verheiratet", "Geschieden", "Verwitwet"])
        info_form.addRow("Familienstand:", self.marital_status)
        
        self.children_count = QSpinBox()
        self.children_count.setRange(0, 20)
        info_form.addRow("Kinder:", self.children_count)
        personal_layout.addLayout(info_form)
        
        # Kontaktdaten
        personal_layout.addWidget(self._create_section_header("📞 Kontaktdaten"))
        contact_form = QFormLayout()
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("privat@email.de")
        contact_form.addRow("E-Mail (privat):", self.email)
        
        self.email_work = QLineEdit()
        self.email_work.setPlaceholderText("arbeit@firma.de")
        contact_form.addRow("E-Mail (Arbeit):", self.email_work)
        
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+49 123 456789")
        contact_form.addRow("Telefon:", self.phone)
        
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("+49 171 1234567")
        contact_form.addRow("Mobil:", self.mobile)
        
        self.mobile_work = QLineEdit()
        self.mobile_work.setPlaceholderText("Diensthandy")
        contact_form.addRow("Mobil (Arbeit):", self.mobile_work)
        
        self.emergency_contact = QLineEdit()
        self.emergency_contact.setPlaceholderText("Name und Telefon")
        contact_form.addRow("Notfallkontakt:", self.emergency_contact)
        personal_layout.addLayout(contact_form)
        
        personal_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(personal_widget), "👤 Persönlich")
        
        # ==================== TAB 2: ADRESSE ====================
        address_widget = QWidget()
        address_layout = QVBoxLayout(address_widget)
        address_layout.setSpacing(15)
        
        # Hauptadresse
        address_layout.addWidget(self._create_section_header("🏠 Wohnadresse"))
        addr_form = QFormLayout()
        
        self.street = QLineEdit()
        addr_form.addRow("Straße:", self.street)
        
        self.street_number = QLineEdit()
        self.street_number.setMaximumWidth(80)
        addr_form.addRow("Hausnummer:", self.street_number)
        
        self.address_extra = QLineEdit()
        self.address_extra.setPlaceholderText("Zusatz (z.B. Hinterhaus, 3. OG)")
        addr_form.addRow("Adresszusatz:", self.address_extra)
        
        self.postal_code = QLineEdit()
        self.postal_code.setMaximumWidth(100)
        addr_form.addRow("PLZ:", self.postal_code)
        
        self.city = QLineEdit()
        addr_form.addRow("Stadt:", self.city)
        
        self.state = QLineEdit()
        self.state.setPlaceholderText("z.B. Bayern")
        addr_form.addRow("Bundesland:", self.state)
        
        self.country = QLineEdit()
        self.country.setText("Deutschland")
        addr_form.addRow("Land:", self.country)
        
        self.distance_to_work = QSpinBox()
        self.distance_to_work.setRange(0, 999)
        self.distance_to_work.setSuffix(" km")
        addr_form.addRow("Entfernung zur Arbeit:", self.distance_to_work)
        address_layout.addLayout(addr_form)
        
        address_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(address_widget), "🏠 Adresse")
        
        # ==================== TAB 3: BESCHÄFTIGUNG ====================
        emp_widget = QWidget()
        emp_layout = QVBoxLayout(emp_widget)
        emp_layout.setSpacing(15)
        
        # Beschäftigungsdaten
        emp_layout.addWidget(self._create_section_header("💼 Beschäftigung"))
        emp_form = QFormLayout()
        
        self.employee_number = QLineEdit()
        self.employee_number.setPlaceholderText("Wird automatisch generiert")
        self.employee_number.setEnabled(False)
        emp_form.addRow("Personalnummer:", self.employee_number)
        
        self.position = QLineEdit()
        self.position.setPlaceholderText("z.B. Zimmermann, Monteur, Bauleiter")
        emp_form.addRow("Position:", self.position)
        
        self.department = QComboBox()
        self.department.setEditable(True)
        self.department.addItems([
            "Produktion", "Montage", "Abbund", "Planung", "CAD/Arbeitsvorbereitung",
            "Bauleitung", "Lager", "Verwaltung", "Buchhaltung", "Einkauf",
            "Vertrieb", "Geschäftsführung"
        ])
        emp_form.addRow("Abteilung:", self.department)
        
        self.team = QLineEdit()
        self.team.setPlaceholderText("z.B. Montagekolonne 1, Team Nord")
        emp_form.addRow("Team/Kolonne:", self.team)
        
        self.supervisor = QLineEdit()
        self.supervisor.setPlaceholderText("Name des Vorgesetzten")
        emp_form.addRow("Vorgesetzter:", self.supervisor)
        
        self.employment_type = QComboBox()
        self.employment_type.addItem("Vollzeit", "fulltime")
        self.employment_type.addItem("Teilzeit", "parttime")
        self.employment_type.addItem("Ausbildung", "apprentice")
        self.employment_type.addItem("Minijob (520€)", "minijob")
        self.employment_type.addItem("Werkstudent", "werkstudent")
        self.employment_type.addItem("Praktikant", "praktikant")
        self.employment_type.addItem("Freiberufler", "freelancer")
        emp_form.addRow("Beschäftigungsart:", self.employment_type)
        
        self.status = QComboBox()
        self.status.addItem("Aktiv", "active")
        self.status.addItem("Inaktiv", "inactive")
        self.status.addItem("Krank", "sick")
        self.status.addItem("Urlaub", "on_leave")
        self.status.addItem("Elternzeit", "parental_leave")
        self.status.addItem("Probezeit", "probation")
        self.status.addItem("Gekündigt", "notice")
        self.status.addItem("Ausgeschieden", "terminated")
        emp_form.addRow("Status:", self.status)
        emp_layout.addLayout(emp_form)
        
        # Termine
        emp_layout.addWidget(self._create_section_header("📅 Beschäftigungszeitraum"))
        dates_form = QFormLayout()
        
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        dates_form.addRow("Eintrittsdatum:", self.hire_date)
        
        self.probation_end = QDateEdit()
        self.probation_end.setCalendarPopup(True)
        self.probation_end.setDate(QDate.currentDate().addMonths(6))
        dates_form.addRow("Ende Probezeit:", self.probation_end)
        
        self.contract_end = QDateEdit()
        self.contract_end.setCalendarPopup(True)
        self.contract_end.setSpecialValueText("Unbefristet")
        dates_form.addRow("Vertragsende:", self.contract_end)
        
        self.termination_date = QDateEdit()
        self.termination_date.setCalendarPopup(True)
        self.termination_date.setSpecialValueText("Nicht ausgeschieden")
        dates_form.addRow("Austrittsdatum:", self.termination_date)
        emp_layout.addLayout(dates_form)
        
        emp_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(emp_widget), "💼 Beschäftigung")
        
        # ==================== TAB 4: ARBEITSZEIT & VERGÜTUNG ====================
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setSpacing(15)
        
        # Arbeitszeit
        time_layout.addWidget(self._create_section_header("⏰ Arbeitszeit"))
        time_form = QFormLayout()
        
        self.weekly_hours = QDoubleSpinBox()
        self.weekly_hours.setRange(0, 60)
        self.weekly_hours.setDecimals(1)
        self.weekly_hours.setValue(40)
        self.weekly_hours.setSuffix(" Std/Woche")
        time_form.addRow("Wochenstunden:", self.weekly_hours)
        
        self.work_start = QTimeEdit()
        self.work_start.setTime(QTime(7, 0))
        time_form.addRow("Arbeitsbeginn:", self.work_start)
        
        self.work_end = QTimeEdit()
        self.work_end.setTime(QTime(16, 0))
        time_form.addRow("Arbeitsende:", self.work_end)
        
        self.break_duration = QSpinBox()
        self.break_duration.setRange(0, 120)
        self.break_duration.setValue(45)
        self.break_duration.setSuffix(" min")
        time_form.addRow("Pause:", self.break_duration)
        
        self.vacation_days = QSpinBox()
        self.vacation_days.setRange(0, 40)
        self.vacation_days.setValue(30)
        self.vacation_days.setSuffix(" Tage/Jahr")
        time_form.addRow("Urlaubsanspruch:", self.vacation_days)
        
        self.overtime_account = QDoubleSpinBox()
        self.overtime_account.setRange(-999, 999)
        self.overtime_account.setDecimals(1)
        self.overtime_account.setSuffix(" Std")
        time_form.addRow("Überstunden-Konto:", self.overtime_account)
        time_layout.addLayout(time_form)
        
        # Vergütung
        time_layout.addWidget(self._create_section_header("💰 Vergütung"))
        wage_form = QFormLayout()
        
        self.wage_type = QComboBox()
        self.wage_type.addItems(["Monatslohn", "Stundenlohn", "Leistungslohn"])
        wage_form.addRow("Lohnart:", self.wage_type)
        
        self.hourly_rate = QDoubleSpinBox()
        self.hourly_rate.setRange(0, 999)
        self.hourly_rate.setDecimals(2)
        self.hourly_rate.setSuffix(" €/Std")
        wage_form.addRow("Stundensatz:", self.hourly_rate)
        
        self.monthly_salary = QDoubleSpinBox()
        self.monthly_salary.setRange(0, 99999)
        self.monthly_salary.setDecimals(2)
        self.monthly_salary.setSuffix(" €/Monat")
        wage_form.addRow("Monatslohn brutto:", self.monthly_salary)
        
        self.cost_rate = QDoubleSpinBox()
        self.cost_rate.setRange(0, 999)
        self.cost_rate.setDecimals(2)
        self.cost_rate.setSuffix(" €/Std")
        wage_form.addRow("Verrechnungssatz:", self.cost_rate)
        
        self.tax_class = QComboBox()
        self.tax_class.addItems(["", "1", "2", "3", "4", "5", "6"])
        wage_form.addRow("Steuerklasse:", self.tax_class)
        time_layout.addLayout(wage_form)
        
        # Bankdaten
        time_layout.addWidget(self._create_section_header("🏦 Bankverbindung"))
        bank_form = QFormLayout()
        
        self.bank_name = QLineEdit()
        bank_form.addRow("Bank:", self.bank_name)
        
        self.iban = QLineEdit()
        self.iban.setPlaceholderText("DE89 3704 0044 0532 0130 00")
        bank_form.addRow("IBAN:", self.iban)
        
        self.bic = QLineEdit()
        bank_form.addRow("BIC:", self.bic)
        time_layout.addLayout(bank_form)
        
        time_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(time_widget), "⏰ Arbeitszeit")
        
        # ==================== TAB 5: QUALIFIKATIONEN ====================
        qual_widget = QWidget()
        qual_layout = QVBoxLayout(qual_widget)
        qual_layout.setSpacing(15)
        
        # Ausbildung
        qual_layout.addWidget(self._create_section_header("🎓 Ausbildung"))
        edu_form = QFormLayout()
        
        self.profession = QComboBox()
        self.profession.setEditable(True)
        self.profession.addItems([
            "", "Zimmerer/Zimmerin", "Zimmermeister/in", "Holzbauingenieur/in",
            "Techniker/in Holzbau", "Holzmechaniker/in", "Tischler/in",
            "Bauingenieur/in", "Architekt/in", "Kaufmann/-frau", "Sonstige"
        ])
        edu_form.addRow("Beruf:", self.profession)
        
        self.highest_education = QComboBox()
        self.highest_education.addItems([
            "", "Hauptschule", "Mittlere Reife", "Abitur", "Berufsausbildung",
            "Meister", "Techniker", "Bachelor", "Master", "Diplom", "Promotion"
        ])
        edu_form.addRow("Höchster Abschluss:", self.highest_education)
        
        self.apprentice_year = QSpinBox()
        self.apprentice_year.setRange(0, 4)
        self.apprentice_year.setSpecialValueText("Keine Ausbildung")
        edu_form.addRow("Lehrjahr (falls Azubi):", self.apprentice_year)
        qual_layout.addLayout(edu_form)
        
        # Führerscheine
        qual_layout.addWidget(self._create_section_header("🚗 Führerscheine"))
        license_form = QFormLayout()
        
        self.license_b = QCheckBox("B (PKW)")
        license_form.addRow("", self.license_b)
        
        self.license_be = QCheckBox("BE (PKW + Anhänger)")
        license_form.addRow("", self.license_be)
        
        self.license_c = QCheckBox("C (LKW)")
        license_form.addRow("", self.license_c)
        
        self.license_ce = QCheckBox("CE (LKW + Anhänger)")
        license_form.addRow("", self.license_ce)
        
        self.forklift_license = QCheckBox("Staplerschein")
        license_form.addRow("", self.forklift_license)
        
        self.crane_license = QCheckBox("Kranschein")
        license_form.addRow("", self.crane_license)
        
        self.lift_license = QCheckBox("Hebebühnenschein")
        license_form.addRow("", self.lift_license)
        qual_layout.addLayout(license_form)
        
        # Zusatzqualifikationen
        qual_layout.addWidget(self._create_section_header("🛠️ Zusatzqualifikationen"))
        skills_form = QFormLayout()
        
        self.first_aid = QCheckBox("Ersthelfer")
        skills_form.addRow("", self.first_aid)
        
        self.first_aid_date = QDateEdit()
        self.first_aid_date.setCalendarPopup(True)
        self.first_aid_date.setSpecialValueText("Nicht absolviert")
        skills_form.addRow("Ersthelfer gültig bis:", self.first_aid_date)
        
        self.safety_officer = QCheckBox("Sicherheitsbeauftragter")
        skills_form.addRow("", self.safety_officer)
        
        self.fire_warden = QCheckBox("Brandschutzhelfer")
        skills_form.addRow("", self.fire_warden)
        
        self.scaffolding_cert = QCheckBox("Gerüstbau-Berechtigung")
        skills_form.addRow("", self.scaffolding_cert)
        
        self.chainsaw_cert = QCheckBox("Motorsägenschein")
        skills_form.addRow("", self.chainsaw_cert)
        
        self.welding_cert = QLineEdit()
        self.welding_cert.setPlaceholderText("z.B. Schweißprüfung EN 287")
        skills_form.addRow("Schweißzertifikat:", self.welding_cert)
        
        self.skills = QTextEdit()
        self.skills.setMaximumHeight(80)
        self.skills.setPlaceholderText("Weitere Fähigkeiten (z.B. CAD, CNC-Abbund, ...)")
        skills_form.addRow("Sonstige Skills:", self.skills)
        qual_layout.addLayout(skills_form)
        
        qual_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(qual_widget), "🎓 Qualifikationen")
        
        # ==================== TAB 6: GESUNDHEIT & SICHERHEIT ====================
        health_widget = QWidget()
        health_layout = QVBoxLayout(health_widget)
        health_layout.setSpacing(15)
        
        # Arbeitsmedizin
        health_layout.addWidget(self._create_section_header("🏥 Arbeitsmedizinische Vorsorge"))
        health_form = QFormLayout()
        
        self.g25_date = QDateEdit()
        self.g25_date.setCalendarPopup(True)
        self.g25_date.setSpecialValueText("Nicht durchgeführt")
        health_form.addRow("G25 (Fahrtätigkeit):", self.g25_date)
        
        self.g37_date = QDateEdit()
        self.g37_date.setCalendarPopup(True)
        self.g37_date.setSpecialValueText("Nicht durchgeführt")
        health_form.addRow("G37 (Bildschirmarbeit):", self.g37_date)
        
        self.g41_date = QDateEdit()
        self.g41_date.setCalendarPopup(True)
        self.g41_date.setSpecialValueText("Nicht durchgeführt")
        health_form.addRow("G41 (Absturzgefahr):", self.g41_date)
        
        self.health_restrictions = QTextEdit()
        self.health_restrictions.setMaximumHeight(60)
        self.health_restrictions.setPlaceholderText("Einschränkungen, Allergien (z.B. Holzstauballergie)")
        health_form.addRow("Einschränkungen:", self.health_restrictions)
        health_layout.addLayout(health_form)
        
        # PSA
        health_layout.addWidget(self._create_section_header("🦺 Persönliche Schutzausrüstung"))
        psa_form = QFormLayout()
        
        self.shoe_size = QLineEdit()
        self.shoe_size.setPlaceholderText("z.B. 44")
        self.shoe_size.setMaximumWidth(80)
        psa_form.addRow("Schuhgröße:", self.shoe_size)
        
        self.clothing_size = QComboBox()
        self.clothing_size.addItems(["", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL"])
        psa_form.addRow("Kleidergröße:", self.clothing_size)
        
        self.glove_size = QComboBox()
        self.glove_size.addItems(["", "7", "8", "9", "10", "11", "12"])
        psa_form.addRow("Handschuhgröße:", self.glove_size)
        
        self.helmet_size = QComboBox()
        self.helmet_size.addItems(["", "52-56", "54-58", "56-62", "58-64"])
        psa_form.addRow("Helmgröße:", self.helmet_size)
        health_layout.addLayout(psa_form)
        
        # Unterweisungen
        health_layout.addWidget(self._create_section_header("📋 Unterweisungen"))
        instr_form = QFormLayout()
        
        self.safety_instruction_date = QDateEdit()
        self.safety_instruction_date.setCalendarPopup(True)
        self.safety_instruction_date.setSpecialValueText("Nicht durchgeführt")
        instr_form.addRow("Sicherheitsunterweisung:", self.safety_instruction_date)
        
        self.fire_instruction_date = QDateEdit()
        self.fire_instruction_date.setCalendarPopup(True)
        self.fire_instruction_date.setSpecialValueText("Nicht durchgeführt")
        instr_form.addRow("Brandschutzunterweisung:", self.fire_instruction_date)
        health_layout.addLayout(instr_form)
        
        health_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(health_widget), "🦺 Gesundheit")
        
        # ==================== TAB 7: DOKUMENTE & IDS ====================
        docs_widget = QWidget()
        docs_layout = QVBoxLayout(docs_widget)
        docs_layout.setSpacing(15)
        
        # IDs
        docs_layout.addWidget(self._create_section_header("🪪 Identifikation"))
        id_form = QFormLayout()
        
        self.social_security_number = QLineEdit()
        self.social_security_number.setPlaceholderText("12 345678 A 123")
        id_form.addRow("Sozialversicherungs-Nr.:", self.social_security_number)
        
        self.tax_id = QLineEdit()
        self.tax_id.setPlaceholderText("Steuer-ID")
        id_form.addRow("Steuer-ID:", self.tax_id)
        
        self.health_insurance = QLineEdit()
        self.health_insurance.setPlaceholderText("Name der Krankenkasse")
        id_form.addRow("Krankenkasse:", self.health_insurance)
        
        self.pension_insurance = QLineEdit()
        self.pension_insurance.setPlaceholderText("BG Bau, SOKA-Bau, etc.")
        id_form.addRow("Zusatzversorgung:", self.pension_insurance)
        docs_layout.addLayout(id_form)
        
        # Ausweise
        docs_layout.addWidget(self._create_section_header("📄 Ausweise"))
        card_form = QFormLayout()
        
        self.id_card_number = QLineEdit()
        id_form.addRow("Personalausweis-Nr.:", self.id_card_number)
        
        self.id_card_valid = QDateEdit()
        self.id_card_valid.setCalendarPopup(True)
        self.id_card_valid.setSpecialValueText("Nicht angegeben")
        id_form.addRow("Ausweis gültig bis:", self.id_card_valid)
        
        self.work_permit = QCheckBox("Arbeitserlaubnis erforderlich")
        card_form.addRow("", self.work_permit)
        
        self.work_permit_valid = QDateEdit()
        self.work_permit_valid.setCalendarPopup(True)
        self.work_permit_valid.setSpecialValueText("Nicht erforderlich")
        card_form.addRow("Arbeitserlaubnis bis:", self.work_permit_valid)
        docs_layout.addLayout(card_form)
        
        docs_layout.addStretch()
        tabs.addTab(self._create_scrollable_tab(docs_widget), "🪪 Dokumente")
        
        # ==================== TAB 8: NOTIZEN ====================
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setSpacing(15)
        
        notes_layout.addWidget(self._create_section_header("📝 Allgemeine Notizen"))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Allgemeine Notizen zum Mitarbeiter...")
        notes_layout.addWidget(self.notes)
        
        notes_layout.addWidget(self._create_section_header("🔒 Vertrauliche Notizen"))
        self.confidential_notes = QTextEdit()
        self.confidential_notes.setPlaceholderText("Vertrauliche Informationen (nur für HR)...")
        self.confidential_notes.setMaximumHeight(100)
        notes_layout.addWidget(self.confidential_notes)
        
        tabs.addTab(self._create_scrollable_tab(notes_widget), "📝 Notizen")
        
        layout.addWidget(tabs)
        
        # ==================== BUTTONS ====================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 40px;
                background-color: #0891b2;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0e7490;
            }
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_employee(self):
        session = self.db.get_session()
        try:
            self.employee = session.get(Employee, uuid.UUID(self.employee_id))
            if not self.employee:
                return
                
            e = self.employee
            
            # Persönliche Daten
            self.first_name.setText(e.first_name or "")
            self.last_name.setText(e.last_name or "")
            self.email.setText(e.email or "")
            self.phone.setText(e.phone or "")
            self.mobile.setText(e.mobile or "")
            
            # Adresse
            self.street.setText(e.street or "")
            self.postal_code.setText(e.postal_code or "")
            self.city.setText(e.city or "")
            
            # Beschäftigung
            self.employee_number.setText(e.employee_number or "")
            self.position.setText(e.position or "")
            
            if e.department:
                idx = self.department.findText(e.department)
                if idx >= 0:
                    self.department.setCurrentIndex(idx)
                else:
                    self.department.setCurrentText(e.department)
            
            if e.employment_type:
                idx = self.employment_type.findData(e.employment_type.value)
                if idx >= 0:
                    self.employment_type.setCurrentIndex(idx)
            
            if e.status:
                idx = self.status.findData(e.status.value)
                if idx >= 0:
                    self.status.setCurrentIndex(idx)
            
            if e.hire_date:
                self.hire_date.setDate(QDate(e.hire_date.year, e.hire_date.month, e.hire_date.day))
            
            # Erweiterte Felder (falls vorhanden)
            if hasattr(e, 'weekly_hours') and e.weekly_hours:
                self.weekly_hours.setValue(float(e.weekly_hours))
            if hasattr(e, 'vacation_days') and e.vacation_days:
                self.vacation_days.setValue(int(e.vacation_days))
            if hasattr(e, 'hourly_rate') and e.hourly_rate:
                self.hourly_rate.setValue(float(e.hourly_rate))
            
            self.notes.setPlainText(e.notes or "")
            
        finally:
            session.close()
    
    def save(self):
        if not self.first_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Vorname eingeben.")
            return
        if not self.last_name.text().strip():
            QMessageBox.warning(self, "Fehler", "Bitte Nachname eingeben.")
            return
        
        session = self.db.get_session()
        try:
            if self.employee_id:
                emp = session.get(Employee, uuid.UUID(self.employee_id))
            else:
                emp = Employee()
                from sqlalchemy import select, func
                count = session.execute(select(func.count(Employee.id))).scalar() or 0
                emp.employee_number = f"M{count + 1:04d}"
                
                if self.user:
                    emp.tenant_id = self.user.tenant_id
            
            # Persönliche Daten
            emp.first_name = self.first_name.text().strip()
            emp.last_name = self.last_name.text().strip()
            emp.email = self.email.text().strip() or None
            emp.phone = self.phone.text().strip() or None
            emp.mobile = self.mobile.text().strip() or None
            
            # Erweiterte persönliche Daten
            if hasattr(emp, 'salutation'):
                emp.salutation = self.salutation.currentText() or None
            if hasattr(emp, 'title'):
                emp.title = self.title.text().strip() or None
            if hasattr(emp, 'email_work'):
                emp.email_work = self.email_work.text().strip() or None
            if hasattr(emp, 'mobile_work'):
                emp.mobile_work = self.mobile_work.text().strip() or None
            if hasattr(emp, 'emergency_contact'):
                emp.emergency_contact = self.emergency_contact.text().strip() or None
            
            # Adresse
            emp.street = self.street.text().strip() or None
            if hasattr(emp, 'street_number'):
                emp.street_number = self.street_number.text().strip() or None
            emp.postal_code = self.postal_code.text().strip() or None
            emp.city = self.city.text().strip() or None
            if hasattr(emp, 'country'):
                emp.country = self.country.text().strip() or None
            
            # Beschäftigung
            emp.position = self.position.text().strip() or None
            emp.department = self.department.currentText()
            emp.employment_type = EmploymentType(self.employment_type.currentData())
            emp.status = EmployeeStatus(self.status.currentData())
            emp.hire_date = self.hire_date.date().toPyDate()
            
            if hasattr(emp, 'team'):
                emp.team = self.team.text().strip() or None
            if hasattr(emp, 'supervisor'):
                emp.supervisor = self.supervisor.text().strip() or None
            
            # Arbeitszeit
            if hasattr(emp, 'weekly_hours'):
                emp.weekly_hours = self.weekly_hours.value() or None
            if hasattr(emp, 'vacation_days'):
                emp.vacation_days = self.vacation_days.value() or None
            
            # Vergütung
            if hasattr(emp, 'hourly_rate'):
                emp.hourly_rate = self.hourly_rate.value() or None
            if hasattr(emp, 'monthly_salary'):
                emp.monthly_salary = self.monthly_salary.value() or None
            if hasattr(emp, 'cost_rate'):
                emp.cost_rate = self.cost_rate.value() or None
            
            # Bankdaten
            if hasattr(emp, 'bank_name'):
                emp.bank_name = self.bank_name.text().strip() or None
            if hasattr(emp, 'iban'):
                emp.iban = self.iban.text().strip() or None
            if hasattr(emp, 'bic'):
                emp.bic = self.bic.text().strip() or None
            
            # Qualifikationen
            if hasattr(emp, 'profession'):
                emp.profession = self.profession.currentText() or None
            if hasattr(emp, 'license_b'):
                emp.license_b = self.license_b.isChecked()
            if hasattr(emp, 'license_ce'):
                emp.license_ce = self.license_ce.isChecked()
            if hasattr(emp, 'forklift_license'):
                emp.forklift_license = self.forklift_license.isChecked()
            if hasattr(emp, 'crane_license'):
                emp.crane_license = self.crane_license.isChecked()
            if hasattr(emp, 'first_aid'):
                emp.first_aid = self.first_aid.isChecked()
            
            # PSA
            if hasattr(emp, 'shoe_size'):
                emp.shoe_size = self.shoe_size.text().strip() or None
            if hasattr(emp, 'clothing_size'):
                emp.clothing_size = self.clothing_size.currentText() or None
            
            # IDs
            if hasattr(emp, 'social_security_number'):
                emp.social_security_number = self.social_security_number.text().strip() or None
            if hasattr(emp, 'tax_id'):
                emp.tax_id = self.tax_id.text().strip() or None
            if hasattr(emp, 'health_insurance'):
                emp.health_insurance = self.health_insurance.text().strip() or None
            
            # Notizen
            emp.notes = self.notes.toPlainText().strip() or None
            if hasattr(emp, 'confidential_notes'):
                emp.confidential_notes = self.confidential_notes.toPlainText().strip() or None
            
            if not self.employee_id:
                session.add(emp)
            
            session.commit()
            self.accept()
            
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
        finally:
            session.close()
