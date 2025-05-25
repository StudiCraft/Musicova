# This is a PyInstaller spec file. It is used by PyInstaller to package the
# Musicova Python application (musicova.py) into a standalone executable,
# bundling necessary assets like the logo.
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Python\\musicova.py'],
    pathex=[],
    binaries=[],
    datas=[('Python/Musicova logo v2.png', 'Python')],
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
    a.binaries,
    a.datas,
    [],
    name='Musicova',
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
)
