# backup_server.py

import socket
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Import new modules
from config_loader import config
from logger_config import get_logger
from database import db
from integrity import IntegrityChecker
from metrics import metrics
from error_handler import SafeSocket, handle_errors

# Initialize logger
logger = get_logger(__name__)

# Configuration from YAML
CHUNK_SIZE = config.get('transfer.chunk_size', 1024 * 1024)
SERVER_PORT = config.get('server.backup.port', 5001)
REPL_PORT = config.get('server.backup.replication_port', 5003)
HEARTBEAT_PORT = config.get('server.backup.heartbeat_port', 5004)
HEARTBEAT_TIMEOUT = config.get('server.backup.heartbeat_timeout', 6)

class BackupFileServerApp:
    def __init__(self, master):
        self.master = master
        master.title("MiniTorrent - Backup Server (Standby)")
        master.geometry("800x600")
        master.configure(bg="#f0f8ff")

        # Data storage for replicated files
        self.files = {}           # filename -> list of chunks
        self.file_sizes = {}      # filename -> file size in bytes
        self.download_counts = {} # filename -> download count
        self.file_checksums = {}  # filename -> list of chunk checksums

        self.last_heartbeat = time.time()
        self.active = False  # When main server fails, become active
        
        # Load existing files from database
        self.load_files_from_db()
        
        # Start metrics collection
        if config.get('metrics.enable', True):
            logger.info("Metrics collection enabled for backup server")

        self.log_area = scrolledtext.ScrolledText(master, height=20, width=90, font=("Courier", 10))
        self.log_area.pack(padx=10, pady=10)
        self.log("Backup server started in STANDBY mode.")

        # Start threads for replication, heartbeat, and monitoring.
        threading.Thread(target=self.listen_replication, daemon=True).start()
        threading.Thread(target=self.listen_heartbeat, daemon=True).start()
        threading.Thread(target=self.monitor_heartbeat, daemon=True).start()

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        logger.info(msg)  # Also log to file
    
    def load_files_from_db(self):
        """Load files from database on startup"""
        if not config.get('database.enable_persistence', True):
            return
        
        try:
            db_files = db.get_all_files()
            logger.info(f"Backup server loading {len(db_files)} files from database...")
            
            for file_info in db_files:
                filename = file_info['filename']
                self.file_sizes[filename] = file_info['file_size']
                self.download_counts[filename] = file_info['download_count']
                self.file_checksums[filename] = file_info['checksums'] or []
                logger.debug(f"Loaded metadata for: {filename}")
            
            logger.info("Backup server database load complete")
        except Exception as e:
            logger.error(f"Error loading files from database: {e}")

    def listen_replication(self):
        """
        Listens for replication messages from the main server on REPL_PORT.
        Protocol:
          For new file replication: "replicate|filename|filesize|chunk_count" then file chunks.
          For dynamic updates: "update|filename|download_count"
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", REPL_PORT))
        s.listen(5)
        self.log(f"Listening for replication on port {REPL_PORT}...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=self.handle_replication, args=(conn, addr), daemon=True).start()

    @handle_errors
    def handle_replication(self, conn, addr):
        try:
            header = conn.recv(1024).decode().strip()
            parts = header.split("|")
            
            if parts[0] == "replicate" and len(parts) >= 4:
                _, filename, filesize_str, chunk_count_str = parts[:4]
                filesize = int(filesize_str)
                chunk_count = int(chunk_count_str)
                
                # Extract checksums if provided
                checksums = []
                if len(parts) == 5:
                    checksums = parts[4].split(',')
                
                # Acknowledge header reception
                conn.sendall(b"ack")
                
                chunks = []
                received = 0
                while received < chunk_count:
                    chunk = conn.recv(CHUNK_SIZE)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    received += 1
                
                if received == chunk_count:
                    # Verify checksums if provided
                    if checksums and len(checksums) == chunk_count:
                        success, failed = IntegrityChecker.verify_chunks(chunks, checksums)
                        if not success:
                            logger.error(f"Checksum verification failed for {filename}, failed chunks: {failed}")
                            self.log(f"Checksum verification failed for {filename}")
                        else:
                            logger.info(f"Checksum verification passed for {filename}")
                    
                    self.files[filename] = chunks
                    self.file_sizes[filename] = filesize
                    self.download_counts[filename] = 0
                    self.file_checksums[filename] = checksums
                    
                    # Save to database
                    db.add_file(filename, filesize, chunk_count, checksums)
                    
                    self.log(f"Replicated file '{filename}' ({chunk_count} chunks, {filesize} bytes)")
                    logger.info(f"Successfully replicated {filename} with {chunk_count} chunks")
                else:
                    self.log(f"Replication incomplete for '{filename}' from {addr}.")
                    logger.error(f"Replication incomplete for '{filename}': received {received}/{chunk_count} chunks")
                    
            elif parts[0] == "update" and len(parts) == 3:
                # Handle dynamic update for download count
                _, filename, count_str = parts
                count = int(count_str)
                
                if filename in self.download_counts:
                    self.download_counts[filename] = count
                    db.update_download_count(filename, count)
                    logger.debug(f"Updated download count for '{filename}' to {count}")
                else:
                    logger.warning(f"Received update for unknown file '{filename}'")
            else:
                logger.warning(f"Invalid replication message from {addr}: {header}")
        except Exception as e:
            logger.error(f"Replication error: {e}")
        finally:
            conn.close()

    def listen_heartbeat(self):
        """
        Listens for heartbeat messages from the main server on HEARTBEAT_PORT.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", HEARTBEAT_PORT))
        s.listen(5)
        self.log(f"Listening for heartbeat on port {HEARTBEAT_PORT}...")
        while True:
            conn, addr = s.accept()
            try:
                data = conn.recv(1024)
                if data.strip() == b"heartbeat":
                    self.last_heartbeat = time.time()
                    # Uncomment the next line to log each heartbeat
                    # self.log("Heartbeat received.")
            except Exception as e:
                self.log(f"Heartbeat error: {e}")
            finally:
                conn.close()

    def monitor_heartbeat(self):
        """
        Monitors the last heartbeat timestamp.
        If the gap is too large, the backup server promotes itself to active.
        """
        while True:
            if (time.time() - self.last_heartbeat) > HEARTBEAT_TIMEOUT and not self.active:
                self.log("No heartbeat detected. Promoting backup server to ACTIVE.")
                self.active = True
                self.master.title("MiniTorrent - Backup Server (Active)")
                threading.Thread(target=self.run_server, daemon=True).start()
            time.sleep(2)

    def run_server(self):
        """
        Once promoted to active, starts accepting client connections on SERVER_PORT.
        Follows the same protocol as the main server.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("0.0.0.0", SERVER_PORT))
        except Exception as e:
            self.log(f"Error binding client port: {e}")
            return
        s.listen(5)
        self.log(f"Backup server (now ACTIVE) listening on port {SERVER_PORT}...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    @handle_errors
    def handle_client(self, conn, addr):
        metrics.increment_connections()
        start_time = time.time()
        
        try:
            request = conn.recv(1024).decode().strip()
            self.log(f"Request from {addr}: {request}")
            
            if request == "list":
                file_list = []
                for filename in self.files:
                    file_size = self.file_sizes.get(filename, 0)
                    download_count = self.download_counts.get(filename, 0)
                    file_list.append(f"{filename}:{file_size}:{download_count}")
                response = "|".join(file_list)
                conn.sendall(response.encode())
                metrics.record_bytes_sent(len(response))
                metrics.record_request(success=True)
                self.log(f"Sent file list to {addr}")
                
            elif request.startswith("count|"):
                _, filename = request.split("|", 1)
                if filename in self.files:
                    count = len(self.files[filename])
                    conn.sendall(str(count).encode())
                    metrics.record_request(success=True)
                    self.log(f"Sent chunk count for '{filename}' to {addr}")
                else:
                    conn.sendall(b"0")
                    metrics.record_request(success=False)
                    logger.warning(f"File '{filename}' not found")
                    
            elif request.startswith("get|"):
                parts = request.split("|")
                if len(parts) != 3:
                    logger.warning(f"Invalid request from {addr}: {request}")
                    metrics.record_request(success=False)
                    return
                _, filename, chunk_index = parts
                
                if filename in self.files and chunk_index.isdigit():
                    index = int(chunk_index)
                    if index == 0:
                        self.download_counts[filename] += 1
                        db.increment_download_count(filename)
                        logger.info(f"Incremented download count for '{filename}' to {self.download_counts[filename]}")
                    
                    chunks = self.files[filename]
                    if 0 <= index < len(chunks):
                        chunk_data = chunks[index]
                        conn.sendall(chunk_data)
                        metrics.record_bytes_sent(len(chunk_data))
                        metrics.record_request(success=True)
                        self.log(f"Sent chunk {index} of '{filename}' to {addr}")
                    else:
                        logger.warning(f"Invalid chunk index from {addr}")
                        metrics.record_request(success=False)
                else:
                    logger.warning(f"Invalid file or chunk index from {addr}")
                    metrics.record_request(success=False)
            else:
                logger.warning(f"Invalid request from {addr}: {request}")
                metrics.record_request(success=False)
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
            metrics.record_request(success=False)
        finally:
            conn.close()
            metrics.decrement_connections()
            duration = time.time() - start_time
            logger.debug(f"Connection from {addr} lasted {duration:.2f}s")

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Starting MiniTorrent Backup Server...")
    logger.info(f"Configuration loaded from config.yaml")
    logger.info(f"Server Port: {SERVER_PORT}")
    logger.info(f"Replication Port: {REPL_PORT}")
    logger.info(f"Heartbeat Port: {HEARTBEAT_PORT}")
    logger.info(f"Heartbeat Timeout: {HEARTBEAT_TIMEOUT}s")
    logger.info("="*50)
    
    root = tk.Tk()
    app = BackupFileServerApp(root)
    root.mainloop()