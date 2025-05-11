import tkinter as tk
from tkinter import ttk, messagebox
import os
import mimetypes
import sys
import cv2
from PIL import Image, ImageTk
import subprocess

class FileItemWidget(ttk.Frame):
    """Custom widget for a file item with a thumbnail, label and checkbox."""

    def __init__(self, parent, file_path, watched=False, progress_callback=None):
        super().__init__(parent)
        self.file_path = file_path
        self.progress_callback = progress_callback or self._default_progress_callback
        
        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        
        # Add thumbnail
        self.icon_label = ttk.Label(self)
        self.set_thumbnail(file_path)
        self.icon_label.grid(row=0, rowspan=2, column=0, padx=(12,8), pady=12)
        
        # Add file name label
        self.filename_label = ttk.Label(
            self, 
            text=os.path.basename(file_path),
            font=('TkDefaultFont', 11, 'bold')
        )
        self.filename_label.grid(row=0, column=1, sticky='sw', padx=(0,12))
        
        # Add file info label
        file_info = self.get_file_info(file_path)
        self.info_label = ttk.Label(
            self,
            text=file_info,
            foreground='gray'
        )
        self.info_label.grid(row=1, column=1, sticky='nw', padx=(0,12))
        
        # Add checkbox
        self.watched_var = tk.BooleanVar(value=watched)
        self.checkbox = ttk.Checkbutton(
            self,
            text="Watched",
            variable=self.watched_var,
            command=self.checkbox_changed
        )
        self.checkbox.grid(row=0, rowspan=2, column=2, padx=12, pady=12)
        
        # Bind double click to all child widgets
        self.bind('<Double-Button-1>', self.on_double_click)
        self.icon_label.bind('<Double-Button-1>', self.on_double_click)
        self.filename_label.bind('<Double-Button-1>', self.on_double_click)
        self.info_label.bind('<Double-Button-1>', self.on_double_click)
        self.checkbox.bind('<Double-Button-1>', self.on_double_click)
        
        # Add hover effect
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        # Set tooltip
        self.tooltip = f"Double-click to open\n{file_path}"
        
        # Style
        self.configure(style='FileItem.TFrame')
        style = ttk.Style()
        style.configure('FileItem.TFrame', padding=4)

    def set_thumbnail(self, file_path):
        """Set appropriate thumbnail for the file type."""
        mime_type, _ = mimetypes.guess_type(file_path)
        icon_size = 48
        
        try:
            if mime_type and mime_type.startswith('video/'):
                # Create thumbnail from video
                photo = self.get_video_thumbnail(file_path, icon_size)
            elif mime_type and mime_type.startswith('image/'):
                # Create thumbnail from image
                img = Image.open(file_path)
                img.thumbnail((icon_size, icon_size))
                photo = ImageTk.PhotoImage(img)
            else:
                # Use default icon based on mime type
                icon_name = self.get_default_icon(mime_type)
                img = Image.open(f"icons/{icon_name}.png")
                img.thumbnail((icon_size, icon_size))
                photo = ImageTk.PhotoImage(img)
            
            if photo:
                self.icon_label.configure(image=photo)
                self.icon_label.image = photo  # Keep reference
            else:
                self.icon_label.configure(text="📄")
            
        except Exception as e:
            print(f"Thumbnail error for {file_path}: {e}")
            # Fallback to text if icon loading fails
            self.icon_label.configure(text="📄")

    def get_video_thumbnail(self, video_path, size):
        """Generate thumbnail from video file."""
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Read first frame
            success, frame = cap.read()
            if not success:
                return None
            
            # Get video duration and seek to 10% of the video
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames > 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(total_frames * 0.1))
                success, frame = cap.read()
            
            cap.release()
            
            if success:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image and resize
                image = Image.fromarray(frame_rgb)
                image.thumbnail((size, size))
                
                # Convert to PhotoImage
                return ImageTk.PhotoImage(image)
            
        except Exception as e:
            print(f"Video thumbnail error: {e}")
        return None

    def get_default_icon(self, mime_type):
        """Return default icon name based on mime type."""
        if not mime_type:
            return "file"
        if mime_type.startswith('video/'):
            return "video"
        elif mime_type.startswith('audio/'):
            return "audio"
        elif 'pdf' in mime_type:
            return "pdf"
        return "file"

    def get_file_info(self, file_path):
        """Get formatted file size and type information."""
        size = os.path.getsize(file_path)
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/(1024*1024):.1f} MB"

        mime_type, _ = mimetypes.guess_type(file_path)
        type_str = mime_type if mime_type else "Unknown type"

        return f"{size_str} • {type_str}"

    def checkbox_changed(self):
        """Handle checkbox state change."""
        try:
            watched = self.watched_var.get()
            self.progress_callback(self.file_path, watched)
        except Exception as e:
            print(f"Error in checkbox_changed: {e}")

    def _default_progress_callback(self, file_path, watched):
        """Default callback if none provided."""
        print(f"File {file_path} {'watched' if watched else 'unwatched'}")

    def open_file(self):
        """Open the file with the system's default application."""
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.file_path])
            elif sys.platform == 'win32':  # Windows
                os.startfile(self.file_path)
            else:  # Linux
                subprocess.run(['xdg-open', self.file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def on_enter(self, event):
        """Handle mouse enter event."""
        self.configure(style='FileItemHover.TFrame')

    def on_leave(self, event):
        """Handle mouse leave event."""
        self.configure(style='FileItem.TFrame')

    def on_double_click(self, event):
        """Handle double click event."""
        self.open_file()
        return "break"  # Prevent event propagation