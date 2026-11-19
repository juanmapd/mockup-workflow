#!/usr/bin/env python3
"""
Mockup Workflow as a Mac app: a native window (WebKit, via pywebview) with the local server inside.

  .venv/bin/python desktop.py               → opens the window
  .venv/bin/python desktop.py workflow.mwf  → opens the window with that workflow

The work folder (gallery, workflows and results) is stored in
~/Library/Application Support/Mockup Workflow/config.json and is changed from the File menu.
"""
import json
import os
import socket
import subprocess
import sys
import threading
import urllib.parse
import urllib.request

from version import APP_NAME, FLOW_EXT, __version__  # noqa: E402

SUPPORT = os.path.expanduser(f'~/Library/Application Support/{APP_NAME}')
CONFIG = os.path.join(SUPPORT, 'config.json')
FROZEN = getattr(sys, 'frozen', False)
LEGACY_NAME = 'Mockup Studio'   # previous name of the app: its settings and default work folder are migrated

# Settings of Mockup Studio (work folder and WebKit storage) move to the new support folder.
_legacy_support = os.path.expanduser(f'~/Library/Application Support/{LEGACY_NAME}')
if os.path.isdir(_legacy_support) and not os.path.exists(SUPPORT):
    os.rename(_legacy_support, SUPPORT)
os.makedirs(SUPPORT, exist_ok=True)


