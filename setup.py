"""
Setup script for creating PEEKer Mac application
"""
from setuptools import setup

APP = ['run_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'matplotlib', 'pandas', 'numpy', 'scipy', 'openpyxl'],
    'iconfile': 'app_icon.icns',  # Your .icns file
    'plist': {
        'CFBundleName': 'PEEKer',
        'CFBundleDisplayName': 'PEEKer',
        'CFBundleGetInfoString': 'HPLC AUC Analysis Tool',
        'CFBundleIdentifier': 'com.iitd.peeker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 IITD. All rights reserved.',
        'NSHighResolutionCapable': True,
    },
}

setup(
    name='PEEKer',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)