"""
SFTP Manager
Handles secure file transfer via SFTP with encryption
"""

import os
import paramiko
import io
from typing import Optional, Tuple
from datetime import datetime


class SFTPManager:
    """Manages SFTP connections and file transfers"""
    
    def __init__(self):
        self.connections = {}  # Cache connections by server_id
    
    def create_connection(self, hostname: str, port: int, username: str, 
                         password: Optional[str] = None, 
                         key_file: Optional[str] = None,
                         key_data: Optional[bytes] = None) -> Tuple[paramiko.SSHClient, paramiko.SFTPClient]:
        """
        Create SFTP connection to remote server
        
        Args:
            hostname: SFTP server hostname or IP
            port: SFTP server port (default 22)
            username: SSH username
            password: SSH password (if using password auth)
            key_file: Path to private key file (if using key auth)
            key_data: Private key data as bytes (if using key auth)
            
        Returns:
            Tuple of (SSHClient, SFTPClient)
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Use key-based authentication if provided
            if key_data or key_file:
                if key_data:
                    # Create temporary key file from data
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem') as f:
                        f.write(key_data.decode() if isinstance(key_data, bytes) else key_data)
                        key_file = f.name
                
                # Try different key types
                try:
                    pkey = paramiko.RSAKey.from_private_key_file(key_file)
                except:
                    try:
                        pkey = paramiko.Ed25519Key.from_private_key_file(key_file)
                    except:
                        pkey = paramiko.ECDSAKey.from_private_key_file(key_file)
                
                ssh.connect(hostname, port=port, username=username, pkey=pkey, timeout=30)
            else:
                # Use password authentication
                ssh.connect(hostname, port=port, username=username, password=password, timeout=30)
            
            sftp = ssh.open_sftp()
            return ssh, sftp
            
        except Exception as e:
            ssh.close()
            raise Exception(f"Failed to connect to SFTP server: {str(e)}")
    
    def upload_file(self, file_data: bytes, remote_path: str, 
                    hostname: str, port: int, username: str,
                    password: Optional[str] = None,
                    key_file: Optional[str] = None,
                    key_data: Optional[bytes] = None) -> dict:
        """
        Upload encrypted file to SFTP server
        
        Args:
            file_data: File data (encrypted) to upload
            remote_path: Remote path on SFTP server
            hostname: SFTP server hostname
            port: SFTP server port
            username: SSH username
            password: SSH password
            key_file: Path to private key file
            key_data: Private key data as bytes
            
        Returns:
            Dict with upload status and info
        """
        ssh = None
        sftp = None
        try:
            ssh, sftp = self.create_connection(hostname, port, username, password, key_file, key_data)
            
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                try:
                    sftp.mkdir(remote_dir)
                except IOError:
                    pass  # Directory might already exist
            
            # Upload file
            with sftp.file(remote_path, 'wb') as remote_file:
                remote_file.write(file_data)
            
            # Get file info
            file_stat = sftp.stat(remote_path)
            
            return {
                'success': True,
                'remote_path': remote_path,
                'file_size': file_stat.st_size,
                'uploaded_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def download_file(self, remote_path: str,
                     hostname: str, port: int, username: str,
                     password: Optional[str] = None,
                     key_file: Optional[str] = None,
                     key_data: Optional[bytes] = None) -> Tuple[bytes, dict]:
        """
        Download encrypted file from SFTP server
        
        Args:
            remote_path: Remote path on SFTP server
            hostname: SFTP server hostname
            port: SFTP server port
            username: SSH username
            password: SSH password
            key_file: Path to private key file
            key_data: Private key data as bytes
            
        Returns:
            Tuple of (file_data, info_dict)
        """
        ssh = None
        sftp = None
        try:
            ssh, sftp = self.create_connection(hostname, port, username, password, key_file, key_data)
            
            # Check if file exists
            try:
                file_stat = sftp.stat(remote_path)
            except IOError:
                raise Exception(f"File not found on SFTP server: {remote_path}")
            
            # Download file
            file_data = b''
            with sftp.file(remote_path, 'rb') as remote_file:
                file_data = remote_file.read()
            
            info = {
                'success': True,
                'remote_path': remote_path,
                'file_size': len(file_data),
                'downloaded_at': datetime.now().isoformat()
            }
            
            return file_data, info
            
        except Exception as e:
            raise Exception(f"Failed to download file from SFTP server: {str(e)}")
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()
    
    def list_files(self, remote_path: str,
                  hostname: str, port: int, username: str,
                  password: Optional[str] = None,
                  key_file: Optional[str] = None,
                  key_data: Optional[bytes] = None) -> list:
        """
        List files in remote directory
        
        Args:
            remote_path: Remote directory path
            hostname: SFTP server hostname
            port: SFTP server port
            username: SSH username
            password: SSH password
            key_file: Path to private key file
            key_data: Private key data as bytes
            
        Returns:
            List of file info dicts
        """
        ssh = None
        sftp = None
        try:
            ssh, sftp = self.create_connection(hostname, port, username, password, key_file, key_data)
            
            files = []
            for item in sftp.listdir_attr(remote_path):
                files.append({
                    'name': item.filename,
                    'size': item.st_size,
                    'modified': datetime.fromtimestamp(item.st_mtime).isoformat(),
                    'is_directory': item.st_mode & 0o040000 != 0
                })
            
            return files
            
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

