"""
Database Service - Optimized SQLAlchemy connection with caching
"""
from sqlalchemy import create_engine, text, inspect, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from functools import lru_cache
from threading import Lock
import ssl
import os

from shared.config import get_settings
from shared.database import Base


class QueryCache:
    """Simple in-memory cache for frequently accessed data"""
    
    def __init__(self, max_size=1000, ttl_seconds=300):
        self._cache = {}
        self._timestamps = {}
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._lock = Lock()
    
    def get(self, key):
        with self._lock:
            if key in self._cache:
                import time
                if time.time() - self._timestamps[key] < self._ttl:
                    return self._cache[key]
                else:
                    del self._cache[key]
                    del self._timestamps[key]
        return None
    
    def set(self, key, value):
        with self._lock:
            import time
            if len(self._cache) >= self._max_size:
                # Remove oldest entries
                oldest = sorted(self._timestamps.items(), key=lambda x: x[1])[:100]
                for k, _ in oldest:
                    del self._cache[k]
                    del self._timestamps[k]
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def invalidate(self, pattern=None):
        with self._lock:
            if pattern:
                keys_to_remove = [k for k in self._cache if pattern in str(k)]
                for k in keys_to_remove:
                    del self._cache[k]
                    del self._timestamps[k]
            else:
                self._cache.clear()
                self._timestamps.clear()


class DatabaseService:
    """Manages database connections and sessions with performance optimizations"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        # Singleton pattern for connection reuse
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._scoped_session = None
        self._session = None
        self.cache = QueryCache()
    
    def connect(self, max_retries=3) -> bool:
        """Establish optimized database connection with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                # Build connection URL
                url = f"postgresql://{self.settings.db_user}:{self.settings.db_password}@{self.settings.db_host}:{self.settings.db_port}/{self.settings.db_name}"
                
                # SSL configuration - try multiple modes
                ssl_args = {}
                ca_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       "certs", "ca-certificate.crt")
                
                # Use SSL require mode
                if os.path.exists(ca_path):
                    ssl_args = {"sslmode": "require", "sslrootcert": ca_path}
                else:
                    ssl_args = {"sslmode": "require"}
                
                # Optimized engine with better pooling
                self.engine = create_engine(
                    url,
                    poolclass=QueuePool,
                    pool_size=5,               # Reduced for stability
                    max_overflow=10,           # Reduced overflow
                    pool_pre_ping=True,        # Check connection health
                    pool_recycle=1800,         # Recycle connections after 30 min
                    pool_timeout=60,           # Longer connection timeout
                    echo=False,                # Disable SQL logging for performance
                    connect_args=ssl_args
                )
                
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self.SessionLocal = sessionmaker(
                    bind=self.engine,
                    autocommit=False,
                    autoflush=False
                )
                
                print(f"Database connected successfully (attempt {attempt + 1})")
                return True
                
            except Exception as e:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Database connection error after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def _run_migrations(self):
        """Run database migrations to add missing columns"""
        if not self.engine:
            return
        
        inspector = inspect(self.engine)
        
        # Define migrations: (table_name, column_name, column_definition)
        migrations = [
            # Tenants table
            ("tenants", "bank_name", "VARCHAR(255)"),
            ("tenants", "iban", "VARCHAR(50)"),
            ("tenants", "bic", "VARCHAR(20)"),
            ("tenants", "logo_url", "VARCHAR(500)"),
            ("tenants", "primary_color", "VARCHAR(7) DEFAULT '#2563eb'"),
            ("tenants", "subscription_plan", "VARCHAR(50) DEFAULT 'starter'"),
            ("tenants", "subscription_expires", "TIMESTAMP"),
            ("tenants", "max_users", "VARCHAR(10) DEFAULT '5'"),
            ("tenants", "trade_register", "VARCHAR(100)"),
            ("tenants", "website", "VARCHAR(255)"),
            ("tenants", "street", "VARCHAR(255)"),
            ("tenants", "street_number", "VARCHAR(20)"),
            ("tenants", "postal_code", "VARCHAR(20)"),
            ("tenants", "city", "VARCHAR(100)"),
            ("tenants", "country", "VARCHAR(100) DEFAULT 'Deutschland'"),
        ]
        
        with self.engine.connect() as conn:
            for table_name, column_name, column_def in migrations:
                try:
                    # Check if table exists
                    if table_name not in inspector.get_table_names():
                        continue
                    
                    # Check if column exists
                    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                    if column_name not in existing_columns:
                        sql = text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                        conn.execute(sql)
                        conn.commit()
                        print(f"Migration: Added column {column_name} to {table_name}")
                except Exception as e:
                    print(f"Migration warning for {table_name}.{column_name}: {e}")
    
    def create_tables(self):
        """Create all database tables"""
        if self.engine:
            # Import all models to register them
            from shared.models import (
                User, Role, Permission, Tenant, RefreshToken,
                Customer, Contact, CustomerAddress,
                Project, ProjectPhase, ProjectTask,
                Material, Supplier, Warehouse, WarehouseLocation, StockLevel,
                Employee, TimeEntry, Absence, Certification,
                Quote, QuoteItem, Order, OrderItem,
                Invoice, InvoiceItem, Payment
            )
            Base.metadata.create_all(bind=self.engine)
            
            # Run migrations to add any missing columns
            self._run_migrations()
    
    def get_session(self) -> Session:
        """Get a new database session with optimized settings"""
        if self.SessionLocal:
            session = self.SessionLocal()
            return session
        return None
    
    @property
    def session(self) -> Session:
        """Get or create a persistent session"""
        if self._session is None or not self._session.is_active:
            self._session = self.get_session()
        return self._session
    
    def close_session(self):
        """Close the current session"""
        if self._session:
            self._session.close()
            self._session = None
    
    def commit(self):
        """Commit current session"""
        if self._session:
            self._session.commit()
    
    def rollback(self):
        """Rollback current session"""
        if self._session:
            self._session.rollback()
    
    def invalidate_cache(self, pattern=None):
        """Invalidate query cache"""
        self.cache.invalidate(pattern)
    
    def cached_query(self, cache_key: str, query_func, ttl=300):
        """Execute query with caching"""
        result = self.cache.get(cache_key)
        if result is not None:
            return result
        result = query_func()
        self.cache.set(cache_key, result)
        return result
