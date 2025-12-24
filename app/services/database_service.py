"""
Database Service - Multi-tenant database support for HolzbauERP
- Auth DB (useraccs): User accounts, roles, permissions, tenants
- User DB: Personal database per user (created on first login)
"""
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from threading import Lock
from contextlib import contextmanager
import os

from shared.config import get_settings
from shared.database import Base
from app.services.cache_service import get_cache_service


class DatabaseService:
    """Manages database connections - Auth DB and per-user databases"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
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
        
        # Auth database (useraccs) - for users, roles, permissions
        self.auth_engine = None
        self.AuthSessionLocal = None
        
        # User's personal database - set after login
        self.user_engine = None
        self.UserSessionLocal = None
        self.current_user_db_name = None
        
        # Legacy aliases (point to user db after login)
        self.engine = None
        self.SessionLocal = None
        self.master_engine = None
        self.MasterSessionLocal = None
        
        self._session = None
        self.cache = get_cache_service()
    
    def _get_ssl_args(self):
        """Get SSL configuration for database connections"""
        ca_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               "certs", "ca-certificate.crt")
        if os.path.exists(ca_path):
            return {"sslmode": "require", "sslrootcert": ca_path}
        return {"sslmode": "require"}
    
    def _create_engine(self, db_url, name="database"):
        """Create SQLAlchemy engine with SSL support and optimized settings"""
        ssl_args = self._get_ssl_args()
        
        # Optimized pool settings for better performance
        engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=10,              # Increased from 5 for better concurrency
            max_overflow=20,           # Increased from 10 for peak load handling
            pool_pre_ping=True,        # Keep connection health checks
            pool_recycle=1800,         # Recycle connections after 30 min
            pool_timeout=30,           # Reduced from 60 - fail faster
            echo=False,
            connect_args=ssl_args,
            # Performance optimizations
            execution_options={
                "compiled_cache": {},  # Enable query compilation cache
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print(f"{name} connected")
        return engine
    
    def _create_admin_engine(self):
        """Create engine for admin operations (creating databases)"""
        admin_url = f"postgresql://{self.settings.master_db.user}:{self.settings.master_db.password}@{self.settings.master_db.host}:{self.settings.master_db.port}/defaultdb"
        ssl_args = self._get_ssl_args()
        
        return create_engine(
            admin_url,
            poolclass=NullPool,
            connect_args=ssl_args,
            isolation_level="AUTOCOMMIT"
        )
    
    def connect(self, max_retries=3) -> bool:
        """Connect to auth database"""
        import time
        
        for attempt in range(max_retries):
            try:
                auth_url = self.settings.auth_db.url
                self.auth_engine = self._create_engine(auth_url, "Auth DB")
                self.AuthSessionLocal = sessionmaker(
                    bind=self.auth_engine,
                    autocommit=False,
                    autoflush=False
                )
                
                print(f"Auth database connected successfully (attempt {attempt + 1})")
                return True
                
            except Exception as e:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Database connection error after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def create_user_database(self, db_name: str) -> bool:
        """Create a new database for a user"""
        try:
            admin_engine = self._create_admin_engine()
            
            with admin_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ), {"db_name": db_name})
                
                if result.fetchone():
                    print(f"Database {db_name} already exists")
                    admin_engine.dispose()
                    return True
                
                # Create database
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"Created database: {db_name}")
            
            admin_engine.dispose()
            
            # Connect to new database and create tables
            self.connect_user_database(db_name)
            self._create_user_tables()
            
            return True
            
        except Exception as e:
            print(f"Error creating user database {db_name}: {e}")
            return False
    
    def connect_user_database(self, db_name: str) -> bool:
        """Connect to a user's personal database"""
        try:
            # Close existing user connection if any
            if self.user_engine:
                self.user_engine.dispose()
            
            # Build URL for user database
            user_url = f"postgresql://{self.settings.master_db.user}:{self.settings.master_db.password}@{self.settings.master_db.host}:{self.settings.master_db.port}/{db_name}"
            
            self.user_engine = self._create_engine(user_url, f"User DB ({db_name})")
            self.UserSessionLocal = sessionmaker(
                bind=self.user_engine,
                autocommit=False,
                autoflush=False
            )
            
            self.current_user_db_name = db_name
            
            # Set legacy aliases to user database
            self.engine = self.user_engine
            self.SessionLocal = self.UserSessionLocal
            self.master_engine = self.user_engine
            self.MasterSessionLocal = self.UserSessionLocal
            
            # Run migrations to add any missing columns
            self._run_migrations(self.user_engine)
            
            return True
            
        except Exception as e:
            print(f"Error connecting to user database {db_name}: {e}")
            return False
    
    def _create_user_tables(self):
        """Create all application tables in user's database"""
        if not self.user_engine:
            return
            
        from shared.models import (
            Tenant,
            Customer, Contact, CustomerAddress,
            Project, ProjectPhase, ProjectTask,
            Material, Supplier, Warehouse, WarehouseLocation, StockLevel,
            Employee, TimeEntry, Absence, Certification,
            Quote, QuoteItem, Order, OrderItem,
            Invoice, InvoiceItem, Payment,
            BankAccount, BankTransaction, LedgerAccount
        )
        
        # Create all tables at once - SQLAlchemy handles FK ordering
        # Exclude auth tables
        auth_tables = {'users', 'roles', 'permissions', 'refresh_tokens', 
                      'user_roles', 'role_permissions'}
        
        # Use create_all for proper FK ordering
        Base.metadata.create_all(bind=self.user_engine, checkfirst=True)
        
        self._run_migrations(self.user_engine)
        print(f"Tables created in user database: {self.current_user_db_name}")
    
    def _run_migrations(self, engine):
        """Run database migrations to add missing columns"""
        if not engine:
            return
        
        inspector = inspect(engine)
        
        migrations = [
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
            ("users", "database_name", "VARCHAR(100)"),
            # Bank account columns
            ("bank_accounts", "provider", "VARCHAR(50) DEFAULT 'manual'"),
            ("bank_accounts", "credentials_encrypted", "TEXT"),
            ("bank_accounts", "balance", "NUMERIC(15,2) DEFAULT 0"),
        ]
        
        with engine.connect() as conn:
            for table_name, column_name, column_def in migrations:
                try:
                    if table_name not in inspector.get_table_names():
                        continue
                    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                    if column_name not in existing_columns:
                        sql = text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                        conn.execute(sql)
                        conn.commit()
                        print(f"Migration: Added column {column_name} to {table_name}")
                except Exception as e:
                    print(f"Migration warning for {table_name}.{column_name}: {e}")
    
    def create_tables(self):
        """Create auth tables in auth database"""
        from shared.models import User, Role, Permission, Tenant, RefreshToken
        
        auth_tables = {'users', 'roles', 'permissions', 'tenants', 'refresh_tokens', 
                      'user_roles', 'role_permissions'}
        
        if self.auth_engine:
            for table in Base.metadata.tables.values():
                if table.name in auth_tables:
                    table.create(self.auth_engine, checkfirst=True)
            self._run_migrations(self.auth_engine)
            print("Auth tables created in useraccs database")
    
    def get_auth_session(self) -> Session:
        """Get session for auth database (users, roles, etc.)"""
        if self.AuthSessionLocal:
            return self.AuthSessionLocal()
        return None
    
    def get_master_session(self) -> Session:
        """Get session for user's database (application data)"""
        if self.UserSessionLocal:
            return self.UserSessionLocal()
        return None
    
    def get_session(self) -> Session:
        """Legacy: Get user database session"""
        return self.get_master_session()
    
    @contextmanager
    def session_scope(self):
        """Context manager for user database sessions"""
        session = self.get_master_session()
        if session is None:
            raise RuntimeError("No user database connected. Please login first.")
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @contextmanager
    def auth_session_scope(self):
        """Context manager for auth database sessions"""
        session = self.get_auth_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @property
    def session(self) -> Session:
        """Get or create a persistent user session"""
        if self._session is None or not self._session.is_active:
            self._session = self.get_master_session()
        return self._session
    
    def close_session(self):
        """Close the current session"""
        if self._session:
            self._session.close()
            self._session = None
    
    def commit(self):
        if self._session:
            self._session.commit()
    
    def rollback(self):
        if self._session:
            self._session.rollback()
    
    def invalidate_cache(self, pattern=None):
        self.cache.invalidate(pattern)
    
    def cached_query(self, cache_key: str, query_func, ttl=300):
        """Execute query with caching support"""
        result = self.cache.get(cache_key)
        if result is not None:
            return result
        result = query_func()
        self.cache.set(cache_key, result, ttl=ttl)
        return result
    
    def execute_batch(self, queries: list):
        """Execute multiple queries in a single transaction for better performance"""
        results = []
        with self.session_scope() as session:
            for query in queries:
                results.append(session.execute(query).fetchall())
        return results
