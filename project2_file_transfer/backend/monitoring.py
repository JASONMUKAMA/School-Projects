"""
Real-time Monitoring Module
Handles real-time monitoring of file transfers and system activities
"""

from flask_socketio import SocketIO, emit
from models import FileTransfer, db
from datetime import datetime
import time


class MonitoringManager:
    """Manages real-time monitoring"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_transfers = {}
    
    def log_transfer(self, user_id: int, file_id: int, transfer_type: str,
                    bytes_transferred: int, transfer_time: float = None,
                    status: str = 'completed', ip_address: str = None):
        """
        Log a file transfer and emit real-time event
        
        Args:
            user_id: ID of user performing transfer
            file_id: ID of file being transferred
            transfer_type: 'upload' or 'download'
            bytes_transferred: Number of bytes transferred
            transfer_time: Time taken for transfer (seconds)
            status: Transfer status ('completed', 'failed')
            ip_address: IP address of client
        """
        transfer = FileTransfer(
            user_id=user_id,
            file_id=file_id,
            transfer_type=transfer_type,
            transfer_status=status,
            bytes_transferred=bytes_transferred,
            transfer_time=transfer_time,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(transfer)
        db.session.commit()
        
        # Emit real-time event
        transfer_data = transfer.to_dict()
        # Use emit without broadcast - it will send to all connected clients
        self.socketio.emit('transfer_update', transfer_data)
        
        return transfer
    
    def start_transfer_monitoring(self, transfer_id: str, user_id: int, file_id: int):
        """Start monitoring a transfer"""
        self.active_transfers[transfer_id] = {
            'user_id': user_id,
            'file_id': file_id,
            'start_time': time.time(),
            'bytes_transferred': 0
        }
    
    def update_transfer_progress(self, transfer_id: str, bytes_transferred: int):
        """Update transfer progress"""
        if transfer_id in self.active_transfers:
            self.active_transfers[transfer_id]['bytes_transferred'] = bytes_transferred
            progress_data = {
                'transfer_id': transfer_id,
                'bytes_transferred': bytes_transferred,
                'progress': self.active_transfers[transfer_id].get('progress', 0)
            }
            # Use emit without broadcast - it will send to all connected clients
            self.socketio.emit('transfer_progress', progress_data)
    
    def end_transfer_monitoring(self, transfer_id: str):
        """End monitoring a transfer"""
        if transfer_id in self.active_transfers:
            transfer_info = self.active_transfers.pop(transfer_id)
            return transfer_info
        return None

