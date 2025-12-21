"""
Payroll Models - Umfassende Lohnverwaltung für Holzbau-ERP
Enthält: Lohnabrechnungen, Abzüge, Zulagen, Sozialversicherung
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Integer, Time, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
import uuid
import enum

from shared.database import Base
from shared.models.base import TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin


class PayrollStatus(enum.Enum):
    """Lohnabrechnungsstatus"""
    DRAFT = "draft"  # Entwurf
    CALCULATED = "calculated"  # Berechnet
    APPROVED = "approved"  # Genehmigt
    PAID = "paid"  # Ausgezahlt
    CORRECTED = "corrected"  # Korrigiert


class PaymentMethod(enum.Enum):
    """Zahlungsart"""
    BANK_TRANSFER = "bank_transfer"  # Überweisung
    CASH = "cash"  # Bar
    CHECK = "check"  # Scheck


class DeductionType(enum.Enum):
    """Abzugsart"""
    # Steuern
    INCOME_TAX = "income_tax"  # Lohnsteuer
    SOLIDARITY_TAX = "solidarity_tax"  # Solidaritätszuschlag
    CHURCH_TAX = "church_tax"  # Kirchensteuer
    
    # Sozialversicherung
    HEALTH_INSURANCE = "health_insurance"  # Krankenversicherung
    PENSION_INSURANCE = "pension_insurance"  # Rentenversicherung
    UNEMPLOYMENT_INSURANCE = "unemployment_insurance"  # Arbeitslosenversicherung
    NURSING_INSURANCE = "nursing_insurance"  # Pflegeversicherung
    
    # Sonstige
    ADVANCE = "advance"  # Vorschuss
    LOAN = "loan"  # Darlehen
    GARNISHMENT = "garnishment"  # Pfändung
    VOLUNTARY = "voluntary"  # Freiwillige Abzüge
    COMPANY_PENSION = "company_pension"  # Betriebliche Altersvorsorge
    OTHER = "other"


class AllowanceType(enum.Enum):
    """Zulagetyp"""
    # Zeit
    OVERTIME = "overtime"  # Überstunden
    NIGHT_SHIFT = "night_shift"  # Nachtzulage
    WEEKEND = "weekend"  # Wochenendzulage
    HOLIDAY = "holiday"  # Feiertagszulage
    
    # Aufwand
    TRAVEL = "travel"  # Fahrkostenzuschuss
    MEAL = "meal"  # Verpflegungszuschuss
    HOUSING = "housing"  # Wohnungszuschuss
    CLOTHING = "clothing"  # Kleidergeld
    PHONE = "phone"  # Telefonzuschuss
    
    # Leistung
    BONUS = "bonus"  # Bonus
    COMMISSION = "commission"  # Provision
    PROFIT_SHARE = "profit_share"  # Gewinnbeteiligung
    
    # Sonderzahlungen
    CHRISTMAS = "christmas"  # Weihnachtsgeld
    VACATION = "vacation"  # Urlaubsgeld
    ANNIVERSARY = "anniversary"  # Jubiläumszuwendung
    
    # Steuerfreie
    TAX_FREE = "tax_free"  # Steuerfreie Sachbezüge
    
    OTHER = "other"


# =============================================================================
# LOHNABRECHNUNGSZEITRAUM
# =============================================================================

class PayrollPeriod(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Lohnabrechnungszeitraum"""
    __tablename__ = "payroll_periods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False)  # z.B. "Januar 2025"
    code = Column(String(20), nullable=False)  # z.B. "2025-01"
    
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Arbeitstage
    work_days = Column(Integer, nullable=True)
    work_hours = Column(Numeric(8, 2), nullable=True)
    
    # Feiertage im Zeitraum
    holidays = Column(JSONB, default=list)
    
    # Status
    status = Column(String(50), default="open")  # open, processing, closed, locked
    
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Fristen
    submission_deadline = Column(Date, nullable=True)  # Abgabefrist
    payment_date = Column(Date, nullable=True)  # Auszahlungsdatum
    
    notes = Column(Text, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'year', 'month', name='uq_payroll_period'),
    )
    
    # Relationships
    payslips = relationship("Payslip", back_populates="payroll_period")


# =============================================================================
# GEHALTSBESTANDTEILE
# =============================================================================

