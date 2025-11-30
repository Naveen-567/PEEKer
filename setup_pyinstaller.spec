# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('app_icon.icns', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'pandas',
        'numpy',
        'scipy',
        'openpyxl',
        'PIL',
        'PIL._tkinter_finder',
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
    name='PEEKer',
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
    icon='app_icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PEEKer',
)

app = BUNDLE(
    coll,
    name='PEEKer.app',
    icon='app_icon.icns',
    bundle_identifier='com.iitd.peeker',
    info_plist={
        'CFBundleName': 'PEEKer',
        'CFBundleDisplayName': 'PEEKer',
        'CFBundleGetInfoString': 'HPLC AUC Analysis Tool',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 IITD. All rights reserved.',
        'NSHighResolutionCapable': True,
    },
)