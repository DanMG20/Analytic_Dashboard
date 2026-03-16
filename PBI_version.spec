# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

# 1. Copy hidden metadata needed by APIs and resilient algorithms
datas = []
datas += copy_metadata('tenacity')
datas += copy_metadata('google-api-python-client')

# 2. Include local project directories and required static files
datas += [
    ('api', 'api'),
    ('database', 'database'),
    ('models', 'models'),
    ('scheduler', 'scheduler'),
    ('services', 'services'),
    ('utils', 'utils'),
    ('credentials/google_credentials.json', 'credentials'),
]

# 3. Add hidden dependencies often missed by the PyInstaller analysis phase
hiddenimports = [
    'pandas',
    'sqlite3',
    'apscheduler',
    'pydantic',
    'googleapiclient',
    'google_auth_oauthlib',
    'charset_normalizer',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['streamlit', 'plotly', 'altair', 'bokeh'], # Explicitly exclude UI heavyweights
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTubeETL_Daemon', # Renamed to reflect its new back-end nature
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Keep it True for initial debugging. Change to False for silent background execution later.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE', 
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTubeETL_Daemon',
)