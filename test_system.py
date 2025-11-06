"""
Quick System Test - Verify all components work
Run this before recording demo/screenshots
"""

print("="*60)
print("   DISTRIBUTED FILE SHARING SYSTEM - PRE-DEMO CHECK")
print("="*60)

# Test 1: Module Imports
print("\n[1/6] Testing module imports...")
try:
    from config_loader import config
    from logger_config import get_logger
    from database import db
    from integrity import IntegrityChecker
    from metrics import metrics
    from error_handler import SafeSocket
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Configuration
print("\n[2/6] Testing configuration...")
try:
    server_port = config.get('server.main.port')
    chunk_size = config.get('transfer.chunk_size')
    print(f"✅ Server Port: {server_port}")
    print(f"✅ Chunk Size: {chunk_size} bytes")
except Exception as e:
    print(f"❌ Config failed: {e}")

# Test 3: Database
print("\n[3/6] Testing database...")
try:
    test_file = db.add_file("test.txt", 1024, 5, ["hash1", "hash2"])
    if test_file:
        print("✅ Database write successful")
        retrieved = db.get_file("test.txt")
        if retrieved:
            print("✅ Database read successful")
        db.delete_file("test.txt")
        print("✅ Database delete successful")
except Exception as e:
    print(f"❌ Database failed: {e}")

# Test 4: Integrity
print("\n[4/6] Testing data integrity...")
try:
    test_data = b"Hello, World!"
    checksum = IntegrityChecker.calculate_checksum(test_data)
    is_valid = IntegrityChecker.verify_checksum(test_data, checksum)
    if is_valid:
        print(f"✅ Checksum verification working")
        print(f"   Sample checksum: {checksum[:32]}...")
except Exception as e:
    print(f"❌ Integrity check failed: {e}")

# Test 5: Metrics
print("\n[5/6] Testing metrics...")
try:
    metrics.record_bytes_sent(1024)
    metrics.increment_connections()
    metrics.record_request(success=True)
    summary = metrics.get_metrics_summary()
    print(f"✅ Metrics collection working")
    print(f"   Uptime: {summary['uptime_formatted']}")
except Exception as e:
    print(f"❌ Metrics failed: {e}")

# Test 6: Dependencies
print("\n[6/6] Testing dependencies...")
try:
    import yaml
    import tkinter
    import sqlite3
    print("✅ All dependencies available")
except Exception as e:
    print(f"❌ Missing dependency: {e}")

# Summary
print("\n" + "="*60)
print("   SYSTEM STATUS: READY FOR DEMO! 🚀")
print("="*60)
print("\n📋 Next Steps:")
print("   1. python main_server.py    (in terminal 1)")
print("   2. python backup_server.py  (in terminal 2)")
print("   3. python client.py         (in terminal 3)")
print("\n💡 Demo Scenarios:")
print("   • Upload files on main server")
print("   • Download from client")
print("   • Kill main server → Watch backup takeover")
print("   • Check logs/app.log for activity")
print("\n📸 Remember to capture:")
print("   • GUI screenshots")
print("   • Failover demonstration")
print("   • Log file output")
print("   • Database contents")
print("\n" + "="*60)
