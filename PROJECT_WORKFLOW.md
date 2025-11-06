# 📋 Distributed File Sharing System - Project Workflow

## 🎯 Project Overview (For LinkedIn/Portfolio)

**Project Name:** Distributed File Sharing System (MiniTorrent/EduShare)  
**Tech Stack:** Python, Socket Programming, SQLite, YAML, Tkinter  
**Architecture:** Primary-Backup Server Model with Automatic Failover  
**GitHub:** https://github.com/bohradivyansh-maker/distributed-file-sharing

---

## 🏗️ System Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM WORKFLOW                          │
└─────────────────────────────────────────────────────────────┘

1. INITIALIZATION PHASE
   ┌──────────────┐
   │ Main Server  │ ◄── Loads config.yaml
   └──────┬───────┘     Initializes database
          │             Starts logging
          ├─── Binds to port 5001 (clients)
          ├─── Binds to port 5003 (replication)
          └─── Binds to port 5004 (heartbeat)

   ┌──────────────┐
   │Backup Server │ ◄── Loads config.yaml
   └──────┬───────┘     Restores from database
          │             Starts monitoring
          ├─── Listens on port 5003 (replication)
          └─── Listens on port 5004 (heartbeat)

2. FILE UPLOAD PHASE
   User → Main Server GUI → "Add Files" button
   │
   ├─── File selected from dialog
   ├─── Split into 1MB chunks
   ├─── Calculate SHA256 checksums
   ├─── Store in memory + database
   └─── Replicate to Backup Server
        │
        ├─── Send metadata + chunks
        ├─── Backup verifies checksums
        └─── Backup stores in database

3. REPLICATION PHASE
   Main Server ──────────────► Backup Server
   │                           │
   ├─ Heartbeat (every 2s) ───►├─ Update timestamp
   ├─ File data + checksums ──►├─ Verify integrity
   └─ Download count updates ─►└─ Sync database

4. CLIENT REQUEST PHASE
   Client → "Refresh" → Request file list
   │
   ├─── Server sends: "file1.txt:1024:5|file2.pdf:2048:10"
   │    (filename:size:downloads)
   │
   ├─── Client displays in table
   │
   └─── User selects file → "Download"
        │
        ├─── Request chunk count
        ├─── Download chunks sequentially
        ├─── Verify checksums
        ├─── Assemble file
        └─── Save to disk

5. FAILOVER PHASE (Disaster Recovery)
   Main Server ──X── (Crashed/Stopped)
   │
   ├─── Heartbeat stops
   │
   Backup Server monitors:
   ├─── Last heartbeat > 6 seconds?
   ├─── YES → Promote to ACTIVE
   │
   └─── Bind to port 5001
        │
        └─── Serve clients seamlessly
             (No data loss!)

6. MONITORING PHASE (Continuous)
   ├─── Log all operations (logs/app.log)
   ├─── Track metrics:
   │    ├─ Uptime
   │    ├─ Bytes sent/received
   │    ├─ Active connections
   │    ├─ Success rate
   │    └─ Download speeds
   └─── Store in database for analytics
```

---

## 🔄 Detailed Component Workflow

### A. Main Server Workflow

```python
START
  ↓
Load Configuration (config.yaml)
  ↓
Initialize Logger (logs/app.log)
  ↓
Connect to Database (data/files.db)
  ↓
Restore File Metadata from DB
  ↓
Start GUI (Tkinter)
  ↓
[WAITING FOR USER INPUT]
  ↓
User clicks "Add Files"
  ↓
1. Select file(s) via dialog
2. Read file → Split into chunks (1MB each)
3. Calculate SHA256 for each chunk
4. Store chunks in memory
5. Save metadata to database
6. Display in file list
  ↓
User clicks "Start Server"
  ↓
1. Bind socket to port 5001
2. Start listening for clients
3. Spawn thread for each connection
  ↓
Background: Start heartbeat thread
  ↓
Every 2 seconds:
  - Send "heartbeat" to backup server (port 5004)
  ↓
Background: Start replication thread
  ↓
When file added:
  - Send to backup (port 5003):
    "replicate|filename|size|chunks|checksums"
    [chunk_data_1][chunk_data_2]...[chunk_data_n]
  ↓
Handle Client Requests:
  - "list" → Return all files
  - "count|filename" → Return chunk count
  - "get|filename|index" → Send chunk data
  ↓
On chunk 0 download:
  - Increment download counter
  - Update database
  - Replicate count to backup
  ↓
[CONTINUE SERVING]
```

### B. Backup Server Workflow

```python
START
  ↓
Load Configuration (config.yaml)
  ↓
Initialize Logger
  ↓
