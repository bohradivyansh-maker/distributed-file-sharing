# 🚀 Quick Start Guide

Get the Distributed File Sharing System up and running in 5 minutes!

## Prerequisites

- Python 3.7+
- Git (for cloning)

## Installation

```bash
# 1. Clone the repository (or use your local copy)
cd "D:\Distributed Computing"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python -c "import yaml; print('✓ Dependencies installed!')"
```

## Configuration

1. **Edit `config.yaml`** with your network settings:

```yaml
server:
  main:
    ip: "YOUR_MAIN_SERVER_IP"    # e.g., "192.168.1.10"
  backup:
    ip: "YOUR_BACKUP_SERVER_IP"   # e.g., "192.168.1.11"
```

## Running the System

### Option 1: Local Testing (Same Machine)

**Terminal 1 - Main Server:**
```bash
python main_server.py
```
1. Click "Add Files" to select files to share
2. Click "Start Server"

**Terminal 2 - Backup Server:**
```bash
python backup_server.py
```
(Runs in standby mode)

**Terminal 3 - Client:**
```bash
python client.py
```
1. Browse and search files
2. Select files to download
3. Monitor progress

### Option 2: Distributed Setup (Multiple Machines)

**Machine 1 (Main Server):**
```bash
python main_server.py
```

**Machine 2 (Backup Server):**
```bash
python backup_server.py
```

**Machine 3+ (Clients):**
```bash
python client.py
```

## Testing Failover

1. Start main server and backup server
2. Add files on main server
3. Connect with a client and verify file list
4. **Stop the main server** (close window or Ctrl+C)
5. Wait 6 seconds
6. Backup server promotes to ACTIVE
7. Client can still download files!

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
start htmlcov/index.html
```

## Quick Feature Demo

### 1. File Sharing
- Main server: Add files → Start server
- Client: Refresh → Select files → Download

### 2. Data Integrity
- Files are chunked and checksummed
- Check logs for "Checksum verification passed"

### 3. Persistence
- Add files and exit server
- Restart server
- Metadata is restored from database (in `data/files.db`)

### 4. Metrics
- Watch logs for periodic metrics summary
- Shows uptime, bytes transferred, success rate

## Troubleshooting

### Port Already in Use
```bash
# Windows: Find process using port 5001
netstat -ano | findstr :5001

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Connection Refused
- Check firewall settings
- Verify IP addresses in config.yaml
- Ensure servers are running

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### PyYAML Not Found
```bash
pip install PyYAML
```

## What to Show Recruiters

1. **README.md** - Professional documentation
2. **Architecture diagram** - System design understanding
3. **config.yaml** - Configuration-driven approach
4. **tests/** - Unit testing culture
5. **Logs** - Structured logging (check `logs/app.log`)
6. **Database** - Persistent state (check `data/files.db`)

## Next Steps

1. ⭐ Star the repository
2. 📝 Customize README with your details
3. 🚀 Push to GitHub
4. 🎯 Add to your CV/portfolio
5. 💼 Share in interviews!

## GitHub Upload

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/distributed-file-sharing.git
git branch -M main
git push -u origin main
```

---

**Questions?** Check the main [README.md](README.md) for detailed documentation.

**Happy coding! 🎉**
