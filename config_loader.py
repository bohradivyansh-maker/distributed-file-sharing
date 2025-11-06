"""
Configuration loader module for the Distributed File Sharing System.
Loads and validates configuration from YAML file.
"""

import yaml
import os
from pathlib import Path

class Config:
    """Singleton configuration class"""
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Create necessary directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        dirs_to_create = [
            self.get('logging.log_file', '').rsplit('/', 1)[0] if self.get('logging.log_to_file') else None,
            self.get('database.path', '').rsplit('/', 1)[0] if self.get('database.enable_persistence') else None,
            self.get('client.download_path', '')
        ]
        
        for dir_path in dirs_to_create:
            if dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get(self, key, default=None):
        """
        Get configuration value using dot notation.
        Example: config.get('server.main.port')
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_all(self):
        """Get entire configuration dictionary"""
        return self._config.copy()
    
    @property
    def main_server(self):
        """Get main server configuration"""
        return self._config.get('server', {}).get('main', {})
    
    @property
    def backup_server(self):
        """Get backup server configuration"""
        return self._config.get('server', {}).get('backup', {})
    
    @property
    def client_config(self):
        """Get client configuration"""
        return self._config.get('client', {})
    
    @property
    def transfer_config(self):
        """Get transfer configuration"""
        return self._config.get('transfer', {})
    
    @property
    def logging_config(self):
        """Get logging configuration"""
        return self._config.get('logging', {})
    
    @property
    def database_config(self):
        """Get database configuration"""
        return self._config.get('database', {})
    
    @property
    def metrics_config(self):
        """Get metrics configuration"""
        return self._config.get('metrics', {})

# Global config instance
config = Config()
