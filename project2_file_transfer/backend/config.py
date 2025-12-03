"""
Configuration file for the Secure File Transfer System
"""

import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "database", "filetransfer.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret keys
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'csv', 'json', 'xml', 'md', 'js', 'py', 'html', 'css', 'mp4', 'mp3', 'wav', 'xlsx', 'pptx'}
    
    # Encryption configuration
    RSA_KEY_SIZE = 2048
    AES_KEY_SIZE = 32  # 256 bits
    
    # CORS configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Admin configuration
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'
    
    # SFTP configuration (defaults - can be overridden per transfer)
    DEFAULT_SFTP_PORT = 22
    DEFAULT_SFTP_REMOTE_PATH = '/tmp/secure_transfers'