# ================================================================ work folder
def read_config():
    try:
        with open(CONFIG, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_config(cfg):
    with open(CONFIG, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)


def work_folder():
    home = read_config().get('home')
    legacy_home = os.path.expanduser(f'~/Documents/{LEGACY_NAME}')
    new_home = os.path.expanduser(f'~/Documents/{APP_NAME}')
    if home and os.path.abspath(home) == legacy_home and os.path.isdir(home) and not os.path.exists(new_home):
        os.rename(home, new_home)   # Mockup Studio's default work folder takes the new name
        home = new_home
        write_config({**read_config(), 'home': home})
    if home and os.path.isdir(home):
        return home
    # From source: the project folder. Packaged: ~/Documents/Mockup Workflow.
    home = os.path.expanduser(f'~/Documents/{APP_NAME}') if FROZEN else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(home, exist_ok=True)
    write_config({**read_config(), 'home': home})
    return home


# The packaged app has no terminal: its output goes to ~/Library/Logs/Mockup Workflow.log.
if FROZEN:
    _log = open(os.path.expanduser(f'~/Library/Logs/{APP_NAME}.log'), 'a', buffering=1, encoding='utf-8')
    sys.stdout = sys.stderr = _log

HOME = work_folder()
os.environ['MW_HOME'] = HOME

import webview  # noqa: E402  (after setting MW_HOME)
from webview.menu import Menu, MenuAction, MenuSeparator  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

import app as server  # noqa: E402

window = None


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


PORT = free_port()
BASE = f'http://127.0.0.1:{PORT}'
FLOW_TYPES = ('Mockup Workflow file (*.mwf)',)


def first(result):
    if not result:
        return None
    return result if isinstance(result, str) else result[0]


# ================================================================ API for the interface (window.pywebview.api)
class Api:
    def save_flow(self, xml, path=None, suggested='Workflow' + FLOW_EXT):
        """Saves the workflow XML. Without a path, asks where with the macOS dialog. Returns the path."""
        if not path:
            path = first(window.create_file_dialog(webview.FileDialog.SAVE, directory=server.FLOWS,
                                                   save_filename=suggested, file_types=FLOW_TYPES))
            if not path:
                return None
        if not path.lower().endswith(FLOW_EXT):
            path += FLOW_EXT
        with open(path, 'w', encoding='utf-8') as f:
            f.write(xml)
        return path

    def pick_design(self):
        """Picks a design with the macOS dialog and returns its path (it is stored in the .mwf)."""
        return first(window.create_file_dialog(webview.FileDialog.OPEN, directory=os.path.expanduser('~/Desktop'),
                                               file_types=('Images (*.png;*.svg;*.jpg;*.jpeg;*.webp)',)))

    def read_file(self, path):
        """Contents of a file in base64 (to draw SVGs chosen with the native dialog)."""
        import base64
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()

    def open_flow(self):
        path = first(window.create_file_dialog(webview.FileDialog.OPEN, directory=server.FLOWS, file_types=FLOW_TYPES))
        return self.read_flow(path) if path else None

    def read_flow(self, path):
        with open(path, encoding='utf-8') as f:
            return {'path': path, 'xml': f.read()}

    def download(self, url, suggested):
        """Saves a file from the local server (a composite or a .zip) where the user chooses."""
        downloads = os.path.expanduser('~/Downloads')
        path = first(window.create_file_dialog(webview.FileDialog.SAVE, directory=downloads, save_filename=suggested))
        if not path:
            return None
        with urllib.request.urlopen(BASE + url) as r, open(path, 'wb') as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
        return path

    def reveal(self, path):
        subprocess.Popen(['open', '-R', path])

    def work_folder(self):
        return HOME


api = Api()


# ================================================================ menus
def js(code):
    if window:
        window.evaluate_js(code)


def choose_work_folder():
    folder = first(window.create_file_dialog(webview.FileDialog.FOLDER, directory=HOME))
    if not folder or os.path.abspath(folder) == os.path.abspath(HOME):
        return
    write_config({**read_config(), 'home': folder})
    if FROZEN:   # relaunches the app so it uses the new folder
        bundle = os.path.abspath(os.path.join(sys.executable, '..', '..', '..'))
        subprocess.Popen(['/bin/sh', '-c', f'sleep 1; open -n "{bundle}"'])
        window.destroy()
    else:
        js("toast('Work folder changed. Quit and reopen Mockup Workflow to use it.')")


MENU = [
    Menu('File', [
        MenuAction('New Workflow…', lambda: js('requestNew()')),
        MenuAction('Open Workflow…  ⌘O', lambda: js('openFlow()')),
        MenuSeparator(),
        MenuAction('Save  ⌘S', lambda: js('saveFlowFile(false)')),
        MenuAction('Save As…  ⇧⌘S', lambda: js('saveFlowFile(true)')),
        MenuSeparator(),
        MenuAction('Show Gallery in Finder', lambda: subprocess.Popen(['open', server.GALLERY])),
        MenuAction('Show Work Folder', lambda: subprocess.Popen(['open', HOME])),
        MenuAction('Change Work Folder…', choose_work_folder),
    ]),
    Menu('Help', [
        MenuAction(f'About {APP_NAME}', lambda: js('openAbout()')),
        MenuAction('Show README', lambda: subprocess.Popen(['open', os.path.join(server.CODE, 'README.md')])),
    ]),
    Menu('View', [
        MenuAction('Fit Canvas', lambda: js('fitZoom()')),
        MenuAction('Arrange Nodes', lambda: js('arrange()')),
        MenuAction('Light or Dark Mode', lambda: js("document.getElementById('btn-theme').click()")),
    ]),
]


# ================================================================ startup
def start_server():
    """
    Starts the server BEFORE opening the window: make_server already leaves the port listening, so WebKit never
    requests the page from a server that does not exist yet (that left the window blank without retrying).
    """
    httpd = make_server('127.0.0.1', PORT, server.app, threaded=True)
    server.start_background()
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


# If the first load fails, WebKit leaves the window blank: this page retries until the server answers.
LOADING_HTML = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
html,body{height:100%;margin:0;background:#fff;color:#6e7489;font:15px -apple-system,system-ui,sans-serif}
body{display:grid;place-items:center}@media(prefers-color-scheme:dark){html,body{background:#161925;color:#9096ab}}
p{opacity:0;animation:s 0s 1.5s forwards}@keyframes s{to{opacity:1}}
</style></head><body><p>Opening Mockup Workflow…</p><script>
(function go(){fetch('{{BASE}}/api/about',{mode:'no-cors',cache:'no-store'}).then(function(){location.replace('{{URL}}')})
.catch(function(){setTimeout(go,400)})})();</script></body></html>'''


def diagnose():
    """MW_DIAG=1: saves a snapshot of what WebKit draws and the window state (for support)."""
    import time
    time.sleep(6)
    try:
        import AppKit
        import WebKit
        from PyObjCTools import AppHelper
        from webview.platforms import cocoa
        bv = cocoa.BrowserView.instances.get(window.uid)
        out = os.path.join(SUPPORT, 'diagnostic.png')

        def check():
            nswin, wv = bv.window, bv.webview
            print('DIAG window', nswin.frame(), 'visible', nswin.isVisible(), 'webview', wv.frame(),
                  'hidden', wv.isHidden(), 'subviews', [type(v).__name__ for v in nswin.contentView().subviews()], flush=True)

            def done(img, err):
                if img is None:
                    print('DIAG snapshot failed', err, flush=True)
                    return
                rep = AppKit.NSBitmapImageRep.imageRepWithData_(img.TIFFRepresentation())
                rep.representationUsingType_properties_(AppKit.NSBitmapImageFileTypePNG, None).writeToFile_atomically_(out, True)
                print('DIAG snapshot', out, flush=True)
            wv.takeSnapshotWithConfiguration_completionHandler_(WebKit.WKSnapshotConfiguration.alloc().init(), done)
        AppHelper.callAfter(check)
        print('DIAG state', window.evaluate_js("JSON.stringify({ready: document.readyState, nodes: document.querySelectorAll('.node').length, "
                                                "theme: document.documentElement.dataset.theme})"), flush=True)
    except Exception as e:
        print('DIAG error', repr(e), flush=True)


def main():
    global window
    start_server()
    url = BASE + '/'
    flow = next((a for a in sys.argv[1:] if a.lower().endswith(FLOW_EXT) and os.path.exists(a)), None)
    if flow:
        url += '?open=' + urllib.parse.quote(os.path.abspath(flow))
    # Always centered on the main screen: with several monitors, macOS could open it on the secondary one and it
    # looked as if the app had not started.
    try:
        screen = list(webview.screens)[0]
    except Exception:
        screen = None
    width, height = 1480, 940
    pos = {}
    if screen is not None:
        width, height = min(width, screen.width - 60), min(height, screen.height - 80)
        pos = {'screen': screen, 'x': screen.x + (screen.width - width) // 2, 'y': screen.y + (screen.height - height) // 2}
    window = webview.create_window(APP_NAME, html=LOADING_HTML.replace('{{BASE}}', BASE).replace('{{URL}}', url), js_api=api, width=width, height=height,
                                   min_size=(980, 640),
                                   background_color='#FFFFFF', text_select=True, **pos)
    diag = os.environ.get('MW_DIAG') or os.environ.get('MS_DIAG')
    webview.start(diagnose if diag else None, menu=MENU, private_mode=False,
                  storage_path=os.path.join(SUPPORT, 'webview'))


if __name__ == '__main__':
    main()
