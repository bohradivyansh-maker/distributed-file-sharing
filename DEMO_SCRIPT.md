# 🎬 Demo Recording Script

## Quick Reference for Recording Screenshots/Video

### ✅ Pre-Recording Checklist

1. **Run System Test**
   ```bash
   python test_system.py
   ```
   ✅ All checks pass? Continue!

2. **Prepare Sample Files**
   - Create a folder: `demo_files/`
   - Add 2-3 files: PDF (5MB), TXT (1KB), Image (2MB)

3. **Clean Logs & Database** (Optional for fresh demo)
   ```bash
   rm logs/app.log
   rm data/files.db
   ```

4. **Recording Tools Ready**
   - Screen recorder: OBS Studio / Windows Game Bar
   - Screenshot tool: Snipping Tool / ShareX
   - Window arrangement: Side-by-side or stacked

---

## 🎥 Recording Sequence (Follow This Order!)

### **Step 1: Startup Screen** (Screenshot)
**Duration:** 30 seconds

Terminal arrangement:
```
┌─────────────────┬─────────────────┐
│  Main Server    │  Backup Server  │
│  Terminal 1     │  Terminal 2     │
├─────────────────┴─────────────────┤
│         Client Terminal 3          │
└────────────────────────────────────┘
```

**Commands:**
```bash
# Terminal 1 (Top Left)
cd "d:\Distributed Computing"
python main_server.py

# Terminal 2 (Top Right)
cd "d:\Distributed Computing"
python backup_server.py

# Terminal 3 (Bottom)
cd "d:\Distributed Computing"
python client.py
```

**📸 Screenshot #1:** All three windows open
- **Annotation:** "Main Server (Primary)" / "Backup Server (Standby)" / "Client"

---

### **Step 2: File Upload** (Video + Screenshots)
**Duration:** 1 minute

1. **Focus on Main Server window**
2. Click "Add Files" button
3. Select 2-3 sample files
4. **📸 Screenshot #2:** Files added with chunk count displayed
5. **📸 Screenshot #3:** Backup server showing "Replicated file..."

**Voice-over points:**
- "Files are automatically chunked into 1MB pieces"
- "SHA256 checksums calculated for each chunk"
- "Data replicated to backup server in real-time"

---

### **Step 3: Start Server** (Video)
**Duration:** 15 seconds

1. Click "Start Server" on Main Server
2. **📸 Screenshot #4:** Status changes to "SERVER RUNNING"
3. Show log messages in console

---

### **Step 4: Client File List** (Video + Screenshots)
**Duration:** 30 seconds

1. **Focus on Client window**
2. Click "Refresh" button
3. **📸 Screenshot #5:** File list populates with:
   - Filename
   - Size
   - Download count

**Voice-over:**
- "Client requests file list from server"
- "Displays file metadata: name, size, downloads"

---

### **Step 5: Download Demo** (Video - IMPORTANT!)
**Duration:** 1 minute

1. Select a file from list
2. Click "Download Selected Files"
3. Choose save location
4. **📸 Screenshot #6:** Progress window showing:
   - Progress bar
   - Percentage (e.g., "45%")
   - Circular progress indicator
5. **Wait for completion**
6. **📸 Screenshot #7:** "Download complete!" message
7. **Open downloaded file** to verify

**Voice-over:**
- "Chunked download with real-time progress tracking"
- "SHA256 verification ensures data integrity"
- "Download counter automatically increments"

---

### **Step 6: Log File Analysis** (Screenshots)
**Duration:** 30 seconds

Open `logs/app.log` in text editor

**📸 Screenshot #8:** Show log entries:
```
2025-11-06 17:08:39 - main_server - INFO - File Added: example.pdf (10 chunks, 10485760 bytes)
2025-11-06 17:08:40 - integrity - INFO - Generated 10 checksums for example.pdf
2025-11-06 17:08:41 - main_server - INFO - Replicated file 'example.pdf' to backup server
2025-11-06 17:09:15 - main_server - INFO - Sent chunk 0 of 'example.pdf' to ('127.0.0.1', 54321)
2025-11-06 17:09:16 - metrics - INFO - === Metrics Summary ===
2025-11-06 17:09:16 - metrics - INFO - Uptime: 1m 35s
2025-11-06 17:09:16 - metrics - INFO - Total Requests: 15 (Success Rate: 100.0%)
```

**Annotations:** Highlight checksum, metrics, replication

---

### **Step 7: Database View** (Screenshot)
**Duration:** 20 seconds

Open database in SQLite viewer or run:
```bash
sqlite3 data/files.db "SELECT * FROM files;"
```

**📸 Screenshot #9:** Database table showing:
- filename
- file_size
- chunk_count
- download_count
- checksums

**Voice-over:**
- "Persistent storage ensures data survives server restarts"
- "Metadata stored with checksums for integrity verification"

