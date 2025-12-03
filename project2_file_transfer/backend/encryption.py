"""
Encryption Module
Handles AES and RSA encryption for secure file transfer
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os
import base64


class EncryptionManager:
    """Manages encryption operations using AES and RSA"""
    
    def __init__(self):
        self.backend = default_backend()
        self.rsa_key_size = 2048
    
    def generate_rsa_keypair(self):
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.rsa_key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def serialize_public_key(self, public_key):
        """Serialize RSA public key to PEM format"""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def deserialize_public_key(self, pem_data):
        """Deserialize RSA public key from PEM format"""
        return serialization.load_pem_public_key(pem_data, backend=self.backend)
    
    def serialize_private_key(self, private_key, password=None):
        """Serialize RSA private key to PEM format"""
        encryption = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
    
    def deserialize_private_key(self, pem_data, password=None):
        """Deserialize RSA private key from PEM format"""
        return serialization.load_pem_private_key(
            pem_data,
            password=password.encode() if password else None,
            backend=self.backend
        )
    
    def generate_aes_key(self):
        """Generate random AES-256 key"""
        return os.urandom(32)  # 256 bits
    
    def encrypt_file_aes(self, file_data, aes_key):
        """
        Encrypt file data using AES-256-CBC
        
        Args:
            file_data: Bytes of file to encrypt
            aes_key: AES key (32 bytes)
            
        Returns:
            Encrypted data (IV + encrypted data)
        """
        # Generate random IV
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Pad the data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(file_data)
        padded_data += padder.finalize()
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + encrypted data
        return iv + encrypted_data
    
    def decrypt_file_aes(self, encrypted_data, aes_key):
        """
        Decrypt file data using AES-256-CBC
        
        Args:
            encrypted_data: IV + encrypted data
            aes_key: AES key (32 bytes)
            
        Returns:
            Decrypted file data
        """
        # Extract IV and encrypted data
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        
        return data
    
    def encrypt_aes_key_rsa(self, aes_key, public_key):
        """
        Encrypt AES key using RSA public key
        
        Args:
            aes_key: AES key to encrypt
            public_key: RSA public key
            
        Returns:
            Base64 encoded encrypted key
        """
        encrypted_key = public_key.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_key).decode('utf-8')
    
    def decrypt_aes_key_rsa(self, encrypted_key_b64, private_key):
        """
        Decrypt AES key using RSA private key
        
        Args:
            encrypted_key_b64: Base64 encoded encrypted key
            private_key: RSA private key
            
        Returns:
            Decrypted AES key
        """
        encrypted_key = base64.b64decode(encrypted_key_b64)
        aes_key = private_key.decrypt(
            encrypted_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return aes_key
    
    def hybrid_encrypt_file(self, file_data, public_key):
        """
        Hybrid encryption: Generate AES key, encrypt file with AES,
        encrypt AES key with RSA
        
        Args:
            file_data: File data to encrypt
            public_key: RSA public key for key encryption
            
        Returns:
            Tuple of (encrypted_file_data, encrypted_aes_key_b64)
        """
        # Generate AES key
        aes_key = self.generate_aes_key()
        
        # Encrypt file with AES
        encrypted_file = self.encrypt_file_aes(file_data, aes_key)
        
        # Encrypt AES key with RSA
        encrypted_aes_key = self.encrypt_aes_key_rsa(aes_key, public_key)
        
        return encrypted_file, encrypted_aes_key
    
    def hybrid_decrypt_file(self, encrypted_file_data, encrypted_aes_key_b64, private_key):
        """
        Hybrid decryption: Decrypt AES key with RSA, decrypt file with AES
        
        Args:
            encrypted_file_data: Encrypted file data
            encrypted_aes_key_b64: Base64 encoded encrypted AES key
            private_key: RSA private key for key decryption
            
        Returns:
            Decrypted file data
        """
        # Decrypt AES key with RSA
        aes_key = self.decrypt_aes_key_rsa(encrypted_aes_key_b64, private_key)
        
        # Decrypt file with AES
        decrypted_file = self.decrypt_file_aes(encrypted_file_data, aes_key)
        
        return decrypted_file

