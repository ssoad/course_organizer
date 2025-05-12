# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Define base directory - fixed to avoid __file__ issue
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.path.abspath(os.getcwd())

# Get poppler path from environment
poppler_path = os.environ.get('POPPLER_PATH', '')

# Define icon path with absolute path
icon_path = os.path.join(BASE_DIR, 'icons', 'app.icns')

# Debug output to help diagnose path issues
print(f"BASE_DIR: {BASE_DIR}")
print(f"POPPLER_PATH: {poppler_path}")
print(f"ICON_PATH: {icon_path}")

a = Analysis(
    [os.path.join(BASE_DIR, 'main.py')],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[
        (os.path.join(BASE_DIR, 'icons', '*.png'), 'icons'),  # Fixed glob pattern
        (os.path.join(BASE_DIR, 'styles.qss'), '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'PyQt6.QtSvg',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'cv2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add platform-specific binaries
if sys.platform.startswith('win'):
    a.binaries += [
        (os.path.join('poppler', 'bin', 'pdftocairo.exe'), os.path.join(poppler_path, 'pdftocairo.exe'), 'BINARY'),
        (os.path.join('poppler', 'bin', 'pdfinfo.exe'), os.path.join(poppler_path, 'pdfinfo.exe'), 'BINARY')
    ]
elif sys.platform.startswith('darwin'):
    # Try various possible locations for poppler binaries
    poppler_bin_locations = [
        os.path.join(poppler_path, 'bin'),
        os.path.join('/usr/local/bin'),
        os.path.join('/opt/homebrew/bin')
    ]
    
    pdftocairo_path = None
    pdfinfo_path = None
    
    # Find actual binary paths
    for location in poppler_bin_locations:
        if os.path.exists(os.path.join(location, 'pdftocairo')):
            pdftocairo_path = os.path.join(location, 'pdftocairo')
        if os.path.exists(os.path.join(location, 'pdfinfo')):
            pdfinfo_path = os.path.join(location, 'pdfinfo')
    
    # Add poppler binaries if found
    if pdftocairo_path and pdfinfo_path:
        a.binaries.append(('poppler/bin/pdftocairo', pdftocairo_path, 'BINARY'))
        a.binaries.append(('poppler/bin/pdfinfo', pdfinfo_path, 'BINARY'))
    else:
        print("WARNING: poppler binaries not found in expected locations")
else:  # Linux
    a.binaries += [
        (os.path.join('poppler', 'bin', 'pdftocairo'), os.path.join(poppler_path, 'bin', 'pdftocairo'), 'BINARY'),
        (os.path.join('poppler', 'bin', 'pdfinfo'), os.path.join(poppler_path, 'bin', 'pdfinfo'), 'BINARY')
    ]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Course Tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Course Tracker',
)

app = BUNDLE(
    coll,
    name='Course Tracker.app',
    icon=icon_path if os.path.exists(icon_path) else None,
    bundle_identifier='com.coursetracker.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.15',
        'CFBundleDisplayName': 'Course Tracker',
        'CFBundleName': 'Course Tracker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    },
)