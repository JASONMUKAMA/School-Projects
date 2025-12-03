"""
Database models for the Secure File Transfer System
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    files = db.relationship('File', backref='owner', lazy=True, cascade='all, delete-orphan')
    transfers = db.relationship('FileTransfer', backref='user', lazy=True)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class File(db.Model):
    """File model"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash
    encrypted_key = db.Column(db.Text, nullable=False)  # RSA encrypted AES key
    encrypted_private_key = db.Column(db.Text)  # Encrypted RSA private key (for demo - store encrypted with master key)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    mime_type = db.Column(db.String(100))
    
    def to_dict(self):
        """Convert file to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'uploaded_at': self.uploaded_at.isoformat(),
            'mime_type': self.mime_type
        }


class FileTransfer(db.Model):
    """File transfer log model"""
    __tablename__ = 'file_transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    transfer_type = db.Column(db.String(20), nullable=False)  # 'upload' or 'download'
    transfer_status = db.Column(db.String(20), default='completed')  # 'completed', 'failed'
    bytes_transferred = db.Column(db.Integer, nullable=False)
    transfer_time = db.Column(db.Float)  # Time in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    
    # Relationship
    file = db.relationship('File', backref='transfers', lazy=True)
    
    def to_dict(self):
        """Convert transfer to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'transfer_type': self.transfer_type,
            'transfer_status': self.transfer_status,
            'bytes_transferred': self.bytes_transferred,
            'transfer_time': self.transfer_time,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'filename': self.file.original_filename if self.file else None
        }


class AdminLog(db.Model):
    """Admin log model"""
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))  # 'user', 'file', 'system'
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    admin = db.relationship('User', foreign_keys=[admin_id], lazy=True)
    
    def to_dict(self):
        """Convert log to dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_username': self.admin.username if self.admin else None,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }

