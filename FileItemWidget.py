from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os
import mimetypes
import subprocess
import sys
from PIL import Image
import cv2
import io
from pdf2image import convert_from_path
from pathlib import Path

class FileItemWidget(QWidget):
    watchedChanged = pyqtSignal(str, bool)
    
    def __init__(self, file_path, watched=False, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.thumbnail_size = QSize(48, 48)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(15)
        
        # Left container for checkbox and icon
        left_container = QHBoxLayout()
        left_container.setSpacing(12)
        
        # Add checkbox with modern style
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(watched)
        self.checkbox.stateChanged.connect(self.on_watch_changed)
        left_container.addWidget(self.checkbox)
        
        # Icon container with shadow
        icon_container = QWidget()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
            }
        """)
        
        # Add shadow to icon container
        # icon_shadow = QGraphicsDropShadowEffect()
        # icon_shadow.setBlurRadius(8)
        # icon_shadow.setXOffset(0)
        # icon_shadow.setYOffset(2)
        # icon_shadow.setColor(QColor(0, 0, 0, 30))
        # icon_container.setGraphicsEffect(icon_shadow)
        
        # Icon layout
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(4, 4, 4, 4)
        
        # Add icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(42, 42)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(self.icon_label)
        
        left_container.addWidget(icon_container)
        layout.addLayout(left_container)
        
        # Center container for file info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # File name with ellipsis
        self.name_label = QLabel(Path(file_path).name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #2c3e50;
            }
        """)
        info_layout.addWidget(self.name_label)
        
        # File details (type and size)
        details_layout = QHBoxLayout()
        details_layout.setSpacing(8)
        
        # File type badge
        mime_type = mimetypes.guess_type(file_path)[0] or "unknown"
        type_label = QLabel(mime_type.split('/')[-1].upper())
        type_label.setStyleSheet("""
            QLabel {
                background-color: #e9ecef;
                color: #495057;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 500;
            }
        """)
        details_layout.addWidget(type_label)
        
        # File size
        try:
            size = os.path.getsize(file_path)
            size_str = self.format_size(size)
            size_label = QLabel(size_str)
            size_label.setStyleSheet("color: #6c757d; font-size: 11px;")
            details_layout.addWidget(size_label)
        except:
            pass
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Apply widget style
        self.setStyleSheet("""
            FileItemWidget {
                background-color: white;
                border-radius: 8px;
            }
            FileItemWidget:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8f9fa, stop:1 #ffffff);
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #adb5bd;
                border-radius: 4px;
            }
            QCheckBox::indicator:hover {
                border-color: #0d6efd;
            }
            QCheckBox::indicator:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
                image: url(icons/check.png);
            }
        """)
        
        self.set_thumbnail_or_icon()
    
    def format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def on_watch_changed(self, state):
        """Handle checkbox state changes"""
        self.watchedChanged.emit(self.file_path, state == Qt.CheckState.Checked)
        
        # Update widget appearance based on watched state
        self.setStyleSheet(self.styleSheet() + f"""
            FileItemWidget {{
                background-color: {'#f8f9fa' if state == Qt.CheckState.Checked else 'white'};
            }}
        """)

    def set_thumbnail_or_icon(self):
        """Set appropriate thumbnail or icon for the file type"""
        mime_type, _ = mimetypes.guess_type(self.file_path)
        
        if mime_type:
            if mime_type.startswith('image/'):
                self.set_image_thumbnail()
            elif mime_type.startswith('video/'):
                self.set_video_thumbnail()
            elif mime_type == 'application/pdf':
                self.set_pdf_thumbnail()
            else:
                self.set_file_icon(mime_type)
        else:
            self.set_file_icon(None)

    def set_image_thumbnail(self):
        """Create thumbnail for image files"""
        try:
            # Open image and create thumbnail
            image = Image.open(self.file_path)
            image.thumbnail((48, 48))
            
            # Convert PIL image to QPixmap
            bytes_io = io.BytesIO()
            image.save(bytes_io, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(bytes_io.getvalue())
            
            self.icon_label.setPixmap(pixmap)
            
        except Exception:
            self.set_file_icon('image/')

    def set_video_thumbnail(self):
        """Create thumbnail from video first frame"""
        try:
            # Open video file
            cap = cv2.VideoCapture(self.file_path)
            
            # Read first frame
            ret, frame = cap.read()
            if ret:
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame
                height, width = frame_rgb.shape[:2]
                aspect_ratio = width / height
                
                if aspect_ratio > 1:
                    new_width = 48
                    new_height = int(48 / aspect_ratio)
                else:
                    new_height = 48
                    new_width = int(48 * aspect_ratio)
                    
                frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
                
                # Convert to QPixmap
                height, width = frame_resized.shape[:2]
                bytes_per_line = 3 * width
                qimage = QImage(frame_resized.data, width, height, 
                              bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                
                # Center the thumbnail
                final_pixmap = QPixmap(48, 48)
                final_pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(final_pixmap)
                x = (48 - new_width) // 2
                y = (48 - new_height) // 2
                painter.drawPixmap(x, y, pixmap)
                painter.end()
                
                self.icon_label.setPixmap(final_pixmap)
            cap.release()
            
        except Exception:
            self.set_file_icon('video/')

    def set_pdf_thumbnail(self):
        """Create thumbnail for PDF files"""
        try:
            # Convert first page of PDF to image
            pages = convert_from_path(
                self.file_path, 
                first_page=1, 
                last_page=1,
                size=(96, 96)  # Larger size for better quality
            )
            
            if pages:
                # Get first page
                page = pages[0]
                
                # Convert PIL image to QPixmap
                bytes_io = io.BytesIO()
                page.save(bytes_io, format='PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(bytes_io.getvalue())
                
                # Scale to thumbnail size maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Create final pixmap with padding
                final_pixmap = QPixmap(48, 48)
                final_pixmap.fill(Qt.GlobalColor.transparent)
                
                # Center the thumbnail
                painter = QPainter(final_pixmap)
                x = (48 - scaled_pixmap.width()) // 2
                y = (48 - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                self.icon_label.setPixmap(final_pixmap)
            else:
                self.set_file_icon('application/pdf')
                
        except Exception as e:
            print(f"PDF thumbnail error: {e}")
            self.set_file_icon('application/pdf')

    def set_file_icon(self, mime_type):
        """Set appropriate icon based on mime type"""
        # Define icon mapping with more specific types
        icon_mapping = {
            'video/': 'video.png',
            'audio/': 'audio.png',
            'image/': 'image.png',
            'application/pdf': 'pdf.png',
            'text/html': 'html.png',
            'text/plain': 'file.png',  # Added specific text/plain mapping
            'text/': 'text.png',
            'application/': 'file.png'
        }
        
        # Additional mime type mappings for specific extensions
        extension_mapping = {
            # Web files
            '.html': 'html.png',
            '.htm': 'html.png',
            '.xhtml': 'html.png',
            '.php': 'html.png',
            '.asp': 'html.png',
            '.jsx': 'html.png',
            # Text files
            '.txt': 'text.png',
            '.log': 'text.png',
            '.md': 'text.png',
            '.json': 'text.png',
            '.xml': 'text.png',
            '.csv': 'text.png',
            '.ini': 'text.png',
            '.conf': 'text.png'
        }
        
        # First check file extension
        file_ext = os.path.splitext(self.file_path)[1].lower()
        icon_file = extension_mapping.get(file_ext)
        
        # If no match in extensions, check mime type
        if not icon_file and mime_type:
            for mime_prefix, icon_name in icon_mapping.items():
                if mime_type.startswith(mime_prefix):
                    icon_file = icon_name
                    break
        
        # Default icon if no matches found
        if not icon_file:
            icon_file = 'file.png'
        
        # Construct icon path
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', icon_file)
        
        # Load and set icon
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to system icons if custom icon not found
            icon = QIcon.fromTheme('text-x-generic')
            pixmap = icon.pixmap(self.thumbnail_size)
            self.icon_label.setPixmap(pixmap)

    def mouseDoubleClickEvent(self, event):
        """Handle double click to open file"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_file()
            
    def open_file(self):
        """Open file with system default application"""
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.file_path])
            elif sys.platform == 'win32':  # Windows
                os.startfile(self.file_path)
            else:  # Linux
                subprocess.run(['xdg-open', self.file_path])
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not open file: {str(e)}")