Connect to Database
  ↓
Restore File Metadata
  ↓
Start GUI (Standby Mode)
  ↓
Spawn 3 background threads:
  ↓
THREAD 1: Replication Listener (port 5003)
  - Receive file data from main
  - Verify checksums
  - Store in memory + database
  ↓
THREAD 2: Heartbeat Listener (port 5004)
  - Receive "heartbeat" messages
  - Update last_heartbeat timestamp
  ↓
THREAD 3: Heartbeat Monitor
  - Every 2 seconds check:
    if (current_time - last_heartbeat) > 6 seconds:
      ↓
      PROMOTE TO ACTIVE!
      ↓
      1. Update GUI title
      2. Bind to port 5001
      3. Start serving clients
      4. Log failover event
  ↓
[WAITING IN STANDBY OR SERVING IF ACTIVE]
```

### C. Client Workflow

```python
START
  ↓
Load Configuration
  ↓
Initialize Logger
  ↓
Start GUI
  ↓
Try connecting to MAIN server
  ↓
If fails → Try BACKUP server
  ↓
Connected! Request file list
  ↓
Server responds: "file1:1024:5|file2:2048:10"
  ↓
Parse and display in table:
  | Name     | Size  | Downloads |
  |----------|-------|-----------|
  | file1    | 1024  | 5         |
  | file2    | 2048  | 10        |
  ↓
User searches/filters files
  ↓
User selects file(s) → "Download"
  ↓
For each file:
  1. Ask save location
  2. Request chunk count from server
  3. Create progress window
     ↓
  FOR each chunk (0 to count-1):
    - Request: "get|filename|index"
    - Receive chunk data
    - Update progress bar
    - Calculate percentage
    - Update circular progress indicator
     ↓
  4. Verify checksums (if available)
  5. Write all chunks to file
  6. Mark as complete
  7. Register as seeder
  ↓
Background: Start seeder server (port 6000)
  - Listen for peer requests
  - Serve downloaded files to other clients
  ↓
[READY FOR MORE DOWNLOADS]
```

---

## 🎬 Demo Workflow (For Screenshots/Video)

### **Scene 1: System Startup** (0:00-0:30)
1. Open 3 terminals side-by-side
2. Terminal 1: `python main_server.py`
   - Screenshot: Main server GUI (empty file list)
3. Terminal 2: `python backup_server.py`
   - Screenshot: Backup server GUI (Standby mode)
4. Terminal 3: `python client.py`
   - Screenshot: Client GUI (empty file list)

### **Scene 2: File Upload** (0:30-1:00)
1. Main server → Click "Add Files"
2. Select sample files (PDF, TXT, images)
3. Screenshot: Files appear in list with chunk count
4. Screenshot: Logs showing checksum calculation
5. Screenshot: Backup server receiving replication

### **Scene 3: Client Download** (1:00-2:00)
1. Client → Click "Refresh"
2. Screenshot: Files populate in table
3. Select a file → "Download Selected Files"
4. Screenshot: Progress window with:
   - Progress bar
   - Percentage
   - Circular indicator
5. Screenshot: Completed download notification
6. Show downloaded file in folder

### **Scene 4: Data Integrity** (2:00-2:30)
1. Open `logs/app.log`
2. Screenshot: Checksum verification logs
3. Screenshot: Database viewer showing `data/files.db`
4. Show file metadata table

### **Scene 5: Failover Demo** (2:30-3:30) ⭐ **IMPRESSIVE!**
1. Client connected to main server
2. Screenshot: Active connections
3. **Close main server window**
4. Screenshot: Backup server logs "No heartbeat detected"
5. Screenshot: Backup promotes to ACTIVE
6. Client continues working!
7. Screenshot: Client downloads from backup
8. **THIS SHOWS FAULT TOLERANCE!**

### **Scene 6: Monitoring & Metrics** (3:30-4:00)
1. Screenshot: Log file showing metrics:
   - Uptime
   - Bytes transferred
   - Success rate
2. Screenshot: Database metrics table
3. Screenshot: Multiple concurrent connections

---

## 📸 Key Screenshots to Capture

### **Technical Screenshots:**
1. ✅ Main server GUI with multiple files
2. ✅ Backup server in standby mode
3. ✅ Client file browser with files
4. ✅ Download progress window
5. ✅ Log file showing structured logging
6. ✅ Database schema (SQLite viewer)
7. ✅ config.yaml file
8. ✅ Checksum verification in logs
9. ✅ Failover event in logs
10. ✅ Metrics summary in logs

### **Architecture Screenshots:**
11. ✅ VS Code showing project structure
12. ✅ README.md on GitHub
13. ✅ Test results (`pytest -v`)
14. ✅ Code showing retry logic
15. ✅ Code showing checksum verification

---

## 🎥 Video Recording Script (2-3 minutes)

### **Option 1: Quick Demo (2 min)**
```
[0:00] Title: "Distributed File Sharing with Fault Tolerance"
[0:05] Show architecture diagram from README
[0:10] Start all 3 components (main, backup, client)
[0:20] Upload files on main server
[0:30] Client downloads a file with progress
[0:45] Kill main server → Show backup takeover
[1:00] Client continues downloading from backup
[1:15] Show logs with checksums and metrics
[1:30] Show database persistence
[1:45] Show GitHub repository
[2:00] End with tech stack and contact
```

### **Option 2: Technical Deep Dive (5 min)**
```
[0:00] Introduction + Problem Statement
[0:30] Architecture explanation
[1:00] Configuration management demo
[1:30] File upload + chunking + checksums
[2:30] Client download with progress
[3:00] Failover demonstration
[3:45] Database persistence
[4:15] Logging and monitoring
[4:45] GitHub + Testing
[5:00] Conclusion + Skills demonstrated
```

---

## 📱 LinkedIn Post Template (Copy-Paste Ready)

```
🚀 Excited to share my latest project: Distributed File Sharing System!

