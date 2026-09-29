# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project = Path(SPECPATH)

block_cipher = None


a = Analysis(
    [str(project / "app.py")],
    pathex=[str(project)],
    binaries=[],
    datas=[
        (str(project / "img" / "2.png"), "img"),
        (str(project / "img" / "2.ico"), "img"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SteamSwapper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(project / "img" / "2.ico"),
)
