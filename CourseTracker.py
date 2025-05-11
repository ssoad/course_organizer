import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
from FileItemWidget import FileItemWidget
from DirectoryItemWidget import DirectoryItemWidget
from course_manager import CourseManager

class CourseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Course Tracker")
        self.geometry("800x600")

        # Initialize course manager
        self.manager = CourseManager()
        self.current_directory = None
        
        self.setup_ui()
        self.load_saved_directories()

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
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL)
        
        # Create inner frame for items
        self.items_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=self.on_scroll)
        self.scrollbar.configure(command=self.canvas.yview)
        
        # Pack scrollbar and canvas
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.items_frame,
            anchor="nw",
            tags="items",
            width=self.canvas.winfo_width()
        )

        # Add resizing behavior
        self.setup_canvas_configuration()
        self.setup_scrolling()

        # Add styles for directory items
        style = ttk.Style()
        style.configure('Directory.TFrame', background='white')
        style.configure('DirectoryHover.TFrame', background='#f0f0f0')

    def on_scroll(self, *args):
        """Handle scroll events and show/hide scrollbar as needed."""
        self.scrollbar.set(*args)
        self.update_scrollbar_visibility()

    def update_scrollbar_visibility(self):
        """Show or hide scrollbar based on content height."""
        canvas_height = self.canvas.winfo_height()
        content_height = self.items_frame.winfo_reqheight()
        
        if content_height > canvas_height:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.scrollbar.pack_forget()

    def setup_canvas_configuration(self):
        def _configure_canvas(event):
            # Update scroll region
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Update frame width to match canvas
            canvas_width = event.width if event else self.canvas.winfo_width()
            self.canvas.itemconfig("items", width=canvas_width)
            # Check if scrollbar is needed
            self.update_scrollbar_visibility()

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
        for directory in self.manager.directories:
            progress = self.manager.calculate_directory_progress(directory)
            self.create_directory_item(directory, progress)

    def create_directory_item(self, directory, progress):
        """Create a directory item widget."""
        directory_widget = DirectoryItemWidget(
            self.items_frame,
            directory,
            progress,
            self.show_directory_contents
        )
        directory_widget.pack(fill=tk.X, padx=10, pady=5)

    def show_directory_contents(self, directory):
        """Show contents of selected directory."""
        self.current_directory = directory
        self.back_button.pack(side=tk.LEFT, before=self.select_dir_button)
        
        # Clear current content
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        try:
            # Get directory contents from manager
            subdirs, files = self.manager.get_directory_contents(directory)
            
            # Show subdirectories
            for dir_path, progress in subdirs:
                self.create_directory_item(dir_path, progress)
            
            # Show files
            for file_path, watched in files:
                file_widget = FileItemWidget(
                    self.items_frame,
                    file_path,
                    watched,
                    self.update_progress
                )
                file_widget.pack(fill=tk.X, padx=5, pady=2)
                
            # Update scroll region and visibility after adding content
            self.canvas.after(100, self.update_content_layout)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_content_layout(self):
        """Update canvas scroll region and scrollbar visibility."""
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update frame width
        self.canvas.itemconfig("items", width=self.canvas.winfo_width())
        
        # Update scrollbar visibility
        self.update_scrollbar_visibility()
        
        # Force geometry update
        self.items_frame.update_idletasks()

    def update_progress(self, file_path, watched):
        """Update the progress data for a file."""
        self.manager.update_file_progress(file_path, watched)
        self.load_saved_directories()

    def select_directory(self):
        """Open a dialog to select directory."""
        selected_dir = filedialog.askdirectory(title="Select Courses Directory")
        if selected_dir:
            if self.manager.add_directory(selected_dir):
                self.load_saved_directories()

    def remove_selected_directory(self):
        """Remove selected directory from tracking."""
        if self.current_directory:
            if self.manager.remove_directory(self.current_directory):
                self.go_back()