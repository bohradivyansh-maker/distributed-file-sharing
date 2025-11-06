"""
Metrics and monitoring module for the Distributed File Sharing System.
Tracks performance metrics and system health.
"""

import time
import threading
from collections import defaultdict
from config_loader import config
from logger_config import get_logger
from database import db

logger = get_logger(__name__)

class MetricsCollector:
    """Collects and tracks system performance metrics"""
    
    def __init__(self):
        self.enabled = config.get('metrics.enable', True)
        self.update_interval = config.get('metrics.update_interval', 5)
        
        # In-memory metrics
        self.start_time = time.time()
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
        self.active_connections = 0
        self.total_requests = 0
        self.failed_requests = 0
        self.download_times = []  # List of (filename, duration) tuples
        self.upload_times = []
        
        # Thread-safe lock
        self._lock = threading.Lock()
        
        if self.enabled:
            logger.info("Metrics collection enabled")
    
    def record_bytes_sent(self, bytes_count):
        """Record bytes sent to clients"""
        with self._lock:
            self.total_bytes_sent += bytes_count
    
    def record_bytes_received(self, bytes_count):
        """Record bytes received from clients"""
        with self._lock:
            self.total_bytes_received += bytes_count
    
    def increment_connections(self):
        """Increment active connection count"""
        with self._lock:
            self.active_connections += 1
    
    def decrement_connections(self):
        """Decrement active connection count"""
        with self._lock:
            self.active_connections = max(0, self.active_connections - 1)
    
    def record_request(self, success=True):
        """Record a client request"""
        with self._lock:
            self.total_requests += 1
            if not success:
                self.failed_requests += 1
    
    def record_download(self, filename, duration):
        """Record a file download with duration in seconds"""
        with self._lock:
            self.download_times.append((filename, duration))
            
            # Keep only last 100 downloads
            if len(self.download_times) > 100:
                self.download_times = self.download_times[-100:]
        
        if self.enabled:
            db.add_metric(f"download_time_{filename}", duration)
    
    def record_upload(self, filename, duration):
        """Record a file upload with duration in seconds"""
        with self._lock:
            self.upload_times.append((filename, duration))
            
            # Keep only last 100 uploads
            if len(self.upload_times) > 100:
                self.upload_times = self.upload_times[-100:]
        
        if self.enabled:
            db.add_metric(f"upload_time_{filename}", duration)
    
    def get_uptime(self):
        """Get server uptime in seconds"""
        return time.time() - self.start_time
    
    def get_upload_speed(self):
        """Get average upload speed in MB/s"""
        uptime = self.get_uptime()
        if uptime > 0:
            return (self.total_bytes_sent / uptime) / (1024 * 1024)
        return 0.0
    
    def get_download_speed(self):
        """Get average download speed in MB/s"""
        uptime = self.get_uptime()
        if uptime > 0:
            return (self.total_bytes_received / uptime) / (1024 * 1024)
        return 0.0
    
    def get_success_rate(self):
        """Get request success rate as percentage"""
        if self.total_requests > 0:
            return ((self.total_requests - self.failed_requests) / self.total_requests) * 100
        return 100.0
    
    def get_avg_download_time(self):
        """Get average download time in seconds"""
        with self._lock:
            if self.download_times:
                return sum(d[1] for d in self.download_times) / len(self.download_times)
            return 0.0
    
    def get_metrics_summary(self):
        """Get a summary of all metrics"""
        uptime = self.get_uptime()
        
        summary = {
            'uptime_seconds': round(uptime, 2),
            'uptime_formatted': self._format_uptime(uptime),
            'total_bytes_sent': self.total_bytes_sent,
            'total_bytes_sent_mb': round(self.total_bytes_sent / (1024 * 1024), 2),
            'total_bytes_received': self.total_bytes_received,
            'total_bytes_received_mb': round(self.total_bytes_received / (1024 * 1024), 2),
            'active_connections': self.active_connections,
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'success_rate': round(self.get_success_rate(), 2),
            'avg_upload_speed_mbps': round(self.get_upload_speed(), 2),
            'avg_download_speed_mbps': round(self.get_download_speed(), 2),
            'avg_download_time': round(self.get_avg_download_time(), 2),
            'recent_downloads': len(self.download_times)
        }
        
        return summary
    
    def _format_uptime(self, seconds):
        """Format uptime as human-readable string"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def log_metrics(self):
        """Log current metrics"""
        summary = self.get_metrics_summary()
        logger.info(f"=== Metrics Summary ===")
        logger.info(f"Uptime: {summary['uptime_formatted']}")
        logger.info(f"Active Connections: {summary['active_connections']}")
        logger.info(f"Total Requests: {summary['total_requests']} (Success Rate: {summary['success_rate']}%)")
        logger.info(f"Data Sent: {summary['total_bytes_sent_mb']} MB")
        logger.info(f"Data Received: {summary['total_bytes_received_mb']} MB")
        logger.info(f"Avg Upload Speed: {summary['avg_upload_speed_mbps']} MB/s")
        logger.info(f"======================")
    
    def start_periodic_logging(self):
        """Start periodic metrics logging in background"""
        if not self.enabled:
            return
        
        def log_loop():
            while True:
                time.sleep(self.update_interval)
                self.log_metrics()
        
        thread = threading.Thread(target=log_loop, daemon=True)
        thread.start()
        logger.info(f"Started periodic metrics logging (every {self.update_interval}s)")

# Global metrics instance
metrics = MetricsCollector()
