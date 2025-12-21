"""
Telemetrie-Datenmodelle für umfassendes System-Monitoring
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum, JSON, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import enum

from shared.models.base import Base, TimestampMixin, TenantMixin


class EventSeverity(enum.Enum):
    """Event-Schweregrad"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventCategory(enum.Enum):
    """Event-Kategorie"""
    SYSTEM = "system"
    USER = "user"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    ERROR = "error"
    AUDIT = "audit"


class MetricType(enum.Enum):
    """Metrik-Typ"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class TelemetryEvent(Base, TimestampMixin):
    """Telemetrie-Events für alle System-Ereignisse"""
    __tablename__ = 'telemetry_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # Event-Identifikation
    event_id = Column(String(100), nullable=False, index=True)
    event_name = Column(String(255), nullable=False, index=True)
    event_version = Column(String(20), default="1.0")
    
    # Kategorisierung
    category = Column(Enum(EventCategory), default=EventCategory.SYSTEM, index=True)
    severity = Column(Enum(EventSeverity), default=EventSeverity.INFO, index=True)
    tags = Column(ARRAY(String), default=[])
    
    # Event-Daten
    event_data = Column(JSONB, default={})
    event_context = Column(JSONB, default={})
    
    # Zeitstempel
    event_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Quelle
    source_module = Column(String(100), nullable=True, index=True)
    source_function = Column(String(255), nullable=True)
    source_file = Column(String(500), nullable=True)
    source_line = Column(Integer, nullable=True)
    
    # User-Kontext
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # Client-Info
    client_ip = Column(INET, nullable=True)
    client_user_agent = Column(Text, nullable=True)
    client_version = Column(String(50), nullable=True)
    client_platform = Column(String(50), nullable=True)
    
    # Korrelation
    correlation_id = Column(String(100), nullable=True, index=True)
    parent_event_id = Column(UUID(as_uuid=True), ForeignKey('telemetry_events.id'), nullable=True)
    trace_id = Column(String(100), nullable=True, index=True)
    span_id = Column(String(100), nullable=True)
    
    # Indexes für schnelle Abfragen
    __table_args__ = (
        Index('ix_telemetry_events_timestamp_category', 'event_timestamp', 'category'),
        Index('ix_telemetry_events_tenant_timestamp', 'tenant_id', 'event_timestamp'),
        Index('ix_telemetry_events_user_timestamp', 'user_id', 'event_timestamp'),
    )


class SystemMetric(Base, TimestampMixin):
    """System-Metriken für Performance-Monitoring"""
    __tablename__ = 'system_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metrik-Identifikation
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(Enum(MetricType), default=MetricType.GAUGE)
    metric_unit = Column(String(50), nullable=True)  # ms, bytes, percent, count
    
    # Werte
    value = Column(Float, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    avg_value = Column(Float, nullable=True)
    sum_value = Column(Float, nullable=True)
    count = Column(Integer, default=1)
    
    # Zeitfenster
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    aggregation_interval = Column(String(20), nullable=True)  # 1m, 5m, 1h, 1d
    
    # Dimensionen/Labels
    labels = Column(JSONB, default={})
    host = Column(String(255), nullable=True, index=True)
    service = Column(String(100), nullable=True, index=True)
    instance = Column(String(100), nullable=True)
    
    # Thresholds
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('ix_system_metrics_name_timestamp', 'metric_name', 'timestamp'),
        Index('ix_system_metrics_service_timestamp', 'service', 'timestamp'),
    )


class PerformanceTrace(Base, TimestampMixin):
    """Performance-Traces für Request-Tracking"""
    __tablename__ = 'performance_traces'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # Trace-Identifikation
    trace_id = Column(String(100), nullable=False, index=True)
    span_id = Column(String(100), nullable=False)
    parent_span_id = Column(String(100), nullable=True)
    
    # Operation
    operation_name = Column(String(255), nullable=False, index=True)
    operation_type = Column(String(50), nullable=True)  # db, http, function, ui
    
    # Timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True, index=True)
    
    # Status
    status_code = Column(String(20), nullable=True)
    is_error = Column(Boolean, default=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Kontext
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Details
    request_data = Column(JSONB, default={})
    response_data = Column(JSONB, default={})
    metadata_info = Column(JSONB, default={})
    tags = Column(ARRAY(String), default=[])
    
    # Resource-Nutzung
    cpu_time_ms = Column(Float, nullable=True)
    memory_used_bytes = Column(Integer, nullable=True)
    db_queries_count = Column(Integer, default=0)
    db_time_ms = Column(Float, nullable=True)
    
    __table_args__ = (
        Index('ix_performance_traces_trace_start', 'trace_id', 'start_time'),
        Index('ix_performance_traces_duration', 'duration_ms'),
    )


class ErrorLog(Base, TimestampMixin):
    """Fehler-Logs für Error-Tracking"""
    __tablename__ = 'error_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # Error-Identifikation
    error_hash = Column(String(64), nullable=False, index=True)  # Für Gruppierung
    error_type = Column(String(255), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    
    # Stack Trace
    stack_trace = Column(Text, nullable=True)
    stack_frames = Column(JSONB, default=[])
    
    # Kontext
    module = Column(String(255), nullable=True, index=True)
    function = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # User/Session
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Request-Kontext
    request_url = Column(String(2000), nullable=True)
    request_method = Column(String(10), nullable=True)
    request_params = Column(JSONB, default={})
    request_headers = Column(JSONB, default={})
    
    # Environment
    environment = Column(String(50), default="production", index=True)
    app_version = Column(String(50), nullable=True)
    python_version = Column(String(20), nullable=True)
    os_info = Column(String(100), nullable=True)
    
    # Severity
    severity = Column(Enum(EventSeverity), default=EventSeverity.ERROR)
    is_handled = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Zusätzliche Daten
    extra_data = Column(JSONB, default={})
    tags = Column(ARRAY(String), default=[])
    
    # Occurrence tracking
    occurrence_count = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('ix_error_logs_hash_env', 'error_hash', 'environment'),
        Index('ix_error_logs_type_last_seen', 'error_type', 'last_seen'),
    )


class UserSession(Base, TimestampMixin):
    """User-Sessions für Session-Tracking"""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Session-Identifikation
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    session_hash = Column(String(64), nullable=True)
    
    # Zeitstempel
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    end_reason = Column(String(50), nullable=True)  # logout, timeout, forced, error
    
    # Client-Info
    client_ip = Column(INET, nullable=True)
    client_user_agent = Column(Text, nullable=True)
    client_device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    client_os = Column(String(100), nullable=True)
    client_browser = Column(String(100), nullable=True)
    client_version = Column(String(50), nullable=True)
    
    # Geolocation
    geo_country = Column(String(100), nullable=True)
    geo_city = Column(String(100), nullable=True)
    geo_latitude = Column(Float, nullable=True)
    geo_longitude = Column(Float, nullable=True)
    
    # Activity Stats
    page_views = Column(Integer, default=0)
    actions_count = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    
    # Security
    is_suspicious = Column(Boolean, default=False)
    security_flags = Column(ARRAY(String), default=[])
    
    __table_args__ = (
        Index('ix_user_sessions_user_active', 'user_id', 'is_active'),
        Index('ix_user_sessions_started', 'started_at'),
    )


class UserActivity(Base, TimestampMixin):
    """User-Aktivitäten für detailliertes Tracking"""
    __tablename__ = 'user_activities'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('user_sessions.id'), nullable=True)
    
    # Activity-Details
    activity_type = Column(String(50), nullable=False, index=True)  # view, click, submit, navigate, etc.
    activity_name = Column(String(255), nullable=False)
    activity_description = Column(Text, nullable=True)
    
    # Location im App
    module = Column(String(100), nullable=True, index=True)
    view = Column(String(100), nullable=True)
    component = Column(String(100), nullable=True)
    
    # Ziel-Entity
    target_entity_type = Column(String(100), nullable=True)  # customer, project, invoice
    target_entity_id = Column(UUID(as_uuid=True), nullable=True)
    target_entity_name = Column(String(255), nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Daten
    activity_data = Column(JSONB, default={})
    previous_state = Column(JSONB, nullable=True)
    new_state = Column(JSONB, nullable=True)
    
    # Ergebnis
    was_successful = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_user_activities_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_user_activities_type_timestamp', 'activity_type', 'timestamp'),
        Index('ix_user_activities_module_timestamp', 'module', 'timestamp'),
    )


class AuditLog(Base, TimestampMixin):
    """Audit-Logs für Compliance"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # User
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)
    user_role = Column(String(100), nullable=True)
    
    # Action
    action = Column(String(50), nullable=False, index=True)  # create, read, update, delete, login, logout
    action_category = Column(String(50), nullable=True)  # data, auth, admin, system
    action_description = Column(Text, nullable=True)
    
    # Resource
    resource_type = Column(String(100), nullable=False, index=True)  # customer, project, invoice
    resource_id = Column(String(100), nullable=True, index=True)
    resource_name = Column(String(255), nullable=True)
    
    # Änderungen
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    changed_fields = Column(ARRAY(String), default=[])
    
    # Kontext
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Compliance
    is_sensitive = Column(Boolean, default=False)  # PII, financial data
    requires_retention = Column(Boolean, default=True)
    retention_until = Column(Date, nullable=True)
    
    # Integrity
    checksum = Column(String(64), nullable=True)  # SHA-256 für Manipulationsschutz
    
    __table_args__ = (
        Index('ix_audit_logs_tenant_timestamp', 'tenant_id', 'timestamp'),
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )


