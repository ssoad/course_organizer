import tkinter as tk
from tkinter import ttk
import os

class DirectoryItemWidget(ttk.Frame):
    def __init__(self, parent, directory_path, progress, click_callback):
        super().__init__(parent)
        self.directory_path = directory_path
        self.click_callback = click_callback
        
        # Configure style
        style = ttk.Style()
        style.configure('Directory.TFrame', padding=10)
        style.configure('DirectoryHover.TFrame', 
                       background='#e8f0fe',
                       padding=10)
        
        # Set initial style
        self.configure(style='Directory.TFrame')
        
        # Create layout
        self.create_widgets(progress)
        self.bind_events()
        
    def create_widgets(self, progress):
        # Container for icon and text
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.X, expand=True)
        
        # Folder icon
        icon_label = ttk.Label(
            content_frame,
            text="📁",
            font=('TkDefaultFont', 48)  # Large icon
        )
        icon_label.pack(side=tk.LEFT, padx=(5, 15))
        
        # Text container
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Directory name
        name_label = ttk.Label(
            text_frame,
            text=os.path.basename(self.directory_path),
            font=('TkDefaultFont', 14, 'bold'),
            wraplength=400
        )
        name_label.pack(anchor=tk.W)
        
        # Progress bar and percentage
        progress_frame = ttk.Frame(text_frame)
        progress_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=200,
            mode='determinate',
            value=progress
        )
        self.progress_bar.pack(side=tk.LEFT)
        
        progress_label = ttk.Label(
            progress_frame,
            text=f"{progress:.1f}%",
            font=('TkDefaultFont', 10)
        )
        progress_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Add separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 0))
        
    def bind_events(self):
        # Bind click and hover events
        for widget in self.winfo_children():
            widget.bind('<Button-1>', self.on_click)
            widget.bind('<Enter>', self.on_enter)
            widget.bind('<Leave>', self.on_leave)
            # Bind events to child widgets too
            for child in widget.winfo_children():
                child.bind('<Button-1>', self.on_click)
                child.bind('<Enter>', self.on_enter)
                child.bind('<Leave>', self.on_leave)
        
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_click(self, event):
        self.click_callback(self.directory_path)
    
    def on_enter(self, event):
        self.configure(style='DirectoryHover.TFrame')
    
    def on_leave(self, event):
        self.configure(style='Directory.TFrame')