from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os

class DirectoryItemWidget(QWidget):
    def __init__(self, directory_path, progress, parent=None, is_subdirectory=False):
        super().__init__(parent)
        self.directory_path = directory_path
        self.progress = progress
        self.is_subdirectory = is_subdirectory
        
        # Create layout with gradient background
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(15)
        
        # Left side container for icon and arrow
        left_container = QHBoxLayout()
        left_container.setSpacing(8)
        
        if is_subdirectory:
            # Add arrow icon for subdirectory
            arrow_label = QLabel("→")
            arrow_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            left_container.addWidget(arrow_label)
        
        # Add folder icon with shadow effect
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48 if is_subdirectory else 64, 48 if is_subdirectory else 64)
        self.set_folder_icon()
        
        # Add shadow to icon
        icon_shadow = QGraphicsDropShadowEffect()
        icon_shadow.setBlurRadius(10)
        icon_shadow.setXOffset(0)
        icon_shadow.setYOffset(2)
        icon_shadow.setColor(QColor(0, 0, 0, 30))
        self.icon_label.setGraphicsEffect(icon_shadow)
        
        left_container.addWidget(self.icon_label)
        layout.addLayout(left_container)
        
        # Add directory info (vertical layout)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        
        # Directory name with new style
        name_container = QHBoxLayout()
        name_container.setSpacing(8)
        
        self.name_label = QLabel(os.path.basename(directory_path))
        self.name_label.setStyleSheet(f"""
            QLabel {{
                font-size: {12 if is_subdirectory else 14}px;
                font-weight: bold;
                color: #2c3e50;
            }}
        """)
        name_container.addWidget(self.name_label)
        
        # Add folder type badge
        folder_type = self.get_folder_type()
        if folder_type:
            type_label = QLabel(folder_type)
            type_label.setStyleSheet("""
                QLabel {
                    background-color: #e9ecef;
                    color: #495057;
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 11px;
                }
            """)
            name_container.addWidget(type_label)
        
        name_container.addStretch()
        info_layout.addLayout(name_container)
        
        # Progress bar and percentage with updated style
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(180 if is_subdirectory else 200)
        self.progress_bar.setMinimumHeight(4 if is_subdirectory else 6)
        self.progress_bar.setMaximumHeight(4 if is_subdirectory else 6)
        self.progress_bar.setValue(int(progress))
        self.progress_bar.setTextVisible(False)
        
        # Set progress bar color based on progress
        progress_color = self.get_progress_color(progress)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #f0f0f0;
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {progress_color};
                border-radius: 2px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress percentage
        self.progress_label = QLabel(f"{progress:.1f}%")
        self.progress_label.setStyleSheet(f"color: {progress_color};")
        progress_layout.addWidget(self.progress_label)
        
        progress_layout.addStretch()
        info_layout.addLayout(progress_layout)
        
        # Add count of items with icons
        try:
            items = os.listdir(directory_path)
            file_count = len([x for x in items if os.path.isfile(os.path.join(directory_path, x))])
            dir_count = len([x for x in items if os.path.isdir(os.path.join(directory_path, x))])
            
            count_layout = QHBoxLayout()
            count_layout.setSpacing(12)
            
            if dir_count > 0:
                folder_count = QLabel(f"📁 {dir_count} folders")
                folder_count.setStyleSheet("color: #6c757d; font-size: 11px;")
                count_layout.addWidget(folder_count)
            
            if file_count > 0:
                file_count_label = QLabel(f"📄 {file_count} files")
                file_count_label.setStyleSheet("color: #6c757d; font-size: 11px;")
                count_layout.addWidget(file_count_label)
            
            count_layout.addStretch()
            info_layout.addLayout(count_layout)
        except Exception:
            pass
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Apply widget style with subtle gradient
        self.setStyleSheet(f"""
            DirectoryItemWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {'#ffffff' if is_subdirectory else '#f8f9fa'}, 
                    stop:1 {'#f8f9fa' if is_subdirectory else '#ffffff'});
                border-radius: 8px;
                border: 1px solid {'#e9ecef' if is_subdirectory else 'transparent'};
            }}
            DirectoryItemWidget:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f8f9fa, stop:1 #f0f2f5);
                border: 1px solid #dee2e6;
            }}
        """)

    def set_folder_icon(self):
        """Set the folder icon with proper sizing"""
        icon_size = self.icon_label.size()
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'folder.png')
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # Scale based on whether it's a subdirectory or not
            target_size = 40 if self.is_subdirectory else 64
            scaled_pixmap = pixmap.scaled(
                target_size, target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Center the pixmap in the label
            x_offset = (self.icon_label.width() - scaled_pixmap.width()) // 2
            y_offset = (self.icon_label.height() - scaled_pixmap.height()) // 2
            
            # Create a new transparent pixmap for padding
            final_pixmap = QPixmap(self.icon_label.size())
            final_pixmap.fill(Qt.GlobalColor.transparent)
            
            # Paint the scaled icon centered
            painter = QPainter(final_pixmap)
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()
            
            self.icon_label.setPixmap(final_pixmap)
        else:
            # Fallback to system icon with proper sizing
            icon = QIcon.fromTheme('folder')
            pixmap = icon.pixmap(
                40 if self.is_subdirectory else 64,
                40 if self.is_subdirectory else 64
            )
            self.icon_label.setPixmap(pixmap)

    def update_progress(self, progress):
        """Update the progress display"""
        self.progress = progress
        self.progress_bar.setValue(int(progress))
        self.progress_label.setText(f"{progress:.1f}%")

    def get_progress_color(self, progress):
        """Return color based on progress percentage"""
        if progress >= 80:
            return "#2ecc71"  # Green
        elif progress >= 50:
            return "#3498db"  # Blue
        elif progress >= 20:
            return "#f1c40f"  # Yellow
        else:
            return "#e74c3c"  # Red

    def get_folder_type(self):
        """Determine folder type based on contents"""
        name = os.path.basename(self.directory_path).lower()
        if any(keyword in name for keyword in ['week', 'lecture', 'chapter']):
            return "Course Content"
        elif any(keyword in name for keyword in ['assignment', 'homework', 'exercise']):
            return "Assignments"
        elif any(keyword in name for keyword in ['resource', 'material']):
            return "Resources"
        return None