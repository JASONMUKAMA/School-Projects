"""
Integrity Verification Module
Handles SHA-256 checksums for file integrity verification
"""

import hashlib
from typing import Tuple


class IntegrityManager:
    """Manages file integrity verification using SHA-256"""
    
    @staticmethod
    def calculate_hash(file_data: bytes) -> str:
        """
        Calculate SHA-256 hash of file data
        
        Args:
            file_data: File data as bytes
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256(file_data)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def calculate_hash_file(file_path: str) -> str:
        """
        Calculate SHA-256 hash of file from path
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def verify_integrity(file_data: bytes, expected_hash: str) -> Tuple[bool, str]:
        """
        Verify file integrity by comparing hash
        
        Args:
            file_data: File data to verify
            expected_hash: Expected SHA-256 hash
            
        Returns:
            Tuple of (is_valid, actual_hash)
        """
        actual_hash = IntegrityManager.calculate_hash(file_data)
        is_valid = actual_hash == expected_hash
        return is_valid, actual_hash
    
    @staticmethod
    def verify_integrity_file(file_path: str, expected_hash: str) -> Tuple[bool, str]:
        """
        Verify file integrity from file path
        
        Args:
            file_path: Path to file
            expected_hash: Expected SHA-256 hash
            
        Returns:
            Tuple of (is_valid, actual_hash)
        """
        actual_hash = IntegrityManager.calculate_hash_file(file_path)
        is_valid = actual_hash == expected_hash
        return is_valid, actual_hash

