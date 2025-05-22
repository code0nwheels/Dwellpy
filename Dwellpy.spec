# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Dwellpy - LAUNCHER VERSION
Usage: pyinstaller dwellpy.spec
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path.cwd()

# Analysis of the main script
a = Analysis(
    # Entry point - use the LAUNCHER script in project root
    ['launcher.py'],  # CHANGED: Now points to launcher.py instead of dwellpy/main.py
    
    # Paths to search for modules
    pathex=[str(project_root)],
    
    # Binary files to include (usually auto-detected, but we can specify)
    binaries=[],
    
    # Data files to include
    datas=[
        # Include documentation
        ('docs/README.md', 'docs'),
        # Include any config files if you have them
        # ('dwellpy/config/*.json', 'dwellpy/config'),
    ],
    
    # Hidden imports that PyInstaller might not detect
    hiddenimports=[
        'pynput',
        'pynput.mouse',
        'pynput.keyboard', 
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        # Include all your package modules explicitly
        'dwellpy',
        'dwellpy.main',  # ADDED: Make sure main module is included
        'dwellpy.core',
        'dwellpy.core.dwell_algorithm',
        'dwellpy.core.click_manager', 
        'dwellpy.core.input_manager',
        'dwellpy.ui',
        'dwellpy.ui.ui_manager',
        'dwellpy.ui.window_manager',
        'dwellpy.ui.dialogs',
        'dwellpy.ui.dialogs.settings_dialog',
        'dwellpy.ui.dialogs.exit_dialog',
        'dwellpy.managers',
        'dwellpy.managers.button_manager',
        'dwellpy.managers.settings_manager',
        'dwellpy.managers.exit_manager',
        'dwellpy.config',
        'dwellpy.config.constants',
        'dwellpy.utils', 
        'dwellpy.utils.helpers',
        'dwellpy.__version__',  # ADDED: Make sure version is included
    ],
    
    # Packages to exclude (reduces size)
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
    ],
    
    # Additional options
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Bundle everything into a single directory
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ONE FILE VERSION - Include all binaries, zipfiles, and datas in the EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,    # Include binaries in the exe
    a.zipfiles,    # Include zipfiles in the exe  
    a.datas,       # Include datas in the exe
    [],
    name='Dwellpy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # Use system temp directory
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,   # Request admin privileges (for mouse control)
    uac_uiaccess=True,
)