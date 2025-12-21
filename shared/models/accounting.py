"""
Accounting Models - Umfassende Buchhaltung für Holzbau-ERP
Enthält: Kontenrahmen, Buchungen, Kostenstellen, Steuer
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


class AccountType(enum.Enum):
    """Kontoarten nach SKR03/SKR04"""
    ASSET = "asset"  # Aktiva
    LIABILITY = "liability"  # Passiva
    EQUITY = "equity"  # Eigenkapital
    REVENUE = "revenue"  # Erlöse
    EXPENSE = "expense"  # Aufwendungen


class AccountCategory(enum.Enum):
    """Kontokategorien"""
    # Aktiva
    FIXED_ASSETS = "fixed_assets"  # Anlagevermögen
    CURRENT_ASSETS = "current_assets"  # Umlaufvermögen
    BANK = "bank"  # Bankkonten
    CASH = "cash"  # Kasse
    RECEIVABLES = "receivables"  # Forderungen
    INVENTORY = "inventory"  # Vorräte
    # Passiva
    LONG_TERM_LIABILITIES = "long_term_liabilities"  # Langfristige Verbindlichkeiten
    SHORT_TERM_LIABILITIES = "short_term_liabilities"  # Kurzfristige Verbindlichkeiten
    PAYABLES = "payables"  # Verbindlichkeiten
    # Eigenkapital
    SHARE_CAPITAL = "share_capital"  # Stammkapital
    RETAINED_EARNINGS = "retained_earnings"  # Gewinnrücklagen
    # Erlöse
    SALES_REVENUE = "sales_revenue"  # Umsatzerlöse
    OTHER_REVENUE = "other_revenue"  # Sonstige Erlöse
    # Aufwendungen
    MATERIAL_COSTS = "material_costs"  # Materialkosten
    PERSONNEL_COSTS = "personnel_costs"  # Personalkosten
    OPERATING_COSTS = "operating_costs"  # Betriebskosten
    DEPRECIATION = "depreciation"  # Abschreibungen
    OTHER_EXPENSES = "other_expenses"  # Sonstige Aufwendungen


class BookingStatus(enum.Enum):
    """Buchungsstatus"""
    DRAFT = "draft"  # Entwurf
    POSTED = "posted"  # Gebucht
    REVERSED = "reversed"  # Storniert


class TaxType(enum.Enum):
    """Steuerarten"""
    VAT_19 = "vat_19"  # 19% MwSt
    VAT_7 = "vat_7"  # 7% MwSt
    VAT_0 = "vat_0"  # 0% MwSt
    VAT_FREE = "vat_free"  # Steuerfrei
    REVERSE_CHARGE = "reverse_charge"  # Reverse Charge
    INTRA_EU = "intra_eu"  # Innergemeinschaftlich


class FiscalYearStatus(enum.Enum):
    """Geschäftsjahrstatus"""
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"


# =============================================================================
# KONTENRAHMEN
# =============================================================================

class ChartOfAccounts(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Kontenrahmen (SKR03, SKR04, oder individuell)"""
    __tablename__ = "chart_of_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False)  # z.B. "SKR03", "SKR04", "Individuell"
    code = Column(String(20), nullable=False)  # z.B. "SKR03"
    description = Column(Text, nullable=True)
    
    # Standard oder individuell
    is_standard = Column(Boolean, default=False)
    base_chart = Column(String(20), nullable=True)  # Basis-Kontenrahmen
    
    country = Column(String(10), default="DE")
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    accounts = relationship("Account", back_populates="chart_of_accounts")


