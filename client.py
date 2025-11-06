# client.py

import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import time
import os

# Import new modules
from config_loader import config
from logger_config import get_logger
from integrity import IntegrityChecker
from metrics import metrics
from error_handler import SafeSocket, retry_with_backoff, RetryableError

# Initialize logger
logger = get_logger(__name__)

# Configuration from YAML
SERVER_PORT = config.get('server.main.port', 5001)
CHUNK_SIZE = config.get('transfer.chunk_size', 1024 * 1024)
SEEDER_PORT = config.get('client.seeder_port', 6000)

# Server IPs
MAIN_SERVER_IP = config.get('server.main.ip', '10.160.68.45')
BACKUP_SERVER_IP = config.get('server.backup.ip', '10.160.67.237')

@retry_with_backoff(max_attempts=3)
def fetch_file_list(server_ip):
    try:
        with SafeSocket() as sock:
            sock.connect(server_ip, SERVER_PORT)
            sock.send(b"list")
            data = sock.receive_all().decode()
            files = []
            if data:
                entries = data.split("|")
                for entry in entries:
                    parts = entry.split(":")
                    if len(parts) == 3:
                        files.append({"name": parts[0], "size": int(parts[1]), "downloads": int(parts[2])})
            logger.info(f"Fetched {len(files)} files from {server_ip}")
            return files
    except Exception as e:
        logger.error(f"Could not fetch file list from {server_ip}: {e}")
        messagebox.showerror("Error", f"Could not fetch file list from {server_ip}: {e}")
        return []

@retry_with_backoff(max_attempts=3)
def get_chunk_count(server_ip, filename):
    try:
        with SafeSocket() as sock:
            sock.connect(server_ip, SERVER_PORT)
            sock.send(f"count|{filename}")
            count = sock.receive(1024).decode()
            logger.debug(f"Chunk count for {filename}: {count}")
            return int(count)
    except Exception as e:
        logger.error(f"Could not get chunk count from {server_ip}: {e}")
        messagebox.showerror("Error", f"Could not get chunk count from {server_ip}: {e}")
        return 0

@retry_with_backoff(max_attempts=3)
def request_chunk(server_ip, filename, chunk_index):
    try:
        with SafeSocket() as sock:
            sock.connect(server_ip, SERVER_PORT)
            sock.send(f"get|{filename}|{chunk_index}")
            data = sock.receive_all()
            logger.debug(f"Downloaded chunk {chunk_index} of {filename}, size: {len(data)} bytes")
            metrics.record_bytes_received(len(data))
            return data
    except Exception as e:
        logger.error(f"Error downloading chunk {chunk_index} from {server_ip}: {e}")
        messagebox.showerror("Error", f"Error downloading chunk {chunk_index} from {server_ip}: {e}")
        return None

