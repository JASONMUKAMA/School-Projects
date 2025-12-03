"""
Database Initialization Script
Creates database tables and default admin user
"""

from app import app, db
from models import User, UserRole
from auth import AuthManager
from config import Config

def init_database():
    """Initialize database with tables and default admin"""
    with app.app_context():
        # Create all tables
        print("[*] Creating database tables...")
        db.create_all()
        print("[+] Database tables created")
        
        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(username=Config.DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            print(f"[*] Creating default admin user: {Config.DEFAULT_ADMIN_USERNAME}")
            admin = AuthManager.create_user(
                username=Config.DEFAULT_ADMIN_USERNAME,
                email='admin@example.com',
                password=Config.DEFAULT_ADMIN_PASSWORD,
                role=UserRole.ADMIN
            )
            print(f"[+] Admin user created")
            print(f"[!] Default credentials: {Config.DEFAULT_ADMIN_USERNAME} / {Config.DEFAULT_ADMIN_PASSWORD}")
            print(f"[!] Please change the password after first login!")
        else:
            print(f"[*] Admin user already exists")
        
        print("[+] Database initialization complete!")

if __name__ == '__main__':
    init_database()

