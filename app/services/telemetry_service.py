"""
Telemetrie-Service für umfassendes System-Monitoring
"""
import uuid
import hashlib
import traceback
import platform
import psutil
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from functools import wraps
import threading
import queue
import time
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from shared.models.telemetry import (
    TelemetryEvent, SystemMetric, PerformanceTrace, ErrorLog,
    UserSession, UserActivity, AuditLog, FeatureUsage, SystemHealth, Alert,
    EventSeverity, EventCategory, MetricType
)


class TelemetryService:
    """Zentraler Telemetrie-Service"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton-Pattern"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_service=None):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.db_service = db_service
        self._event_queue = queue.Queue(maxsize=10000)
        self._metric_queue = queue.Queue(maxsize=10000)
        self._is_running = False
        self._worker_thread = None
        self._metric_thread = None
        
        # Current context
        self._current_user_id = None
        self._current_tenant_id = None
        self._current_session_id = None
        
        # Caches
        self._metric_cache: Dict[str, Any] = {}
        self._feature_cache: Dict[str, int] = {}
        
        # App info
        self._app_version = "1.0.0"
        self._environment = os.getenv("ENVIRONMENT", "production")
        
        self._initialized = True
    
    def start(self):
        """Startet die Background-Worker"""
        if self._is_running:
            return
            
        self._is_running = True
        
        # Event-Worker starten
        self._worker_thread = threading.Thread(target=self._event_worker, daemon=True)
        self._worker_thread.start()
        
        # Metric-Worker starten
        self._metric_thread = threading.Thread(target=self._metric_worker, daemon=True)
        self._metric_thread.start()
        
        # System-Health-Check starten
        self._health_thread = threading.Thread(target=self._health_worker, daemon=True)
        self._health_thread.start()
    
    def stop(self):
        """Stoppt die Background-Worker"""
        self._is_running = False
        self._flush_queues()
    
    def set_context(self, user_id: str = None, tenant_id: str = None, session_id: str = None):
        """Setzt den aktuellen Kontext"""
        if user_id:
            try:
                self._current_user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            except (ValueError, AttributeError):
                self._current_user_id = None
        if tenant_id:
            try:
                self._current_tenant_id = uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
            except (ValueError, AttributeError):
                self._current_tenant_id = None
        if session_id:
            self._current_session_id = session_id
    
    def clear_context(self):
        """Löscht den aktuellen Kontext"""
        self._current_user_id = None
        self._current_tenant_id = None
        self._current_session_id = None
    
    # ==================== Events ====================
    
    def track_event(
        self,
        event_name: str,
        category: EventCategory = EventCategory.SYSTEM,
        severity: EventSeverity = EventSeverity.INFO,
        data: Dict[str, Any] = None,
        tags: List[str] = None,
        source_module: str = None,
        correlation_id: str = None
    ):
        """Trackt ein Event"""
        event = {
            'event_id': str(uuid.uuid4()),
            'event_name': event_name,
            'category': category,
            'severity': severity,
            'event_data': data or {},
            'tags': tags or [],
            'source_module': source_module,
            'correlation_id': correlation_id,
            'user_id': self._current_user_id,
            'tenant_id': self._current_tenant_id,
            'session_id': self._current_session_id,
            'event_timestamp': datetime.utcnow()
        }
        
        try:
            self._event_queue.put_nowait(event)
        except queue.Full:
            pass  # Queue voll, Event verwerfen
    
    def track_user_action(
        self,
        action_name: str,
        module: str = None,
        view: str = None,
        target_entity_type: str = None,
        target_entity_id: str = None,
        data: Dict[str, Any] = None,
        was_successful: bool = True
    ):
        """Trackt eine User-Aktion"""
        self.track_event(
            event_name=action_name,
            category=EventCategory.USER,
            severity=EventSeverity.INFO,
            data={
                'module': module,
                'view': view,
                'target_entity_type': target_entity_type,
                'target_entity_id': str(target_entity_id) if target_entity_id else None,
                'was_successful': was_successful,
                **(data or {})
            },
            source_module=module
        )
    
    def track_business_event(
        self,
        event_name: str,
        entity_type: str,
        entity_id: str = None,
        data: Dict[str, Any] = None
    ):
        """Trackt ein Business-Event"""
        self.track_event(
            event_name=event_name,
            category=EventCategory.BUSINESS,
            severity=EventSeverity.INFO,
            data={
                'entity_type': entity_type,
                'entity_id': str(entity_id) if entity_id else None,
                **(data or {})
            }
        )
    
    def track_security_event(
        self,
        event_name: str,
        severity: EventSeverity = EventSeverity.WARNING,
        data: Dict[str, Any] = None
    ):
        """Trackt ein Security-Event"""
        self.track_event(
            event_name=event_name,
            category=EventCategory.SECURITY,
            severity=severity,
            data=data
        )
    
    # ==================== Metriken ====================
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        unit: str = None,
        labels: Dict[str, str] = None,
        service: str = "holzbau_erp"
    ):
        """Zeichnet eine Metrik auf"""
        metric = {
            'metric_name': name,
            'value': value,
            'metric_type': metric_type,
            'metric_unit': unit,
            'labels': labels or {},
            'service': service,
            'host': platform.node(),
            'timestamp': datetime.utcnow()
        }
        
        try:
            self._metric_queue.put_nowait(metric)
        except queue.Full:
            pass
    
    def increment_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None):
        """Inkrementiert einen Counter"""
        self.record_metric(name, value, MetricType.COUNTER, labels=labels)
    
    def record_timing(self, name: str, duration_ms: float, labels: Dict[str, str] = None):
        """Zeichnet eine Timing-Metrik auf"""
        self.record_metric(name, duration_ms, MetricType.TIMER, unit="ms", labels=labels)
    
    def record_gauge(self, name: str, value: float, unit: str = None, labels: Dict[str, str] = None):
        """Zeichnet eine Gauge-Metrik auf"""
        self.record_metric(name, value, MetricType.GAUGE, unit=unit, labels=labels)
    
    # ==================== Performance Tracing ====================
    
    def start_trace(self, operation_name: str, operation_type: str = None) -> 'TraceContext':
        """Startet einen Performance-Trace"""
        return TraceContext(self, operation_name, operation_type)
    
    def record_trace(
        self,
        operation_name: str,
        duration_ms: float,
        operation_type: str = None,
        is_error: bool = False,
        error_message: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Zeichnet einen Trace auf"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:16]
        
        if self.db_service:
            try:
                with self.db_service.get_session() as session:
                    trace = PerformanceTrace(
                        trace_id=trace_id,
                        span_id=span_id,
                        operation_name=operation_name,
                        operation_type=operation_type,
                        start_time=datetime.utcnow() - timedelta(milliseconds=duration_ms),
                        end_time=datetime.utcnow(),
                        duration_ms=duration_ms,
                        is_error=is_error,
                        error_message=error_message,
                        user_id=self._current_user_id,
                        tenant_id=self._current_tenant_id,
                        session_id=self._current_session_id,
                        metadata_info=metadata or {}
                    )
                    session.add(trace)
                    session.commit()
            except Exception:
                pass
    
    # ==================== Error Tracking ====================
    
    def track_error(
        self,
        error: Exception,
        module: str = None,
        extra_data: Dict[str, Any] = None,
        is_handled: bool = True
    ):
        """Trackt einen Fehler"""
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Error-Hash für Gruppierung
        error_hash = hashlib.sha256(
            f"{error_type}:{error_message}:{module}".encode()
        ).hexdigest()[:64]
        
        # Stack-Frames extrahieren
        tb = traceback.extract_tb(error.__traceback__)
        stack_frames = [
            {
                'filename': frame.filename,
                'line': frame.lineno,
                'function': frame.name,
                'code': frame.line
            }
            for frame in tb
        ]
        
        if self.db_service:
            try:
                with self.db_service.get_session() as session:
                    # Prüfen ob Error bereits existiert
                    existing = session.query(ErrorLog).filter(
                        ErrorLog.error_hash == error_hash,
                        ErrorLog.is_resolved == False
                    ).first()
                    
                    if existing:
                        existing.occurrence_count += 1
                        existing.last_seen = datetime.utcnow()
                    else:
                        error_log = ErrorLog(
                            error_hash=error_hash,
                            error_type=error_type,
                            error_message=error_message,
                            stack_trace=stack_trace,
                            stack_frames=stack_frames,
                            module=module,
                            user_id=self._current_user_id,
                            tenant_id=self._current_tenant_id,
                            session_id=self._current_session_id,
                            environment=self._environment,
                            app_version=self._app_version,
                            python_version=sys.version,
                            os_info=f"{platform.system()} {platform.release()}",
                            is_handled=is_handled,
                            extra_data=extra_data or {}
                        )
                        session.add(error_log)
                    
                    session.commit()
            except Exception:
                pass
        
        # Auch als Event tracken
        self.track_event(
            event_name=f"error:{error_type}",
            category=EventCategory.ERROR,
            severity=EventSeverity.ERROR,
            data={
                'error_type': error_type,
                'error_message': error_message,
                'module': module,
                'is_handled': is_handled
            },
            source_module=module
        )
    
    # ==================== Audit Logging ====================
    
    def audit_log(
        self,
        action: str,
        resource_type: str,
        resource_id: str = None,
        resource_name: str = None,
        old_values: Dict[str, Any] = None,
        new_values: Dict[str, Any] = None,
        description: str = None,
        is_sensitive: bool = False
    ):
        """Erstellt einen Audit-Log-Eintrag"""
        changed_fields = []
        if old_values and new_values:
            changed_fields = [k for k in new_values.keys() if k in old_values and old_values[k] != new_values[k]]
        
        # Checksum für Integrität
        checksum_data = f"{action}:{resource_type}:{resource_id}:{datetime.utcnow().isoformat()}"
        checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
        
        if self.db_service:
            try:
                with self.db_service.get_session() as session:
                    audit = AuditLog(
                        user_id=self._current_user_id,
                        tenant_id=self._current_tenant_id,
                        action=action,
                        action_description=description,
                        resource_type=resource_type,
                        resource_id=str(resource_id) if resource_id else None,
                        resource_name=resource_name,
                        old_values=old_values,
                        new_values=new_values,
                        changed_fields=changed_fields,
                        session_id=self._current_session_id,
                        is_sensitive=is_sensitive,
                        checksum=checksum
                    )
                    session.add(audit)
                    session.commit()
            except Exception:
                pass
    
    # ==================== Feature Usage ====================
    
    def track_feature_usage(self, feature_name: str, category: str = None, duration_ms: float = None, was_successful: bool = True):
        """Trackt die Nutzung eines Features"""
        today = datetime.utcnow().date()
        cache_key = f"{feature_name}:{today}"
        
        # Lokalen Cache updaten
        if cache_key not in self._feature_cache:
            self._feature_cache[cache_key] = {'count': 0, 'duration': 0, 'success': 0, 'error': 0}
        
        self._feature_cache[cache_key]['count'] += 1
        if duration_ms:
            self._feature_cache[cache_key]['duration'] += duration_ms
        if was_successful:
            self._feature_cache[cache_key]['success'] += 1
        else:
            self._feature_cache[cache_key]['error'] += 1
        
        # Event tracken
        self.track_event(
            event_name=f"feature:{feature_name}",
            category=EventCategory.USER,
            severity=EventSeverity.INFO,
            data={
                'category': category,
                'duration_ms': duration_ms,
                'was_successful': was_successful
            }
        )
    
    # ==================== System Health ====================
    
    def check_system_health(self) -> Dict[str, Any]:
        """Führt einen System-Health-Check durch"""
        health = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        # CPU
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            health['checks']['cpu'] = {
                'status': 'healthy' if cpu_percent < 80 else 'degraded' if cpu_percent < 95 else 'unhealthy',
                'value': cpu_percent,
                'unit': 'percent'
            }
        except Exception:
            health['checks']['cpu'] = {'status': 'unknown'}
        
        # Memory
        try:
            memory = psutil.virtual_memory()
            health['checks']['memory'] = {
                'status': 'healthy' if memory.percent < 80 else 'degraded' if memory.percent < 95 else 'unhealthy',
                'value': memory.percent,
                'unit': 'percent',
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2)
            }
        except Exception:
            health['checks']['memory'] = {'status': 'unknown'}
        
        # Disk
        try:
            disk = psutil.disk_usage('/')
            health['checks']['disk'] = {
                'status': 'healthy' if disk.percent < 80 else 'degraded' if disk.percent < 95 else 'unhealthy',
                'value': disk.percent,
                'unit': 'percent',
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            }
        except Exception:
            health['checks']['disk'] = {'status': 'unknown'}
        
        # Database
        if self.db_service:
            try:
                start = time.time()
                with self.db_service.get_session() as session:
                    session.execute("SELECT 1")
                latency = (time.time() - start) * 1000
                health['checks']['database'] = {
                    'status': 'healthy' if latency < 100 else 'degraded' if latency < 500 else 'unhealthy',
                    'latency_ms': round(latency, 2)
                }
            except Exception as e:
                health['checks']['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        # Gesamtstatus berechnen
        statuses = [c.get('status', 'unknown') for c in health['checks'].values()]
        if 'unhealthy' in statuses:
            health['status'] = 'unhealthy'
        elif 'degraded' in statuses:
            health['status'] = 'degraded'
        
        return health
    
    def record_system_health(self, health_data: Dict[str, Any]):
        """Speichert System-Health-Daten"""
        if not self.db_service:
            return
            
        try:
            with self.db_service.get_session() as session:
                for check_name, check_data in health_data.get('checks', {}).items():
                    health = SystemHealth(
                        check_name=check_name,
                        check_type=check_name,
                        status=check_data.get('status', 'unknown'),
                        is_healthy=check_data.get('status') == 'healthy',
                        cpu_percent=health_data['checks'].get('cpu', {}).get('value'),
                        memory_percent=health_data['checks'].get('memory', {}).get('value'),
                        disk_percent=health_data['checks'].get('disk', {}).get('value'),
                        response_time_ms=check_data.get('latency_ms'),
                        details=check_data
                    )
                    session.add(health)
                session.commit()
        except Exception:
            pass
    
    # ==================== Alerting ====================
    
    def create_alert(
        self,
        alert_name: str,
        alert_type: str,
        severity: EventSeverity,
        message: str,
        trigger_value: float = None,
        threshold_value: float = None,
        source_metric: str = None,
        details: Dict[str, Any] = None
    ):
        """Erstellt einen Alert"""
        if not self.db_service:
            return
            
        try:
            with self.db_service.get_session() as session:
                alert = Alert(
                    tenant_id=self._current_tenant_id,
                    alert_name=alert_name,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    trigger_value=trigger_value,
                    threshold_value=threshold_value,
                    source_metric=source_metric,
                    details=details or {}
                )
                session.add(alert)
                session.commit()
                
                # Event tracken
                self.track_event(
                    event_name=f"alert:{alert_name}",
                    category=EventCategory.SYSTEM,
                    severity=severity,
                    data={
                        'alert_type': alert_type,
                        'message': message,
                        'trigger_value': trigger_value,
                        'threshold_value': threshold_value
                    }
                )
        except Exception:
            pass
    
    # ==================== Reports & Analytics ====================
    
    def get_dashboard_metrics(self, tenant_id: str = None, days: int = 7) -> Dict[str, Any]:
        """Holt Dashboard-Metriken"""
        if not self.db_service:
            return {}
            
        since = datetime.utcnow() - timedelta(days=days)
        
        try:
            with self.db_service.get_session() as session:
                # Event-Counts
                event_counts = session.query(
                    TelemetryEvent.category,
                    func.count(TelemetryEvent.id)
                ).filter(
                    TelemetryEvent.event_timestamp >= since
                ).group_by(TelemetryEvent.category).all()
                
                # Error-Counts
                error_count = session.query(func.count(ErrorLog.id)).filter(
                    ErrorLog.created_at >= since,
                    ErrorLog.is_resolved == False
                ).scalar()
                
                # Active Sessions
                active_sessions = session.query(func.count(UserSession.id)).filter(
                    UserSession.is_active == True
                ).scalar()
                
                # Top Features
                top_features = session.query(
                    FeatureUsage.feature_name,
                    func.sum(FeatureUsage.usage_count)
                ).filter(
                    FeatureUsage.date >= since.date()
                ).group_by(
                    FeatureUsage.feature_name
                ).order_by(
                    desc(func.sum(FeatureUsage.usage_count))
                ).limit(10).all()
                
                return {
                    'event_counts': {str(cat): count for cat, count in event_counts},
                    'error_count': error_count or 0,
                    'active_sessions': active_sessions or 0,
                    'top_features': [{'name': name, 'count': count} for name, count in top_features]
                }
        except Exception:
            return {}
    
    def get_error_summary(self, days: int = 7) -> List[Dict[str, Any]]:
        """Holt eine Fehler-Zusammenfassung"""
        if not self.db_service:
            return []
            
        since = datetime.utcnow() - timedelta(days=days)
        
        try:
            with self.db_service.get_session() as session:
                errors = session.query(ErrorLog).filter(
                    ErrorLog.created_at >= since
                ).order_by(
                    desc(ErrorLog.occurrence_count)
                ).limit(20).all()
                
                return [
                    {
                        'id': str(e.id),
                        'error_type': e.error_type,
                        'error_message': e.error_message[:200],
                        'module': e.module,
                        'occurrence_count': e.occurrence_count,
                        'first_seen': e.first_seen.isoformat() if e.first_seen else None,
                        'last_seen': e.last_seen.isoformat() if e.last_seen else None,
                        'is_resolved': e.is_resolved
                    }
                    for e in errors
                ]
        except Exception:
            return []
    
    def get_performance_stats(self, operation: str = None, days: int = 7) -> Dict[str, Any]:
        """Holt Performance-Statistiken"""
        if not self.db_service:
            return {}
            
        since = datetime.utcnow() - timedelta(days=days)
        
        try:
            with self.db_service.get_session() as session:
                query = session.query(
                    func.avg(PerformanceTrace.duration_ms).label('avg_duration'),
                    func.min(PerformanceTrace.duration_ms).label('min_duration'),
                    func.max(PerformanceTrace.duration_ms).label('max_duration'),
                    func.count(PerformanceTrace.id).label('count')
                ).filter(
                    PerformanceTrace.start_time >= since
                )
                
                if operation:
                    query = query.filter(PerformanceTrace.operation_name == operation)
                
                result = query.first()
                
                return {
                    'avg_duration_ms': round(result.avg_duration or 0, 2),
                    'min_duration_ms': round(result.min_duration or 0, 2),
                    'max_duration_ms': round(result.max_duration or 0, 2),
                    'request_count': result.count or 0
                }
        except Exception:
            return {}
    
    # ==================== Background Workers ====================
    
    def _event_worker(self):
        """Background-Worker für Event-Verarbeitung"""
        batch = []
        batch_size = 100
        flush_interval = 5  # Sekunden
        last_flush = time.time()
        
        while self._is_running:
            try:
                # Events sammeln
                try:
                    event = self._event_queue.get(timeout=1)
                    batch.append(event)
                except queue.Empty:
                    pass
                
                # Batch speichern wenn voll oder Intervall erreicht
                if len(batch) >= batch_size or (time.time() - last_flush >= flush_interval and batch):
                    self._save_events(batch)
                    batch = []
                    last_flush = time.time()
                    
            except Exception:
                pass
        
        # Restliche Events speichern
        if batch:
            self._save_events(batch)
    
    def _metric_worker(self):
        """Background-Worker für Metrik-Verarbeitung"""
        batch = []
        batch_size = 100
        flush_interval = 10
        last_flush = time.time()
        
        while self._is_running:
            try:
                try:
                    metric = self._metric_queue.get(timeout=1)
                    batch.append(metric)
                except queue.Empty:
                    pass
                
                if len(batch) >= batch_size or (time.time() - last_flush >= flush_interval and batch):
                    self._save_metrics(batch)
                    batch = []
                    last_flush = time.time()
                    
            except Exception:
                pass
        
        if batch:
            self._save_metrics(batch)
    
    def _health_worker(self):
        """Background-Worker für Health-Checks"""
        while self._is_running:
            try:
                health = self.check_system_health()
                self.record_system_health(health)
                
                # Metriken aufzeichnen
                for check_name, check_data in health.get('checks', {}).items():
                    if 'value' in check_data:
                        self.record_gauge(
                            f"system.{check_name}",
                            check_data['value'],
                            unit=check_data.get('unit', '')
                        )
                
                # Alle 60 Sekunden
                time.sleep(60)
            except Exception:
                time.sleep(60)
    
    def _save_events(self, events: List[Dict[str, Any]]):
        """Speichert Events in die Datenbank"""
        if not self.db_service or not events:
            return
            
        try:
            with self.db_service.get_session() as session:
                for event_data in events:
                    event = TelemetryEvent(
                        event_id=event_data['event_id'],
                        event_name=event_data['event_name'],
                        category=event_data['category'],
                        severity=event_data['severity'],
                        event_data=event_data['event_data'],
                        tags=event_data.get('tags', []),
                        source_module=event_data.get('source_module'),
                        correlation_id=event_data.get('correlation_id'),
                        user_id=event_data.get('user_id'),
                        tenant_id=event_data.get('tenant_id'),
                        session_id=event_data.get('session_id'),
                        event_timestamp=event_data['event_timestamp']
                    )
                    session.add(event)
                session.commit()
        except Exception:
            pass
    
    def _save_metrics(self, metrics: List[Dict[str, Any]]):
        """Speichert Metriken in die Datenbank"""
        if not self.db_service or not metrics:
            return
            
        try:
            with self.db_service.get_session() as session:
                for metric_data in metrics:
                    metric = SystemMetric(
                        metric_name=metric_data['metric_name'],
                        value=metric_data['value'],
                        metric_type=metric_data['metric_type'],
                        metric_unit=metric_data.get('metric_unit'),
                        labels=metric_data.get('labels', {}),
                        service=metric_data.get('service'),
                        host=metric_data.get('host'),
                        timestamp=metric_data['timestamp']
                    )
                    session.add(metric)
                session.commit()
        except Exception:
            pass
    
    def _flush_queues(self):
        """Leert alle Queues"""
        events = []
        metrics = []
        
        while not self._event_queue.empty():
            try:
                events.append(self._event_queue.get_nowait())
            except queue.Empty:
                break
        
        while not self._metric_queue.empty():
            try:
                metrics.append(self._metric_queue.get_nowait())
            except queue.Empty:
                break
        
        if events:
            self._save_events(events)
        if metrics:
            self._save_metrics(metrics)


class TraceContext:
    """Context Manager für Performance-Tracing"""
    
    def __init__(self, telemetry: TelemetryService, operation_name: str, operation_type: str = None):
        self.telemetry = telemetry
        self.operation_name = operation_name
        self.operation_type = operation_type
        self.start_time = None
        self.is_error = False
        self.error_message = None
        self.metadata = {}
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.is_error = True
            self.error_message = str(exc_val)
        
        self.telemetry.record_trace(
            operation_name=self.operation_name,
            duration_ms=duration_ms,
            operation_type=self.operation_type,
            is_error=self.is_error,
            error_message=self.error_message,
            metadata=self.metadata
        )
        
        return False  # Exception nicht unterdrücken
    
    def set_metadata(self, key: str, value: Any):
        """Setzt Metadata für den Trace"""
        self.metadata[key] = value
    
    def mark_error(self, message: str):
        """Markiert den Trace als fehlerhaft"""
        self.is_error = True
        self.error_message = message


def track_performance(operation_name: str = None, operation_type: str = None):
    """Decorator für automatisches Performance-Tracking"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            telemetry = TelemetryService()
            
            with telemetry.start_trace(name, operation_type):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def track_feature(feature_name: str, category: str = None):
    """Decorator für Feature-Usage-Tracking"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = TelemetryService()
            start = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                telemetry.track_feature_usage(feature_name, category, duration_ms, success)
        
        return wrapper
    return decorator


# Globale Instanz
_telemetry_instance: Optional[TelemetryService] = None


def get_telemetry() -> TelemetryService:
    """Holt die globale Telemetrie-Instanz"""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = TelemetryService()
    return _telemetry_instance


def init_telemetry(db_service) -> TelemetryService:
    """Initialisiert das Telemetrie-System"""
    global _telemetry_instance
    _telemetry_instance = TelemetryService(db_service)
    _telemetry_instance.start()
    return _telemetry_instance
