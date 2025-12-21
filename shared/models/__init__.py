"""
Shared Models - All Database Models Export
Enterprise Holzbau ERP
"""
from shared.database import Base

# Auth Models
from shared.models.auth import (
    User, Role, Permission, RefreshToken, Tenant,
    user_roles, role_permissions
)

# Customer Models
from shared.models.customer import (
    Customer, Contact, CustomerAddress,
    CustomerType, CustomerStatus
)

# Project Models
from shared.models.project import (
    Project, ProjectPhase, ProjectTask, ProjectDocument, ProjectTeamMember,
    ProjectType, ProjectStatus, ConstructionType
)

# Inventory Models
from shared.models.inventory import (
    Material, Supplier, SupplierArticle,
    Warehouse, WarehouseLocation, StockLevel, StockMovement,
    MaterialCategory, StockMovementType
)

# Employee Models
from shared.models.employee import (
    Employee, TimeEntry, Absence, Certification,
    EmploymentType, EmployeeStatus
)

# Order Models
from shared.models.order import (
    Quote, QuoteItem, Order, OrderItem,
    PurchaseOrder, PurchaseOrderItem,
    QuoteStatus, OrderStatus
)

# Invoice Models
from shared.models.invoice import (
    Invoice, InvoiceItem, RecurringInvoice, RecurringInvoiceItem,
    InvoiceType, InvoiceStatus, PaymentMethod
)

# Construction Diary Models
from shared.models.construction import (
    ConstructionDiary, ConstructionDiaryEntry, SiteInspection, WeatherLog,
    WeatherCondition, DiaryEntryType
)

# Fleet & Equipment Models
from shared.models.fleet import (
    Vehicle, Equipment, FuelLog, MileageLog,
    VehicleMaintenance, EquipmentMaintenance, EquipmentReservation,
    VehicleType, VehicleStatus, EquipmentType
)

# CRM Models
from shared.models.crm import (
    Activity, Lead, CommunicationTemplate, Campaign, CustomerInteraction, Task,
    ActivityType, ActivityPriority, LeadStatus, LeadSource
)

# Quality Control Models
from shared.models.quality import (
    Defect, QualityCheck, QualityCheckTemplate, Warranty, Certificate,
    DefectSeverity, DefectStatus, QualityCheckType
)

# Telemetry Models
from shared.models.telemetry import (
    TelemetryEvent, SystemMetric, PerformanceTrace, ErrorLog,
    UserSession, UserActivity, AuditLog, FeatureUsage, SystemHealth, Alert,
    ReportSchedule, EventSeverity, EventCategory, MetricType
)

# Accounting Models
from shared.models.accounting import (
    ChartOfAccounts, Account, CostCenter, CostObject,
    FiscalYear, FiscalPeriod, Journal, JournalItem,
    TaxRate, TaxReport, BankStatement, BankTransaction,
    Budget, BudgetItem, FixedAsset, DepreciationEntry,
    AccountType, AccountCategory, BookingStatus, TaxType, FiscalYearStatus
)

# Payroll Models
from shared.models.payroll import (
    PayrollPeriod, SalaryComponent, EmployeeSalary, EmployeeSalaryComponent,
    Payslip, PayslipItem, BonusPayment, EmployeeAdvance, AdvanceRepayment,
    EmployeeLoan, Garnishment, SocialSecurityReport, TaxPayrollReport,
    CompanyPensionPlan, PensionEnrollment,
    PayrollStatus, PaymentMethod as PayrollPaymentMethod, DeductionType, AllowanceType
)

# Finance Models
from shared.models.finance import (
    BankAccount, Payment, PaymentAllocation,
    SepaMandate, SepaBatch, DunningRun, DunningNotice, DunningNoticeItem,
    DunningBlock, CashFlowForecast, CashFlowForecastItem, FinancialKPI,
    Loan, LoanPayment, FinanceSettings,
    PaymentStatus, PaymentDirection, PaymentMethodType, DunningLevel
)