class Account(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Sachkonto"""
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id = Column(UUID(as_uuid=True), ForeignKey('chart_of_accounts.id'), nullable=False)
    
    # Kontonummer und Name
    account_number = Column(String(20), nullable=False, index=True)  # z.B. "1200" (Bank)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Klassifizierung
    account_type = Column(Enum(AccountType), nullable=False)
    category = Column(Enum(AccountCategory), nullable=True)
    
    # Hierarchie
    parent_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    level = Column(Integer, default=1)  # Hierarchieebene
    is_header = Column(Boolean, default=False)  # Summenkonto (nicht bebuchbar)
    
    # Steuer
    default_tax_type = Column(Enum(TaxType), nullable=True)
    tax_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)  # Zugehöriges Steuerkonto
    
    # Soll/Haben
    normal_balance = Column(String(10), default="debit")  # debit oder credit
    
    # Kostenstelle
    requires_cost_center = Column(Boolean, default=False)
    default_cost_center_id = Column(UUID(as_uuid=True), ForeignKey('cost_centers.id'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system_account = Column(Boolean, default=False)  # Systemkonto (nicht löschbar)
    
    # Eröffnungsbilanz
    opening_balance = Column(Numeric(15, 2), default=0)
    opening_balance_date = Column(Date, nullable=True)
    
    # Salden (Cache für Performance)
    current_balance = Column(Numeric(15, 2), default=0)
    ytd_debit = Column(Numeric(15, 2), default=0)  # Year-to-date Soll
    ytd_credit = Column(Numeric(15, 2), default=0)  # Year-to-date Haben
    
    # Bankverbindung (für Bankkonten)
    bank_name = Column(String(255), nullable=True)
    iban = Column(String(50), nullable=True)
    bic = Column(String(20), nullable=True)
    
    # Zusatzinfos
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'chart_id', 'account_number', name='uq_account_number'),
    )
    
    # Relationships
    chart_of_accounts = relationship("ChartOfAccounts", back_populates="accounts")
    parent_account = relationship("Account", remote_side=[id], foreign_keys=[parent_account_id])
    tax_account = relationship("Account", remote_side=[id], foreign_keys=[tax_account_id])
    journal_items = relationship("JournalItem", back_populates="account", foreign_keys="[JournalItem.account_id]")


# =============================================================================
# KOSTENSTELLEN & KOSTENTRÄGER
# =============================================================================

class CostCenter(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Kostenstelle"""
    __tablename__ = "cost_centers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    code = Column(String(50), nullable=False, index=True)  # z.B. "100" (Produktion)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchie
    parent_id = Column(UUID(as_uuid=True), ForeignKey('cost_centers.id'), nullable=True)
    level = Column(Integer, default=1)
    
    # Verantwortlich
    manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Budget
    annual_budget = Column(Numeric(15, 2), nullable=True)
    monthly_budget = Column(Numeric(15, 2), nullable=True)
    
    # Typ
    cost_center_type = Column(String(50), nullable=True)  # production, administration, sales, etc.
    
    is_active = Column(Boolean, default=True)
    
    # Zusatzinfos
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_cost_center_code'),
    )
    
    # Relationships
    parent = relationship("CostCenter", remote_side=[id], foreign_keys=[parent_id])


class CostObject(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Kostenträger (Projekt, Auftrag, Produkt)"""
    __tablename__ = "cost_objects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Typ
    object_type = Column(String(50), nullable=False)  # project, order, product
    
    # Referenz
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # Projekt-ID, Auftrags-ID, etc.
    reference_type = Column(String(50), nullable=True)
    
    # Budget & Kosten
    budget = Column(Numeric(15, 2), nullable=True)
    actual_costs = Column(Numeric(15, 2), default=0)
    planned_costs = Column(Numeric(15, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Zeitraum
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    custom_fields = Column(JSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_cost_object_code'),
    )


# =============================================================================
# GESCHÄFTSJAHR & PERIODEN
# =============================================================================

class FiscalYear(Base, TimestampMixin, TenantMixin):
    """Geschäftsjahr"""
    __tablename__ = "fiscal_years"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(50), nullable=False)  # z.B. "2025"
    code = Column(String(20), nullable=False)  # z.B. "GJ2025"
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(Enum(FiscalYearStatus), default=FiscalYearStatus.OPEN)
    
    # Vorjahr
    previous_year_id = Column(UUID(as_uuid=True), ForeignKey('fiscal_years.id'), nullable=True)
    
    # Abschluss
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    periods = relationship("FiscalPeriod", back_populates="fiscal_year")
    previous_year = relationship("FiscalYear", remote_side=[id], foreign_keys=[previous_year_id])


class FiscalPeriod(Base, TimestampMixin, TenantMixin):
    """Buchungsperiode (Monat)"""
    __tablename__ = "fiscal_periods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_year_id = Column(UUID(as_uuid=True), ForeignKey('fiscal_years.id'), nullable=False)
    
    name = Column(String(50), nullable=False)  # z.B. "Januar 2025"
    period_number = Column(Integer, nullable=False)  # 1-12 (oder 13 für Abschluss)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    status = Column(Enum(FiscalYearStatus), default=FiscalYearStatus.OPEN)
    
    # Abschluss
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    fiscal_year = relationship("FiscalYear", back_populates="periods")
    journals = relationship("Journal", back_populates="fiscal_period")


# =============================================================================
# BUCHUNGEN
# =============================================================================

class Journal(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Buchungssatz / Journal Entry"""
    __tablename__ = "journals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_period_id = Column(UUID(as_uuid=True), ForeignKey('fiscal_periods.id'), nullable=True)
    
    # Belegnummer
    document_number = Column(String(50), nullable=False, index=True)  # Fortlaufende Nummer
    document_date = Column(Date, nullable=False)  # Belegdatum
    posting_date = Column(Date, nullable=False)  # Buchungsdatum
    
    # Beschreibung
    description = Column(Text, nullable=False)  # Buchungstext
    reference = Column(String(255), nullable=True)  # Referenz (z.B. Rechnungsnummer)
    
    # Referenz zu anderen Dokumenten
    source_type = Column(String(50), nullable=True)  # invoice, payment, manual, etc.
    source_id = Column(UUID(as_uuid=True), nullable=True)  # ID des Quelldokuments
    
    # Beträge (Summen)
    total_debit = Column(Numeric(15, 2), nullable=False)
    total_credit = Column(Numeric(15, 2), nullable=False)
    
    # Währung
    currency = Column(String(3), default="EUR")
    exchange_rate = Column(Numeric(10, 6), default=1)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.DRAFT)
    posted_at = Column(DateTime, nullable=True)
    posted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Storno
    is_reversal = Column(Boolean, default=False)
    reversed_journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    reversal_journal_id = Column(UUID(as_uuid=True), nullable=True)  # ID der Storno-Buchung
    reversed_at = Column(DateTime, nullable=True)
    reversed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Wiederkehrend
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(JSONB, nullable=True)  # Wiederholungsmuster
    
    # Dokumente
    attachments = Column(JSONB, default=list)  # Angehängte Belege
    
    # Prüfung
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    fiscal_period = relationship("FiscalPeriod", back_populates="journals")
    items = relationship("JournalItem", back_populates="journal", cascade="all, delete-orphan")
    reversed_journal = relationship("Journal", remote_side=[id], foreign_keys=[reversed_journal_id])


