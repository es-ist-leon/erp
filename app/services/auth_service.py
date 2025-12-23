"""
Authentication Service with Security Mechanisms
"""
from typing import Optional
from dataclasses import dataclass, field
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime

from shared.models import User, Role, Tenant
from shared.utils.security import (
    hash_password, verify_password, validate_password_strength,
    check_account_lockout, get_lockout_time, validate_email,
    validate_username, sanitize_string, mask_email,
    MAX_LOGIN_ATTEMPTS
)
from app.services.audit_service import get_audit_service, AuditEventType


@dataclass
class UserData:
    """Simple data class to hold user info outside of SQLAlchemy session"""
    id: uuid.UUID
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    tenant_id: Optional[uuid.UUID] = None
    tenant_name: Optional[str] = None
    company_name: Optional[str] = None
    database_name: Optional[str] = None
    roles: list = field(default_factory=list)
    
    def has_role(self, role_name: str) -> bool:
        return role_name in self.roles


class AuthService:
    """Handles user authentication with security mechanisms"""
    
    def __init__(self, db_service):
        self.db = db_service
        self.current_user: Optional[UserData] = None
        self.audit = get_audit_service()
    
    def login(self, email: str, password: str, ip_address: str = None) -> tuple[bool, str]:
        """
        Authenticate user with email and password.
        Includes rate limiting, account lockout, and audit logging.
        Returns: (success, message)
        """
        # Sanitize input
        email = sanitize_string(email.lower().strip(), 255) if email else ""
        
        session = self.db.get_auth_session()
        try:
            # Find user by email
            result = session.execute(
                select(User)
                .options(selectinload(User.roles), selectinload(User.tenant))
                .where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                self.audit.log_login_failed(email, ip_address, "User not found")
                return False, "Ungültige Anmeldedaten"  # Don't reveal if user exists
            
            # Check account lockout
            failed_attempts = int(user.failed_login_attempts or "0")
            is_locked, lock_message = check_account_lockout(failed_attempts, user.locked_until)
            
            if is_locked:
                self.audit.log_login_failed(email, ip_address, "Account locked")
                return False, lock_message
            
            if not user.is_active:
                self.audit.log_login_failed(email, ip_address, "Account disabled")
                return False, "Benutzerkonto ist deaktiviert"
            
            if user.is_deleted:
                self.audit.log_login_failed(email, ip_address, "Account deleted")
                return False, "Ungültige Anmeldedaten"
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                # Increment failed attempts
                failed_attempts += 1
                user.failed_login_attempts = str(failed_attempts)
                
                # Lock account if too many attempts
                if failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.locked_until = get_lockout_time()
                    session.commit()
                    self.audit.log_account_locked(user.id, email, ip_address)
                    self.audit.log_brute_force_attempt(email, ip_address, failed_attempts)
                    return False, f"Konto wurde nach {MAX_LOGIN_ATTEMPTS} fehlgeschlagenen Versuchen gesperrt"
                
                session.commit()
                remaining = MAX_LOGIN_ATTEMPTS - failed_attempts
                self.audit.log_login_failed(email, ip_address, "Wrong password")
                return False, f"Falsches Passwort. Noch {remaining} Versuche verbleibend."
            
            # Successful login - reset failed attempts
            user.failed_login_attempts = "0"
            user.locked_until = None
            
            # Create user database if not exists
            if not user.database_name:
                db_name = self._create_user_database(user)
                if db_name:
                    user.database_name = db_name
                    self.audit.log_database_created(user.id, email, db_name)
            
            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()
            
            # Create UserData object
            self.current_user = UserData(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                is_verified=user.is_verified,
                tenant_id=user.tenant_id,
                tenant_name=user.tenant.name if user.tenant else None,
                company_name=user.tenant.company_name if user.tenant else None,
                database_name=user.database_name,
                roles=[r.name for r in user.roles]
            )
            
            # Connect to user's personal database
            if user.database_name:
                self.db.connect_user_database(user.database_name)
                self._sync_tenant_to_master(user.tenant_id)
            
            # Log successful login
            self.audit.log_login_success(user.id, email, ip_address)
            
            return True, "Erfolgreich angemeldet"
            
        except Exception as e:
            session.rollback()
            self.audit.log_login_failed(email, ip_address, f"Error: {str(e)}")
            return False, f"Anmeldefehler: {str(e)}"
        finally:
            session.close()
    
    def _create_user_database(self, user) -> Optional[str]:
        """Create a personal database for the user"""
        import re
        
        # Generate safe database name from username
        safe_name = re.sub(r'[^a-z0-9]', '_', user.username.lower())
        db_name = f"user_{safe_name}_{str(user.id)[:8]}"
        
        try:
            success = self.db.create_user_database(db_name)
            if success:
                print(f"Created database for user {user.email}: {db_name}")
                return db_name
        except Exception as e:
            print(f"Error creating user database: {e}")
        
        return None
    
    def register(self, email: str, username: str, password: str, 
                 first_name: str = None, last_name: str = None) -> tuple[bool, str]:
        """
        Register a new user with input validation
        Returns: (success, message)
        """
        # Validate email
        email = sanitize_string(email.lower().strip(), 255) if email else ""
        valid, msg = validate_email(email)
        if not valid:
            return False, msg
        
        # Validate username
        username = sanitize_string(username.strip(), 50) if username else ""
        valid, msg = validate_username(username)
        if not valid:
            return False, msg
        
        # Validate password strength
        valid, msg = validate_password_strength(password)
        if not valid:
            return False, msg
        
        # Sanitize optional fields
        first_name = sanitize_string(first_name, 100) if first_name else None
        last_name = sanitize_string(last_name, 100) if last_name else None
        
        session = self.db.get_auth_session()
        try:
            # Check if email exists
            result = session.execute(select(User).where(User.email == email))
            if result.scalar_one_or_none():
                return False, "E-Mail-Adresse bereits registriert"
            
            # Check if username exists
            result = session.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none():
                return False, "Benutzername bereits vergeben"
            
            # Get or create default tenant
            result = session.execute(select(Tenant).where(Tenant.slug == "demo"))
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                tenant = Tenant(
                    id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                    name="Demo Holzbau GmbH",
                    slug="demo",
                    company_name="Demo Holzbau GmbH",
                    is_active=True
                )
                session.add(tenant)
                session.flush()
            
            # Create user
            user = User(
                email=email,
                username=username,
                hashed_password=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                tenant_id=tenant.id,
                is_active=True,
                is_verified=True
            )
            
            # Get default role
            result = session.execute(select(Role).where(Role.name == "employee"))
            role = result.scalar_one_or_none()
            
            if not role:
                role = Role(name="employee", display_name="Mitarbeiter", is_system=True)
                session.add(role)
                session.flush()
            
            user.roles.append(role)
            session.add(user)
            session.commit()
            
            # Log user creation
            self.audit.log_user_created(user.id, email)
            
            return True, "Registrierung erfolgreich"
            
        except Exception as e:
            session.rollback()
            return False, f"Registrierungsfehler: {str(e)}"
        finally:
            session.close()
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.audit.log(
                AuditEventType.LOGOUT,
                user_id=self.current_user.id,
                user_email=self.current_user.email
            )
        self.current_user = None
    
    def change_password(self, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change password for current user"""
        if not self.current_user:
            return False, "Nicht angemeldet"
        
        # Validate new password
        valid, msg = validate_password_strength(new_password)
        if not valid:
            return False, msg
        
        session = self.db.get_auth_session()
        try:
            user = session.get(User, self.current_user.id)
            if not user:
                return False, "Benutzer nicht gefunden"
            
            # Verify old password
            if not verify_password(old_password, user.hashed_password):
                return False, "Aktuelles Passwort ist falsch"
            
            # Update password
            user.hashed_password = hash_password(new_password)
            session.commit()
            
            self.audit.log_password_change(user.id, user.email)
            
            return True, "Passwort erfolgreich geändert"
            
        except Exception as e:
            session.rollback()
            return False, f"Fehler: {str(e)}"
        finally:
            session.close()
    
    def has_role(self, role_name: str) -> bool:
        """Check if current user has a specific role"""
        if not self.current_user:
            return False
        return self.current_user.has_role(role_name)
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        if not self.current_user:
            return False
        return self.current_user.is_superuser or self.has_role("admin")
    
    def create_initial_admin(self):
        """Create initial admin user if none exists, or update password hash if needed"""
        session = self.db.get_auth_session()
        try:
            # Check if admin user exists
            result = session.execute(select(User).where(User.email == "admin@holzbau-erp.de"))
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                # Update password hash if it's using old bcrypt format
                if not existing_admin.hashed_password.startswith('$pbkdf2$'):
                    existing_admin.hashed_password = hash_password("admin123")
                    session.commit()
                    print("Admin password hash updated to new format")
                return
            
            # Check if any user exists (but no admin)
            result = session.execute(select(User).limit(1))
            if result.scalar_one_or_none():
                return  # Other users exist, don't create admin
            
            # Create tenant
            tenant = Tenant(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                name="Demo Holzbau GmbH",
                slug="demo",
                company_name="Demo Holzbau GmbH",
                is_active=True
            )
            session.add(tenant)
            session.flush()
            
            # Create admin role
            admin_role = Role(name="admin", display_name="Administrator", is_system=True)
            session.add(admin_role)
            session.flush()
            
            # Create admin user
            admin = User(
                email="admin@holzbau-erp.de",
                username="admin",
                hashed_password=hash_password("admin123"),
                first_name="System",
                last_name="Administrator",
                tenant_id=tenant.id,
                is_active=True,
                is_superuser=True,
                is_verified=True
            )
            admin.roles.append(admin_role)
            session.add(admin)
            
            session.commit()
            print("Initial admin user created: admin@holzbau-erp.de / admin123")
            
        except Exception as e:
            session.rollback()
            print(f"Error creating admin: {e}")
        finally:
            session.close()
    
    def _sync_tenant_to_master(self, tenant_id):
        """Ensure tenant exists in user's database for FK references"""
        if not tenant_id:
            return
            
        try:
            # Get tenant from auth DB
            auth_session = self.db.get_auth_session()
            tenant = auth_session.get(Tenant, tenant_id)
            
            if tenant and self.db.user_engine:
                # Check if tenant exists in user's DB
                user_session = self.db.get_master_session()
                if user_session:
                    existing = user_session.get(Tenant, tenant_id)
                    
                    if not existing:
                        # Create tenant in user's DB
                        user_tenant = Tenant(
                            id=tenant.id,
                            name=tenant.name,
                            slug=tenant.slug,
                            company_name=tenant.company_name,
                            is_active=tenant.is_active
                        )
                        user_session.add(user_tenant)
                        user_session.commit()
                        print(f"Tenant synced to user DB: {tenant.name}")
                    
                    user_session.close()
            auth_session.close()
        except Exception as e:
            print(f"Error syncing tenant: {e}")
