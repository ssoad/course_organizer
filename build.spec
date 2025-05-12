# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Define base directory
BASE_DIR = os.path.abspath(os.path.dirname('__main__'))

# Get poppler path from environment
poppler_path = os.getenv('POPPLER_PATH', '/opt/homebrew/opt/poppler')

# Define icon path with absolute path
icon_path = os.path.join(BASE_DIR, 'icons', 'app.icns')

a = Analysis(
    [os.path.join(BASE_DIR, 'main.py')],
    pathex=[BASE_DIR],
    binaries=[
        (os.path.join(poppler_path, 'bin/pdftocairo'), 'poppler/bin'),
        (os.path.join(poppler_path, 'bin/pdfinfo'), 'poppler/bin'),
    ],
    datas=[
        (os.path.join(BASE_DIR, 'icons/*'), 'icons'),
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