class JournalItem(Base, TimestampMixin, TenantMixin):
    """Einzelposition einer Buchung"""
    __tablename__ = "journal_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    
    # Soll/Haben
    debit = Column(Numeric(15, 2), default=0)  # Soll
    credit = Column(Numeric(15, 2), default=0)  # Haben
    
    # Beschreibung
    description = Column(Text, nullable=True)
    
    # Kostenstelle & Kostenträger
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey('cost_centers.id'), nullable=True)
    cost_object_id = Column(UUID(as_uuid=True), ForeignKey('cost_objects.id'), nullable=True)
    
    # Steuer
    tax_type = Column(Enum(TaxType), nullable=True)
    tax_amount = Column(Numeric(15, 2), default=0)
    tax_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # Währung (wenn abweichend)
    amount_currency = Column(Numeric(15, 2), nullable=True)  # Betrag in Fremdwährung
    currency = Column(String(3), nullable=True)
    
    # Gegenkonto (für einfache Buchungen)
    counter_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # Sortierung
    line_number = Column(Integer, default=1)
    
    # Abgleich
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciliation_id = Column(UUID(as_uuid=True), nullable=True)
    
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    journal = relationship("Journal", back_populates="items")
    account = relationship("Account", back_populates="journal_items", foreign_keys=[account_id])
    cost_center = relationship("CostCenter")
    cost_object = relationship("CostObject")


# =============================================================================
# STEUERN
# =============================================================================

class TaxRate(Base, TimestampMixin, SoftDeleteMixin, TenantMixin):
    """Steuersätze"""
    __tablename__ = "tax_rates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False)  # z.B. "19% MwSt"
    code = Column(String(20), nullable=False)  # z.B. "VAT19"
    
    tax_type = Column(Enum(TaxType), nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)  # z.B. 19.00
    
    # Konten
    sales_tax_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)  # Umsatzsteuer
    purchase_tax_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)  # Vorsteuer
    
    # Gültigkeitszeitraum
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    
    # Für bestimmte Kategorien
    applies_to = Column(ARRAY(String), default=list)  # Produktkategorien
    
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    description = Column(Text, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'code', name='uq_tax_rate_code'),
    )