class FeatureUsage(Base, TimestampMixin):
    """Feature-Nutzung für Product Analytics"""
    __tablename__ = 'feature_usage'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # Feature
    feature_name = Column(String(255), nullable=False, index=True)
    feature_category = Column(String(100), nullable=True)
    feature_version = Column(String(20), nullable=True)
    
    # Nutzung
    date = Column(Date, nullable=False, index=True)
    usage_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    total_duration_ms = Column(Integer, default=0)
    avg_duration_ms = Column(Float, nullable=True)
    
    # Erfolgsrate
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    
    # Zusätzliche Metriken
    additional_metrics = Column(JSONB, default={})
    
    __table_args__ = (
        Index('ix_feature_usage_feature_date', 'feature_name', 'date'),
        Index('ix_feature_usage_tenant_date', 'tenant_id', 'date'),
    )


class SystemHealth(Base, TimestampMixin):
    """System-Health-Checks"""
    __tablename__ = 'system_health'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Check-Info
    check_name = Column(String(255), nullable=False, index=True)
    check_type = Column(String(50), nullable=True)  # database, api, service, disk, memory
    
    # Status
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), nullable=False)  # healthy, degraded, unhealthy
    is_healthy = Column(Boolean, default=True, index=True)
    
    # Metriken
    response_time_ms = Column(Float, nullable=True)
    latency_p50_ms = Column(Float, nullable=True)
    latency_p95_ms = Column(Float, nullable=True)
    latency_p99_ms = Column(Float, nullable=True)
    
    # Resource-Nutzung
    cpu_percent = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)
    disk_percent = Column(Float, nullable=True)
    
    # Details
    details = Column(JSONB, default={})
    error_message = Column(Text, nullable=True)
    
    # Verfügbarkeit
    uptime_seconds = Column(Integer, nullable=True)
    last_downtime = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('ix_system_health_check_timestamp', 'check_name', 'timestamp'),
    )


