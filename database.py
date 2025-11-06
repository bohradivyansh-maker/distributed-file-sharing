"""
Database persistence module for the Distributed File Sharing System.
Manages file metadata storage using SQLite.
"""

import sqlite3
import json
from pathlib import Path
from config_loader import config
from logger_config import get_logger

logger = get_logger(__name__)

class Database:
    """SQLite database manager for file metadata"""
    
    def __init__(self):
        self.db_path = config.get('database.path', 'data/files.db')
        self.enabled = config.get('database.enable_persistence', True)
        
        if self.enabled:
            # Create database directory if it doesn't exist
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            logger.info(f"Database initialized at {self.db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    file_size INTEGER NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    download_count INTEGER DEFAULT 0,
                    checksums TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Chunks table (optional - for future P2P tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, chunk_index)
                )
            ''')
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.debug("Database schema initialized")
    
    def add_file(self, filename, file_size, chunk_count, checksums=None):
        """Add a new file to the database"""
        if not self.enabled:
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                checksums_json = json.dumps(checksums) if checksums else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO files 
                    (filename, file_size, chunk_count, checksums, download_count)
                    VALUES (?, ?, ?, ?, COALESCE((SELECT download_count FROM files WHERE filename = ?), 0))
                ''', (filename, file_size, chunk_count, checksums_json, filename))
                
                conn.commit()
                file_id = cursor.lastrowid
                logger.info(f"Added file to database: {filename} (ID: {file_id})")
                return file_id
        except Exception as e:
            logger.error(f"Error adding file to database: {e}")
            return None
    
    def get_file(self, filename):
        """Get file metadata from database"""
        if not self.enabled:
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, filename, file_size, chunk_count, download_count, checksums
                    FROM files WHERE filename = ?
                ''', (filename,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'filename': row[1],
                        'file_size': row[2],
                        'chunk_count': row[3],
                        'download_count': row[4],
                        'checksums': json.loads(row[5]) if row[5] else None
                    }
                return None
        except Exception as e:
            logger.error(f"Error retrieving file from database: {e}")
            return None
    
    def get_all_files(self):
        """Get all files from database"""
        if not self.enabled:
            return []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT filename, file_size, chunk_count, download_count, checksums
                    FROM files ORDER BY created_at DESC
                ''')
                
                files = []
                for row in cursor.fetchall():
                    files.append({
                        'filename': row[0],
                        'file_size': row[1],
                        'chunk_count': row[2],
                        'download_count': row[3],
                        'checksums': json.loads(row[4]) if row[4] else None
                    })
                return files
        except Exception as e:
            logger.error(f"Error retrieving all files: {e}")
            return []
    
    def update_download_count(self, filename, count):
        """Update download count for a file"""
        if not self.enabled:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE files SET download_count = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE filename = ?
                ''', (count, filename))
                conn.commit()
                logger.debug(f"Updated download count for {filename}: {count}")
                return True
        except Exception as e:
            logger.error(f"Error updating download count: {e}")
            return False
    
    def increment_download_count(self, filename):
        """Increment download count for a file"""
        if not self.enabled:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE files SET download_count = download_count + 1,
                    updated_at = CURRENT_TIMESTAMP WHERE filename = ?
                ''', (filename,))
                conn.commit()
                logger.info(f"Incremented download count for {filename}")
                return True
        except Exception as e:
            logger.error(f"Error incrementing download count: {e}")
            return False
    
    def delete_file(self, filename):
        """Delete a file from database"""
        if not self.enabled:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM files WHERE filename = ?', (filename,))
                conn.commit()
                logger.info(f"Deleted file from database: {filename}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def add_metric(self, metric_name, metric_value):
        """Add a performance metric"""
        if not self.enabled:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics (metric_name, metric_value)
                    VALUES (?, ?)
                ''', (metric_name, metric_value))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding metric: {e}")
            return False
    
    def get_metrics(self, metric_name, limit=100):
        """Get recent metrics"""
        if not self.enabled:
            return []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT metric_value, timestamp FROM metrics
                    WHERE metric_name = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (metric_name, limit))
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            return []

# Global database instance
db = Database()