class SalaryComponent(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Gehaltsbestandteil-Definition"""
    __tablename__ = "salary_components"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)  # Eindeutiger Code
    description = Column(Text, nullable=True)
    
    # Typ
    component_type = Column(String(50), nullable=False)  # earning, deduction, employer_contribution
    sub_type = Column(String(50), nullable=True)  # Weitere Klassifizierung
    
    # Berechnung
    calculation_type = Column(String(50), default="fixed")  # fixed, percentage, formula
    default_amount = Column(Numeric(15, 2), nullable=True)
    percentage = Column(Numeric(8, 4), nullable=True)
    formula = Column(Text, nullable=True)  # Berechnungsformel
    
    # Basis
    base_component_id = Column(UUID(as_uuid=True), ForeignKey('salary_components.id'), nullable=True)
    
    # Steuern & SV
    is_taxable = Column(Boolean, default=True)  # Steuerpflichtig
    is_sv_liable = Column(Boolean, default=True)  # Sozialversicherungspflichtig
    tax_treatment = Column(String(50), nullable=True)  # Steuerliche Behandlung
    
    # Grenzen
    min_amount = Column(Numeric(15, 2), nullable=True)
    max_amount = Column(Numeric(15, 2), nullable=True)
    
    # Buchhaltung
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    liability_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # Sortierung & Anzeige
    display_order = Column(Integer, default=100)
    show_on_payslip = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Systemkomponente (nicht löschbar)
    
    notes = Column(Text, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_salary_component_code'),
    )


class EmployeeSalary(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Mitarbeiter-Gehaltsvereinbarung"""
    __tablename__ = "employee_salaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Gültigkeitszeitraum
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    
    # Vergütungstyp
    salary_type = Column(String(50), default="monthly")  # hourly, monthly, annual
    
    # Grundgehalt
    base_salary = Column(Numeric(15, 2), nullable=False)  # Grundgehalt
    hourly_rate = Column(Numeric(10, 2), nullable=True)  # Stundensatz
    
    # Arbeitszeit
    weekly_hours = Column(Numeric(5, 2), default=40)
    monthly_hours = Column(Numeric(6, 2), nullable=True)
    
    # Tarifvertrag
    collective_agreement = Column(String(100), nullable=True)
    wage_group = Column(String(50), nullable=True)
    wage_level = Column(String(50), nullable=True)
    
    # Zusätzliche feste Vergütung
    fixed_allowances = Column(JSONB, default=dict)  # {"Fahrtgeld": 100, ...}
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Genehmigung
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Grund für Änderung
    change_reason = Column(Text, nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    employee = relationship("Employee")
    components = relationship("EmployeeSalaryComponent", back_populates="salary")


class EmployeeSalaryComponent(Base, TimestampMixin, TenantMixin):
    """Mitarbeiter-spezifische Gehaltsbestandteile"""
    __tablename__ = "employee_salary_components"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salary_id = Column(UUID(as_uuid=True), ForeignKey('employee_salaries.id'), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey('salary_components.id'), nullable=False)
    
    # Individueller Betrag/Prozentsatz
    amount = Column(Numeric(15, 2), nullable=True)
    percentage = Column(Numeric(8, 4), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    salary = relationship("EmployeeSalary", back_populates="components")
    component = relationship("SalaryComponent")


# =============================================================================
# LOHNABRECHNUNG
# =============================================================================

class Payslip(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Lohnabrechnung / Gehaltsabrechnung"""
    __tablename__ = "payslips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    payroll_period_id = Column(UUID(as_uuid=True), ForeignKey('payroll_periods.id'), nullable=False)
    
    # Nummer
    payslip_number = Column(String(50), nullable=False, index=True)
    
    # Zeitraum
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Arbeitszeit
    work_days = Column(Numeric(5, 2), nullable=True)  # Arbeitstage
    work_hours = Column(Numeric(8, 2), nullable=True)  # Arbeitsstunden
    overtime_hours = Column(Numeric(8, 2), default=0)  # Überstunden
    absence_days = Column(Numeric(5, 2), default=0)  # Abwesenheitstage
    sick_days = Column(Numeric(5, 2), default=0)  # Krankheitstage
    vacation_days = Column(Numeric(5, 2), default=0)  # Urlaubstage
    
    # === BRUTTOBEZÜGE ===
    base_salary = Column(Numeric(15, 2), default=0)  # Grundgehalt
    hourly_wages = Column(Numeric(15, 2), default=0)  # Stundenlohn-Anteil
    overtime_pay = Column(Numeric(15, 2), default=0)  # Überstundenvergütung
    
    # Zulagen
    allowances_taxable = Column(Numeric(15, 2), default=0)  # Steuerpflichtige Zulagen
    allowances_tax_free = Column(Numeric(15, 2), default=0)  # Steuerfreie Zulagen
    bonuses = Column(Numeric(15, 2), default=0)  # Boni/Prämien
    commissions = Column(Numeric(15, 2), default=0)  # Provisionen
    other_earnings = Column(Numeric(15, 2), default=0)  # Sonstige Bezüge
    
    gross_salary = Column(Numeric(15, 2), nullable=False)  # Gesamtbrutto
    
    # === ABZÜGE ARBEITNEHMER ===
    # Steuern
    income_tax = Column(Numeric(15, 2), default=0)  # Lohnsteuer
    solidarity_tax = Column(Numeric(15, 2), default=0)  # Solidaritätszuschlag
    church_tax = Column(Numeric(15, 2), default=0)  # Kirchensteuer
    total_taxes = Column(Numeric(15, 2), default=0)  # Gesamt Steuern
    
    # Sozialversicherung AN
    health_insurance_employee = Column(Numeric(15, 2), default=0)  # KV Arbeitnehmeranteil
    pension_insurance_employee = Column(Numeric(15, 2), default=0)  # RV Arbeitnehmeranteil
    unemployment_insurance_employee = Column(Numeric(15, 2), default=0)  # AV Arbeitnehmeranteil
    nursing_insurance_employee = Column(Numeric(15, 2), default=0)  # PV Arbeitnehmeranteil
    nursing_insurance_surcharge = Column(Numeric(15, 2), default=0)  # PV Kinderlosenzuschlag
    total_social_security_employee = Column(Numeric(15, 2), default=0)  # Gesamt SV Arbeitnehmer
    
    # Sonstige Abzüge
    other_deductions = Column(Numeric(15, 2), default=0)
    advance_payment = Column(Numeric(15, 2), default=0)  # Vorschuss
    loan_repayment = Column(Numeric(15, 2), default=0)  # Darlehensrückzahlung
    garnishment = Column(Numeric(15, 2), default=0)  # Pfändung
    company_pension_employee = Column(Numeric(15, 2), default=0)  # BAV Arbeitnehmeranteil
    
    total_deductions = Column(Numeric(15, 2), nullable=False)  # Gesamt Abzüge
    
    # === NETTO ===
    net_salary = Column(Numeric(15, 2), nullable=False)  # Nettolohn
    
    # Sachbezüge (werden nicht ausgezahlt)
    benefits_in_kind = Column(Numeric(15, 2), default=0)  # Sachbezüge
    
    payment_amount = Column(Numeric(15, 2), nullable=False)  # Auszahlungsbetrag
    
    # === ARBEITGEBERANTEILE ===
    health_insurance_employer = Column(Numeric(15, 2), default=0)
    pension_insurance_employer = Column(Numeric(15, 2), default=0)
    unemployment_insurance_employer = Column(Numeric(15, 2), default=0)
    nursing_insurance_employer = Column(Numeric(15, 2), default=0)
    accident_insurance = Column(Numeric(15, 2), default=0)  # Berufsgenossenschaft
    insolvency_insurance = Column(Numeric(15, 2), default=0)  # Insolvenzgeldumlage
    company_pension_employer = Column(Numeric(15, 2), default=0)  # BAV Arbeitgeberanteil
    
    total_employer_costs = Column(Numeric(15, 2), default=0)  # Gesamt AG-Kosten
    
    # === GESAMTKOSTEN ===
    total_costs = Column(Numeric(15, 2), nullable=False)  # Gesamte Personalkosten
    
    # === STEUER-/SV-DATEN ===
    tax_class = Column(String(10), nullable=True)  # Steuerklasse
    tax_factor = Column(Numeric(6, 4), nullable=True)  # Faktor
    tax_allowance = Column(Numeric(15, 2), default=0)  # Freibetrag
    tax_id = Column(String(50), nullable=True)  # Steuer-ID
    
    social_security_number = Column(String(50), nullable=True)
    health_insurance_name = Column(String(255), nullable=True)
    health_insurance_rate = Column(Numeric(6, 4), nullable=True)
    
    # === KOSTENSTELLE ===
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey('cost_centers.id'), nullable=True)
    cost_object_id = Column(UUID(as_uuid=True), ForeignKey('cost_objects.id'), nullable=True)
    
    # === STATUS ===
    status = Column(Enum(PayrollStatus), default=PayrollStatus.DRAFT)
    
    calculated_at = Column(DateTime, nullable=True)
    calculated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # === ZAHLUNG ===
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.BANK_TRANSFER)
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    bank_name = Column(String(255), nullable=True)
    iban = Column(String(50), nullable=True)
    bic = Column(String(20), nullable=True)
    
    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    
    # === BUCHUNG ===
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    
    # === KORREKTUR ===
    is_correction = Column(Boolean, default=False)
    corrects_payslip_id = Column(UUID(as_uuid=True), ForeignKey('payslips.id'), nullable=True)
    corrected_by_payslip_id = Column(UUID(as_uuid=True), nullable=True)
    
    # === DOKUMENTE ===
    pdf_url = Column(String(500), nullable=True)  # PDF der Abrechnung
    attachments = Column(JSONB, default=list)
    
    # === ZUSÄTZLICHE INFOS ===
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Details als JSON für Flexibilität
    calculation_details = Column(JSONB, default=dict)  # Detaillierte Berechnung
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'payslip_number', name='uq_payslip_number'),
    )
    
    # Relationships
    employee = relationship("Employee")
    payroll_period = relationship("PayrollPeriod", back_populates="payslips")
    items = relationship("PayslipItem", back_populates="payslip", cascade="all, delete-orphan")
    cost_center = relationship("CostCenter")
    corrects_payslip = relationship("Payslip", remote_side=[id], foreign_keys=[corrects_payslip_id])


class PayslipItem(Base, TimestampMixin, TenantMixin):
    """Einzelposition auf der Lohnabrechnung"""
    __tablename__ = "payslip_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payslip_id = Column(UUID(as_uuid=True), ForeignKey('payslips.id'), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey('salary_components.id'), nullable=True)
    
    # Bezeichnung
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Typ
    item_type = Column(String(50), nullable=False)  # earning, deduction, employer_cost, info
    sub_type = Column(String(50), nullable=True)
    
    # Berechnung
    quantity = Column(Numeric(10, 2), nullable=True)  # z.B. Stunden
    rate = Column(Numeric(15, 4), nullable=True)  # z.B. Stundensatz
    percentage = Column(Numeric(8, 4), nullable=True)  # Prozentsatz
    base_amount = Column(Numeric(15, 2), nullable=True)  # Basisbetrag
    
    amount = Column(Numeric(15, 2), nullable=False)  # Betrag
    
    # Steuer-/SV-Behandlung
    is_taxable = Column(Boolean, default=True)
    is_sv_liable = Column(Boolean, default=True)
    tax_treatment = Column(String(50), nullable=True)
    
    # Sortierung
    display_order = Column(Integer, default=100)
    show_on_payslip = Column(Boolean, default=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    payslip = relationship("Payslip", back_populates="items")
    component = relationship("SalaryComponent")


# =============================================================================
# LOHN-SONDERZAHLUNGEN
# =============================================================================

class BonusPayment(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Sonderzahlungen (Bonus, Prämie, Weihnachtsgeld, etc.)"""
    __tablename__ = "bonus_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Art
    bonus_type = Column(String(50), nullable=False)  # bonus, christmas, vacation, anniversary, commission
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Betrag
    gross_amount = Column(Numeric(15, 2), nullable=False)
    
    # Versteuerung
    taxation_method = Column(String(50), default="normal")  # normal, fifth_rule, tax_free
    
    # Zeitraum/Anlass
    reference_period_start = Column(Date, nullable=True)
    reference_period_end = Column(Date, nullable=True)
    reason = Column(Text, nullable=True)
    
    # Auszahlung
    payroll_period_id = Column(UUID(as_uuid=True), ForeignKey('payroll_periods.id'), nullable=True)
    planned_payment_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String(50), default="planned")  # planned, approved, paid, cancelled
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    employee = relationship("Employee")


# =============================================================================
# VORSCHÜSSE & DARLEHEN
# =============================================================================

class EmployeeAdvance(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Mitarbeiter-Vorschuss"""
    __tablename__ = "employee_advances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Vorschuss
    advance_number = Column(String(50), nullable=False)
    advance_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    reason = Column(Text, nullable=True)
    
    # Rückzahlung
    repayment_method = Column(String(50), default="deduction")  # deduction, manual
    repayment_start_date = Column(Date, nullable=True)
    repayment_amount = Column(Numeric(15, 2), nullable=True)  # Pro Periode
    repayment_periods = Column(Integer, nullable=True)  # Anzahl Raten
    
    # Saldo
    amount_repaid = Column(Numeric(15, 2), default=0)
    amount_remaining = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, active, repaid, cancelled
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee")
    repayments = relationship("AdvanceRepayment", back_populates="advance")


class AdvanceRepayment(Base, TimestampMixin, TenantMixin):
    """Vorschuss-Rückzahlung"""
    __tablename__ = "advance_repayments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advance_id = Column(UUID(as_uuid=True), ForeignKey('employee_advances.id'), nullable=False)
    payslip_id = Column(UUID(as_uuid=True), ForeignKey('payslips.id'), nullable=True)
    
    repayment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    method = Column(String(50), default="deduction")  # deduction, manual
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    advance = relationship("EmployeeAdvance", back_populates="repayments")


class EmployeeLoan(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Mitarbeiterdarlehen"""
    __tablename__ = "employee_loans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    loan_number = Column(String(50), nullable=False)
    loan_date = Column(Date, nullable=False)
    
    # Darlehensdetails
    principal_amount = Column(Numeric(15, 2), nullable=False)  # Darlehenssumme
    interest_rate = Column(Numeric(6, 4), default=0)  # Zinssatz p.a.
    term_months = Column(Integer, nullable=False)  # Laufzeit in Monaten
    
    # Rückzahlung
    monthly_payment = Column(Numeric(15, 2), nullable=False)  # Monatliche Rate
    first_payment_date = Column(Date, nullable=False)
    
    # Saldo
    amount_repaid = Column(Numeric(15, 2), default=0)
    interest_paid = Column(Numeric(15, 2), default=0)
    amount_remaining = Column(Numeric(15, 2), nullable=False)
    
    # Zweck
    purpose = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, active, repaid, defaulted
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Vertrag
    contract_url = Column(String(500), nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    employee = relationship("Employee")


# =============================================================================
# PFÄNDUNGEN
# =============================================================================

class Garnishment(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Lohnpfändung"""
    __tablename__ = "garnishments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Pfändungsbescheid
    case_number = Column(String(100), nullable=False)  # Aktenzeichen
    court = Column(String(255), nullable=True)  # Gericht
    creditor = Column(String(255), nullable=False)  # Gläubiger
    
    # Pfändungsart
    garnishment_type = Column(String(50), nullable=False)  # wage, child_support, tax
    
    # Beträge
    total_amount = Column(Numeric(15, 2), nullable=True)  # Gesamtforderung
    monthly_amount = Column(Numeric(15, 2), nullable=True)  # Fester monatlicher Betrag
    
    # Pfändungstabelle
    use_garnishment_table = Column(Boolean, default=True)  # Pfändungstabelle anwenden
    dependents_count = Column(Integer, default=0)  # Anzahl unterhaltsberechtigte Personen
    
    # Zeitraum
    effective_date = Column(Date, nullable=False)  # Ab wann
    end_date = Column(Date, nullable=True)  # Bis wann
    
    # Priorität (bei mehreren Pfändungen)
    priority = Column(Integer, default=1)
    
    # Saldo
    amount_deducted = Column(Numeric(15, 2), default=0)
    amount_remaining = Column(Numeric(15, 2), nullable=True)
    
    # Zahlungsempfänger
    payment_recipient = Column(String(255), nullable=True)
    payment_iban = Column(String(50), nullable=True)
    payment_bic = Column(String(20), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(50), default="active")  # active, suspended, completed, cancelled
    
    # Dokumente
    documents = Column(JSONB, default=list)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee")


# =============================================================================
# SOZIALVERSICHERUNGSMELDUNGEN
# =============================================================================

class SocialSecurityReport(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Sozialversicherungsmeldung"""
    __tablename__ = "social_security_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    # Meldeart
    report_type = Column(String(50), nullable=False)  # registration, deregistration, annual, change
    report_code = Column(String(10), nullable=False)  # DEÜV-Abgabegrund
    
    # Zeitraum
    report_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    
    # Beträge
    gross_salary = Column(Numeric(15, 2), nullable=True)
    sv_gross = Column(Numeric(15, 2), nullable=True)  # SV-Brutto
    
    # Beitragsgruppe
    contribution_group = Column(String(10), nullable=True)  # z.B. "1111"
    personnel_group = Column(String(10), nullable=True)  # Personengruppe
    
    # Krankenkasse
    health_insurance_id = Column(String(20), nullable=True)  # Betriebsnummer KK
    health_insurance_name = Column(String(255), nullable=True)
    
    # Status
    status = Column(String(50), default="created")  # created, submitted, accepted, rejected
    
    submitted_at = Column(DateTime, nullable=True)
    response_date = Column(Date, nullable=True)
    response_message = Column(Text, nullable=True)
    
    # Referenz
    reference_number = Column(String(100), nullable=True)  # Datensatznummer
    
    # Rohdaten
    raw_data = Column(JSONB, default=dict)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee")


# =============================================================================
# LOHNSTEUERANMELDUNG
# =============================================================================

class TaxPayrollReport(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Lohnsteueranmeldung"""
    __tablename__ = "tax_payroll_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Zeitraum
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)  # Für monatliche Anmeldung
    quarter = Column(Integer, nullable=True)  # Für quartalsweise
    
    report_type = Column(String(50), nullable=False)  # monthly, quarterly, annual
    
    # Beträge
    total_gross = Column(Numeric(15, 2), default=0)  # Summe Bruttolöhne
    income_tax = Column(Numeric(15, 2), default=0)  # Lohnsteuer
    solidarity_tax = Column(Numeric(15, 2), default=0)  # Solidaritätszuschlag
    church_tax = Column(Numeric(15, 2), default=0)  # Kirchensteuer
    total_tax = Column(Numeric(15, 2), default=0)  # Gesamte Lohnsteuer
    
    employee_count = Column(Integer, default=0)  # Anzahl Arbeitnehmer
    
    # Detaildaten
    details = Column(JSONB, default=dict)
    
    # Status
    status = Column(String(50), default="draft")  # draft, calculated, submitted, accepted
    
    submitted_at = Column(DateTime, nullable=True)
    submission_reference = Column(String(100), nullable=True)  # ELSTER-Referenz
    
    # Zahlung
    due_date = Column(Date, nullable=True)
    paid_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    notes = Column(Text, nullable=True)


# =============================================================================
# BETRIEBLICHE ALTERSVORSORGE
# =============================================================================

class CompanyPensionPlan(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Betriebliche Altersvorsorge - Versorgungswerk"""
    __tablename__ = "company_pension_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    plan_type = Column(String(50), nullable=False)  # direct_insurance, pension_fund, support_fund
    provider = Column(String(255), nullable=True)  # Versicherungsgesellschaft
    contract_number = Column(String(100), nullable=True)
    
    # Beitragsgrenzen
    employee_contribution_min = Column(Numeric(15, 2), nullable=True)
    employee_contribution_max = Column(Numeric(15, 2), nullable=True)
    employer_contribution = Column(Numeric(15, 2), nullable=True)
    employer_contribution_percent = Column(Numeric(6, 4), nullable=True)
    
    # Steuer-/SV-Behandlung
    tax_treatment = Column(String(50), nullable=True)
    sv_treatment = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    description = Column(Text, nullable=True)
    documents = Column(JSONB, default=list)
    
    # Relationships
    enrollments = relationship("PensionEnrollment", back_populates="plan")


class PensionEnrollment(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Mitarbeiter-Anmeldung zur BAV"""
    __tablename__ = "pension_enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('company_pension_plans.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    
    enrollment_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Beiträge
    employee_contribution = Column(Numeric(15, 2), nullable=False)
    employer_contribution = Column(Numeric(15, 2), default=0)
    
    contribution_frequency = Column(String(20), default="monthly")
    
    # Vertrag
    insurance_number = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), default="active")  # active, paused, terminated
    
    termination_date = Column(Date, nullable=True)
    termination_reason = Column(Text, nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    plan = relationship("CompanyPensionPlan", back_populates="enrollments")
    employee = relationship("Employee")