class TaxReport(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Umsatzsteuervoranmeldung / Steuererklärung"""
    __tablename__ = "tax_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    report_type = Column(String(50), nullable=False)  # vat_advance, vat_annual, income_tax
    
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=True)  # Für monatliche/quartalsweise
    period_quarter = Column(Integer, nullable=True)  # Q1, Q2, Q3, Q4
    
    # Beträge
    taxable_sales = Column(Numeric(15, 2), default=0)  # Steuerpflichtige Umsätze
    tax_free_sales = Column(Numeric(15, 2), default=0)  # Steuerfreie Umsätze
    intra_eu_sales = Column(Numeric(15, 2), default=0)  # Innergemeinschaftliche Lieferungen
    
    output_tax = Column(Numeric(15, 2), default=0)  # Umsatzsteuer
    input_tax = Column(Numeric(15, 2), default=0)  # Vorsteuer
    tax_payable = Column(Numeric(15, 2), default=0)  # Zu zahlende Steuer
    
    # Detaildaten
    details = Column(JSONB, default=dict)
    
    # Status
    status = Column(String(50), default="draft")  # draft, calculated, submitted, accepted
    submitted_at = Column(DateTime, nullable=True)
    submission_reference = Column(String(100), nullable=True)  # Finanzamt-Referenz
    
    # Fristen
    due_date = Column(Date, nullable=True)
    paid_date = Column(Date, nullable=True)
    
    notes = Column(Text, nullable=True)
    attachments = Column(JSONB, default=list)


# =============================================================================
# BANKABGLEICH
# =============================================================================

class BankStatement(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Kontoauszug"""
    __tablename__ = "bank_statements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    
    statement_number = Column(String(50), nullable=False)  # Auszugsnummer
    statement_date = Column(Date, nullable=False)
    
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    
    total_credits = Column(Numeric(15, 2), default=0)  # Summe Gutschriften
    total_debits = Column(Numeric(15, 2), default=0)  # Summe Lastschriften
    
    # Import
    import_source = Column(String(50), nullable=True)  # MT940, CSV, manual
    import_file = Column(String(500), nullable=True)
    imported_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default="imported")  # imported, reconciling, reconciled
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    bank_account = relationship("Account")
    transactions = relationship("BankTransaction", back_populates="statement")


class BankTransaction(Base, TimestampMixin, TenantMixin):
    """Einzelne Bankbewegung"""
    __tablename__ = "bank_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    statement_id = Column(UUID(as_uuid=True), ForeignKey('bank_statements.id'), nullable=False)
    
    # Transaktionsdaten
    transaction_date = Column(Date, nullable=False)
    value_date = Column(Date, nullable=True)  # Wertstellungsdatum
    
    amount = Column(Numeric(15, 2), nullable=False)  # Positiv = Gutschrift, Negativ = Lastschrift
    
    # Partner
    partner_name = Column(String(255), nullable=True)
    partner_iban = Column(String(50), nullable=True)
    partner_bic = Column(String(20), nullable=True)
    
    # Verwendungszweck
    description = Column(Text, nullable=True)
    reference = Column(String(255), nullable=True)  # Kundenreferenz
    bank_reference = Column(String(100), nullable=True)  # Bankreferenz
    
    # Kategorisierung
    transaction_type = Column(String(50), nullable=True)  # transfer, sepa_dd, sepa_ct, etc.
    purpose_code = Column(String(10), nullable=True)  # SEPA Purpose Code
    
    # Abgleich
    is_reconciled = Column(Boolean, default=False)
    reconciled_journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Automatische Erkennung
    auto_matched = Column(Boolean, default=False)
    match_confidence = Column(Numeric(5, 2), nullable=True)  # Erkennungsgenauigkeit
    suggested_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    suggested_customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    suggested_invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    statement = relationship("BankStatement", back_populates="transactions")
    reconciled_journal = relationship("Journal")


# =============================================================================
# BUDGETIERUNG
# =============================================================================

