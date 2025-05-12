#!/bin/bash

# Install requirements
pip3 install -r requirements.txt

# Install poppler if not present
if ! command -v pdftocairo &> /dev/null
then
    echo "Installing poppler..."
    brew install poppler
fi

# Get poppler path
POPPLER_PATH=$(brew --prefix poppler)
echo "Poppler path: $POPPLER_PATH"

# Ensure icons directory exists
mkdir -p icons

# Copy system icons if custom ones don't exist
if [ ! -f icons/folder.png ]; then
    cp /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericFolderIcon.icns icons/folder.png
fi

if [ ! -f icons/file.png ]; then
    cp /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericDocumentIcon.icns icons/file.png
fi

# Export for PyInstaller
export POPPLER_PATH
export QT_MAC_WANTS_LAYER=1

# Clean previous builds
rm -rf build dist

# Build the app
python3 -m PyInstaller build.spec --clean --noconfirm

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