from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from course_manager import CourseManager
from FileItemWidget import FileItemWidget
from DirectoryItemWidget import DirectoryItemWidget
import os
from natsort import natsorted

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
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setFixedHeight(90)  # Increased height
        self.addToolBar(toolbar)
        
        # Define button style
        button_style = """
            QToolButton {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 100px;
                min-height: 36px;
            }
            QToolButton:hover {
                background-color: #f8f9fa;
                border-color: #0d6efd;
                color: #0d6efd;
            }
            QToolButton:pressed {
                background-color: #e7f5ff;
            }
            QToolButton:disabled {
                background-color: #f8f9fa;
                border-color: #e9ecef;
                color: #adb5bd;
            }
        """
        
        # Add custom toolbar buttons
        self.back_action = QAction("Back", self)
        self.back_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'back.png')))
        
        self.add_action = QAction("Add Directory", self)
        self.add_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'add.png')))
        
        self.remove_action = QAction("Remove Directory", self)
        self.remove_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), 'icons', 'remove.png')))
        
        # Create custom toolbar buttons
        back_button = QToolButton()
        back_button.setDefaultAction(self.back_action)
        back_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        back_button.setStyleSheet(button_style)
        
        add_button = QToolButton()
        add_button.setDefaultAction(self.add_action)
        add_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        add_button.setStyleSheet(button_style)
        
        remove_button = QToolButton()
        remove_button.setDefaultAction(self.remove_action)
        remove_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        remove_button.setStyleSheet(button_style)
        
        # Create spacer widget for toolbar
        def create_spacer(width):
            spacer = QWidget()
            spacer.setFixedWidth(width)
            return spacer
        
        # Add buttons to toolbar with spacing widgets
        toolbar.addWidget(back_button)
        toolbar.addWidget(create_spacer(8))  # Replace addSpacing
        toolbar.addWidget(add_button)
        toolbar.addWidget(create_spacer(8))  # Replace addSpacing
        toolbar.addWidget(remove_button)
        
        # Add expanding spacer to toolbar
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        # Connect actions to slots
        self.back_action.triggered.connect(self.go_back)
        self.add_action.triggered.connect(self.add_directory)
        self.remove_action.triggered.connect(self.remove_directory)
        
        # Add padding to main layout
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(0)
        
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
        # Set application font
        self.setFont(QFont('SF Pro Display', 10))
        
        # Load styles from QSS file
        try:
            style_file = os.path.join(os.path.dirname(__file__), 'styles.qss')
            with open(style_file, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading styles: {e}")
        
        # Apply drop shadow to the main window
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.content_list.setGraphicsEffect(shadow)

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
        """Load and display naturally sorted directory list"""
        self.content_list.clear()
        
        # Sort directories naturally before displaying
        sorted_directories = natsorted(self.manager.directories)
        
        for directory in sorted_directories:
            progress = self.manager.calculate_directory_progress(directory)
            item = QListWidgetItem(self.content_list)
            item.setSizeHint(QSize(0, 120))
            item.setData(Qt.ItemDataRole.UserRole, directory)
            
            widget = DirectoryItemWidget(directory, progress)
            self.content_list.setItemWidget(item, widget)

    def load_directory_contents(self, directory):
        self.content_list.clear()
        try:
            subdirs, files = self.manager.get_directory_contents(directory)
            
            # Add subdirectories with custom widget
            for dir_path, progress in subdirs:
                item = QListWidgetItem(self.content_list)
                item.setSizeHint(QSize(0, 100))  # Adjusted height for subdirectories
                item.setData(Qt.ItemDataRole.UserRole, dir_path)
                
                widget = DirectoryItemWidget(dir_path, progress, is_subdirectory=True)
                self.content_list.setItemWidget(item, widget)
                
            # Add files
            for file_path, watched in files:
                item = QListWidgetItem(self.content_list)
                item.setSizeHint(QSize(0, 100))
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                
                widget = FileItemWidget(
                    file_path, 
                    watched, 
                    manager=self.manager  # Pass manager reference
                )
                widget.watchedChanged.connect(self.on_file_watched_changed)
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

    def on_file_watched_changed(self, file_path, watched):
        """Handle file watched state changes"""
        directory = os.path.dirname(file_path)
        
        # Update watched state and get new progress
        progress = self.manager.update_file_watched_state(file_path, watched)
        
        # Update UI
        self.update_directory_progress(directory, progress)
        
        # If we're in a subdirectory, update parent directory progress too
        if self.current_directory:
            parent_progress = self.manager.calculate_directory_progress(self.current_directory)
            self.update_directory_progress(self.current_directory, parent_progress)

    def update_directory_progress(self, directory, progress=None):
        """Update the progress display for a directory item"""
        if progress is None:
            progress = self.manager.calculate_directory_progress(directory)
            
        # Find and update directory widget
        for index in range(self.content_list.count()):
            item = self.content_list.item(index)
            if item and item.data(Qt.ItemDataRole.UserRole) == directory:
                widget = self.content_list.itemWidget(item)
                if isinstance(widget, DirectoryItemWidget):
                    widget.update_progress(progress)
                break