"""
Finance Models - Umfassende Finanzverwaltung für Holzbau-ERP
Enthält: Zahlungen, Bankkonten, Mahnwesen, Liquiditätsplanung
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


class PaymentStatus(enum.Enum):
    """Zahlungsstatus"""
    PENDING = "pending"  # Ausstehend
    SCHEDULED = "scheduled"  # Geplant
    PROCESSING = "processing"  # In Bearbeitung
    COMPLETED = "completed"  # Abgeschlossen
    FAILED = "failed"  # Fehlgeschlagen
    CANCELLED = "cancelled"  # Storniert
    REFUNDED = "refunded"  # Erstattet


class PaymentDirection(enum.Enum):
    """Zahlungsrichtung"""
    INCOMING = "incoming"  # Eingehend (von Kunden)
    OUTGOING = "outgoing"  # Ausgehend (an Lieferanten)


class PaymentMethodType(enum.Enum):
    """Zahlungsmethode"""
    BANK_TRANSFER = "bank_transfer"  # Überweisung
    SEPA_DD = "sepa_dd"  # SEPA-Lastschrift
    SEPA_CT = "sepa_ct"  # SEPA-Überweisung
    CASH = "cash"  # Bar
    CHECK = "check"  # Scheck
    CREDIT_CARD = "credit_card"  # Kreditkarte
    PAYPAL = "paypal"  # PayPal
    DIRECT_DEBIT = "direct_debit"  # Abbuchung


class DunningLevel(enum.Enum):
    """Mahnstufe"""
    REMINDER = "reminder"  # Zahlungserinnerung
    FIRST = "first"  # 1. Mahnung
    SECOND = "second"  # 2. Mahnung
    THIRD = "third"  # 3. Mahnung
    FINAL = "final"  # Letzte Mahnung
    COLLECTION = "collection"  # Inkasso
    LEGAL = "legal"  # Gerichtliches Mahnverfahren


# =============================================================================
# BANKKONTEN
# =============================================================================

class BankAccount(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Bankkonto"""
    __tablename__ = "bank_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Kontobezeichnung
    name = Column(String(255), nullable=False)  # z.B. "Geschäftskonto Sparkasse"
    description = Column(Text, nullable=True)
    
    # Bankverbindung
    bank_name = Column(String(255), nullable=False)
    bank_code = Column(String(20), nullable=True)  # BLZ (veraltet, aber für Altdaten)
    iban = Column(String(50), nullable=False)
    bic = Column(String(20), nullable=True)
    account_holder = Column(String(255), nullable=True)
    
    # Kontotyp
    account_type = Column(String(50), default="checking")  # checking, savings, credit_line, loan
    
    # Währung
    currency = Column(String(3), default="EUR")
    
    # Buchhaltung
    ledger_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # Salden
    current_balance = Column(Numeric(15, 2), default=0)
    available_balance = Column(Numeric(15, 2), default=0)
    credit_limit = Column(Numeric(15, 2), default=0)  # Kreditlinie/Dispo
    
    balance_date = Column(Date, nullable=True)  # Stand per
    
    # Online-Banking
    online_banking_enabled = Column(Boolean, default=False)
    bank_connection_id = Column(String(100), nullable=True)  # finAPI / FinTS ID
    last_sync = Column(DateTime, nullable=True)
    
    # SEPA-Mandate
    creditor_id = Column(String(50), nullable=True)  # Gläubiger-ID für Lastschriften
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Standardkonto
    
    # Kontakt
    bank_phone = Column(String(50), nullable=True)
    bank_email = Column(String(255), nullable=True)
    bank_contact = Column(String(255), nullable=True)  # Ansprechpartner
    
    # Zusätzliche Infos
    opening_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # FinTS/HBCI Online-Banking
    provider = Column(String(50), default="manual")  # fints, manual
    credentials_encrypted = Column(Text, nullable=True)  # Verschlüsselte Zugangsdaten
    balance = Column(Numeric(15, 2), default=0)  # Aktueller Kontostand (von FinTS)
    
    # Relationships
    transactions = relationship("Payment", back_populates="bank_account")
    bank_transactions = relationship("OnlineBankingTransaction", back_populates="account")


# Alias für Banking-Service Kompatibilität
BankAccountModel = BankAccount


