# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# Collect all data files for ttkbootstrap
ttkbootstrap_datas = collect_data_files('ttkbootstrap')

# Enhanced collection for problematic packages
win32_submodules = collect_submodules('win32com')
pythoncom_submodules = collect_submodules('pythoncom')
pywintypes_submodules = collect_submodules('pywintypes')

# Comprehensive pydantic collection
pydantic_datas, pydantic_binaries, pydantic_hiddenimports = collect_all('pydantic')
pydantic_core_datas, pydantic_core_binaries, pydantic_core_hiddenimports = collect_all('pydantic_core')

a = Analysis(
    ['ITM_Translate.py'],
    pathex=[],
    binaries=[] + pydantic_binaries + pydantic_core_binaries,
    datas=[
        ('Resource/icon.ico', 'Resource'),
        ('Resource/English.ng', 'Resource'),
        ('Resource/icon_OFF.ico', 'Resource'),
        ('Resource/icon_ON.ico', 'Resource'),
        ('Resource/Vietnam.png', 'Resource'),
        ('version.json', '.'),
        ('core/version.json', 'core'),
    ] + ttkbootstrap_datas + pydantic_datas + pydantic_core_datas,
    hiddenimports=[
        # GUI frameworks
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'ttkbootstrap.style',
        'ttkbootstrap.constants',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        # Windows COM and API
        'pythoncom',
        'win32com',
        'win32com.client',
        'win32com.client.gencache',
        'win32com.client.dynamic',
        'win32com.server',
        'pywintypes',
        'win32api',
        'win32gui',
        'win32con',
        'win32process',
        'win32event',
        'win32file',
        # Input handling
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        # AI and HTTP
        'google.generativeai',
        'requests',
        'requests.adapters',
        'requests.packages',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        # Image processing
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        # Pydantic - CRITICAL for DLL fix
        'pydantic',
        'pydantic.main',
        'pydantic.fields',
        'pydantic.types',
        'pydantic.validators',
        'pydantic.utils',
        'pydantic.json',
        'pydantic.dataclasses',
        'pydantic.env_settings',
        'pydantic_core',
        'pydantic_core._pydantic_core',
        'typing_extensions',
        'annotated_types',
        # System modules
        'json',
        'threading',
        'tempfile',
        'subprocess',
        'shutil',
        'zipfile',
        'queue',
        'ctypes',
        'ctypes.wintypes',
        'ssl',
        'platform',
        'stat',
        'os',
        'sys',
    ] + win32_submodules + pythoncom_submodules + pywintypes_submodules + pydantic_hiddenimports + pydantic_core_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ITM_Translate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # CRITICAL: Disable UPX compression to prevent DLL conflicts
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Resource\\icon.ico'],
    # Additional flags to fix DLL loading
    include_msvcrt=True,  # Include Microsoft Visual C++ Runtime
)
