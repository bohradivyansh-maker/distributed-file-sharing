"""
Tests for data integrity (checksum) functionality
"""

import pytest
from integrity import IntegrityChecker

def test_calculate_checksum():
    """Test checksum calculation"""
    data = b"Hello, World!"
    checksum = IntegrityChecker.calculate_checksum(data)
    
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA256 produces 64 hex characters
    
def test_calculate_checksum_consistency():
    """Test that same data produces same checksum"""
    data = b"Test data for consistency"
    checksum1 = IntegrityChecker.calculate_checksum(data)
    checksum2 = IntegrityChecker.calculate_checksum(data)
    
    assert checksum1 == checksum2

def test_verify_checksum_valid():
    """Test checksum verification with valid data"""
    data = b"Valid data"
    checksum = IntegrityChecker.calculate_checksum(data)
    
    is_valid = IntegrityChecker.verify_checksum(data, checksum)
    assert is_valid is True

def test_verify_checksum_invalid():
    """Test checksum verification with invalid data"""
    data = b"Original data"
    checksum = IntegrityChecker.calculate_checksum(data)
    
    corrupted_data = b"Corrupted data"
    is_valid = IntegrityChecker.verify_checksum(corrupted_data, checksum)
    assert is_valid is False

def test_create_chunk_manifest():
    """Test chunk manifest creation"""
    chunks = [b"chunk1", b"chunk2", b"chunk3"]
    manifest = IntegrityChecker.create_chunk_manifest(chunks)
    
    assert len(manifest) == len(chunks)
    assert all(isinstance(checksum, str) for checksum in manifest)
    assert all(len(checksum) == 64 for checksum in manifest)

def test_verify_chunks_success():
    """Test successful chunk verification"""
    chunks = [b"chunk1", b"chunk2", b"chunk3"]
    manifest = IntegrityChecker.create_chunk_manifest(chunks)
    
    success, failed = IntegrityChecker.verify_chunks(chunks, manifest)
    assert success is True
    assert len(failed) == 0

def test_verify_chunks_failure():
    """Test failed chunk verification"""
    original_chunks = [b"chunk1", b"chunk2", b"chunk3"]
    manifest = IntegrityChecker.create_chunk_manifest(original_chunks)
    
    # Corrupt one chunk
    corrupted_chunks = [b"chunk1", b"CORRUPTED", b"chunk3"]
    success, failed = IntegrityChecker.verify_chunks(corrupted_chunks, manifest)
    
    assert success is False
    assert 1 in failed  # Second chunk (index 1) should fail

def test_checksum_type_error():
    """Test that non-bytes data raises TypeError"""
    with pytest.raises(TypeError):
        IntegrityChecker.calculate_checksum("string instead of bytes")
