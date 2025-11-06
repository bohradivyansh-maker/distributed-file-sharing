# 🖥️ Local Testing Setup Guide

## Quick Fix for Local Testing

The project is now configured for **localhost testing** on a single machine.

### ✅ Current Configuration

Your `config.yaml` is set to:
- **Main Server IP:** `127.0.0.1` (localhost)
- **Backup Server IP:** `127.0.0.1` (localhost)
- All servers bind to `0.0.0.0` (all interfaces)

This allows you to run all 3 components on the same computer!

---

## 🚀 Step-by-Step Local Testing

### **Step 1: Start Main Server**
```bash
# Terminal 1
cd "d:\Distributed Computing"
python main_server.py
```

**What you should see:**
- GUI window opens
- Console shows: "Starting MiniTorrent Main Server..."
- Status: "SERVER NOT RUNNING" (until you click Start)

**Actions:**
1. Click **"Add Files"** - Select 1-2 test files
2. Click **"Start Server"** - Status changes to "SERVER RUNNING"

---

### **Step 2: Start Backup Server**
```bash
# Terminal 2 (New PowerShell window)
cd "d:\Distributed Computing"
python backup_server.py
```

**What you should see:**
- GUI window opens
- Console shows: "Starting MiniTorrent Backup Server..."
- Title: "Backup Server (Standby)"
- Log: "Backup server started in STANDBY mode."

**Note:** You should see replication messages if files were added to main server!

---

### **Step 3: Start Client**
```bash
# Terminal 3 (New PowerShell window)
cd "d:\Distributed Computing"
python client.py
```

**What you should see:**
- GUI window opens
- Title: "EduShare File Sharing Client"
- Empty file list initially

**Actions:**
1. Click **"Refresh"** - Files should appear!
2. Select a file
3. Click **"Download Selected Files"**
4. Choose save location
5. Watch progress bar!

---

## 🔧 Troubleshooting

### Error: "Connection timeout to 127.0.0.1:5001"

**Cause:** Main server not started or not listening

**Fix:**
1. Make sure Main Server is running
2. Click "Start Server" button on Main Server GUI
3. Check console for "Server started on port 5001"

---

### Error: "Could not fetch file list"

**Cause:** Client trying to connect before server is ready

**Fix:**
1. Ensure Main Server shows "SERVER RUNNING"
2. Wait 2-3 seconds after starting server
3. Click "Refresh" on client

---

### Error: Port already in use

**Cause:** Previous server instance still running

**Fix (Windows):**
```powershell
# Find process using port 5001
netstat -ano | findstr :5001

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

---

### Backup Server doesn't receive files

**Cause:** Main server couldn't connect to backup

**Solutions:**
1. Make sure backup server is started FIRST
2. Check backup server console for errors
3. Restart main server after backup is ready

---

## 🎯 Testing Checklist

### Basic Functionality
- [ ] Main server starts without errors
- [ ] Backup server starts in STANDBY mode
- [ ] Files can be added to main server
- [ ] Files appear in main server list
- [ ] Backup server receives replication
- [ ] Client can connect and fetch file list
- [ ] Client can download files
- [ ] Progress bar shows correctly
- [ ] Downloaded file is valid

### Advanced Features
- [ ] Logs are created in `logs/app.log`
- [ ] Database is created in `data/files.db`
- [ ] Download count increments
- [ ] Checksums are verified (check logs)
- [ ] Metrics are logged every 5 seconds

### Failover Testing
- [ ] Main server is serving files
- [ ] Client downloads successfully
- [ ] **Close main server window**
- [ ] Wait 6-8 seconds
- [ ] Backup server promotes to ACTIVE
- [ ] Client can still download files
- [ ] No data loss occurred

---

## 📊 Expected Behavior

### Main Server Console Output:
```
==================================================
Starting MiniTorrent Main Server...
Configuration loaded from config.yaml
Server Port: 5001
Replication Port: 5003
Heartbeat Port: 5004
Backup Server IP: 127.0.0.1
==================================================
```

### Backup Server Console Output:
```
==================================================
Starting MiniTorrent Backup Server...
Configuration loaded from config.yaml
Server Port: 5001
Replication Port: 5003
Heartbeat Port: 5004
Heartbeat Timeout: 6s
==================================================
```

### Log File (logs/app.log):
```
2025-11-06 17:30:00 - main_server - INFO - File Added: test.txt (5 chunks, 5242880 bytes)
2025-11-06 17:30:01 - integrity - INFO - Generated 5 checksums for test.txt
2025-11-06 17:30:02 - database - INFO - Added file to database: test.txt (ID: 1)
2025-11-06 17:30:03 - main_server - INFO - Replicated file 'test.txt' to backup server.
```

---

## 🌐 Network Testing (Different Computers)

If you want to test across multiple computers:

### **Step 1: Find Your IP Address**
```powershell
ipconfig
```
Look for: `IPv4 Address. . . . . . . . . . . : 192.168.1.XXX`

### **Step 2: Update config.yaml**
```yaml
server:
  main:
    ip: "192.168.1.10"  # Main server's actual IP
  backup:
    ip: "192.168.1.11"  # Backup server's actual IP
```

### **Step 3: Configure Firewall**
Allow incoming connections on ports:
- 5001 (Client connections)
- 5003 (Replication)
- 5004 (Heartbeat)

```powershell
# Windows Firewall (Run as Administrator)
New-NetFirewallRule -DisplayName "MiniTorrent Main" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "MiniTorrent Replication" -Direction Inbound -LocalPort 5003 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "MiniTorrent Heartbeat" -Direction Inbound -LocalPort 5004 -Protocol TCP -Action Allow
```

---

## 💡 Pro Tips

1. **Start Order Matters:**
   - Start Backup Server FIRST (so it's ready for replication)
   - Then start Main Server
   - Finally start Client(s)

2. **Window Arrangement:**
   - Tile windows side-by-side for easy monitoring
   - Keep log file open in VS Code to watch real-time activity

3. **Test Files:**
   - Use small files first (< 10MB) for quick testing
   - Try different file types (PDF, TXT, images)

4. **Log Monitoring:**
   ```powershell
   # Watch logs in real-time
   Get-Content "logs/app.log" -Wait -Tail 20
   ```

5. **Database Inspection:**
   ```powershell
   # View database contents
   sqlite3 data/files.db "SELECT filename, file_size, download_count FROM files;"
   ```

---

## 🎬 Quick Demo Command Sequence

Copy-paste these into 3 separate terminals:

**Terminal 1:**
```powershell
cd "d:\Distributed Computing" ; python backup_server.py
```

**Terminal 2:**
```powershell
cd "d:\Distributed Computing" ; python main_server.py
```

**Terminal 3:**
```powershell
cd "d:\Distributed Computing" ; python client.py
```

Then:
1. Main Server: Add files → Start Server
2. Client: Refresh → Download

---

## ✅ Success Indicators

You know it's working when:
- ✅ No error messages in consoles
- ✅ Files appear in client after refresh
- ✅ Download progress bar moves smoothly
- ✅ Downloaded files are valid
- ✅ Logs show activity in `logs/app.log`
- ✅ Database has entries in `data/files.db`
- ✅ Backup server receives replication messages

---

**Ready to test! Start with backup server first, then main, then client.** 🚀
