"""
Tests for metrics collection
"""

import pytest
from metrics import MetricsCollector

@pytest.fixture
def metrics_collector():
    """Create a fresh metrics collector for testing"""
    return MetricsCollector()

def test_metrics_initialization(metrics_collector):
    """Test metrics collector initializes properly"""
    assert metrics_collector.total_bytes_sent == 0
    assert metrics_collector.total_bytes_received == 0
    assert metrics_collector.active_connections == 0
    assert metrics_collector.total_requests == 0
    assert metrics_collector.failed_requests == 0

def test_record_bytes_sent(metrics_collector):
    """Test recording sent bytes"""
    metrics_collector.record_bytes_sent(1024)
    assert metrics_collector.total_bytes_sent == 1024
    
    metrics_collector.record_bytes_sent(2048)
    assert metrics_collector.total_bytes_sent == 3072

def test_record_bytes_received(metrics_collector):
    """Test recording received bytes"""
    metrics_collector.record_bytes_received(512)
    assert metrics_collector.total_bytes_received == 512

def test_connection_management(metrics_collector):
    """Test connection increment and decrement"""
    metrics_collector.increment_connections()
    assert metrics_collector.active_connections == 1
    
    metrics_collector.increment_connections()
    assert metrics_collector.active_connections == 2
    
    metrics_collector.decrement_connections()
    assert metrics_collector.active_connections == 1
    
    metrics_collector.decrement_connections()
    assert metrics_collector.active_connections == 0

def test_decrement_connections_never_negative(metrics_collector):
    """Test that active connections never goes negative"""
    metrics_collector.decrement_connections()
    assert metrics_collector.active_connections == 0

def test_record_request(metrics_collector):
    """Test recording requests"""
    metrics_collector.record_request(success=True)
    assert metrics_collector.total_requests == 1
    assert metrics_collector.failed_requests == 0
    
    metrics_collector.record_request(success=False)
    assert metrics_collector.total_requests == 2
    assert metrics_collector.failed_requests == 1

def test_success_rate(metrics_collector):
    """Test success rate calculation"""
    # No requests yet
    assert metrics_collector.get_success_rate() == 100.0
    
    # All successful
    metrics_collector.record_request(success=True)
    metrics_collector.record_request(success=True)
    assert metrics_collector.get_success_rate() == 100.0
    
    # 50% success
    metrics_collector.record_request(success=False)
    metrics_collector.record_request(success=False)
    assert metrics_collector.get_success_rate() == 50.0

def test_get_uptime(metrics_collector):
    """Test uptime tracking"""
    uptime = metrics_collector.get_uptime()
    assert uptime >= 0

def test_record_download(metrics_collector):
    """Test recording download times"""
    metrics_collector.record_download("file1.txt", 5.2)
    assert len(metrics_collector.download_times) == 1
    
    metrics_collector.record_download("file2.txt", 3.8)
    assert len(metrics_collector.download_times) == 2

def test_get_avg_download_time(metrics_collector):
    """Test average download time calculation"""
    # No downloads yet
    assert metrics_collector.get_avg_download_time() == 0.0
    
    metrics_collector.record_download("file1.txt", 4.0)
    metrics_collector.record_download("file2.txt", 6.0)
    assert metrics_collector.get_avg_download_time() == 5.0

def test_metrics_summary(metrics_collector):
    """Test getting metrics summary"""
    metrics_collector.record_bytes_sent(1024)
    metrics_collector.increment_connections()
    metrics_collector.record_request(success=True)
    
    summary = metrics_collector.get_metrics_summary()
    
    assert 'uptime_seconds' in summary
    assert 'total_bytes_sent' in summary
    assert 'active_connections' in summary
    assert 'total_requests' in summary
    assert 'success_rate' in summary
