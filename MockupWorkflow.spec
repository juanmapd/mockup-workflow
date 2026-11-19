# -*- mode: python ; coding: utf-8 -*-
# Packages Mockup Workflow as a Mac app:  .venv/bin/pyinstaller --noconfirm MockupWorkflow.spec
# Output: dist/Mockup Workflow.app

import os, sys
sys.path.insert(0, os.path.abspath('.'))
from version import APP_NAME, BUNDLE_ID, __copyright__, __version__ as VERSION

a = Analysis(
    ['desktop.py'],
    pathex=['.'],
    datas=[('static', 'static'), ('README.md', '.'), ('LICENSE', '.'), ('CHANGELOG.md', '.')],
    hiddenimports=['app', 'engine', 'version', 'webview.platforms.cocoa'],
    excludes=['tkinter', 'matplotlib', 'IPython', 'pytest', 'pandas'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
    argv_emulation=True,          # the flow file the app is opened with arrives in sys.argv
    icon='assets/MockupWorkflow.icns',
)

coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME)

app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon='assets/MockupWorkflow.icns',
    bundle_identifier=BUNDLE_ID,
    version=VERSION,
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleShortVersionString': VERSION,
        'CFBundleVersion': VERSION,
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.graphics-design',
        'NSHumanReadableCopyright': f'{__copyright__}. MIT License.',
        # The app's server listens on 127.0.0.1: allow local networking without HTTPS.
        'NSAppTransportSecurity': {'NSAllowsLocalNetworking': True},
        # Workflow files (.mwf): a custom XML-based type opened by this app.
        'UTExportedTypeDeclarations': [{
            'UTTypeIdentifier': f'{BUNDLE_ID}.flow',
            'UTTypeDescription': 'Mockup Workflow file',
            'UTTypeConformsTo': ['public.xml', 'public.data'],
            'UTTypeTagSpecification': {'public.filename-extension': ['mwf'],
                                       'public.mime-type': ['application/xml']},
        }],
        'CFBundleDocumentTypes': [{
            'CFBundleTypeName': 'Mockup Workflow file',
            'CFBundleTypeRole': 'Editor',
            'LSHandlerRank': 'Owner',
            'LSItemContentTypes': [f'{BUNDLE_ID}.flow'],
            'CFBundleTypeIconFile': 'MockupWorkflow.icns',
        }],
    },
)
