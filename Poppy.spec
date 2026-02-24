# -*- mode: python ; coding: utf-8 -*-
import os

# Include the vosk package directory so its DLLs are available at runtime.
# PyInstaller doesn't bundle it by default; without this, add_dll_directory() fails.
try:
    import vosk
    vosk_dir = os.path.dirname(vosk.__file__)
    vosk_datas = [(vosk_dir, 'vosk')]
except ImportError:
    vosk_datas = []
    print('Warning: vosk not found. Install it in this environment before building.')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('model', 'model')] + vosk_datas,
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Poppy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Poppy',
)
