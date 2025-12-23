"""
Security Utilities - Password hashing, JWT handling, and security mechanisms
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import jwt, JWTError
import secrets
import hashlib
import os
import re
import html

from shared.config import get_settings

settings = get_settings()

# ============== PASSWORD SECURITY ==============

# Password requirements
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGIT = True
REQUIRE_SPECIAL = True
SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

# Login security
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def _hash_pbkdf2(password: str, salt: bytes = None) -> str:
    """Hash password using PBKDF2-SHA256 with 100,000 iterations"""
    if salt is None:
        salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return f"$pbkdf2${salt.hex()}${pwd_hash.hex()}"


def _verify_pbkdf2(password: str, stored_hash: str) -> bool:
    """Verify password against PBKDF2 hash using constant-time comparison"""
    try:
        parts = stored_hash.split('$')
        if len(parts) != 4 or parts[1] != 'pbkdf2':
            return False
        salt = bytes.fromhex(parts[2])
        stored_pwd_hash = parts[3]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(pwd_hash.hex(), stored_pwd_hash)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256"""
    return _hash_pbkdf2(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return _verify_pbkdf2(plain_password, hashed_password)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    Returns: (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Passwort muss mindestens {MIN_PASSWORD_LENGTH} Zeichen lang sein"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Passwort darf maximal {MAX_PASSWORD_LENGTH} Zeichen lang sein"
    
    if REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Passwort muss mindestens einen Großbuchstaben enthalten"
    
    if REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Passwort muss mindestens einen Kleinbuchstaben enthalten"
    
    if REQUIRE_DIGIT and not re.search(r'\d', password):
        return False, "Passwort muss mindestens eine Zahl enthalten"
    
    if REQUIRE_SPECIAL and not re.search(f'[{re.escape(SPECIAL_CHARS)}]', password):
        return False, "Passwort muss mindestens ein Sonderzeichen enthalten (!@#$%^&*...)"
    
    # Check for common weak passwords
    weak_passwords = ['password', 'passwort', '12345678', 'qwertyui', 'admin123', 'letmein']
    if password.lower() in weak_passwords:
        return False, "Dieses Passwort ist zu schwach. Bitte wählen Sie ein sichereres Passwort."
    
    return True, ""


def check_account_lockout(failed_attempts: int, locked_until: Optional[datetime]) -> Tuple[bool, str]:
    """
    Check if account is locked out.
    Returns: (is_locked, message)
    """
    if locked_until and locked_until > datetime.utcnow():
        remaining = (locked_until - datetime.utcnow()).seconds // 60
        return True, f"Konto ist für {remaining + 1} Minuten gesperrt"
    
    if failed_attempts >= MAX_LOGIN_ATTEMPTS:
        return True, f"Zu viele fehlgeschlagene Anmeldeversuche. Konto temporär gesperrt."
    
    return False, ""


def get_lockout_time() -> datetime:
    """Get the datetime when lockout should expire"""
    return datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)


# ============== JWT TOKENS ==============

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
        "type": "access",
        "jti": secrets.token_urlsafe(16)  # Unique token ID
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
        "jti": secrets.token_urlsafe(32)
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


# ============== INPUT VALIDATION & SANITIZATION ==============

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input to prevent XSS and injection attacks"""
    if not value:
        return ""
    
    # Truncate to max length
    value = value[:max_length]
    
    # HTML escape to prevent XSS
    value = html.escape(value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    value = value.strip()
    
    return value


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    if not email:
        return False, "E-Mail-Adresse erforderlich"
    
    email = email.strip().lower()
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Ungültige E-Mail-Adresse"
    
    if len(email) > 255:
        return False, "E-Mail-Adresse zu lang"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format"""
    if not username:
        return False, "Benutzername erforderlich"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Benutzername muss mindestens 3 Zeichen lang sein"
    
    if len(username) > 50:
        return False, "Benutzername darf maximal 50 Zeichen lang sein"
    
    # Only alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten"
    
    return True, ""


def sanitize_sql_identifier(name: str) -> str:
    """Sanitize a string for use as SQL identifier (table/column name)"""
    # Remove all non-alphanumeric chars except underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name)
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    return sanitized[:63]  # PostgreSQL max identifier length


# ============== UTILITY FUNCTIONS ==============

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code"""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def mask_email(email: str) -> str:
    """Mask email for logging (e.g., j***@example.com)"""
    if not email or '@' not in email:
        return '***'
    local, domain = email.split('@', 1)
    if len(local) <= 1:
        return f"*@{domain}"
    return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters"""
    if not data or len(data) <= visible_chars:
        return '*' * len(data) if data else ''
    return '*' * (len(data) - visible_chars) + data[-visible_chars:]
