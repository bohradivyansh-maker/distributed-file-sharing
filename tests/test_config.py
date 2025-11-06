"""
Tests for configuration loading
"""

import pytest
import os
from config_loader import Config

def test_config_singleton():
    """Test that Config implements singleton pattern"""
    config1 = Config()
    config2 = Config()
    assert config1 is config2

def test_config_loads_yaml():
    """Test that configuration loads from YAML file"""
    config = Config()
    assert config.get('server.main.port') is not None
    assert config.get('transfer.chunk_size') is not None

def test_config_get_with_default():
    """Test config.get() with default value"""
    config = Config()
    value = config.get('nonexistent.key', 'default_value')
    assert value == 'default_value'

def test_config_properties():
    """Test configuration properties"""
    config = Config()
    assert config.main_server is not None
    assert config.backup_server is not None
    assert config.transfer_config is not None

def test_chunk_size_configuration():
    """Test chunk size is properly configured"""
    config = Config()
    chunk_size = config.get('transfer.chunk_size')
    assert isinstance(chunk_size, int)
    assert chunk_size > 0