Built a production-ready distributed system featuring:

✅ Fault Tolerance: Primary-backup architecture with automatic failover
✅ Data Integrity: SHA256 hash verification for all file transfers
✅ Scalability: Chunked transfers handling large files efficiently
✅ Observability: Structured logging + real-time metrics
✅ Persistence: SQLite database for stateful storage
✅ Resilience: Exponential backoff & retry logic

🎯 Key Highlights:
• Zero data loss during server failover
• Configuration-driven deployment (YAML)
• Comprehensive test suite (pytest)
• Full documentation & deployment guides

💡 Technical Stack:
Python | Socket Programming | SQLite | Threading | YAML | Tkinter

This project demonstrates distributed systems concepts, fault tolerance, and production-ready software engineering practices.

🔗 GitHub: https://github.com/bohradivyansh-maker/distributed-file-sharing

[Include screenshots/video here]

#DistributedSystems #Python #SoftwareEngineering #BackendDevelopment #FaultTolerance #SystemDesign #OpenSource

---

What distributed systems concepts would you add next? Drop your thoughts! 💭
```

---

## 🎨 Screenshot Composition Tips

### **For LinkedIn:**
- Use dark theme VS Code for "professional" look
- Annotate screenshots with arrows and text
- Create a collage of 3-4 key screenshots
- Show before/after of failover

### **Tools to Use:**
- **Recording:** OBS Studio (free) or Windows Game Bar
- **Screenshots:** Snipping Tool or ShareX
- **Editing:** Canva (for collages), Paint.NET
- **GIF Creation:** ScreenToGif (for quick demos)

---

## 🔥 Quick Test Commands (For Demo)

```bash
# Terminal 1 - Main Server
cd "d:\Distributed Computing"
python main_server.py

# Terminal 2 - Backup Server
cd "d:\Distributed Computing"
python backup_server.py

# Terminal 3 - Client
cd "d:\Distributed Computing"
python client.py

# Terminal 4 - Run Tests (for screenshot)
pytest tests/ -v --cov=. --cov-report=term

# Check logs
Get-Content "logs/app.log" -Tail 20

# View database
sqlite3 data/files.db "SELECT * FROM files;"
```

---

## ✨ Gemini Prompt (For LinkedIn Post Generation)

```
Create a compelling LinkedIn post for my Distributed File Sharing System project.

Project Details:
- Fault-tolerant distributed system with primary-backup replication
- Automatic failover mechanism (backup takes over when main fails)
- SHA256 hash verification for data integrity
- SQLite database for persistent storage
- Structured logging and real-time metrics
- Configuration-driven deployment with YAML
- Comprehensive test suite with pytest
- Technologies: Python, Socket Programming, SQLite, Threading, YAML, Tkinter

Key Features:
1. Zero data loss during server failures
2. Chunked file transfer (1MB chunks)
3. Peer-to-peer seeding capabilities
4. Production-ready error handling with exponential backoff
5. Real-time performance monitoring

Target Audience: Technical recruiters, engineering managers, backend developers

Tone: Professional but approachable, showing both technical depth and practical impact

Include:
- Attention-grabbing opening
- Bullet points of key features
- Technical skills demonstrated
- Call to action
- Relevant hashtags

GitHub: https://github.com/bohradivyansh-maker/distributed-file-sharing
Author: Divyansh Bohra
```

---

**Ready to showcase your work! 🎉**
