#!/usr/bin/env python3
"""
Screenshots of the app for the project page: the real interface drawn by WebKit, as in the Mac app.

  MW_HOME=<work folder> .venv/bin/python scripts/screenshots.py <output folder>

Use a copy of a work folder (it runs the Demo workflow and writes its results there). It saves PNGs at 2x:
canvas-light.png, canvas-dark.png, new-workflow.png and profile.png, and copies the rendered composites
of the run to <output folder>/results/.
"""
import json
import os
import shutil
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
if not os.environ.get('MW_HOME'):
    sys.exit('Set MW_HOME to a copy of a work folder.')
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'shots')
os.makedirs(os.path.join(OUT, 'results'), exist_ok=True)

import webview  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

import app as server  # noqa: E402

PORT = 5199
window = None


def js(code):
    return window.evaluate_js(code)


def wait_for(code, timeout=180, step=0.5):
    end = time.time() + timeout
    while time.time() < end:
        if js(code):
            return True
        time.sleep(step)
    raise TimeoutError(code)


def snapshot(name):
    """Saves what WebKit draws in the window (the same pixels the user sees) as <name>.png."""
    import AppKit
    import WebKit
    from PyObjCTools import AppHelper
    from webview.platforms import cocoa
    done = threading.Event()
    path = os.path.join(OUT, name + '.png')

    def shoot():
        wv = cocoa.BrowserView.instances.get(window.uid).webview

        def handler(img, err):
            if img is not None:
                rep = AppKit.NSBitmapImageRep.imageRepWithData_(img.TIFFRepresentation())
                rep.representationUsingType_properties_(AppKit.NSBitmapImageFileTypePNG, None).writeToFile_atomically_(path, True)
            print('shot', name, 'ok' if img is not None else err, flush=True)
            done.set()
        wv.takeSnapshotWithConfiguration_completionHandler_(WebKit.WKSnapshotConfiguration.alloc().init(), handler)
    AppHelper.callAfter(shoot)
    done.wait(30)


THEME = """(function(t){ if (document.documentElement.dataset.theme !== t) document.getElementById('btn-theme').click(); })('%s')"""


def script():
    try:
        wait_for("typeof S !== 'undefined' && document.querySelectorAll('.node').length > 1", 60)
        time.sleep(2)   # the splash screen fades out
        js(THEME % 'light')
        # Run the Demo workflow so the history shows real results.
        js("runWorkflow('full')")
        time.sleep(2)
        wait_for("S.runs.length && ['success','partial','failed'].includes(S.runs[0].status)", 600, 2)
        js("renderRuns(); fitZoom()")
        time.sleep(2.5)
        snapshot('canvas-light')
        js(THEME % 'dark')
        time.sleep(1)
        snapshot('canvas-dark')
        js(THEME % 'light')
        # New workflow dialog: two designs and four mockups chosen in a custom order.
        js("S.fileDirty = false; openNewDialog()")
        time.sleep(1.5)
        js("""(function(){ const ins=[...document.querySelectorAll('#gallery input')];
              [2,0,4,1].forEach(i=>{ if (ins[i]) { ins[i].checked=true; ins[i].dispatchEvent(new Event('change',{bubbles:true})); } });
              document.getElementById('new-name').value='Spring campaign'; document.activeElement.blur(); })()""")
        time.sleep(1)
        snapshot('new-workflow')
        js("document.getElementById('new-dialog').close()")
        time.sleep(0.5)
        # Profile of the mockup with the most Smart Objects.
        js("openProfile(S.mockups.slice().sort((a,b)=>b.smartObjects.length-a.smartObjects.length)[0].id)")
        time.sleep(2)
        snapshot('profile')
        runs = json.loads(js("JSON.stringify(S.runs)"))
        rid = runs[0]['id']
        for st in runs[0]['steps']:
            if st.get('file'):
                shutil.copyfile(os.path.join(server.RUNS, rid, st['file']), os.path.join(OUT, 'results', st['file']))
        print('results', rid, flush=True)
    except Exception as e:
        print('error', repr(e), flush=True)
    finally:
        window.destroy()


def main():
    global window
    httpd = make_server('127.0.0.1', PORT, server.app, threaded=True)
    server.start_background()
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    window = webview.create_window('Mockup Workflow', f'http://127.0.0.1:{PORT}/', width=1440, height=900,
                                   background_color='#FFFFFF')
    webview.start(script, private_mode=True)


if __name__ == '__main__':
    main()
