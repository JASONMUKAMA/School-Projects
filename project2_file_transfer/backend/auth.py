"""
Authentication Module
Handles user authentication and authorization
"""

import bcrypt
from typing import Optional, Tuple
from flask_jwt_extended import create_access_token, get_jwt_identity
from models import User, UserRole, db
from functools import wraps


class AuthManager:
    """Manages authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_user(username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user"""
        password_hash = AuthManager.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate user and return user object and access token
        
        Returns:
            Tuple of (User object or None, access token or None)
        """
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_active and AuthManager.verify_password(password, user.password_hash):
            access_token = create_access_token(identity=str(user.id))
            return user, access_token
        
        return None, None
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """Get current authenticated user"""
        user_id = get_jwt_identity()
        if user_id:
            # Convert to int since JWT identity is stored as string
            return User.query.get(int(user_id))
        return None
    
    @staticmethod
    def is_admin(user: User) -> bool:
        """Check if user is admin"""
        return user.role == UserRole.ADMIN


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = AuthManager.get_current_user()
        if not user or not AuthManager.is_admin(user):
            return {'error': 'Admin access required'}, 403
        return f(*args, **kwargs)
    return decorated_function

