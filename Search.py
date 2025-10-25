import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import os
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import queue


class OptimizedFileSearchGUI(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Fast File Search")
        self.geometry("1000x700")
        
        self.search_cancelled = False
        self.result_queue = queue.Queue()
        
        
        self.create_widgets()
        self.search_entry.bind('<Return>', lambda e: self.search())

        self.process_results()
        
    def create_widgets(self):
     
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=X, side=TOP)
        
        ttk.Label(top_frame, text="Search:", font=("", 11, "bold")).pack(side=LEFT, padx=(0, 10))
        
        self.search_entry = ttk.Entry(top_frame, font=("", 11))
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.search_entry.focus()
        
        self.search_btn = ttk.Button(
            top_frame, 
            text="Search", 
            command=self.search,
            bootstyle=PRIMARY,
            width=12
        )
        self.search_btn.pack(side=LEFT, padx=(0, 5))
        
        self.cancel_btn = ttk.Button(
            top_frame,
            text="Cancel",
            command=self.cancel_search,
            bootstyle=DANGER,
            width=10,
            state=DISABLED
        )
        self.cancel_btn.pack(side=LEFT, padx=(0, 5))
        
        self.clear_btn = ttk.Button(
            top_frame,
            text="Clear",
            command=self.clear_search,
            bootstyle=SECONDARY,
            width=10
        )
        self.clear_btn.pack(side=LEFT)
        
        location_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        location_frame.pack(fill=X, side=TOP)
        
        ttk.Label(location_frame, text="Search in:").pack(side=LEFT, padx=(0, 10))
        
        self.location_var = ttk.StringVar(value=str(Path.home()))
        self.location_entry = ttk.Entry(location_frame, textvariable=self.location_var, font=("", 10))
        self.location_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        ttk.Button(
            location_frame,
            text="Browse",
            command=self.browse_location,
            width=10
        ).pack(side=LEFT, padx=(0, 10))
        
        # Quick location buttons
        ttk.Button(
            location_frame,
            text="Home",
            command=lambda: self.location_var.set(str(Path.home())),
            width=8
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            location_frame,
            text="Desktop",
            command=lambda: self.location_var.set(str(Path.home() / "Desktop")),
            width=8
        ).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(
            location_frame,
            text="Downloads",
            command=lambda: self.location_var.set(str(Path.home() / "Downloads")),
            width=10
        ).pack(side=LEFT)
        
        # Filter frame
        filter_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        filter_frame.pack(fill=X, side=TOP)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=LEFT, padx=(0, 10))
        
        self.filter_var = ttk.StringVar(value="All Files")
        filters = ["All Files", "Documents", "Images", "Videos", "Audio", "Code", "Archives", "Folders Only"]
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=filters,
            state="readonly",
            width=15
        )
        self.filter_combo.pack(side=LEFT, padx=(0, 20))
        
        # Match case checkbox
        self.match_case = ttk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame,
            text="Match Case",
            variable=self.match_case,
            bootstyle="primary-round-toggle"
        ).pack(side=LEFT, padx=(0, 20))
        
        # Search subfolders
        self.search_subfolders = ttk.BooleanVar(value=True)
        ttk.Checkbutton(
            filter_frame,
            text="Subfolders",
            variable=self.search_subfolders,
            bootstyle="primary-round-toggle"
        ).pack(side=LEFT, padx=(0, 20))
        
        # Max results
        ttk.Label(filter_frame, text="Max:").pack(side=LEFT, padx=(0, 5))
        self.max_results = ttk.IntVar(value=500)
        max_spin = ttk.Spinbox(
            filter_frame,
            from_=100,
            to=5000,
            increment=100,
            textvariable=self.max_results,
            width=8
        )
        max_spin.pack(side=LEFT)
        
        # Results frame
        results_frame = ttk.Frame(self, padding=10)
        results_frame.pack(fill=BOTH, expand=True)
        
        # Treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(results_frame, orient=VERTICAL)
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        
        tree_scroll_x = ttk.Scrollbar(results_frame, orient=HORIZONTAL)
        tree_scroll_x.pack(side=BOTTOM, fill=X)
        
        self.tree = ttk.Treeview(
            results_frame,
            columns=("name", "path", "size", "modified"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse"
        )
        
        # Sortable columns
        self.tree.heading("name", text="Name ▼", anchor=W, command=lambda: self.sort_column("name"))
        self.tree.heading("path", text="Path", anchor=W, command=lambda: self.sort_column("path"))
        self.tree.heading("size", text="Size", anchor=E, command=lambda: self.sort_column("size"))
        self.tree.heading("modified", text="Modified", anchor=W, command=lambda: self.sort_column("modified"))
        
        self.tree.column("name", width=250, anchor=W)
        self.tree.column("path", width=350, anchor=W)
        self.tree.column("size", width=100, anchor=E)
        self.tree.column("modified", width=150, anchor=W)
        
        self.tree.pack(fill=BOTH, expand=True)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Double-click to open file
        self.tree.bind('<Double-Button-1>', self.open_file)
        
        # Right-click context menu
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            bootstyle="primary-striped"
        )
        
        # Status bar
        status_frame = ttk.Frame(self, padding=5)
        status_frame.pack(fill=X, side=BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=("", 9)
        )
        self.status_label.pack(side=LEFT)
        
        self.result_count_label = ttk.Label(
            status_frame,
            text="",
            font=("", 9)
        )
        self.result_count_label.pack(side=RIGHT)
    
    def browse_location(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(initialdir=self.location_var.get())
        if directory:
            self.location_var.set(directory)
    
    def search(self):
        query = self.search_entry.get().strip()
        if not query:
            Messagebox.show_warning("Please enter a search term", "No Search Term")
            return
        
        location = Path(self.location_var.get())
        if not location.exists():
            Messagebox.show_error(f"Location does not exist: {location}", "Invalid Location")
            return
        
        self.search_cancelled = False
        self.status_label.config(text="Searching...")
        self.search_btn.config(state=DISABLED)
        self.cancel_btn.config(state=NORMAL)
        self.tree.delete(*self.tree.get_children())
        
        # Show progress bar
        self.progress.pack(fill=X, padx=10, pady=(0, 5), before=self.children['!frame4'])
        self.progress.start(10)
        
        # Run search in background thread
        thread = threading.Thread(target=self.perform_optimized_search, args=(query, location))
        thread.daemon = True
        thread.start()
    
    def cancel_search(self):
        self.search_cancelled = True
        self.status_label.config(text="Cancelling...")
        self.cancel_btn.config(state=DISABLED)
    
    def perform_optimized_search(self, query, location):
        """Optimized search using pathlib with early termination"""
        try:
            match_case = self.match_case.get()
            search_subfolders = self.search_subfolders.get()
            max_results = self.max_results.get()
            filter_type = self.filter_var.get()
            
            # Prepare search query
            search_query = query if match_case else query.lower()
            
            # File extension filters (as sets for O(1) lookup)
            filter_exts = {
                "Documents": {'.doc', '.docx', '.pdf', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.rtf'},
                "Images": {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'},
                "Videos": {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'},
                "Audio": {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus'},
                "Code": {'.py', '.java', '.cpp', '.c', '.h', '.js', '.html', '.css', '.php', '.go', '.rs'},
                "Archives": {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}
            }
            
            allowed_exts = filter_exts.get(filter_type, None)
            
            count = 0
            results = []
            
            # Use pathlib for faster iteration
            if search_subfolders:
                # Recursive search
                pattern = "**/*" if filter_type != "Folders Only" else "**/"
                iterator = location.glob(pattern)
            else:
                # Non-recursive search
                iterator = location.iterdir()
            
            # Process files
            for path in iterator:
                if self.search_cancelled or count >= max_results:
                    break
                
                try:
                    name = path.name
                    
                    # Skip hidden files/folders for speed
                    if name.startswith('.'):
                        continue
                    
                    # Apply folder filter
                    is_dir = path.is_dir()
                    if filter_type == "Folders Only" and not is_dir:
                        continue
                    if filter_type == "Folders Only" and is_dir:
                        pass  # Include folders
                    elif is_dir and filter_type != "All Files":
                        continue  # Skip folders for specific file type filters
                    
                    # Match case sensitivity
                    name_to_check = name if match_case else name.lower()
                    
                    # Check if query matches (optimized with 'in' operator)
                    if search_query not in name_to_check:
                        continue
                    
                    # Check file type filter (only for files)
                    if not is_dir and allowed_exts is not None:
                        if path.suffix.lower() not in allowed_exts:
                            continue
                    
                    # Get file info (lazy evaluation)
                    try:
                        if is_dir:
                            size_str = "<DIR>"
                            size_bytes = 0
                        else:
                            stat = path.stat()
                            size_bytes = stat.st_size
                            size_str = self.format_size(size_bytes)
                        
                        modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    except (PermissionError, OSError):
                        size_str = ""
                        size_bytes = 0
                        modified = ""
                    
                    results.append((name, str(path.parent), size_str, modified, str(path), size_bytes))
                    count += 1
                    
                    # Batch update UI every 25 results
                    if count % 25 == 0:
                        batch = results[-25:]
                        self.result_queue.put(('batch', batch))
                        self.after(0, self.status_label.config, {"text": f"Found {count} results..."})
                
                except (PermissionError, OSError):
                    continue
            
            # Send remaining results
            if results and count % 25 != 0:
                remaining = results[-(count % 25):]
                self.result_queue.put(('batch', remaining))
            
            # Signal completion
            self.result_queue.put(('done', count))
            
        except Exception as e:
            self.result_queue.put(('error', str(e)))
    
    def process_results(self):
        """Process results from queue without blocking UI"""
        try:
            while True:
                msg_type, data = self.result_queue.get_nowait()
                
                if msg_type == 'batch':
                    # Insert batch of results
                    for name, path, size, modified, full_path, size_bytes in data:
                        self.tree.insert(
                            "",
                            END,
                            values=(name, path, size, modified),
                            tags=(full_path, size_bytes)
                        )
                
                elif msg_type == 'done':
                    count = data
                    self.finish_search(count)
                
                elif msg_type == 'error':
                    self.show_error(f"Search error: {data}")
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(50, self.process_results)
    
    def finish_search(self, count):
        # Stop progress bar
        self.progress.stop()
        self.progress.pack_forget()
        
        result_text = f"Found {count} results"
        if count >= self.max_results.get():
            result_text += " (limit reached)"
        
        self.result_count_label.config(text=result_text)
        self.status_label.config(text="Search complete")
        self.search_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
    
    def sort_column(self, col):
        """Sort treeview by column"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Sort numerically for size column
        if col == "size":
            items = sorted(items, key=lambda x: self.tree.item(x[1])['tags'][1] if len(self.tree.item(x[1])['tags']) > 1 else 0, reverse=True)
        else:
            items.sort(reverse=False)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update heading
        self.tree.heading(col, text=f"{col.title()} ▼")
    
    def clear_search(self):
        self.search_entry.delete(0, END)
        self.tree.delete(*self.tree.get_children())
        self.result_count_label.config(text="")
        self.status_label.config(text="Ready")
        self.search_entry.focus()
    
    def open_file(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        if not item['tags']:
            return
            
        full_path = item['tags'][0]
        
        try:
            os.startfile(full_path)
        except Exception as e:
            Messagebox.show_error(f"Cannot open: {str(e)}", "Error")
    
    def show_context_menu(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        if not item['tags']:
            return
            
        full_path = item['tags'][0]
        
        menu = ttk.Menu(self, tearoff=0)
        menu.add_command(label="Open", command=lambda: self.open_file(event))
        menu.add_command(
            label="Open Folder Location",
            command=lambda: self.open_folder_location(full_path)
        )
        menu.add_separator()
        menu.add_command(
            label="Copy Path",
            command=lambda: self.copy_to_clipboard(full_path)
        )
        menu.add_command(
            label="Copy Name",
            command=lambda: self.copy_to_clipboard(os.path.basename(full_path))
        )
        
        menu.post(event.x_root, event.y_root)
    
    def open_folder_location(self, path):
        try:
            subprocess.Popen(f'explorer /select,"{path}"')
        except Exception as e:
            Messagebox.show_error(f"Cannot open folder: {str(e)}", "Error")
    
    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_label.config(text="Copied to clipboard")
    
    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def show_error(self, message):
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text=message)
        self.search_btn.config(state=NORMAL)
        self.cancel_btn.config(state=DISABLED)
        Messagebox.show_error(message, "Error")


if __name__ == "__main__":
    app = OptimizedFileSearchGUI()
    app.mainloop()
