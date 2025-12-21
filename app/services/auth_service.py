"""
Authentication Service
"""
from typing import Optional
from dataclasses import dataclass, field
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime

from shared.models import User, Role, Tenant
from shared.utils.security import hash_password, verify_password


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
    roles: list = field(default_factory=list)
    
    def has_role(self, role_name: str) -> bool:
        return role_name in self.roles


class AuthService:
    """Handles user authentication"""
    
    def __init__(self, db_service):
        self.db = db_service
        self.current_user: Optional[UserData] = None
    
    def login(self, email: str, password: str) -> tuple[bool, str]:
        """
        Authenticate user with email and password
        Returns: (success, message)
        """
        session = self.db.get_session()
        try:
            # Find user by email
            result = session.execute(
                select(User)
                .options(selectinload(User.roles), selectinload(User.tenant))
                .where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False, "Benutzer nicht gefunden"
            
            if not user.is_active:
                return False, "Benutzerkonto ist deaktiviert"
            
            if user.is_deleted:
                return False, "Benutzerkonto existiert nicht"
            
            if not verify_password(password, user.hashed_password):
                return False, "Falsches Passwort"
            
            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()
            
            # Create UserData object with all needed information
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
                roles=[r.name for r in user.roles]
            )
            
            return True, "Erfolgreich angemeldet"
            
        except Exception as e:
            session.rollback()
            return False, f"Anmeldefehler: {str(e)}"
        finally:
            session.close()
    
    def register(self, email: str, username: str, password: str, 
                 first_name: str = None, last_name: str = None) -> tuple[bool, str]:
        """
        Register a new user
        Returns: (success, message)
        """
        session = self.db.get_session()
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
            
            return True, "Registrierung erfolgreich"
            
        except Exception as e:
            session.rollback()
            return False, f"Registrierungsfehler: {str(e)}"
        finally:
            session.close()
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
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
        session = self.db.get_session()
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
