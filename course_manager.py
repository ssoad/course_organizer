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
        self.directories = self.load_directories()
        self.watched_files = self.load_watched_files()
        self.progress = self.load_progress()
        
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

    def load_progress(self):
        """Load progress data from file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'progress.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading progress: {e}")
        return {}

    def save_progress(self):
        """Save progress data to file"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), 'config')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'progress.json')
            with open(config_path, 'w') as f:
                json.dump(self.progress, f)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def load_directories(self):
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
        """Add directory with natural sorting"""
        if directory not in self.directories:
            self.directories.append(directory)
            # Sort directories naturally
            self.directories = natsorted(self.directories)
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
        """Get naturally sorted contents of directory with watched states"""
        subdirs = []
        files = []
        
        try:
            # Get all items and sort them naturally
            items = natsorted(os.listdir(directory))
            
            for item in items:
                item_path = os.path.join(directory, item)
                
                if os.path.isdir(item_path):
                    progress = self.calculate_directory_progress(item_path)
                    subdirs.append((item_path, progress))
                else:
                    # Skip excluded file types
                    if not self.is_excluded_file(item_path):
                        is_watched = self.is_file_watched(item_path)
                        files.append((item_path, is_watched))
                    
            # Sort subdirectories and files naturally by their paths
            subdirs = natsorted(subdirs, key=lambda x: x[0])
            files = natsorted(files, key=lambda x: x[0])
            
            return subdirs, files
        except Exception as e:
            raise Exception(f"Error reading directory: {e}")

    def calculate_directory_progress(self, directory):
        """Calculate directory progress based on watched files"""
        if not os.path.exists(directory):
            return 0
            
        total_files = 0
        watched_files = 0
        
        # Count files in directory
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                # Only count non-excluded files
                if not self.is_excluded_file(file_path):
                    total_files += 1
                    if self.is_file_watched(file_path):
                        watched_files += 1
        
        return (watched_files / total_files * 100) if total_files > 0 else 0

    def update_file_progress(self, file_path, watched):
        self.progress[file_path] = watched
        self.save_progress()

    def load_watched_files(self):
        """Load watched files from config, defaulting to False"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'watched.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    # Ensure all values are explicitly boolean
                    return {
                        directory: {
                            filename: bool(watched)
                            for filename, watched in files.items()
                        }
                        for directory, files in data.items()
                    }
        except Exception as e:
            print(f"Error loading watched files: {e}")
        return {}

    def save_watched_files(self):
        """Save watched files to config with explicit False values"""
        try:
            config_dir = os.path.join(os.path.dirname(__file__), 'config')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'watched.json')
            
            # Ensure all values are explicitly False if not True
            watched_data = {}
            for directory, files in self.watched_files.items():
                watched_data[directory] = {
                    filename: bool(watched) 
                    for filename, watched in files.items()
                }
            
            with open(config_path, 'w') as f:
                json.dump(watched_data, f, indent=2, default=lambda x: False)
                
        except Exception as e:
            print(f"Error saving watched files: {e}")

    def update_file_watched_state(self, file_path, watched):
        """Update file watched state and recalculate progress"""
        directory = os.path.dirname(file_path)
        if directory not in self.watched_files:
            self.watched_files[directory] = {}
        
        self.watched_files[directory][os.path.basename(file_path)] = watched
        self.save_watched_files()
        
        # Update progress
        progress = self.calculate_directory_progress(directory)
        self.progress[directory] = progress
        self.save_progress()
        
        return progress

    def is_file_watched(self, file_path):
        """Check if a file is watched"""
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return self.watched_files.get(directory, {}).get(filename, False)