class Alert(Base, TimestampMixin):
    """Alerts für Benachrichtigungen"""
    __tablename__ = 'alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # Alert-Info
    alert_name = Column(String(255), nullable=False)
    alert_type = Column(String(50), nullable=False, index=True)  # threshold, anomaly, pattern
    severity = Column(Enum(EventSeverity), default=EventSeverity.WARNING, index=True)
    
    # Trigger
    trigger_condition = Column(Text, nullable=True)
    trigger_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    
    # Status
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    is_active = Column(Boolean, default=True, index=True)
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(ARRAY(String), default=[])  # email, sms, push
    
    # Kontext
    source_metric = Column(String(255), nullable=True)
    source_service = Column(String(100), nullable=True)
    related_entity_type = Column(String(100), nullable=True)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Details
    message = Column(Text, nullable=True)
    details = Column(JSONB, default={})
    resolution_notes = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_alerts_active_severity', 'is_active', 'severity'),
        Index('ix_alerts_triggered', 'triggered_at'),
    )


class ReportSchedule(Base, TimestampMixin, TenantMixin):
    """Geplante Reports"""
    __tablename__ = 'report_schedules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report-Info
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    report_format = Column(String(20), default="pdf")  # pdf, excel, csv
    
    # Schedule
    is_active = Column(Boolean, default=True)
    schedule_cron = Column(String(100), nullable=True)  # Cron-Expression
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    
    # Recipients
    recipients = Column(ARRAY(String), default=[])  # E-Mail-Adressen
    
    # Filter/Parameter
    report_parameters = Column(JSONB, default={})
    date_range_type = Column(String(50), default="last_7_days")
    
    # Created by
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
