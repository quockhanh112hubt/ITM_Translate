# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ITM_Translate.py'],
    pathex=[],
    binaries=[],
    datas=[('Resource/icon.ico', 'Resource')],
    hiddenimports=['ttkbootstrap', 'pydantic_core', 'pydantic_core._pydantic_core'],
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
    upx=True,
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
