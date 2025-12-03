"""
Main Flask Application
Secure File Transfer and Monitoring System
"""

import os
import io
import hashlib
import base64
import struct
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import time
from cryptography.fernet import Fernet

from config import Config
from models import db, User, File, FileTransfer, AdminLog, UserRole
from auth import AuthManager, admin_required
from encryption import EncryptionManager
from integrity import IntegrityManager
from admin_logs import AdminLogger
from monitoring import MonitoringManager
from sftp_manager import SFTPManager

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure JWT config is set correctly
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES

# Initialize extensions
db.init_app(app)
CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'])

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    import traceback
    print(f"JWT Invalid Token Error: {str(error)}")
    print(f"Request headers: {dict(request.headers)}")
    traceback.print_exc()
    return jsonify({'error': f'Invalid token: {str(error)}'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is missing'}), 401

# Initialize managers
encryption_manager = EncryptionManager()
integrity_manager = IntegrityManager()
auth_manager = AuthManager()
admin_logger = AdminLogger()
monitoring_manager = MonitoringManager(socketio)
sftp_manager = SFTPManager()

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)


# ==================== Authentication Routes ====================

@app.route('/api/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        user = AuthManager.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        # Create token properly
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user, access_token = AuthManager.authenticate_user(data['username'], data['password'])
    
    if user and access_token:
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    user = AuthManager.get_current_user()
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'error': 'User not found'}), 404


