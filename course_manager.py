import os
from pathlib import Path
import json
from natsort import natsorted

class CourseManager:
    def __init__(self):
        self.config_dir = Path.home() / '.course_organizer'
        self.progress_file = self.config_dir / 'progress.json'
        self.directories_file = self.config_dir / 'directories.json'
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load saved data
        self.progress = self._load_progress()
        self.directories = self._load_directories()
        
        # Define excluded file types
        self.excluded_extensions = {
            '.srt',  # SubRip subtitles
            '.vtt',  # WebVTT subtitles
            '.sub',  # SubViewer subtitles
            '.smi',  # SAMI subtitles
            '.ssa',  # SubStation Alpha
            '.ass',  # Advanced SubStation Alpha
            '.idx',  # VobSub index
            '.mks',  # Matroska subtitles
        }

    def _load_progress(self):
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading progress: {e}")
        return {}

    def _save_progress(self):
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def _load_directories(self):
        if self.directories_file.exists():
            try:
                with open(self.directories_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading directories: {e}")
        return []

    def _save_directories(self):
        try:
            with open(self.directories_file, 'w') as f:
                json.dump(self.directories, f, indent=2)
        except Exception as e:
            print(f"Error saving directories: {e}")

    def add_directory(self, directory):
        if directory and directory not in self.directories:
            self.directories.append(directory)
            self._save_directories()
            return True
        return False

    def remove_directory(self, directory):
        if directory in self.directories:
            self.directories.remove(directory)
            self._save_directories()
            return True
        return False

    def set_excluded_extensions(self, extensions):
        """Update the list of excluded file extensions."""
        if isinstance(extensions, (list, set)):
            self.excluded_extensions = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                                     for ext in extensions}
    
    def add_excluded_extension(self, extension):
        """Add a single extension to excluded list."""
        if extension:
            ext = extension.lower()
            ext = ext if ext.startswith('.') else f'.{ext}'
            self.excluded_extensions.add(ext)
    
    def remove_excluded_extension(self, extension):
        """Remove a single extension from excluded list."""
        if extension:
            ext = extension.lower()
            ext = ext if ext.startswith('.') else f'.{ext}'
            self.excluded_extensions.discard(ext)
    
    def is_excluded_file(self, file_path):
        """Check if a file should be excluded."""
        return Path(file_path).suffix.lower() in self.excluded_extensions

    def get_directory_contents(self, directory):
        if not os.path.exists(directory):
            return [], []

        items = os.listdir(directory)
        subdirs = []
        files = []

        for item in natsorted(items):
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                progress = self.calculate_directory_progress(full_path)
                subdirs.append((full_path, progress))
            elif os.path.isfile(full_path) and not self.is_excluded_file(full_path):
                watched = self.progress.get(full_path, False)
                files.append((full_path, watched))

        return subdirs, files

    def calculate_directory_progress(self, directory):
        total_files = 0
        watched_files = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                if not self.is_excluded_file(full_path):
                    total_files += 1
                    if self.progress.get(full_path, False):
                        watched_files += 1
        
        return (watched_files / total_files * 100) if total_files > 0 else 0

    def update_file_progress(self, file_path, watched):
        self.progress[file_path] = watched
        self._save_progress()