class EduShareClientApp:
    def __init__(self, master):
        self.master = master
        master.title("EduShare File Sharing Client")
        master.geometry("900x700")
        master.configure(bg="#f9f9ff")

        self.header_label = tk.Label(master, text="Welcome to EduShare – Your Academic File Hub!",
                                     font=("Helvetica", 20, "bold"), bg="#f9f9ff")
        self.header_label.pack(pady=15)
        self.bounce_header(0, 0)

        # Ask for server choice: primary or backup? (Client will try primary then fallback)
        self.server_ip = MAIN_SERVER_IP

        # File lists
        self.full_file_list = []
        self.filtered_files = []

        # --- Search Frame ---
        self.search_frame = tk.Frame(master, bg="#f9f9ff")
        self.search_frame.pack(fill="both", expand=True)

        search_bar_frame = tk.Frame(self.search_frame, bg="#f9f9ff")
        search_bar_frame.pack(pady=5)
        tk.Label(search_bar_frame, text="Search Files:", font=("Helvetica", 12), bg="#f9f9ff").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_bar_frame, textvariable=self.search_var, width=45)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_bar_frame, text="Search", command=self.on_search, bg="#673ab7", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(search_bar_frame, text="Refresh", command=self.refresh_file_list, bg="#009688", fg="white").pack(side=tk.LEFT, padx=5)

        columns = ("Name", "Size (bytes)", "Downloads")
        self.file_tree = ttk.Treeview(self.search_frame, columns=columns, show="headings", selectmode="extended", height=10)
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=250)
        self.file_tree.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Button(self.search_frame, text="Download Selected Files", command=self.on_download,
                  bg="#3f51b5", fg="white", font=("Helvetica", 12, "bold")).pack(pady=10)

        # Start a seeder thread so that once files are downloaded, this client can serve chunks to peers.
        threading.Thread(target=self.start_seeder, daemon=True).start()

        # Fetch file list from server (try primary; fallback to backup if needed)
        self.refresh_file_list()

    def bounce_header(self, delta, direction):
        y = self.header_label.winfo_y()
        new_y = y + direction * 2
        if new_y < 10 or new_y > 50:
            direction = -direction
        self.header_label.place(x=10, y=new_y)
        self.master.after(50, lambda: self.bounce_header(delta+1, direction))
        self.animate_header_color(delta)

    def animate_header_color(self, idx):
        colors = ["#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3", "#03a9f4"]
        self.header_label.config(fg=colors[idx % len(colors)])

    def refresh_file_list(self):
        # Try main server first
        self.full_file_list = fetch_file_list(MAIN_SERVER_IP)
        if not self.full_file_list:
            # Try backup server if main server fails
            self.full_file_list = fetch_file_list(BACKUP_SERVER_IP)
            self.server_ip = BACKUP_SERVER_IP
        else:
            self.server_ip = MAIN_SERVER_IP

        self.filtered_files = self.full_file_list
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        for f in self.filtered_files:
            self.file_tree.insert("", tk.END, values=(f["name"], f["size"], f["downloads"]))

    def on_search(self):
        query = self.search_var.get().strip().lower()
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.filtered_files = (self.full_file_list if not query else
                               [f for f in self.full_file_list if query in f["name"].lower()])
        for f in self.filtered_files:
            self.file_tree.insert("", tk.END, values=(f["name"], f["size"], f["downloads"]))

    def on_download(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showerror("Error", "No file selected.")
            return
        selected_files = []
        for item in selected:
            info = self.file_tree.item(item)["values"]
            selected_files.append({"name": info[0], "size": info[1], "downloads": info[2]})
        self.download_sequence(selected_files, 0)

    def download_sequence(self, files, index):
        if index >= len(files):
            messagebox.showinfo("Info", "All selected files have been downloaded.")
            return
        file = files[index]
        save_path = filedialog.asksaveasfilename(initialfile=file["name"])
        if not save_path:
            self.master.after(0, lambda: self.download_sequence(files, index+1))
            return
        self.start_download_window(file, save_path, lambda: self.download_sequence(files, index+1))

    def start_download_window(self, file, save_path, callback):
        win = tk.Toplevel(self.master)
        win.title(f"Downloading: {file['name']}")
        win.geometry("600x300")
        win.configure(bg="#ffffff")

        status_label = tk.Label(win, text=f"Downloading '{file['name']}'...", font=("Helvetica", 14), bg="#ffffff")
        status_label.pack(pady=10)

        progress = ttk.Progressbar(win, orient="horizontal", length=500, mode="determinate")
        progress.pack(pady=10)
        percent_label = tk.Label(win, text="0%", font=("Helvetica", 12), bg="#ffffff")
        percent_label.pack(pady=5)

        # Circular progress indicator (optional)
        circle_canvas = tk.Canvas(win, width=100, height=100, bg="#ffffff", highlightthickness=0)
        circle_canvas.pack(pady=10)
        circle_canvas.create_oval(10, 10, 90, 90, outline="#cccccc", width=8)
        progress_arc = circle_canvas.create_arc(10, 10, 90, 90, start=90, extent=0, outline="#3f51b5", width=8, style="arc")

        def update_circle(percent):
            extent = (percent/100) * -360
            circle_canvas.itemconfig(progress_arc, extent=extent)

        def download_current():
            # Get chunk count from the active server
            chunk_count = get_chunk_count(self.server_ip, file["name"])
            if chunk_count <= 0:
                win.after(0, lambda: messagebox.showerror("Error", f"No chunks available for {file['name']}"))
                win.after(0, win.destroy)
                callback()
                return
            bytes_downloaded = 0
            total_bytes = chunk_count * CHUNK_SIZE
            try:
                with open(save_path, "wb") as f_out:
                    for i in range(chunk_count):
                        chunk = request_chunk(self.server_ip, file["name"], i)
                        if chunk:
                            f_out.write(chunk)
                            bytes_downloaded += len(chunk)
                            percent = int((bytes_downloaded / total_bytes) * 100)
                            if percent > 100:
                                percent = 100
                            win.after(0, lambda p=percent: percent_label.config(text=f"{p}%"))
                            win.after(0, lambda: progress.configure(value=bytes_downloaded))
                            win.after(0, lambda p=percent: update_circle(p))
                        else:
                            win.after(0, lambda: messagebox.showerror("Error", f"Failed at chunk {i}"))
                            win.after(0, win.destroy)
                            callback()
                            return
            except Exception as e:
                win.after(0, lambda: messagebox.showerror("Error", f"Download error: {e}"))
                win.after(0, win.destroy)
                callback()
                return

            win.after(0, lambda: progress.configure(value=total_bytes))
            win.after(0, lambda: percent_label.config(text="100%"))
            win.after(0, lambda: status_label.config(text="Download complete!"))
            win.after(3000, lambda: (win.destroy(), callback()))
            # After download, add file to seeder list
            self.add_seeder_file(file["name"], save_path)

        threading.Thread(target=download_current, daemon=True).start()

    def add_seeder_file(self, filename, filepath):
        """
        Once download is complete, add the file to a local seeder directory,
        so that other peers (clients) can request chunks from this client.
        """
        # For demonstration, we simply store the path in a dictionary.
        # In a full system, you could copy the file to a central "seed" folder.
        if not hasattr(self, 'seed_files'):
            self.seed_files = {}
        self.seed_files[filename] = filepath
        print(f"File '{filename}' registered for seeding.")

    def start_seeder(self):
        """
        Start a simple server thread that listens on SEEDER_PORT for incoming requests
        from peer clients asking for file chunks.
        Protocol is similar: "get|filename|chunk_index"
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("0.0.0.0", SEEDER_PORT))
        except Exception as e:
            print(f"Seeder error binding to port: {e}")
            return
        s.listen(5)
        print(f"Peer seeder listening on port {SEEDER_PORT}...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=self.handle_peer_request, args=(conn, addr), daemon=True).start()

    def handle_peer_request(self, conn, addr):
        try:
            request = conn.recv(1024).decode().strip()
            # Expecting request "get|filename|chunk_index"
            parts = request.split("|")
            if len(parts) != 3 or parts[0] != "get":
                conn.close()
                return
            _, filename, chunk_index = parts
            if filename not in getattr(self, 'seed_files', {}):
                conn.sendall(b"")
                conn.close()
                return
            filepath = self.seed_files[filename]
            try:
                chunk_index = int(chunk_index)
            except ValueError:
                conn.sendall(b"")
                conn.close()
                return
            # Calculate offset in file and send the chunk
            with open(filepath, "rb") as f:
                f.seek(chunk_index * CHUNK_SIZE)
                data = f.read(CHUNK_SIZE)
                conn.sendall(data)
            print(f"Served chunk {chunk_index} of '{filename}' to peer {addr}")
        except Exception as e:
            print(f"Error serving peer request: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = EduShareClientApp(root)
    root.mainloop()