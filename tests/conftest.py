"""pytest setup: each test session uses a temporary work folder, with Mockup Studio folders to migrate."""
import io
import json
import os
import sys
import tempfile

import pytest
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
# app.py sets its paths (and migrates old folders) when imported: the temporary work folder must exist first.
HOME = tempfile.mkdtemp(prefix='mockup-workflow-tests-')
os.environ['MW_HOME'] = HOME

# A work folder as Mockup Studio left it: Spanish folder and group names, and paths that point to them.
os.makedirs(os.path.join(HOME, 'Galería de mockups', 'Exterior'))
os.makedirs(os.path.join(HOME, 'Flujos'))
os.makedirs(os.path.join(HOME, 'data', 'mockups'))
open(os.path.join(HOME, 'Galería de mockups', 'Exterior', 'Old.psd'), 'wb').write(b'x')
open(os.path.join(HOME, 'Flujos', 'Mine.mwf'), 'w').write('<mockupWorkflow version="1"/>')
with open(os.path.join(HOME, 'data', 'mockups', 'old-111111.json'), 'w', encoding='utf-8') as f:
    json.dump({'id': 'old-111111', 'name': 'Old', 'file': 'Old.psd', 'path': 'Galería de mockups/Exterior/Old.psd',
               'profilePath': 'Galería de mockups/Exterior/Old.mockup.json', 'category': 'Exterior',
               'smartObjects': []}, f, ensure_ascii=False)
with open(os.path.join(HOME, 'data', 'workflow.json'), 'w', encoding='utf-8') as f:
    json.dump({'title': 'Mine', 'filePath': os.path.join(HOME, 'Flujos', 'Mine.mwf')}, f, ensure_ascii=False)


@pytest.fixture(scope='session')
def server():
    import app
    return app


@pytest.fixture()
def client(server):
    server.app.config['TESTING'] = True
    return server.app.test_client()


def png_bytes(size=(64, 48), color=(255, 255, 255, 255), transparent=True):
    img = Image.new('RGBA', size, (0, 0, 0, 0) if transparent else color)
    if transparent:
        img.paste(Image.new('RGBA', (size[0] // 2, size[1] // 2), color), (size[0] // 4, size[1] // 4))
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return buf.getvalue()


@pytest.fixture()
def png():
    return png_bytes