---

### **Step 8: FAILOVER DEMO** (Video - SHOW STOPPER! 🌟)
**Duration:** 1.5 minutes

**This is the most impressive part!**

1. **Ensure client is connected to main server**
2. **Show main server is active** (SERVER RUNNING)
3. **📸 Screenshot #10:** All three windows active

**ACTION:**
4. **Close Main Server window** (or Ctrl+C)
5. **Switch to Backup Server window immediately**
6. **📸 Screenshot #11:** Watch logs:
   ```
   No heartbeat detected. Promoting backup server to ACTIVE.
   Backup server (now ACTIVE) listening on port 5001...
   ```
7. **Title changes:** "Backup Server (Active)"

8. **Switch to Client window**
9. **Client still works!** Try downloading another file
10. **📸 Screenshot #12:** Successful download from backup

**Voice-over:**
- "Main server failure detected"
- "Backup server automatically promotes to active within 6 seconds"
- "Zero data loss, seamless failover"
- "Client continues operations without interruption"

---

### **Step 9: Metrics Dashboard** (Screenshot)
**Duration:** 20 seconds

Check logs for metrics summary:

**📸 Screenshot #13:** Metrics output:
```
=== Metrics Summary ===
Uptime: 5m 23s
Active Connections: 2
Total Requests: 47 (Success Rate: 97.87%)
Data Sent: 15.3 MB
Data Received: 0.2 MB
Avg Upload Speed: 2.85 MB/s
```

---

### **Step 10: Code Walkthrough** (Screenshots)
**Duration:** 1 minute

Open VS Code and show:

**📸 Screenshot #14:** Project structure
```
distributed-file-sharing/
├── main_server.py
├── backup_server.py
├── client.py
├── config.yaml        ← Configuration
├── database.py        ← Persistence
├── integrity.py       ← Checksums
├── logger_config.py   ← Logging
├── error_handler.py   ← Retry logic
├── metrics.py         ← Monitoring
└── tests/             ← Unit tests
```

**📸 Screenshot #15:** `integrity.py` - SHA256 implementation
**📸 Screenshot #16:** `config.yaml` - Configuration file
**📸 Screenshot #17:** Test results:
```bash
pytest tests/ -v
```

---

### **Step 11: GitHub Repository** (Screenshots)
**Duration:** 30 seconds

Open: https://github.com/bohradivyansh-maker/distributed-file-sharing

**📸 Screenshot #18:** GitHub landing page showing:
- README with architecture diagram
- Professional documentation
- Topics/tags
- License badge

**📸 Screenshot #19:** README.md rendered view

---

## 📊 Screenshot Organization

### **For LinkedIn Post** (Choose 3-4)
1. System architecture diagram (from README)
2. Download progress window
3. Failover demonstration (before/after)
4. Metrics summary

### **For Portfolio** (All)
- All screenshots organized in folders:
  ```
  screenshots/
  ├── 01_system_startup/
  ├── 02_file_upload/
  ├── 03_download_progress/
  ├── 04_failover_demo/
  ├── 05_logs_metrics/
  └── 06_code_github/
  ```

---

## 🎨 Editing Tips

### **Annotations to Add:**
- ✅ Arrows pointing to key features
- ✅ Text boxes explaining what's happening
- ✅ Highlight important log lines
- ✅ Circle/box around critical UI elements

### **Tools:**
- **Free:** Canva, Paint.NET, GIMP
- **Paid:** Adobe Photoshop, Snagit

### **Video Editing:**
- Add text overlays at each step
- Speed up long processes (2x)
- Add background music (low volume)
- Include intro/outro with contact info

---

## 🎯 LinkedIn Post Assets

### **Format Options:**

**Option 1: Image Carousel** (Recommended)
- 4-6 key screenshots in sequence
- Each with annotation
- Swipe-through story

**Option 2: Single Infographic**
- Collage of 4 screenshots
- Title at top
- Tech stack at bottom

**Option 3: Video (Best Engagement)**
- 60-90 second highlight reel
- Show startup → upload → download → failover
- Text overlays explaining each step

---

## ✅ Final Checklist

Before posting:
- [ ] All screenshots captured
- [ ] Screenshots annotated
- [ ] Video edited (if applicable)
- [ ] LinkedIn post written (use Gemini prompt from workflow)
- [ ] Hashtags added
- [ ] GitHub link verified
- [ ] Contact info visible

---

## 🚀 Ready to Record!

**Pro Tips:**
1. Close unnecessary applications
2. Set Windows theme to Dark (looks professional)
3. Increase font size in terminals for readability
4. Use fullscreen for cleaner screenshots
5. Practice the failover demo first!

**When to record:**
- Late evening (less distractions)
- After testing everything works
- When you have 30-60 minutes uninterrupted

---

**Good luck with your demo! You've got this! 🎉**
