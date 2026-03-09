# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# 1. Copiamos la metadata oculta que Streamlit y otras librerías necesitan
datas = []
datas += copy_metadata('streamlit')
datas += collect_data_files('streamlit')
datas += copy_metadata('plotly')
datas += copy_metadata('tenacity')
datas += copy_metadata('google-api-python-client')

# 2. Le decimos que incluya tus carpetas locales
datas += [
    ('api', 'api'),
    ('database', 'database'),
    ('models', 'models'),
    ('scheduler', 'scheduler'),
    ('services', 'services'),
    ('ui', 'ui'),
    ('utils', 'utils'),
    ('credentials/google_credentials.json', 'credentials'),
]

# 3. Agregamos dependencias ocultas que Pandas y Streamlit a veces pierden
hiddenimports = [
    'streamlit',
    'plotly',
    'pandas',
    'sqlite3',
    'apscheduler',
    'pydantic',
    'googleapiclient',
    'google_auth_oauthlib',
    'charset_normalizer',
    'streamlit.runtime.scriptrunner.magic_funcs'
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
    name='AnalyticDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Déjalo en True la primera vez para ver si hay errores. Luego puedes pasarlo a False.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE', # Si tienes un .ico, pon la ruta aquí (ej. 'assets/icon.ico')
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AnalyticDashboard',
)