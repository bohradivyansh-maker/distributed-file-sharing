"""
Data integrity module for the Distributed File Sharing System.
Provides checksum calculation and verification for file chunks.
"""

import hashlib
from logger_config import get_logger

logger = get_logger(__name__)

class IntegrityChecker:
    """Handles data integrity verification using SHA256"""
    
    @staticmethod
    def calculate_checksum(data):
        """
        Calculate SHA256 checksum of data.
        
        Args:
            data: Bytes to calculate checksum for
            
        Returns:
            Hexadecimal checksum string
        """
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def verify_checksum(data, expected_checksum):
        """
        Verify data matches expected checksum.
        
        Args:
            data: Bytes to verify
            expected_checksum: Expected SHA256 checksum
            
        Returns:
            True if checksum matches, False otherwise
        """
        actual_checksum = IntegrityChecker.calculate_checksum(data)
        is_valid = actual_checksum == expected_checksum
        
        if not is_valid:
            logger.warning(f"Checksum mismatch! Expected: {expected_checksum}, Got: {actual_checksum}")
        
        return is_valid
    
    @staticmethod
    def calculate_file_checksum(filepath, chunk_size=8192):
        """
        Calculate checksum for an entire file.
        
        Args:
            filepath: Path to file
            chunk_size: Size of chunks to read at a time
            
        Returns:
            Hexadecimal checksum string
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file checksum for {filepath}: {e}")
            raise
    
    @staticmethod
    def create_chunk_manifest(chunks):
        """
        Create a manifest of checksums for all chunks.
        
        Args:
            chunks: List of chunk data (bytes)
            
        Returns:
            List of checksums in order
        """
        manifest = []
        for i, chunk in enumerate(chunks):
            checksum = IntegrityChecker.calculate_checksum(chunk)
            manifest.append(checksum)
            logger.debug(f"Chunk {i} checksum: {checksum}")
        
        return manifest
    
    @staticmethod
    def verify_chunks(chunks, manifest):
        """
        Verify all chunks against a manifest.
        
        Args:
            chunks: List of chunk data (bytes)
            manifest: List of expected checksums
            
        Returns:
            Tuple of (success: bool, failed_indices: list)
        """
        if len(chunks) != len(manifest):
            logger.error(f"Chunk count mismatch: {len(chunks)} chunks vs {len(manifest)} checksums")
            return False, []
        
        failed = []
        for i, (chunk, expected_checksum) in enumerate(zip(chunks, manifest)):
            if not IntegrityChecker.verify_checksum(chunk, expected_checksum):
                failed.append(i)
                logger.error(f"Chunk {i} failed integrity check")
        
        if failed:
            logger.warning(f"Integrity check failed for {len(failed)} chunks: {failed}")
            return False, failed
        
        logger.info(f"All {len(chunks)} chunks passed integrity check")
        return True, []
