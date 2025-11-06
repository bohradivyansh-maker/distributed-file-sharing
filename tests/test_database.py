"""
Tests for database operations
"""

import pytest
import os
import tempfile
from database import Database

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    # Create database instance with temp path
    db = Database()
    db.db_path = db_path
    db.enabled = True
    db._init_db()
    
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    os.rmdir(temp_dir)

def test_add_file(temp_db):
    """Test adding a file to database"""
    file_id = temp_db.add_file("test.txt", 1024, 5, ["hash1", "hash2"])
    assert file_id is not None
    assert isinstance(file_id, int)

def test_get_file(temp_db):
    """Test retrieving a file from database"""
    temp_db.add_file("test.txt", 1024, 5, ["hash1", "hash2"])
    
    file_info = temp_db.get_file("test.txt")
    assert file_info is not None
    assert file_info['filename'] == "test.txt"
    assert file_info['file_size'] == 1024
    assert file_info['chunk_count'] == 5

def test_get_nonexistent_file(temp_db):
    """Test retrieving a file that doesn't exist"""
    file_info = temp_db.get_file("nonexistent.txt")
    assert file_info is None

def test_get_all_files(temp_db):
    """Test retrieving all files"""
    temp_db.add_file("file1.txt", 1024, 2)
    temp_db.add_file("file2.txt", 2048, 4)
    
    files = temp_db.get_all_files()
    assert len(files) == 2
    assert any(f['filename'] == 'file1.txt' for f in files)
    assert any(f['filename'] == 'file2.txt' for f in files)

def test_update_download_count(temp_db):
    """Test updating download count"""
    temp_db.add_file("test.txt", 1024, 5)
    
    success = temp_db.update_download_count("test.txt", 10)
    assert success is True
    
    file_info = temp_db.get_file("test.txt")
    assert file_info['download_count'] == 10

def test_increment_download_count(temp_db):
    """Test incrementing download count"""
    temp_db.add_file("test.txt", 1024, 5)
    
    temp_db.increment_download_count("test.txt")
    file_info = temp_db.get_file("test.txt")
    assert file_info['download_count'] == 1
    
    temp_db.increment_download_count("test.txt")
    file_info = temp_db.get_file("test.txt")
    assert file_info['download_count'] == 2

def test_delete_file(temp_db):
    """Test deleting a file"""
    temp_db.add_file("test.txt", 1024, 5)
    
    success = temp_db.delete_file("test.txt")
    assert success is True
    
    file_info = temp_db.get_file("test.txt")
    assert file_info is None

def test_add_metric(temp_db):
    """Test adding a metric"""
    success = temp_db.add_metric("test_metric", 123.45)
    assert success is True

def test_get_metrics(temp_db):
    """Test retrieving metrics"""
    temp_db.add_metric("test_metric", 100.0)
    temp_db.add_metric("test_metric", 200.0)
    
    metrics = temp_db.get_metrics("test_metric", limit=10)
    assert len(metrics) == 2