# =============================================================================
# BANK-TRANSAKTIONEN (von Online-Banking/FinTS)
# =============================================================================

class OnlineBankingTransaction(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Banktransaktion von Online-Banking Sync (FinTS/HBCI)"""
    __tablename__ = "online_banking_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('bank_accounts.id'), nullable=False)
    
    # Datum
    date = Column(Date, nullable=False, index=True)
    value_date = Column(Date, nullable=True)
    
    # Betrag
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Beschreibung
    description = Column(Text, nullable=True)
    booking_text = Column(String(255), nullable=True)
    
    # Partner
    partner_name = Column(String(255), nullable=True)
    partner_iban = Column(String(50), nullable=True)
    
    # Referenz
    reference = Column(String(255), nullable=True)
    
    # Transaktionstyp
    transaction_type = Column(String(20), nullable=False)  # CREDIT, DEBIT
    
    # Matching
    is_matched = Column(Boolean, default=False)
    matched_invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=True)
    matched_payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id'), nullable=True)
    
    # Kategorie
    category = Column(String(100), nullable=True)
    
    # Relationships
    account = relationship("BankAccount", back_populates="bank_transactions")
    matched_invoice = relationship("Invoice", foreign_keys=[matched_invoice_id])
    matched_payment = relationship("Payment", foreign_keys=[matched_payment_id])


# Alias für Banking-Service Kompatibilität
BankTransactionModel = OnlineBankingTransaction


# =============================================================================
# ZAHLUNGEN
# =============================================================================

class Payment(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Zahlung (Ein- und Ausgang)"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Zahlungsnummer
    payment_number = Column(String(50), nullable=False, index=True)
    
    # Richtung
    direction = Column(Enum(PaymentDirection), nullable=False)
    
    # Methode
    payment_method = Column(Enum(PaymentMethodType), default=PaymentMethodType.BANK_TRANSFER)
    
    # Betrag
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    exchange_rate = Column(Numeric(10, 6), default=1)
    amount_in_base_currency = Column(Numeric(15, 2), nullable=True)
    
    # Daten
    payment_date = Column(Date, nullable=False)  # Zahlungsdatum
    value_date = Column(Date, nullable=True)  # Wertstellung
    due_date = Column(Date, nullable=True)  # Fälligkeitsdatum
    
    # Bankkonto
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey('bank_accounts.id'), nullable=True)
    
    # Partner
    partner_type = Column(String(50), nullable=True)  # customer, supplier
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), nullable=True)  # Für Lieferanten
    
    # Partner-Bankdaten
    partner_name = Column(String(255), nullable=True)
    partner_iban = Column(String(50), nullable=True)
    partner_bic = Column(String(20), nullable=True)
    partner_bank = Column(String(255), nullable=True)
    
    # Referenz
    reference = Column(String(255), nullable=True)  # Verwendungszweck
    internal_reference = Column(String(100), nullable=True)  # Interne Referenz
    bank_reference = Column(String(100), nullable=True)  # Bank-Transaktions-ID
    
    # Verknüpfte Dokumente
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=True)
    
    # Skonto
    discount_amount = Column(Numeric(15, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Buchhaltung
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    
    # SEPA
    sepa_batch_id = Column(UUID(as_uuid=True), ForeignKey('sepa_batches.id'), nullable=True)
    mandate_id = Column(UUID(as_uuid=True), ForeignKey('sepa_mandates.id'), nullable=True)
    
    # Fehler
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Dokumente
    attachments = Column(JSONB, default=list)
    
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'payment_number', name='uq_payment_number'),
    )
    
    # Relationships
    bank_account = relationship("BankAccount", back_populates="transactions")
    customer = relationship("Customer")
    invoice = relationship("Invoice", back_populates="payments")
    allocations = relationship("PaymentAllocation", back_populates="payment")


class PaymentAllocation(Base, TimestampMixin, TenantMixin):
    """Zahlungszuordnung zu Rechnungen"""
    __tablename__ = "payment_allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id'), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    
    amount = Column(Numeric(15, 2), nullable=False)  # Zugeordneter Betrag
    discount_amount = Column(Numeric(15, 2), default=0)  # Skonto
    
    allocation_date = Column(Date, nullable=False)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="allocations")
    invoice = relationship("Invoice")


# =============================================================================
# SEPA
# =============================================================================

class SepaMandate(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """SEPA-Lastschriftmandat"""
    __tablename__ = "sepa_mandates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    
    # Mandatsreferenz
    mandate_reference = Column(String(35), nullable=False, unique=True)
    
    # Mandatstyp
    mandate_type = Column(String(20), default="RCUR")  # OOFF (einmalig), RCUR (wiederkehrend)
    sequence_type = Column(String(10), default="RCUR")  # FRST, RCUR, OOFF, FNAL
    
    # Unterschrift
    signature_date = Column(Date, nullable=False)
    signature_city = Column(String(100), nullable=True)
    
    # Bankverbindung
    debtor_name = Column(String(255), nullable=False)
    debtor_iban = Column(String(50), nullable=False)
    debtor_bic = Column(String(20), nullable=True)
    
    # Gültigkeit
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    
    # Letzte Nutzung
    last_used_date = Column(Date, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="active")  # active, suspended, cancelled, expired
    cancellation_date = Column(Date, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Dokument
    document_url = Column(String(500), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")


class SepaBatch(Base, TimestampMixin, TenantMixin, AuditMixin):
    """SEPA-Sammler (für Lastschriften oder Überweisungen)"""
    __tablename__ = "sepa_batches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Batch-Infos
    batch_number = Column(String(50), nullable=False, index=True)
    batch_type = Column(String(20), nullable=False)  # direct_debit, credit_transfer
    
    # Ausführungsdatum
    execution_date = Column(Date, nullable=False)
    
    # Beträge
    total_amount = Column(Numeric(15, 2), nullable=False)
    transaction_count = Column(Integer, default=0)
    
    # Bankkonto
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey('bank_accounts.id'), nullable=False)
    
    # Status
    status = Column(String(50), default="created")  # created, validated, submitted, processed, failed
    
    # SEPA-XML
    sepa_file_url = Column(String(500), nullable=True)
    message_id = Column(String(50), nullable=True)
    
    # Verarbeitung
    submitted_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Fehler
    error_message = Column(Text, nullable=True)
    rejected_count = Column(Integer, default=0)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    bank_account = relationship("BankAccount")
    payments = relationship("Payment", backref="sepa_batch")


# =============================================================================
# MAHNWESEN
# =============================================================================

class DunningRun(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Mahnlauf"""
    __tablename__ = "dunning_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    run_number = Column(String(50), nullable=False, index=True)
    run_date = Column(Date, nullable=False)
    
    # Einstellungen
    reference_date = Column(Date, nullable=False)  # Stichtag
    min_amount = Column(Numeric(15, 2), default=0)  # Mindestbetrag
    grace_days = Column(Integer, default=0)  # Karenzzeit
    
    # Ergebnis
    total_customers = Column(Integer, default=0)
    total_invoices = Column(Integer, default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(String(50), default="created")  # created, processing, completed, cancelled
    
    completed_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    notices = relationship("DunningNotice", back_populates="dunning_run")


class DunningNotice(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Mahnung"""
    __tablename__ = "dunning_notices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dunning_run_id = Column(UUID(as_uuid=True), ForeignKey('dunning_runs.id'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    
    # Mahnnummer
    notice_number = Column(String(50), nullable=False, index=True)
    notice_date = Column(Date, nullable=False)
    
    # Mahnstufe
    dunning_level = Column(Enum(DunningLevel), nullable=False)
    
    # Frist
    due_date = Column(Date, nullable=False)  # Zahlungsfrist
    
    # Beträge
    outstanding_amount = Column(Numeric(15, 2), nullable=False)  # Offener Betrag
    dunning_fee = Column(Numeric(15, 2), default=0)  # Mahngebühr
    interest_amount = Column(Numeric(15, 2), default=0)  # Verzugszinsen
    total_amount = Column(Numeric(15, 2), nullable=False)  # Gesamtforderung
    
    # Zinsen
    interest_rate = Column(Numeric(6, 4), nullable=True)  # Zinssatz p.a.
    interest_from = Column(Date, nullable=True)
    interest_to = Column(Date, nullable=True)
    
    # Versand
    sent_at = Column(DateTime, nullable=True)
    send_method = Column(String(50), nullable=True)  # email, mail, both
    email_address = Column(String(255), nullable=True)
    
    # Dokument
    pdf_url = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), default="created")  # created, sent, paid, cancelled, escalated
    
    # Reaktion
    response_date = Column(Date, nullable=True)
    response_notes = Column(Text, nullable=True)
    payment_promise_date = Column(Date, nullable=True)  # Zahlungszusage
    
    # Eskalation
    escalated_at = Column(DateTime, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    collection_agency = Column(String(255), nullable=True)  # Inkassobüro
    
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'notice_number', name='uq_dunning_notice_number'),
    )
    
    # Relationships
    dunning_run = relationship("DunningRun", back_populates="notices")
    customer = relationship("Customer")
    items = relationship("DunningNoticeItem", back_populates="notice", cascade="all, delete-orphan")


class DunningNoticeItem(Base, TimestampMixin, TenantMixin):
    """Mahnposition (einzelne Rechnung in der Mahnung)"""
    __tablename__ = "dunning_notice_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notice_id = Column(UUID(as_uuid=True), ForeignKey('dunning_notices.id'), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=False)
    
    # Rechnungsdaten
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)
    original_due_date = Column(Date, nullable=False)
    
    # Beträge
    invoice_amount = Column(Numeric(15, 2), nullable=False)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    
    # Verzug
    days_overdue = Column(Integer, default=0)
    
    # Zinsen
    interest_amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    notice = relationship("DunningNotice", back_populates="items")
    invoice = relationship("Invoice")


class DunningBlock(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Mahnsperre"""
    __tablename__ = "dunning_blocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Entweder Kunde oder Rechnung
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey('invoices.id'), nullable=True)
    
    # Zeitraum
    block_from = Column(Date, nullable=False)
    block_until = Column(Date, nullable=True)
    
    reason = Column(Text, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    notes = Column(Text, nullable=True)


# =============================================================================
# LIQUIDITÄTSPLANUNG
# =============================================================================

class CashFlowForecast(Base, TimestampMixin, TenantMixin, AuditMixin):
    """Liquiditätsplanung"""
    __tablename__ = "cash_flow_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Planungszeitraum
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Planungsintervall
    interval = Column(String(20), default="weekly")  # daily, weekly, monthly
    
    # Startsaldo
    opening_balance = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(String(50), default="draft")  # draft, approved, active, archived
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("CashFlowForecastItem", back_populates="forecast", cascade="all, delete-orphan")


class CashFlowForecastItem(Base, TimestampMixin, TenantMixin):
    """Einzelposition der Liquiditätsplanung"""
    __tablename__ = "cash_flow_forecast_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey('cash_flow_forecasts.id'), nullable=False)
    
    # Periode
    period_date = Column(Date, nullable=False)  # Datum der Periode
    period_label = Column(String(50), nullable=True)  # z.B. "KW 1", "Januar"
    
    # === EINNAHMEN ===
    # Geplant
    planned_receivables = Column(Numeric(15, 2), default=0)  # Erwartete Kundenzahlungen
    planned_other_income = Column(Numeric(15, 2), default=0)  # Sonstige Einnahmen
    total_planned_income = Column(Numeric(15, 2), default=0)
    
    # Tatsächlich
    actual_income = Column(Numeric(15, 2), default=0)
    
    # === AUSGABEN ===
    # Geplant
    planned_payables = Column(Numeric(15, 2), default=0)  # Lieferantenzahlungen
    planned_payroll = Column(Numeric(15, 2), default=0)  # Gehälter
    planned_taxes = Column(Numeric(15, 2), default=0)  # Steuern
    planned_rent = Column(Numeric(15, 2), default=0)  # Miete
    planned_insurance = Column(Numeric(15, 2), default=0)  # Versicherungen
    planned_loans = Column(Numeric(15, 2), default=0)  # Kredittilgung
    planned_other_expenses = Column(Numeric(15, 2), default=0)  # Sonstige
    total_planned_expenses = Column(Numeric(15, 2), default=0)
    
    # Tatsächlich
    actual_expenses = Column(Numeric(15, 2), default=0)
    
    # === SALDO ===
    planned_net_flow = Column(Numeric(15, 2), default=0)  # Geplanter Netto-Cashflow
    actual_net_flow = Column(Numeric(15, 2), default=0)  # Tatsächlicher Netto-Cashflow
    
    planned_closing_balance = Column(Numeric(15, 2), default=0)  # Geplanter Endstand
    actual_closing_balance = Column(Numeric(15, 2), default=0)  # Tatsächlicher Endstand
    
    # Detaildaten
    details = Column(JSONB, default=dict)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    forecast = relationship("CashFlowForecast", back_populates="items")


# =============================================================================
# FINANZIELLE KENNZAHLEN
# =============================================================================

class FinancialKPI(Base, TimestampMixin, TenantMixin):
    """Finanzielle Kennzahlen"""
    __tablename__ = "financial_kpis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Periode
    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=True)
    period_quarter = Column(Integer, nullable=True)
    
    period_type = Column(String(20), nullable=False)  # monthly, quarterly, annual
    
    # === LIQUIDITÄTSKENNZAHLEN ===
    current_ratio = Column(Numeric(10, 4), nullable=True)  # Liquidität 3. Grades
    quick_ratio = Column(Numeric(10, 4), nullable=True)  # Liquidität 2. Grades
    cash_ratio = Column(Numeric(10, 4), nullable=True)  # Liquidität 1. Grades
    
    working_capital = Column(Numeric(15, 2), nullable=True)  # Working Capital
    
    # === RENTABILITÄTSKENNZAHLEN ===
    gross_margin = Column(Numeric(10, 4), nullable=True)  # Rohertragsmarge
    operating_margin = Column(Numeric(10, 4), nullable=True)  # Operative Marge
    net_margin = Column(Numeric(10, 4), nullable=True)  # Nettomarge
    
    return_on_equity = Column(Numeric(10, 4), nullable=True)  # Eigenkapitalrendite
    return_on_assets = Column(Numeric(10, 4), nullable=True)  # Gesamtkapitalrendite
    return_on_investment = Column(Numeric(10, 4), nullable=True)  # ROI
    
    # === EFFIZIENZ ===
    days_sales_outstanding = Column(Numeric(10, 2), nullable=True)  # DSO (Debitorenlaufzeit)
    days_payables_outstanding = Column(Numeric(10, 2), nullable=True)  # DPO (Kreditorenlaufzeit)
    inventory_turnover = Column(Numeric(10, 2), nullable=True)  # Lagerumschlag
    
    # === UMSATZ ===
    revenue = Column(Numeric(15, 2), nullable=True)  # Umsatz
    revenue_growth = Column(Numeric(10, 4), nullable=True)  # Umsatzwachstum
    
    # === SCHULDEN ===
    debt_to_equity = Column(Numeric(10, 4), nullable=True)  # Verschuldungsgrad
    interest_coverage = Column(Numeric(10, 4), nullable=True)  # Zinsdeckungsgrad
    
    # === PERSONAL ===
    revenue_per_employee = Column(Numeric(15, 2), nullable=True)  # Umsatz pro Mitarbeiter
    
    # Berechnung
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Details
    calculation_details = Column(JSONB, default=dict)
    
    notes = Column(Text, nullable=True)


# =============================================================================
# KREDITE & FINANZIERUNGEN
# =============================================================================

class Loan(Base, TimestampMixin, SoftDeleteMixin, TenantMixin, AuditMixin):
    """Kredit / Darlehen"""
    __tablename__ = "loans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identifikation
    loan_number = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Kreditgeber
    lender_name = Column(String(255), nullable=False)
    lender_account_number = Column(String(100), nullable=True)
    
    # Kreditart
    loan_type = Column(String(50), nullable=False)  # term_loan, credit_line, mortgage, leasing
    
    # Beträge
    principal_amount = Column(Numeric(15, 2), nullable=False)  # Kreditsumme
    current_balance = Column(Numeric(15, 2), nullable=False)  # Aktueller Saldo
    
    # Zinsen
    interest_rate = Column(Numeric(8, 4), nullable=False)  # Zinssatz p.a.
    interest_type = Column(String(50), default="fixed")  # fixed, variable
    reference_rate = Column(String(50), nullable=True)  # z.B. EURIBOR
    
    # Laufzeit
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    term_months = Column(Integer, nullable=False)
    
    # Tilgung
    repayment_type = Column(String(50), default="annuity")  # annuity, linear, bullet
    payment_frequency = Column(String(20), default="monthly")  # monthly, quarterly, semi_annual, annual
    monthly_payment = Column(Numeric(15, 2), nullable=True)  # Rate
    
    first_payment_date = Column(Date, nullable=True)
    next_payment_date = Column(Date, nullable=True)
    
    # Sicherheiten
    collateral = Column(Text, nullable=True)
    
    # Gebühren
    origination_fee = Column(Numeric(15, 2), default=0)  # Bearbeitungsgebühr
    
    # Buchhaltung
    liability_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    interest_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # Status
    status = Column(String(50), default="active")  # pending, active, paid_off, defaulted
    
    # Dokumente
    contract_url = Column(String(500), nullable=True)
    attachments = Column(JSONB, default=list)
    
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=list)
    custom_fields = Column(JSONB, default=dict)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'loan_number', name='uq_loan_number'),
    )
    
    # Relationships
    payments = relationship("LoanPayment", back_populates="loan")


