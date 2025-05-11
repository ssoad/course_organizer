import sys
import os
import json
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from CourseTracker import CourseTrackerApp

# Configuration
APP_DIR = Path.home() / '.course_organizer'
PROGRESS_FILE = APP_DIR / 'progress.json'
LOG_FILE = APP_DIR / 'app.log'
DIRECTORIES_FILE = APP_DIR / 'directories.json'

# Ensure app directory exists
APP_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_progress():
    """Load progress data from JSON file."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading progress: {e}")
            print(f"Could not load progress data: {e}")
    return {}

def save_progress(data):
    """Save progress data to JSON file."""
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logging.info("Progress saved successfully")
    except Exception as e:
        logging.error(f"Error saving progress: {e}")
        print(f"Could not save progress data: {e}")

def load_directories():
    """Load saved directories from JSON file."""
    if DIRECTORIES_FILE.exists():
        try:
            with open(DIRECTORIES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading directories: {e}")
    return []

def save_directories(directories):
    """Save directories to JSON file."""
    try:
        with open(DIRECTORIES_FILE, 'w') as f:
            json.dump(directories, f, indent=2)
    except Exception as e:
        print(f"Error saving directories: {e}")

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = CourseTrackerApp()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()