# ==================== File Operations ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload and encrypt file"""
    print(f"[DEBUG] Upload request received")
    print(f"[DEBUG] Request files: {list(request.files.keys())}")
    print(f"[DEBUG] Content-Type: {request.content_type}")
    
    if 'file' not in request.files:
        print("[DEBUG] No 'file' key in request.files")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    print(f"[DEBUG] File received: {file.filename}, Content-Type: {file.content_type}")
    
    if file.filename == '' or file.filename is None:
        print("[DEBUG] Empty filename")
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        print(f"[DEBUG] File type not allowed: {file.filename}")
        return jsonify({'error': f'File type not allowed. Allowed types: {app.config["ALLOWED_EXTENSIONS"]}'}), 400
    
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Read file data
        file_data = file.read()
        file_size = len(file_data)
        
        # Calculate hash before encryption
        file_hash = integrity_manager.calculate_hash(file_data)
        
        # Generate RSA keypair for this file
        # For demo: Store private key encrypted with master secret
        # In production, use proper key management (HSM, key vault, etc.)
        private_key, public_key = encryption_manager.generate_rsa_keypair()
        
        # Encrypt file using hybrid encryption
        encrypted_data, encrypted_aes_key = encryption_manager.hybrid_encrypt_file(file_data, public_key)
        
        # Store private key encrypted with master secret (for demo only)
        # In production, use proper key encryption (e.g., encrypt with user's password-derived key)
        master_key = hashlib.sha256(app.config['SECRET_KEY'].encode()).digest()[:32]
        fernet_key = base64.urlsafe_b64encode(master_key)
        fernet = Fernet(fernet_key)
        private_key_pem = encryption_manager.serialize_private_key(private_key)
        # private_key_pem is already bytes, no need to encode
        encrypted_private_key = fernet.encrypt(private_key_pem).decode()
        
        # Save encrypted file
        secure_name = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        encrypted_filename = f"{timestamp}_{secure_name}.enc"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
        
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Store file metadata in database
        file_record = File(
            filename=encrypted_filename,
            original_filename=secure_name,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            encrypted_key=encrypted_aes_key,
            encrypted_private_key=encrypted_private_key,  # Store encrypted private key for decryption
            user_id=user.id,
            mime_type=file.content_type
        )
        db.session.add(file_record)
        db.session.commit()
        
        # Log transfer
        start_time = time.time()
        transfer_time = time.time() - start_time
        monitoring_manager.log_transfer(
            user_id=user.id,
            file_id=file_record.id,
            transfer_type='upload',
            bytes_transferred=file_size,
            transfer_time=transfer_time,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': file_record.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
@jwt_required()
def list_files():
    """List user's files"""
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    files = File.query.filter_by(user_id=user.id).order_by(File.uploaded_at.desc()).all()
    return jsonify([f.to_dict() for f in files]), 200


@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Download and decrypt file"""
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    file_record = File.query.get(file_id)
    if not file_record:
        print(f"[DEBUG] Download: File ID {file_id} not found in database")
        return jsonify({'error': 'File not found in database'}), 404
    
    # Check ownership (or admin)
    if file_record.user_id != user.id and not AuthManager.is_admin(user):
        print(f"[DEBUG] Download: Access denied for user {user.id} to file {file_id}")
        return jsonify({'error': 'Access denied'}), 403
    
    print(f"[DEBUG] Download: File ID {file_id}, Path: {file_record.file_path}, Exists: {os.path.exists(file_record.file_path)}")
    
    try:
        # Read encrypted file
        file_path = file_record.file_path
        if not os.path.exists(file_path):
            print(f"[WARNING] Download: Stored path does not exist: {file_path}")
            # Try to find file by original filename in upload directory
            upload_dir = app.config.get('UPLOAD_FOLDER', '/app/uploads')
            if os.path.exists(upload_dir):
                # Look for files matching the original filename pattern
                import glob
                import re
                # Escape special characters in filename for glob pattern
                safe_filename = re.escape(file_record.original_filename)
                pattern = os.path.join(upload_dir, f"*{safe_filename}*")
                print(f"[DEBUG] Download: Searching for file with pattern: {pattern}")
                matching_files = glob.glob(pattern)
                print(f"[DEBUG] Download: Found {len(matching_files)} matching files: {matching_files}")
                if matching_files:
                    file_path = matching_files[0]
                    print(f"[INFO] Download: Found file at alternative path: {file_path}")
                    print(f"[WARNING] Download: File path mismatch! Database has: {file_record.file_path}, but using: {file_path}")
                    print(f"[WARNING] Download: This file may have been re-uploaded. Decryption may fail if keys don't match.")
                else:
                    # Try a simpler pattern without escaping (in case filename has no special chars)
                    simple_pattern = os.path.join(upload_dir, f"*{file_record.original_filename}*")
                    matching_files = glob.glob(simple_pattern)
                    print(f"[DEBUG] Download: Simple pattern search found {len(matching_files)} files: {matching_files}")
                    if matching_files:
                        file_path = matching_files[0]
                        print(f"[INFO] Download: Found file at alternative path: {file_path}")
                    else:
                        print(f"[ERROR] Download: File not found at stored path or by pattern search")
                        return jsonify({
                            'error': 'File not found on server. The file may have been deleted or the server was restarted. Please re-upload the file.',
                            'file_id': file_id
                        }), 404
            else:
                return jsonify({
                    'error': 'File not found on server. The file may have been deleted or the server was restarted. Please re-upload the file.',
                    'file_id': file_id
                }), 404
        
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        print(f"[DEBUG] Download: Read {len(encrypted_data)} bytes from file")
        
        # Decrypt the stored private key
        if not file_record.encrypted_private_key:
            print(f"[ERROR] Download: No encrypted_private_key stored for file ID {file_id}")
            return jsonify({'error': 'Private key not found. File may have been uploaded with an older version. Please re-upload the file.'}), 500
        
        try:
            # Decrypt private key using master secret
            master_key = hashlib.sha256(app.config['SECRET_KEY'].encode()).digest()[:32]
            fernet_key = base64.urlsafe_b64encode(master_key)
            fernet = Fernet(fernet_key)
            private_key_pem = fernet.decrypt(file_record.encrypted_private_key.encode())
            private_key = encryption_manager.deserialize_private_key(private_key_pem)
            print(f"[DEBUG] Download: Successfully decrypted and loaded private key")
        except Exception as key_error:
            print(f"[ERROR] Failed to decrypt private key: {key_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to decrypt private key: {str(key_error)}. The file may have been encrypted with different keys. Please re-upload the file.'}), 500
        
        # Decrypt file
        try:
            print(f"[DEBUG] Download: Attempting to decrypt file with stored encrypted_key")
            decrypted_data = encryption_manager.hybrid_decrypt_file(
                encrypted_data,
                file_record.encrypted_key,
                private_key
            )
            print(f"[DEBUG] Download: Successfully decrypted {len(decrypted_data)} bytes")
        except Exception as decrypt_error:
            print(f"[ERROR] Decryption failed: {decrypt_error}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'File decryption failed: {str(decrypt_error)}. The file on disk may have been encrypted with different keys than stored in database. Please re-upload the file.'}), 500
        
        # Verify integrity
        is_valid, actual_hash = integrity_manager.verify_integrity(decrypted_data, file_record.file_hash)
        
        if not is_valid:
            print(f"[ERROR] Integrity check failed. Expected: {file_record.file_hash}, Got: {actual_hash}")
            return jsonify({'error': 'File integrity check failed'}), 500
        
        # Log transfer
        start_time = time.time()
        transfer_time = time.time() - start_time
        monitoring_manager.log_transfer(
            user_id=user.id,
            file_id=file_record.id,
            transfer_type='download',
            bytes_transferred=len(decrypted_data),
            transfer_time=transfer_time,
            ip_address=request.remote_addr
        )
        
        # Return file
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype=file_record.mime_type,
            as_attachment=True,
            download_name=file_record.original_filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete file"""
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    file_record = File.query.get_or_404(file_id)
    
    # Check ownership (or admin)
    if file_record.user_id != user.id and not AuthManager.is_admin(user):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Store filename for logging before deletion
        original_filename = file_record.original_filename
        
        # Delete related FileTransfer records first (to avoid foreign key constraint issues)
        FileTransfer.query.filter_by(file_id=file_id).delete()
        
        # Delete file from filesystem
        if os.path.exists(file_record.file_path):
            try:
                os.remove(file_record.file_path)
            except OSError as e:
                print(f"[WARNING] Could not delete file from filesystem: {e}")
                # Continue with database deletion even if file doesn't exist
        
        # Delete from database
        db.session.delete(file_record)
        db.session.commit()
        
        # Log admin action if admin
        if AuthManager.is_admin(user):
            AdminLogger.log_file_action(user.id, 'delete_file', file_id, f'Deleted file: {original_filename}')
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Delete failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500


# ==================== Admin Routes ====================

@app.route('/api/admin/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_logs():
    """Get admin logs"""
    limit = request.args.get('limit', 100, type=int)
    admin_id = request.args.get('admin_id', type=int)
    target_type = request.args.get('target_type')
    
    logs = AdminLogger.get_logs(limit=limit, admin_id=admin_id, target_type=target_type)
    return jsonify(logs), 200


@app.route('/api/admin/transfers', methods=['GET'])
@jwt_required()
@admin_required
def get_all_transfers():
    """Get all file transfers"""
    transfers = FileTransfer.query.order_by(FileTransfer.timestamp.desc()).limit(100).all()
    return jsonify([t.to_dict() for t in transfers]), 200


@app.route('/api/encrypt', methods=['POST'])
@jwt_required()
def encrypt_file_standalone():
    """Encrypt a file without storing it (standalone encryption)"""
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read file data
        file_data = file.read()
        
        # Generate RSA keypair
        private_key, public_key = encryption_manager.generate_rsa_keypair()
        
        # Encrypt file using hybrid encryption
        encrypted_data, encrypted_aes_key = encryption_manager.hybrid_encrypt_file(file_data, public_key)
        
        # Store private key encrypted with master secret
        master_key = hashlib.sha256(app.config['SECRET_KEY'].encode()).digest()[:32]
        fernet_key = base64.urlsafe_b64encode(master_key)
        fernet = Fernet(fernet_key)
        private_key_pem = encryption_manager.serialize_private_key(private_key)
        encrypted_private_key = fernet.encrypt(private_key_pem).decode()
        
        # Combine encrypted data with metadata (encrypted_key + encrypted_private_key)
        # Format: [4 bytes: encrypted_key_length][encrypted_key][4 bytes: private_key_length][encrypted_private_key][encrypted_file_data]
        encrypted_key_bytes = encrypted_aes_key.encode('utf-8')
        encrypted_private_key_bytes = encrypted_private_key.encode('utf-8')
        
        metadata = struct.pack('>I', len(encrypted_key_bytes))
        metadata += encrypted_key_bytes
        metadata += struct.pack('>I', len(encrypted_private_key_bytes))
        metadata += encrypted_private_key_bytes
        
        final_data = metadata + encrypted_data
        
        # Return encrypted file
        return send_file(
            io.BytesIO(final_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=secure_filename(file.filename) + '.enc'
        )
        
    except Exception as e:
        print(f"[ERROR] Encryption failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Encryption failed: {str(e)}'}), 500


@app.route('/api/decrypt', methods=['POST'])
@jwt_required()
def decrypt_file_standalone():
    """Decrypt a file (standalone decryption)"""
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read encrypted file
        encrypted_file_data = file.read()
        
        # Extract metadata and encrypted data
        if len(encrypted_file_data) < 8:
            return jsonify({'error': 'Invalid encrypted file format'}), 400
        
        # Read encrypted_key length and data
        encrypted_key_length = struct.unpack('>I', encrypted_file_data[0:4])[0]
        encrypted_key = encrypted_file_data[4:4+encrypted_key_length].decode('utf-8')
        
        # Read encrypted_private_key length and data
        private_key_start = 4 + encrypted_key_length
        private_key_length = struct.unpack('>I', encrypted_file_data[private_key_start:private_key_start+4])[0]
        encrypted_private_key = encrypted_file_data[private_key_start+4:private_key_start+4+private_key_length].decode('utf-8')
        
        # Encrypted file data starts after metadata
        encrypted_data = encrypted_file_data[private_key_start+4+private_key_length:]
        
        # Decrypt private key
        master_key = hashlib.sha256(app.config['SECRET_KEY'].encode()).digest()[:32]
        fernet_key = base64.urlsafe_b64encode(master_key)
        fernet = Fernet(fernet_key)
        private_key_pem = fernet.decrypt(encrypted_private_key.encode())
        private_key = encryption_manager.deserialize_private_key(private_key_pem)
        
        # Decrypt file
        decrypted_data = encryption_manager.hybrid_decrypt_file(
            encrypted_data,
            encrypted_key,
            private_key
        )
        
        # Determine original filename
        original_filename = file.filename.replace('.enc', '')
        
        # Return decrypted file
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=original_filename
        )
        
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Decryption failed: {str(e)}'}), 500


@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


# ==================== SFTP Transfer Routes ====================

@app.route('/api/sftp/upload', methods=['POST'])
@jwt_required()
def sftp_upload_file():
    """
    Encrypt file and upload to SFTP server (Server A -> Server B)
    Workflow: Upload file -> Encrypt -> Transfer via SFTP -> Store on remote server
    """
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Get file and SFTP configuration from request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get SFTP configuration
        sftp_host = request.form.get('sftp_host')
        sftp_port = int(request.form.get('sftp_port', 22))
        sftp_username = request.form.get('sftp_username')
        sftp_password = request.form.get('sftp_password', '')
        sftp_remote_path = request.form.get('sftp_remote_path', f'/tmp/secure_transfers/{secure_filename(file.filename)}.enc')
        sftp_key_data = request.form.get('sftp_key_data', '')  # Optional SSH key
        
        if not sftp_host or not sftp_username:
            return jsonify({'error': 'SFTP host and username are required'}), 400
        
        # Read file data
        file_data = file.read()
        
        # Encrypt file using hybrid encryption
        private_key, public_key = encryption_manager.generate_rsa_keypair()
        encrypted_data, encrypted_aes_key = encryption_manager.hybrid_encrypt_file(file_data, public_key)
        
        # Store private key encrypted with master secret (for later decryption)
        master_key = hashlib.sha256(app.config['SECRET_KEY'].encode()).digest()[:32]
        fernet_key = base64.urlsafe_b64encode(master_key)
        fernet = Fernet(fernet_key)
        private_key_pem = encryption_manager.serialize_private_key(private_key)
        encrypted_private_key = fernet.encrypt(private_key_pem).decode()
        
        # Combine encrypted data with metadata (same format as standalone encryption)
        encrypted_key_bytes = encrypted_aes_key.encode('utf-8')
        encrypted_private_key_bytes = encrypted_private_key.encode('utf-8')
        
        metadata = struct.pack('>I', len(encrypted_key_bytes))
        metadata += encrypted_key_bytes
        metadata += struct.pack('>I', len(encrypted_private_key_bytes))
        metadata += encrypted_private_key_bytes
        
        final_encrypted_data = metadata + encrypted_data
        
        # Upload to SFTP server
        key_data_bytes = sftp_key_data.encode() if sftp_key_data else None
        upload_result = sftp_manager.upload_file(
            file_data=final_encrypted_data,
            remote_path=sftp_remote_path,
            hostname=sftp_host,
            port=sftp_port,
            username=sftp_username,
            password=sftp_password if sftp_password else None,
            key_data=key_data_bytes
        )
        
        if not upload_result['success']:
            return jsonify({'error': f"SFTP upload failed: {upload_result.get('error', 'Unknown error')}"}), 500
        
        # Log transfer
        monitoring_manager.log_transfer(
            user_id=user.id,
            file_id=None,  # Not stored in local DB
            transfer_type='sftp_upload',
            bytes_transferred=len(final_encrypted_data),
            transfer_time=0,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'message': 'File encrypted and uploaded to SFTP server successfully',
            'remote_path': upload_result['remote_path'],
            'file_size': upload_result['file_size'],
            'encrypted_key': encrypted_aes_key,  # Return for decryption later
            'encrypted_private_key': encrypted_private_key  # Return for decryption later
        }), 200
        
    except Exception as e:
        print(f"[ERROR] SFTP upload failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'SFTP upload failed: {str(e)}'}), 500


@app.route('/api/sftp/download', methods=['POST'])
@jwt_required()
def sftp_download_file():
    """
    Download encrypted file from SFTP server and decrypt (Server B -> Server A)
    Workflow: Download from SFTP -> Decrypt -> Return decrypted file
    """
    user = AuthManager.get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        data = request.get_json()
        
        # Get SFTP configuration
        sftp_host = data.get('sftp_host')
        sftp_port = int(data.get('sftp_port', 22))
        sftp_username = data.get('sftp_username')
        sftp_password = data.get('sftp_password', '')
        sftp_remote_path = data.get('sftp_remote_path')
        sftp_key_data = data.get('sftp_key_data', '')
        
        # Get decryption keys (from previous upload or provided)
        encrypted_aes_key = data.get('encrypted_key')
        encrypted_private_key = data.get('encrypted_private_key')
        
        if not sftp_host or not sftp_username or not sftp_remote_path:
            return jsonify({'error': 'SFTP host, username, and remote path are required'}), 400
        
        if not encrypted_aes_key or not encrypted_private_key:
            return jsonify({'error': 'Decryption keys are required'}), 400
        
        # Download encrypted file from SFTP server
        key_data_bytes = sftp_key_data.encode() if sftp_key_data else None
        encrypted_file_data, download_info = sftp_manager.download_file(
            remote_path=sftp_remote_path,
            hostname=sftp_host,
            port=sftp_port,
            username=sftp_username,
            password=sftp_password if sftp_password else None,
            key_data=key_data_bytes
        )
        
        # Extract metadata and encrypted data
        if len(encrypted_file_data) < 8:
            return jsonify({'error': 'Invalid encrypted file format'}), 400
        
        # Read encrypted_key length and data
        encrypted_key_length = struct.unpack('>I', encrypted_file_data[0:4])[0]
        stored_encrypted_key = encrypted_file_data[4:4+encrypted_key_length].decode('utf-8')
        
        # Read encrypted_private_key length and data
        private_key_start = 4 + encrypted_key_length
        private_key_length = struct.unpack('>I', encrypted_file_data[private_key_start:private_key_start+4])[0]
        stored_encrypted_private_key = encrypted_file_data[private_key_start+4:private_key_start+4+private_key_length].decode('utf-8')
        
        # Encrypted file data starts after metadata
        encrypted_data = encrypted_file_data[private_key_start+4+private_key_length:]
        
        # Use provided keys or stored keys (prefer provided for flexibility)
        key_to_use = encrypted_aes_key if encrypted_aes_key else stored_encrypted_key
        private_key_to_use = encrypted_private_key if encrypted_private_key else stored_encrypted_private_key
        
        # Decrypt private key
        master_key = hashlib.sha256(app.config['SECRET_KEY'].encode()).digest()[:32]
        fernet_key = base64.urlsafe_b64encode(master_key)
        fernet = Fernet(fernet_key)
        private_key_pem = fernet.decrypt(private_key_to_use.encode())
        private_key = encryption_manager.deserialize_private_key(private_key_pem)
        
        # Decrypt file
        decrypted_data = encryption_manager.hybrid_decrypt_file(
            encrypted_data,
            key_to_use,
            private_key
        )
        
        # Determine original filename
        original_filename = os.path.basename(sftp_remote_path).replace('.enc', '')
        
        # Log transfer
        monitoring_manager.log_transfer(
            user_id=user.id,
            file_id=None,
            transfer_type='sftp_download',
            bytes_transferred=len(decrypted_data),
            transfer_time=0,
            ip_address=request.remote_addr
        )
        
        # Return decrypted file
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=original_filename
        )
        
    except Exception as e:
        print(f"[ERROR] SFTP download/decrypt failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'SFTP download/decrypt failed: {str(e)}'}), 500


# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to monitoring server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    pass


# ==================== Main ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Run on all interfaces for Docker compatibility
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

