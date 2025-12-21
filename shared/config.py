"""
Shared Configuration Module for HolzbauERP
"""
from functools import lru_cache
from typing import Optional
import os


class Settings:
    """Application settings loaded from credentials file"""
    
    def __init__(self):
        self.db_host: str = "localhost"
        self.db_port: int = 5432
        self.db_user: str = "postgres"
        self.db_password: str = ""
        self.db_name: str = "holzbau_erp"
        self.db_ssl_mode: str = "require"
        
        self.app_name: str = "HolzbauERP"
        self.app_version: str = "1.0.0"
        
        # Load credentials from file
        self._load_credentials()
    
    def _load_credentials(self):
        """Load database credentials from file"""
        # Look for credentials file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cred_paths = [
            os.path.join(base_dir, "dbcredentials.txt.txt"),
            os.path.join(base_dir, "dbcredentials.txt"),
            os.path.join(base_dir, ".env"),
        ]
        
        for cred_path in cred_paths:
            if os.path.exists(cred_path):
                try:
                    with open(cred_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Try to parse key: value format first
                    for line in content.split("\n"):
                        line = line.strip()
                        
                        # Parse "Key: Value" format
                        if ":" in line and not line.startswith("-"):
                            key, value = line.split(":", 1)
                            key = key.strip().lower()
                            value = value.strip()
                            
                            if key == "host":
                                self.db_host = value
                            elif key == "port":
                                self.db_port = int(value)
                            elif key == "username":
                                self.db_user = value
                            elif key == "password":
                                self.db_password = value
                            elif key == "database name":
                                self.db_name = value
                            elif key == "ssl mode":
                                self.db_ssl_mode = value
                        
                        # Also support "key = value" format
                        elif "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            key = key.strip().lower()
                            value = value.strip().strip('"').strip("'")
                            
                            if key in ("db_host", "host", "database_host"):
                                self.db_host = value
                            elif key in ("db_port", "port", "database_port"):
                                self.db_port = int(value)
                            elif key in ("db_user", "user", "username", "database_user"):
                                self.db_user = value
                            elif key in ("db_password", "password", "database_password"):
                                self.db_password = value
                            elif key in ("db_name", "database", "database_name"):
                                self.db_name = value
                            elif key in ("db_ssl_mode", "ssl_mode", "sslmode"):
                                self.db_ssl_mode = value
                    break
                except Exception as e:
                    print(f"Error loading credentials: {e}")
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
