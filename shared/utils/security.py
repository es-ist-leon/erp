"""
Security Utilities - Password hashing, JWT handling
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import secrets
import hashlib
import os

from shared.config import get_settings

settings = get_settings()

# Use native hashlib for password hashing (no bcrypt dependency issues)
def _hash_pbkdf2(password: str, salt: bytes = None) -> str:
    """Hash password using PBKDF2-SHA256"""
    if salt is None:
        salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return f"$pbkdf2${salt.hex()}${pwd_hash.hex()}"

def _verify_pbkdf2(password: str, stored_hash: str) -> bool:
    """Verify password against PBKDF2 hash"""
    try:
        parts = stored_hash.split('$')
        if len(parts) != 4 or parts[1] != 'pbkdf2':
            return False
        salt = bytes.fromhex(parts[2])
        stored_pwd_hash = parts[3]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return pwd_hash.hex() == stored_pwd_hash
    except:
        return False


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256"""
    return _hash_pbkdf2(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return _verify_pbkdf2(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token (longer lived)"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID
    })
    
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code"""
    return "".join(secrets.choice("0123456789") for _ in range(length))
