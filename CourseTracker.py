from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from course_manager import CourseManager
from FileItemWidget import FileItemWidget
import os

class CourseTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Course Tracker")
        self.setMinimumSize(800, 600)
        
        # Initialize course manager
        self.manager = CourseManager()
        self.current_directory = None
        
        # Setup UI
        self.setup_ui()
        self.load_directory_list()
        
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar with modern style
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # Add actions
        self.back_action = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.add_action = QAction(QIcon.fromTheme("list-add"), "Add Directory", self)
        self.remove_action = QAction(QIcon.fromTheme("list-remove"), "Remove Directory", self)
        
        # Connect actions to slots
        self.back_action.triggered.connect(self.go_back)
        self.add_action.triggered.connect(self.add_directory)
        self.remove_action.triggered.connect(self.remove_directory)
        
        toolbar.addAction(self.back_action)
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.remove_action)
        
        # Create content list with custom style
        self.content_list = QListWidget()
        self.content_list.setSpacing(8)
        self.content_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.content_list)
        
        # Set initial button states
        self.back_action.setEnabled(False)
        self.remove_action.setEnabled(False)
        
        # Apply styles
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 8px;
            }
            QListWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)

    def add_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            if self.manager.add_directory(directory):
                self.load_directory_list()

    def remove_directory(self):
        if self.current_directory:
            if self.manager.remove_directory(self.current_directory):
                self.go_back()

    def go_back(self):
        self.current_directory = None
        self.back_action.setEnabled(False)
        self.remove_action.setEnabled(False)
        self.load_directory_list()

    def on_item_double_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
            
        if os.path.isdir(path):
            # Handle directory double-click
            self.current_directory = path
            self.back_action.setEnabled(True)
            self.remove_action.setEnabled(path in self.manager.directories)
            self.load_directory_contents(path)
        else:
            # For files, the FileItemWidget will handle the double-click
            pass

    def load_directory_list(self):
        self.content_list.clear()
        for directory in self.manager.directories:
            progress = self.manager.calculate_directory_progress(directory)
            item = QListWidgetItem(f"{os.path.basename(directory)} ({progress:.1f}%)")
            item.setData(Qt.ItemDataRole.UserRole, directory)
            self.content_list.addItem(item)

    def load_directory_contents(self, directory):
        self.content_list.clear()
        try:
            subdirs, files = self.manager.get_directory_contents(directory)
            
            # Add subdirectories first
            for dir_path, progress in subdirs:
                item = QListWidgetItem(self.content_list)
                item.setData(Qt.ItemDataRole.UserRole, dir_path)
                item_text = f"📁 {os.path.basename(dir_path)} ({progress:.1f}%)"
                item.setText(item_text)
                self.content_list.addItem(item)
            
            # Then add files
            for file_path, watched in files:
                item = QListWidgetItem(self.content_list)
                item.setSizeHint(QSize(0, 64))  # Increased height for thumbnails
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                
                widget = FileItemWidget(file_path, watched)
                widget.watchedChanged.connect(self.on_watch_changed)
                self.content_list.setItemWidget(item, widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_watch_changed(self, file_path, watched):
        """Handle watch status changes"""
        self.manager.update_file_progress(file_path, watched)
        # Refresh directory progress
        if self.current_directory:
            progress = self.manager.calculate_directory_progress(self.current_directory)
            self.update_directory_progress(self.current_directory, progress)