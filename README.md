# 🚀 Distributed File Sharing System (MiniTorrent/EduShare)

A fault-tolerant distributed file sharing system built with Python, featuring primary-backup replication, automatic failover, chunked file transfer, and peer-to-peer capabilities.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [System Design](#system-design)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **✅ Fault-Tolerant Architecture**: Primary-backup server model with automatic failover
- **✅ Chunked File Transfer**: Efficient large file handling with 1MB chunks
- **✅ Data Integrity**: SHA256 hash verification for all file chunks
- **✅ Persistent Storage**: SQLite database for stateful file metadata
- **✅ Real-time Replication**: Automatic data synchronization between servers
- **✅ Heartbeat Monitoring**: Health checks with configurable timeout thresholds
- **✅ Peer-to-Peer Support**: Clients can seed files to other peers
- **✅ Multi-threaded**: Concurrent client handling for scalability

### Production-Ready Features
- **✅ Configuration Management**: YAML-based configuration for multi-environment deployment
- **✅ Structured Logging**: Comprehensive logging with rotation and configurable levels
- **✅ Error Handling**: Exponential backoff and retry logic for network operations
- **✅ Metrics & Monitoring**: Real-time tracking of performance metrics
- **✅ Connection Pooling**: Resource management for optimal performance
- **✅ GUI Interface**: User-friendly Tkinter-based interface with animations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Distributed System                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         Heartbeat          ┌──────────────┐
│  │              │◄────────────────────────────│              │
│  │  Main Server │                             │Backup Server │
│  │  (Primary)   │────────────────────────────►│  (Standby)   │
│  │              │      Replication            │              │
│  └──────┬───────┘                             └──────┬───────┘
│         │                                            │
│         │ File Requests                              │
│         │ (list, count, get)                         │
│         │                                            │
│         ├──────────┬──────────┬──────────┬──────────┤
│         ▼          ▼          ▼          ▼          ▼
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│    │Client 1│ │Client 2│ │Client 3│ │Client 4│ │Client N│
│    │(Seeder)│ │(Seeder)│ │(Seeder)│ │(Seeder)│ │(Seeder)│
│    └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
│         ▲          ▲          ▲          ▲          ▲
│         └──────────┴──────────┴──────────┴──────────┘
│              Peer-to-Peer File Sharing
│
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Main Server** (`main_server.py`)
   - Hosts and serves files to clients
   - Replicates data to backup server
   - Sends periodic heartbeats
   - Tracks download statistics

2. **Backup Server** (`backup_server.py`)
   - Receives replicated data
   - Monitors main server health
   - Promotes to active on failure
   - Serves clients seamlessly

3. **Client** (`client.py`)
   - Downloads files with progress tracking
   - Automatically fails over to backup
   - Acts as seeder for P2P
   - Search and browse capabilities

## 🛠️ Technology Stack

- **Language**: Python 3.7+
- **Networking**: TCP Sockets (Socket Programming)
- **Concurrency**: Threading (Multi-threaded I/O)
- **GUI**: Tkinter (Cross-platform)
- **Database**: SQLite (Embedded Database)
- **Configuration**: YAML
- **Security**: SHA256 (Cryptographic Hashing)
- **Logging**: Python logging module with rotation

## 📥 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/distributed-file-sharing.git
   cd distributed-file-sharing
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**
   - Edit `config.yaml` with your network settings
   - Update server IPs and ports as needed

4. **Create necessary directories**
   ```bash
   mkdir logs data downloads
   ```

## ⚙️ Configuration

Edit `config.yaml` to customize your deployment:

```yaml
server:
  main:
    ip: "192.168.1.10"      # Your main server IP
    port: 5001
  backup:
    ip: "192.168.1.11"      # Your backup server IP
    heartbeat_timeout: 6    # Seconds before failover

transfer:
  chunk_size: 1048576       # 1 MB chunks
  max_connections: 10

logging:
  level: "INFO"             # DEBUG, INFO, WARNING, ERROR
  log_to_file: true
```

## 🚀 Usage

### Starting the Main Server

```bash
python main_server.py
```

1. Click "Add Files" to select files to share
2. Click "Start Server" to begin accepting connections
3. Monitor logs for client activity

### Starting the Backup Server

```bash
python backup_server.py
```

- Runs in standby mode by default
- Automatically promotes to active if main server fails

### Running the Client

```bash
python client.py
```

1. Browse available files
2. Use search to filter files
3. Select files and click "Download Selected Files"
4. Choose save location
5. Monitor download progress

## 📂 Project Structure

```
distributed-file-sharing/
│
├── main_server.py          # Main server implementation
├── backup_server.py        # Backup server implementation
├── client.py               # Client application
│
├── config_loader.py        # Configuration management
├── logger_config.py        # Logging setup
├── database.py             # SQLite database operations
├── integrity.py            # Checksum verification
├── metrics.py              # Performance monitoring
├── error_handler.py        # Error handling & retry logic
│
├── config.yaml             # System configuration
├── requirements.txt        # Python dependencies
├── README.md               # This file
│
├── logs/                   # Log files directory
├── data/                   # Database files
└── downloads/              # Default download location
```

## 🎯 System Design

### File Transfer Protocol

```
CLIENT → SERVER

1. List Files:    "list" → "file1.txt:1024:5|file2.pdf:2048:10"
2. Chunk Count:   "count|file1.txt" → "10"
3. Get Chunk:     "get|file1.txt|0" → [binary chunk data]
```

### Replication Protocol

```
MAIN SERVER → BACKUP SERVER

1. File Replication:  "replicate|filename|filesize|chunk_count|checksums"
                      [chunk1_data][chunk2_data]...[chunkN_data]

2. Update:            "update|filename|download_count"
```

### Heartbeat Protocol

```
MAIN SERVER → BACKUP SERVER

Every 2 seconds:      "heartbeat"
```

### Failover Mechanism

1. Backup monitors last heartbeat timestamp
2. If no heartbeat for > 6 seconds, backup promotes to active
3. Backup binds to port 5001 and serves clients
4. Clients automatically retry and connect to backup

##  Future Enhancements

- [ ] End-to-end encryption (TLS/SSL)
- [ ] User authentication and authorization
- [ ] Multi-master replication
- [ ] Distributed hash table (DHT) for P2P
- [ ] Resume interrupted downloads
- [ ] Bandwidth throttling
- [ ] Docker containerization
- [ ] RESTful API
- [ ] Web-based UI
- [ ] Prometheus metrics export

## 🧪 Testing

Run unit tests:

```bash
pytest tests/ -v --cov=.
```

Check test coverage:

```bash
pytest --cov=. --cov-report=html
```

## 📊 Performance Metrics

The system tracks:
- Uptime
- Total bytes sent/received
- Active connections
- Request success rate
- Average upload/download speeds
- Per-file download statistics

View metrics in logs or GUI status area.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Divyansh Bohra**  
- GitHub: [@bohradivyansh-maker](https://github.com/bohradivyansh-maker)
- LinkedIn: [Divyansh Bohra](https://www.linkedin.com/in/divyansh-bohra-99414a349/)
- Email: bohradivyansh123@gmail.com

## 🙏 Acknowledgments

- Inspired by BitTorrent protocol
- Educational distributed systems project

---

**⭐ Star this repository if you find it helpful!**