__all__ = [
    # Base
    "Base",
    
    # Auth
    "User", "Role", "Permission", "RefreshToken", "Tenant",
    "user_roles", "role_permissions",
    
    # Customer
    "Customer", "Contact", "CustomerAddress",
    "CustomerType", "CustomerStatus",
    
    # Project
    "Project", "ProjectPhase", "ProjectTask", "ProjectDocument", "ProjectTeamMember",
    "ProjectType", "ProjectStatus", "ConstructionType",
    
    # Inventory
    "Material", "Supplier", "SupplierArticle",
    "Warehouse", "WarehouseLocation", "StockLevel", "StockMovement",
    "MaterialCategory", "StockMovementType",
    
    # Employee
    "Employee", "TimeEntry", "Absence", "Certification",
    "EmploymentType", "EmployeeStatus",
    
    # Order
    "Quote", "QuoteItem", "Order", "OrderItem",
    "PurchaseOrder", "PurchaseOrderItem",
    "QuoteStatus", "OrderStatus",
    
    # Invoice
    "Invoice", "InvoiceItem", "RecurringInvoice", "RecurringInvoiceItem",
    "InvoiceType", "InvoiceStatus", "PaymentMethod",
    
    # Construction Diary
    "ConstructionDiary", "ConstructionDiaryEntry", "SiteInspection", "WeatherLog",
    "WeatherCondition", "DiaryEntryType",
    
    # Fleet & Equipment
    "Vehicle", "Equipment", "FuelLog", "MileageLog",
    "VehicleMaintenance", "EquipmentMaintenance", "EquipmentReservation",
    "VehicleType", "VehicleStatus", "EquipmentType",
    
    # CRM
    "Activity", "Lead", "CommunicationTemplate", "Campaign", "CustomerInteraction", "Task",
    "ActivityType", "ActivityPriority", "LeadStatus", "LeadSource",
    
    # Quality Control
    "Defect", "QualityCheck", "QualityCheckTemplate", "Warranty", "Certificate",
    "DefectSeverity", "DefectStatus", "QualityCheckType",
    
    # Telemetry
    "TelemetryEvent", "SystemMetric", "PerformanceTrace", "ErrorLog",
    "UserSession", "UserActivity", "AuditLog", "FeatureUsage", "SystemHealth", "Alert",
    "ReportSchedule", "EventSeverity", "EventCategory", "MetricType",
    
    # Accounting
    "ChartOfAccounts", "Account", "CostCenter", "CostObject",
    "FiscalYear", "FiscalPeriod", "Journal", "JournalItem",
    "TaxRate", "TaxReport", "BankStatement", "BankTransaction",
    "Budget", "BudgetItem", "FixedAsset", "DepreciationEntry",
    "AccountType", "AccountCategory", "BookingStatus", "TaxType", "FiscalYearStatus",
    
    # Payroll
    "PayrollPeriod", "SalaryComponent", "EmployeeSalary", "EmployeeSalaryComponent",
    "Payslip", "PayslipItem", "BonusPayment", "EmployeeAdvance", "AdvanceRepayment",
    "EmployeeLoan", "Garnishment", "SocialSecurityReport", "TaxPayrollReport",
    "CompanyPensionPlan", "PensionEnrollment",
    "PayrollStatus", "PayrollPaymentMethod", "DeductionType", "AllowanceType",
    
    # Finance
    "BankAccount", "Payment", "PaymentAllocation",
    "SepaMandate", "SepaBatch", "DunningRun", "DunningNotice", "DunningNoticeItem",
    "DunningBlock", "CashFlowForecast", "CashFlowForecastItem", "FinancialKPI",
    "Loan", "LoanPayment", "FinanceSettings",
    "PaymentStatus", "PaymentDirection", "PaymentMethodType", "DunningLevel",
]