class LoanPayment(Base, TimestampMixin, TenantMixin):
    """Kredit-Zahlung / Rate"""
    __tablename__ = "loan_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey('loans.id'), nullable=False)
    
    payment_number = Column(Integer, nullable=False)  # Ratennummer
    due_date = Column(Date, nullable=False)  # Fälligkeitsdatum
    
    # Beträge
    payment_amount = Column(Numeric(15, 2), nullable=False)  # Gesamtrate
    principal_amount = Column(Numeric(15, 2), nullable=False)  # Tilgung
    interest_amount = Column(Numeric(15, 2), nullable=False)  # Zinsen
    fee_amount = Column(Numeric(15, 2), default=0)  # Gebühren
    
    # Salden
    balance_before = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    
    # Zahlung
    payment_date = Column(Date, nullable=True)
    paid_amount = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, paid, overdue, waived
    
    # Buchung
    journal_id = Column(UUID(as_uuid=True), ForeignKey('journals.id'), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    loan = relationship("Loan", back_populates="payments")


# =============================================================================
# EINSTELLUNGEN
# =============================================================================

class FinanceSettings(Base, TimestampMixin, TenantMixin):
    """Finanz-Einstellungen"""
    __tablename__ = "finance_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # === ZAHLUNGSBEDINGUNGEN ===
    default_payment_terms = Column(Integer, default=30)  # Tage
    
    # Skonto
    cash_discount_percent = Column(Numeric(5, 2), default=2)
    cash_discount_days = Column(Integer, default=10)
    
    # === MAHNWESEN ===
    dunning_enabled = Column(Boolean, default=True)
    
    # Mahngebühren
    reminder_fee = Column(Numeric(10, 2), default=0)
    first_dunning_fee = Column(Numeric(10, 2), default=5)
    second_dunning_fee = Column(Numeric(10, 2), default=10)
    third_dunning_fee = Column(Numeric(10, 2), default=15)
    
    # Verzugszinsen
    default_interest_rate = Column(Numeric(6, 4), default=9)  # Basiszins + 9%
    
    # Fristen (Tage nach Fälligkeit)
    reminder_days = Column(Integer, default=7)
    first_dunning_days = Column(Integer, default=14)
    second_dunning_days = Column(Integer, default=28)
    third_dunning_days = Column(Integer, default=42)
    
    # Mindestbetrag
    min_dunning_amount = Column(Numeric(10, 2), default=5)
    
    # === BANKVERBINDUNG ===
    default_bank_account_id = Column(UUID(as_uuid=True), ForeignKey('bank_accounts.id'), nullable=True)
    
    # SEPA
    creditor_id = Column(String(50), nullable=True)  # Gläubiger-ID
    
    # === BUCHHALTUNG ===
    default_receivables_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    default_payables_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    default_revenue_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=True)
    
    # === WÄHRUNG ===
    base_currency = Column(String(3), default="EUR")
    display_currency_symbol = Column(Boolean, default=True)
    decimal_places = Column(Integer, default=2)
    
    # === ZUSÄTZLICHE EINSTELLUNGEN ===
    custom_settings = Column(JSONB, default=dict)
