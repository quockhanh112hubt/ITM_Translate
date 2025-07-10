# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files for ttkbootstrap
ttkbootstrap_datas = collect_data_files('ttkbootstrap')

# Collect all submodules for problematic packages
win32_submodules = collect_submodules('win32com')
pythoncom_submodules = collect_submodules('pythoncom')
pywintypes_submodules = collect_submodules('pywintypes')
pydantic_submodules = collect_submodules('pydantic')
pydantic_core_submodules = collect_submodules('pydantic_core')

a = Analysis(
    ['ITM_Translate.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Resource/icon.ico', 'Resource'),
        ('version.json', '.'),
        ('core/version.json', 'core'),
    ] + ttkbootstrap_datas,
    hiddenimports=[
        'ttkbootstrap',
        'ttkbootstrap.themes',
        'ttkbootstrap.style',
        'ttkbootstrap.constants',
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
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'google.generativeai',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'requests',
        'requests.adapters',
        'requests.packages',
        'urllib3',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'json',
        'threading',
        'tempfile',
        'subprocess',
        'shutil',
        'zipfile',
        'queue',
        'ctypes',
        'ctypes.wintypes',
        'pydantic',
        'pydantic_core',
        'pydantic_core._pydantic_core',
        'typing_extensions',
        'annotated_types',
    ] + win32_submodules + pythoncom_submodules + pywintypes_submodules + pydantic_submodules + pydantic_core_submodules,
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
    upx=False,  # Disable UPX compression to avoid DLL issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Resource\\icon.ico'],
)
