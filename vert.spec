# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
root_dir = Path.cwd()

datas = [
    (str(root_dir / 'ui' / 'styles.qss'), 'ui'),
    (str(root_dir / 'assets' / 'fonts'), 'assets/fonts'),
    (str(root_dir / 'Vert.png'), '.'),
    (str(root_dir / 'Vert.ico'), '.'),
    (str(root_dir / 'engines' / 'ffmpeg.exe'), 'engines'),
]

a = Analysis(
    ['main.py'],
    pathex=[str(root_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'PIL',
        'pymupdf',
        'fitz',
        'pypdf',
        'pdf2docx',
        'pdfplumber',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'tkinter', 'pandas', 'IPython'],
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
    name='Vert',
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
    icon=str(root_dir / 'Vert.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Vert',
)
