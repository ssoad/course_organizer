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

    def _load_progress(self):
        """Load progress data from JSON file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading progress: {e}")
        return {}

    def _save_progress(self):
        """Save progress data to JSON file."""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def _load_directories(self):
        """Load saved directories from JSON file."""
        if self.directories_file.exists():
            try:
                with open(self.directories_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading directories: {e}")
        return []

    def _save_directories(self):
        """Save directories to JSON file."""
        try:
            with open(self.directories_file, 'w') as f:
                json.dump(self.directories, f, indent=2)
        except Exception as e:
            print(f"Error saving directories: {e}")

    def add_directory(self, directory):
        """Add a directory to tracking."""
        if directory and directory not in self.directories:
            self.directories.append(directory)
            self._save_directories()
            return True
        return False

    def remove_directory(self, directory):
        """Remove a directory from tracking."""
        if directory in self.directories:
            self.directories.remove(directory)
            self._save_directories()
            return True
        return False

    def get_directory_contents(self, directory):
        """Get sorted contents of a directory."""
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
            elif os.path.isfile(full_path):
                watched = self.progress.get(full_path, False)
                files.append((full_path, watched))

        return subdirs, files

    def calculate_directory_progress(self, directory):
        """Calculate watch progress for a directory."""
        total_files = 0
        watched_files = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                total_files += 1
                if self.progress.get(full_path, False):
                    watched_files += 1
        
        return (watched_files / total_files * 100) if total_files > 0 else 0

    def update_file_progress(self, file_path, watched):
        """Update progress for a file."""
        self.progress[file_path] = watched
        self._save_progress()