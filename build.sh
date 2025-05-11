#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Install poppler if not present
if ! command -v pdftocairo &> /dev/null
then
    echo "Installing poppler..."
    brew install poppler
fi

# Clean previous builds
rm -rf build dist

# Build the app
pyinstaller build.spec

# Create dmg (optional)
create-dmg \
  --volname "Course Tracker" \
  --volicon "icons/app.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Course Tracker.app" 175 120 \
  --hide-extension "Course Tracker.app" \
  --app-drop-link 425 120 \
  "Course Tracker.dmg" \
  "dist/"