class Budget(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Budget"""
    __tablename__ = "budgets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    budget_type = Column(String(50), nullable=False)  # annual, quarterly, monthly, project
    
    fiscal_year_id = Column(UUID(as_uuid=True), ForeignKey('fiscal_years.id'), nullable=True)
    
    # Zeitraum
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Gesamtbudget
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="draft")  # draft, approved, active, closed
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Relationships
    items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")


class BudgetItem(Base, TimestampMixin, TenantMixin):
    """Budget-Position"""
    __tablename__ = "budget_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey('budgets.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey('cost_centers.id'), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Budgetierte Beträge pro Periode
    amount_jan = Column(Numeric(15, 2), default=0)
    amount_feb = Column(Numeric(15, 2), default=0)
    amount_mar = Column(Numeric(15, 2), default=0)
    amount_apr = Column(Numeric(15, 2), default=0)
    amount_may = Column(Numeric(15, 2), default=0)
    amount_jun = Column(Numeric(15, 2), default=0)
    amount_jul = Column(Numeric(15, 2), default=0)
    amount_aug = Column(Numeric(15, 2), default=0)
    amount_sep = Column(Numeric(15, 2), default=0)
    amount_oct = Column(Numeric(15, 2), default=0)
    amount_nov = Column(Numeric(15, 2), default=0)
    amount_dec = Column(Numeric(15, 2), default=0)
    
    # Gesamtbetrag
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Ist-Werte (Cache)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance = Column(Numeric(15, 2), default=0)  # Budget - Ist
    variance_percent = Column(Numeric(8, 2), default=0)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    budget = relationship("Budget", back_populates="items")
    account = relationship("Account")
    cost_center = relationship("CostCenter")


# =============================================================================
# ABSCHREIBUNGEN
# =============================================================================

class FixedAsset(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Anlagevermögen / Wirtschaftsgut"""
    __tablename__ = "fixed_assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identifikation
    asset_number = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Klassifizierung
    asset_type = Column(String(50), nullable=False)  # machinery, vehicle, building, equipment, etc.
    asset_category = Column(String(100), nullable=True)
    
    # Konten
    asset_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    depreciation_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # Kostenstelle
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey('cost_centers.id'), nullable=True)
    
    # Anschaffung
    acquisition_date = Column(Date, nullable=False)
    in_service_date = Column(Date, nullable=True)  # Inbetriebnahme
    acquisition_cost = Column(Numeric(15, 2), nullable=False)
    
    # Lieferant
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    invoice_reference = Column(String(100), nullable=True)
    
    # Abschreibung
    depreciation_method = Column(String(50), default="linear")  # linear, declining, units
    useful_life_years = Column(Integer, nullable=False)  # Nutzungsdauer in Jahren
    useful_life_months = Column(Integer, nullable=True)  # Zusätzliche Monate
    residual_value = Column(Numeric(15, 2), default=0)  # Restwert
    depreciation_rate = Column(Numeric(8, 4), nullable=True)  # AfA-Satz in %
    
    # Werte
    current_book_value = Column(Numeric(15, 2), nullable=False)  # Aktueller Buchwert
    accumulated_depreciation = Column(Numeric(15, 2), default=0)  # Kumulierte AfA
    
    # Status
    status = Column(String(50), default="active")  # active, disposed, scrapped
    disposal_date = Column(Date, nullable=True)
    disposal_amount = Column(Numeric(15, 2), nullable=True)  # Verkaufserlös
    disposal_reason = Column(Text, nullable=True)
    
    # Standort
    location = Column(String(255), nullable=True)
    responsible_employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    
    # Seriennummer / Inventarnummer
    serial_number = Column(String(100), nullable=True)
    inventory_number = Column(String(100), nullable=True)
    
    # Versicherung
    insured = Column(Boolean, default=False)
    insurance_value = Column(Numeric(15, 2), nullable=True)
    insurance_policy = Column(String(100), nullable=True)
    
    # Wartung
    warranty_expires = Column(Date, nullable=True)
    maintenance_contract = Column(Boolean, default=False)
    next_maintenance = Column(Date, nullable=True)
    
    # Dokumente
    attachments = Column(JSONB, default=list)
    
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'asset_number', name='uq_fixed_asset_number'),
    )
    
    # Relationships
    depreciation_entries = relationship("DepreciationEntry", back_populates="fixed_asset")


class DepreciationEntry(Base, TimestampMixin, TenantMixin):
    """Abschreibungsbuchung"""
    __tablename__ = "depreciation_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fixed_asset_id = Column(UUID(as_uuid=True), ForeignKey('fixed_assets.id'), nullable=False)
    
    fiscal_year_id = Column(UUID(as_uuid=True), ForeignKey('fiscal_years.id'), nullable=True)
    fiscal_period_id = Column(UUID(as_uuid=True), ForeignKey('fiscal_periods.id'), nullable=True)
    
    # Abschreibung
    depreciation_date = Column(Date, nullable=False)
    depreciation_amount = Column(Numeric(15, 2), nullable=False)
    
    # Buchwerte
    book_value_before = Column(Numeric(15, 2), nullable=False)
    book_value_after = Column(Numeric(15, 2), nullable=False)
    
    # Buchung
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    
    # Status
    status = Column(String(50), default="planned")  # planned, posted, reversed
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    fixed_asset = relationship("FixedAsset", back_populates="depreciation_entries")
    journal = relationship("Journal")
