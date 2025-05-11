import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from FileItemWidget import FileItemWidget
import os
import sys
from main import load_progress, save_progress
from natsort import natsorted  # Add this import at the top
from main import load_directories, save_directories

class CourseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Course Tracker")
        self.geometry("800x600")

        # Load progress data from JSON
        self.progress = load_progress()
        
        # Load saved directories
        self.directories = load_directories()
        
        self.setup_ui()

    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top panel with navigation and actions
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add back button (hidden by default)
        self.back_button = ttk.Button(
            top_frame,
            text="← Back",
            command=self.go_back
        )
        
        # Add directory button
        self.select_dir_button = ttk.Button(
            top_frame,
            text="Add Directory",
            command=self.select_directory
        )
        self.select_dir_button.pack(side=tk.LEFT, padx=(0, 5))

        self.remove_dir_button = ttk.Button(
            top_frame,
            text="Remove Directory",
            command=self.remove_selected_directory
        )
        self.remove_dir_button.pack(side=tk.LEFT)

        # Main content area
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollable canvas for content
        self.canvas = tk.Canvas(
            self.content_frame,
            bg=self.cget('bg'),
            borderwidth=0,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL)
        
        # Create inner frame for items
        self.items_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.canvas.yview)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.items_frame,
            anchor="nw",
            tags="items"
        )

        # Add resizing behavior
        self.setup_canvas_configuration()
        self.setup_scrolling()

        # Add styles for directory items
        style = ttk.Style()
        style.configure('Directory.TFrame', background='white')
        style.configure('DirectoryHover.TFrame', background='#f0f0f0')

        self.load_saved_directories()

    def setup_canvas_configuration(self):
        def _configure_canvas(event):
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Update frame width to match canvas
            canvas_width = event.width if event else self.canvas.winfo_width()
            self.canvas.itemconfig("items", width=canvas_width)

        self.items_frame.bind("<Configure>", _configure_canvas)
        self.canvas.bind("<Configure>", _configure_canvas)
        self.canvas.after(100, lambda: _configure_canvas(None))

    def setup_scrolling(self):
        """Setup mouse wheel scrolling for canvas."""
        def _on_mousewheel(event):
            if sys.platform == "darwin":
                # macOS scrolling
                delta = event.delta
                scroll_speed = 1  # Adjust this value to change scroll speed
                self.canvas.yview_scroll(-int(delta * scroll_speed), "units")
            else:
                # Windows/Linux scrolling
                self.canvas.yview_scroll(int(-1 * (event.delta/120)), "units")

        def _bind_mousewheel(event):
            # Bind mouse wheel for all platforms
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            if not sys.platform == "darwin":
                self.canvas.bind_all("<Button-4>", _on_mousewheel)
                self.canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_mousewheel(event):
            # Unbind mouse wheel events
            self.canvas.unbind_all("<MouseWheel>")
            if not sys.platform == "darwin":
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")

        # Bind enter/leave events for mousewheel
        self.canvas.bind('<Enter>', _bind_mousewheel)
        self.canvas.bind('<Leave>', _unbind_mousewheel)

    def go_back(self):
        """Return to main directory list."""
        self.back_button.pack_forget()
        self.current_directory = None
        self.load_saved_directories()

    def load_saved_directories(self):
        """Show main directory list."""
        # Clear current content
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        # Show directories
        for directory in self.directories:
            if os.path.exists(directory):
                progress = self.calculate_directory_progress(directory)
                self.create_directory_item(directory, progress)

    def create_directory_item(self, directory, progress):
        """Create a clickable directory item with folder icon."""
        frame = ttk.Frame(self.items_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Add folder icon
        folder_label = ttk.Label(
            frame,
            text="📁",  # Folder emoji as icon
            font=('TkDefaultFont', 14)
        )
        folder_label.pack(side=tk.LEFT, padx=(5, 0), pady=5)
        
        # Add directory name and progress
        label = ttk.Label(
            frame, 
            text=f"{os.path.basename(directory)} ({progress:.1f}%)",
            font=('TkDefaultFont', 11)
        )
        label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Make all elements clickable
        for widget in (frame, folder_label, label):
            widget.bind('<Button-1>', lambda e, d=directory: self.show_directory_contents(d))
            # Add hover effect
            widget.bind('<Enter>', lambda e, w=frame: w.configure(style='DirectoryHover.TFrame'))
            widget.bind('<Leave>', lambda e, w=frame: w.configure(style='Directory.TFrame'))

    def show_directory_contents(self, directory):
        """Show contents of selected directory."""
        self.current_directory = directory
        self.back_button.pack(side=tk.LEFT, before=self.select_dir_button)
        
        # Clear and show files
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        try:
            # Get all items in directory
            items = os.listdir(directory)
            
            # Show subdirectories first
            for item in natsorted(items):
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    progress = self.calculate_directory_progress(full_path)
                    self.create_directory_item(full_path, progress)
            
            # Then show files
            for item in natsorted(items):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path):
                    watched = self.progress.get(full_path, False)
                    file_widget = FileItemWidget(
                        self.items_frame,
                        full_path,
                        watched,
                        self.update_progress
                    )
                    file_widget.pack(fill=tk.X, padx=5, pady=2)
                    
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_selected_directory(self):
        """Remove selected directory from tracking."""
        if self.current_directory:
            directory = self.current_directory
            if directory in self.directories:
                self.directories.remove(directory)
                save_directories(self.directories)
                self.go_back()

    def select_directory(self):
        """Open a dialog to select the courses directory."""
        selected_dir = filedialog.askdirectory(title="Select Courses Directory")
        if selected_dir and selected_dir not in self.directories:
            self.directories.append(selected_dir)
            save_directories(self.directories)
            self.load_saved_directories()

    def calculate_directory_progress(self, directory):
        """Calculate watch progress for a directory."""
        total_files = 0
        watched_files = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                total_files += 1
                if self.progress.get(full_path, False):
                    watched_files += 1
        
        return (watched_files / total_files * 100) if total_files > 0 else 0

    def update_progress(self, file_path, watched):
        """Update the progress data for a file and save to JSON."""
        self.progress[file_path] = watched
        save_progress(self.progress)
        
        # Update progress for the containing directory
        directory = os.path.dirname(file_path)
        while directory:
            if directory in self.directories:
                progress = self.calculate_directory_progress(directory)
                self.load_saved_directories()
                break
            directory = os.path.dirname(directory)