# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Get poppler path - assumes it's installed via homebrew
poppler_path = '/opt/homebrew/Cellar/poppler/23.11.0/bin'  # Update version as needed
pdf2image_path = 'pdf2image'

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        (os.path.join(poppler_path, 'pdftocairo'), 'poppler/bin'),
        (os.path.join(poppler_path, 'pdfinfo'), 'poppler/bin'),
    ],
    datas=[
        ('icons/*', 'icons'),
    ],
    hiddenimports=['PIL._tkinter_finder'],
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
    icon=None,
    bundle_identifier='com.coursetracker.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.15',
        'NSDocumentTypes': [{
            'CFBundleTypeName': 'PDF',
            'CFBundleTypeRole': 'Viewer',
            'LSHandlerRank': 'Alternate',
            'LSItemContentTypes': ['com.adobe.pdf'],
        }],
    },
)