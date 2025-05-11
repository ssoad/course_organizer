from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os

class DirectoryItemWidget(QWidget):
    def __init__(self, directory_path, progress, parent=None):
        super().__init__(parent)
        self.directory_path = directory_path
        self.progress = progress
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Add folder icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.set_folder_icon()
        layout.addWidget(self.icon_label)
        
        # Add directory info (vertical layout)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Directory name
        self.name_label = QLabel(os.path.basename(directory_path))
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        info_layout.addWidget(self.name_label)
        
        # Progress bar and percentage
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setMinimumHeight(6)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setValue(int(progress))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f0f0f0;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress percentage
        self.progress_label = QLabel(f"{progress:.1f}%")
        self.progress_label.setStyleSheet("color: #7f8c8d;")
        progress_layout.addWidget(self.progress_label)
        
        progress_layout.addStretch()
        info_layout.addLayout(progress_layout)
        
        # Add count of items
        try:
            items = os.listdir(directory_path)
            file_count = len([x for x in items if os.path.isfile(os.path.join(directory_path, x))])
            dir_count = len([x for x in items if os.path.isdir(os.path.join(directory_path, x))])
            count_text = []
            if dir_count > 0:
                count_text.append(f"{dir_count} folders")
            if file_count > 0:
                count_text.append(f"{file_count} files")
            self.count_label = QLabel(" • ".join(count_text))
            self.count_label.setStyleSheet("color: #95a5a6;")
            info_layout.addWidget(self.count_label)
        except Exception:
            pass
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Apply widget style
        self.setStyleSheet("""
            DirectoryItemWidget {
                background-color: white;
                border-radius: 8px;
            }
            DirectoryItemWidget:hover {
                background-color: #f8f9fa;
            }
        """)
        
    def set_folder_icon(self):
        """Set the folder icon"""
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'folder.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(
                64, 64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to system icon
            icon = QIcon.fromTheme('folder')
            pixmap = icon.pixmap(64, 64)
            self.icon_label.setPixmap(pixmap)