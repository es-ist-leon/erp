"""
Shared Configuration Module for HolzbauERP
Supports two databases:
- useraccs: User accounts and authentication only
- master: All application data (projects, customers, inventory, etc.)
"""
from functools import lru_cache
from typing import Optional
import os


class DatabaseConfig:
    """Configuration for a single database connection"""
    def __init__(self):
        self.host: str = "localhost"
        self.port: int = 5432
        self.user: str = "postgres"
        self.password: str = ""
        self.name: str = "postgres"
        self.ssl_mode: str = "require"
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings:
    """Application settings with dual database support"""
    
    def __init__(self):
        # User accounts database (useraccs)
        self.auth_db = DatabaseConfig()
        
        # Master database for application data
        self.master_db = DatabaseConfig()
        
        # Legacy aliases (point to auth_db for backward compatibility)
        self.db_host: str = ""
        self.db_port: int = 5432
        self.db_user: str = ""
        self.db_password: str = ""
        self.db_name: str = ""
        self.db_ssl_mode: str = "require"
        
        self.app_name: str = "HolzbauERP"
        self.app_version: str = "1.0.0"
        
        # JWT settings
        self.jwt_secret: str = "holzbau-erp-secret-key-change-in-production"
        self.jwt_algorithm: str = "HS256"
        self.jwt_expiration_hours: int = 24
        
        # Load credentials from files
        self._load_credentials()
    
    def _parse_credentials_file(self, filepath: str) -> DatabaseConfig:
        """Parse a credentials file and return DatabaseConfig"""
        config = DatabaseConfig()
        
        if not os.path.exists(filepath):
            return config
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            for line in content.split("\n"):
                line = line.strip()
                
                # Parse "Key: Value" format
                if ":" in line and not line.startswith("-") and not line.startswith("Connection"):
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == "host":
                        config.host = value
                    elif key == "port":
                        config.port = int(value)
                    elif key == "username":
                        config.user = value
                    elif key == "password":
                        config.password = value
                    elif key == "database name":
                        config.name = value
                    elif key == "ssl mode":
                        config.ssl_mode = value.lower()
        except Exception as e:
            print(f"Error loading credentials from {filepath}: {e}")
        
        return config
    
    def _load_credentials(self):
        """Load database credentials from files"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load auth database (useraccs) from dbcredentials.txt.txt
        auth_paths = [
            os.path.join(base_dir, "dbcredentials.txt.txt"),
            os.path.join(base_dir, "dbcredentials.txt"),
        ]
        for path in auth_paths:
            if os.path.exists(path):
                self.auth_db = self._parse_credentials_file(path)
                break
        
        # Load master database from dbcredentials-master.txt
        master_path = os.path.join(base_dir, "dbcredentials-master.txt")
        if os.path.exists(master_path):
            self.master_db = self._parse_credentials_file(master_path)
        else:
            # Fallback to auth_db if master not found
            self.master_db = self.auth_db
        
        # Set legacy aliases to auth_db for backward compatibility
        self.db_host = self.auth_db.host
        self.db_port = self.auth_db.port
        self.db_user = self.auth_db.user
        self.db_password = self.auth_db.password
        self.db_name = self.auth_db.name
        self.db_ssl_mode = self.auth_db.ssl_mode
    
    @property
    def database_url(self) -> str:
        """Legacy: returns auth database URL"""
        return self.auth_db.url
    
    @property
    def auth_database_url(self) -> str:
        """URL for user accounts database"""
        return self.auth_db.url
    
    @property
    def master_database_url(self) -> str:
        """URL for master application database"""
        return self.master_db.url


@lru_cache()
def get_settings() -> Settings:
    return Settings()
