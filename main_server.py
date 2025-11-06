# main_server.py

import socket
import threading
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Import new modules
from config_loader import config
from logger_config import get_logger
from database import db
from integrity import IntegrityChecker
from metrics import metrics
from error_handler import SafeSocket, retry_with_backoff, handle_errors

# Initialize logger
logger = get_logger(__name__)

# Configuration from YAML
CHUNK_SIZE = config.get('transfer.chunk_size', 1024 * 1024)
SERVER_PORT = config.get('server.main.port', 5001)
REPL_PORT = config.get('server.main.replication_port', 5003)
HEARTBEAT_PORT = config.get('server.main.heartbeat_port', 5004)
BACKUP_IP = config.get('server.backup.ip', '10.160.67.237')

# GUI animation constants
RAINBOW_COLORS = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff", "#4b0082", "#8b00ff"]
BANNER_MESSAGES = [
    "Welcome to MiniTorrent Server!",
    "You can add files even while running.",
    "Stay tuned for new file updates!",
    "Serving your shared files in real time."
]

class MainFileServerApp:
    def __init__(self, master):
        self.master = master
        master.title("MiniTorrent - Main Server")
        master.geometry("800x600")
        master.configure(bg="#f0f8ff")

        # Data dictionaries (with database persistence)
        self.files = {}            # filename -> list of chunks
        self.file_sizes = {}       # filename -> total file size (bytes)
        self.download_counts = {}  # filename -> download counter
        self.file_checksums = {}   # filename -> list of chunk checksums
        
        # Load existing files from database
        self.load_files_from_db()
        
        # Start metrics collection
        if config.get('metrics.enable', True):
            metrics.start_periodic_logging()
            logger.info("Metrics collection started")

        # --- Animated Status Label ---
        self.status_label = tk.Label(master, text="SERVER NOT RUNNING", font=("Helvetica", 18, "bold"), bg="#f0f8ff")
        self.status_label.pack(pady=10)
        self.server_started = False
        self.animate_status_label(0)

        # --- Animated Banner ---
        self.banner_label = tk.Label(master, text="", font=("Helvetica", 14, "bold"), bg="#f0f8ff")
        self.banner_label.pack(side=tk.BOTTOM, pady=10)
        self.banner_index = 0
        self.animate_banner()

        # --- Buttons ---
        self.select_button = tk.Button(master, text="Add Files", font=("Helvetica", 12, "bold"),
                                       command=self.select_files, bg="#4CAF50", fg="white")
        self.select_button.pack(pady=5)

        self.start_button = tk.Button(master, text="Start Server", font=("Helvetica", 12, "bold"),
                                      command=self.start_server, bg="#2196F3", fg="white")
        self.start_button.pack(pady=5)

        # --- Listbox to show files ---
        self.file_listbox = tk.Listbox(master, height=6, font=("Helvetica", 12))
        self.file_listbox.pack(padx=10, pady=10, fill=tk.X)

        # --- Log Area ---
        self.log_area = scrolledtext.ScrolledText(master, height=15, width=90, font=("Courier", 10))
        self.log_area.pack(padx=10, pady=10)
        self.animate_log_bg()

        # Start heartbeat thread (to send heartbeat messages to backup server)
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

    def animate_status_label(self, idx):
        color = RAINBOW_COLORS[idx % len(RAINBOW_COLORS)]
        text = "SERVER RUNNING" if self.server_started else "SERVER NOT RUNNING"
        self.status_label.config(text=text, fg=color)
        self.master.after(300, lambda: self.animate_status_label(idx + 1))

    def animate_banner(self):
        message = BANNER_MESSAGES[self.banner_index % len(BANNER_MESSAGES)]
        self.banner_label.config(text=message, fg=RAINBOW_COLORS[self.banner_index % len(RAINBOW_COLORS)])
        self.banner_index += 1
        self.master.after(2500, self.animate_banner)

    def animate_log_bg(self):
        current = self.log_area.cget("bg")
        new_color = "#f0f8ff" if current == "#e6f2ff" else "#e6f2ff"
        self.log_area.config(bg=new_color)
        self.master.after(1500, self.animate_log_bg)

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
            logger.info(f"Loading {len(db_files)} files from database...")
            
            for file_info in db_files:
                filename = file_info['filename']
                self.file_sizes[filename] = file_info['file_size']
                self.download_counts[filename] = file_info['download_count']
                self.file_checksums[filename] = file_info['checksums'] or []
                
                # Note: Actual chunk data is not persisted, only metadata
                # Files need to be re-added manually or implement file storage
                logger.debug(f"Loaded metadata for: {filename}")
            
            logger.info("Database load complete")
        except Exception as e:
            logger.error(f"Error loading files from database: {e}")

    def select_files(self):
        filenames = filedialog.askopenfilenames()
        for filepath in filenames:
            filename = os.path.basename(filepath)
            if filename not in self.files:
                chunks = self.split_file(filepath)
                if not chunks:
                    continue
                    
                self.files[filename] = chunks
                self.file_sizes[filename] = os.path.getsize(filepath)
                self.download_counts[filename] = 0
                
                # Calculate checksums for data integrity
                checksums = IntegrityChecker.create_chunk_manifest(chunks)
                self.file_checksums[filename] = checksums
                logger.info(f"Generated {len(checksums)} checksums for {filename}")
                
                # Save to database
                db.add_file(filename, self.file_sizes[filename], len(chunks), checksums)

                display_text = f"{filename} ({len(chunks)} chunks, {self.file_sizes[filename]} bytes)"
                self.file_listbox.insert(tk.END, display_text)
                self.log(f"File Added: {display_text}")
                self.show_file_added_banner(filename)

                # Replicate file to backup server
                threading.Thread(target=self.replicate_file, args=(filename, filepath, chunks, checksums), daemon=True).start()
            else:
                self.log(f"{filename} is already added.")

    def split_file(self, filepath):
        chunks = []
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    chunks.append(chunk)
            logger.info(f"Split {filepath} into {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            messagebox.showerror("Error", f"Failed to read file: {e}")
        return chunks

    def show_file_added_banner(self, filename):
        banner = tk.Label(self.master, text=f"File '{filename}' added!", font=("Helvetica", 14, "bold"),
                          fg="white", bg="#f44336")
        banner.place(relx=1.0, rely=0.2, anchor="e")
        def slide_left(pos):
            if pos > 0.5:
                banner.place_configure(relx=pos)
                self.master.after(30, lambda: slide_left(pos - 0.02))
            else:
                self.fade_out(banner, 100)
        slide_left(1.0)

    def fade_out(self, widget, alpha):
        if alpha <= 0:
            widget.destroy()
        else:
            hex_alpha = format(alpha, '02x')
            widget.config(bg="#" + hex_alpha*3)
            self.master.after(50, lambda: self.fade_out(widget, alpha - 10))

    def start_server(self):
        self.server_started = True
        threading.Thread(target=self.run_server, daemon=True).start()
        self.log(f"Server started on port {SERVER_PORT}...")

    def run_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", SERVER_PORT))
        s.listen(5)
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
                return
                
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
                    self.log(f"File '{filename}' not found")
                return
                
            elif request.startswith("get|"):
                parts = request.split("|")
                if len(parts) != 3:
                    logger.warning(f"Invalid request from {addr}: {request}")
                    metrics.record_request(success=False)
                    return
                _, filename, chunk_index = parts
                
                if filename in self.files and chunk_index.isdigit():
                    index = int(chunk_index)
                    
                    # Increment download count on first chunk
                    if index == 0:
                        self.download_counts[filename] += 1
                        db.increment_download_count(filename)
                        threading.Thread(target=self.replicate_update, args=(filename, self.download_counts[filename]), daemon=True).start()
                        self.log(f"Incremented download count for '{filename}' to {self.download_counts[filename]}")
                    
                    chunks = self.files[filename]
                    if 0 <= index < len(chunks):
                        chunk_data = chunks[index]
                        conn.sendall(chunk_data)
                        metrics.record_bytes_sent(len(chunk_data))
                        metrics.record_request(success=True)
                        self.log(f"Sent chunk {index} of '{filename}' to {addr}")
                    else:
                        logger.warning(f"Invalid chunk index {index} from {addr}")
                        metrics.record_request(success=False)
                else:
                    logger.warning(f"Invalid file or chunk index from {addr}")
                    metrics.record_request(success=False)
                return
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

    @retry_with_backoff(max_attempts=3)
    def replicate_file(self, filename, filepath, chunks, checksums):
        """
        Connects to the backup server (via REPL_PORT) and sends the replication data.
        Protocol:
          First send "replicate|filename|filesize|chunk_count"
          Then send each chunk in order.
        """
        try:
            filesize = os.path.getsize(filepath)
            chunk_count = len(chunks)
            
            with SafeSocket() as sock:
                sock.connect(BACKUP_IP, REPL_PORT)
                header = f"replicate|{filename}|{filesize}|{chunk_count}|{','.join(checksums)}"
                sock.send(header)
                ack = sock.receive(1024)  # optional acknowledgment
                
                for i, chunk in enumerate(chunks):
                    sock.send(chunk)
                    logger.debug(f"Sent chunk {i+1}/{chunk_count} to backup")
                
            self.log(f"Replicated file '{filename}' to backup server.")
            logger.info(f"Successfully replicated {filename} with {chunk_count} chunks")
        except Exception as e:
            logger.error(f"Replication failed for '{filename}': {e}")
            self.log(f"Replication failed for '{filename}': {e}")

    @retry_with_backoff(max_attempts=3)
    def replicate_update(self, filename, download_count):
        """
        Connects to the backup server (via REPL_PORT) and sends an update message
        to synchronize the download count.
        Protocol: "update|filename|download_count"
        """
        try:
            with SafeSocket() as sock:
                sock.connect(BACKUP_IP, REPL_PORT)
                update_msg = f"update|{filename}|{download_count}"
                sock.send(update_msg)
                # Optionally, wait for an acknowledgment (not implemented here)
            logger.debug(f"Replicated update for '{filename}': download count = {download_count}")
        except Exception as e:
            logger.error(f"Update replication failed for '{filename}': {e}")

    def send_heartbeat(self):
        """
        Send heartbeat messages to the backup server every 2 seconds.
        """
        while True:
            try:
                with SafeSocket(timeout=1) as hb:
                    hb.connect(BACKUP_IP, HEARTBEAT_PORT)
                    hb.send(b"heartbeat")
                # Uncomment below to log heartbeat activity
                # logger.debug("Heartbeat sent to backup.")
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Starting MiniTorrent Main Server...")
    logger.info(f"Configuration loaded from config.yaml")
    logger.info(f"Server Port: {SERVER_PORT}")
    logger.info(f"Replication Port: {REPL_PORT}")
    logger.info(f"Heartbeat Port: {HEARTBEAT_PORT}")
    logger.info(f"Backup Server IP: {BACKUP_IP}")
    logger.info("="*50)
    
    root = tk.Tk()
    app = MainFileServerApp(root)
    root.mainloop()


