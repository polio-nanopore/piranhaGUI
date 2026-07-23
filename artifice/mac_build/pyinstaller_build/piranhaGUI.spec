# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['../../artifice.pyw'],
    pathex=[],
    binaries=[],
    datas=[('../../config.yml', '.'), ('../../resources', './resources')],
    hiddenimports=[],
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
    name='piranhaGUIv1.6.13',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../resources/piranha_resized.icns',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='artifice',
)
app = BUNDLE(
    coll,
    name='piranhaGUIv1.6.13.app',
    icon='../../resources/piranha_resized.icns',
    bundle_identifier=None,
)
