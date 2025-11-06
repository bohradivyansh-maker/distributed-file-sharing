"""
Logging configuration module for the Distributed File Sharing System.
Provides structured logging with file rotation and configurable levels.
"""

import logging
import logging.handlers
from pathlib import Path
from config_loader import config

class LoggerSetup:
    """Centralized logging setup"""
    _loggers = {}
    
    @staticmethod
    def get_logger(name):
        """
        Get or create a logger with the specified name.
        
        Args:
            name: Logger name (usually __name__ of the module)
            
        Returns:
            Configured logger instance
        """
        if name in LoggerSetup._loggers:
            return LoggerSetup._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.get('logging.level', 'INFO')))
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        if config.get('logging.log_to_file', False):
            log_file = config.get('logging.log_file', 'logs/app.log')
            
            # Create logs directory if it doesn't exist
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=config.get('logging.max_bytes', 10485760),  # 10 MB
                backupCount=config.get('logging.backup_count', 5)
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        LoggerSetup._loggers[name] = logger
        return logger

# Convenience function
def get_logger(name):
    """Get a configured logger instance"""
    return LoggerSetup.get_logger(name)
