import PyInstaller.__main__
import os
import shutil

def build_app():
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # Create icons directory in dist
    icons_dir = os.path.join('dist', 'Course Organizer.app', 'Contents', 'MacOS', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    # Copy icons
    for icon in ['file.png', 'video.png', 'audio.png', 'pdf.png']:
        src = os.path.join('icons', icon)
        dst = os.path.join(icons_dir, icon)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # Build the app
    PyInstaller.__main__.run([
        'main.py',
        '--name=Course Organizer',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--add-data=icons:icons',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=cv2',
        '--collect-all=cv2',
        '--noupx',  # Disable UPX compression
        '--optimize=2',  # Enable Python optimization
    ])

if __name__ == '__main__':
    build_app()