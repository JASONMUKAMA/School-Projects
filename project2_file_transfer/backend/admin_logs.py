"""
Admin Logging Module
Handles comprehensive logging of system activities
"""

from models import AdminLog, db
from datetime import datetime
from flask import request


class AdminLogger:
    """Manages admin logging operations"""
    
    @staticmethod
    def log_action(admin_id: int, action: str, target_type: str = None,
                   target_id: int = None, details: str = None):
        """
        Log an admin action
        
        Args:
            admin_id: ID of admin performing action
            action: Description of action
            target_type: Type of target (user, file, system)
            target_id: ID of target
            details: Additional details
        """
        log_entry = AdminLog(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr if request else None,
            timestamp=datetime.utcnow()
        )
        db.session.add(log_entry)
        db.session.commit()
    
    @staticmethod
    def log_user_action(admin_id: int, action: str, user_id: int, details: str = None):
        """Log action on a user"""
        AdminLogger.log_action(admin_id, action, 'user', user_id, details)
    
    @staticmethod
    def log_file_action(admin_id: int, action: str, file_id: int, details: str = None):
        """Log action on a file"""
        AdminLogger.log_action(admin_id, action, 'file', file_id, details)
    
    @staticmethod
    def log_system_action(admin_id: int, action: str, details: str = None):
        """Log system-level action"""
        AdminLogger.log_action(admin_id, action, 'system', None, details)
    
    @staticmethod
    def get_logs(limit: int = 100, admin_id: int = None, target_type: str = None):
        """Get admin logs with optional filters"""
        query = AdminLog.query
        
        if admin_id:
            query = query.filter_by(admin_id=admin_id)
        
        if target_type:
            query = query.filter_by(target_type=target_type)
        
        logs = query.order_by(AdminLog.timestamp.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]

