#!/usr/bin/env python3
"""
Mockup Workflow: a local web app that places PNG or SVG designs on several PSD mockups at once.

  .venv/bin/python app.py        → http://127.0.0.1:5173

Folders (inside the work folder):
  Mockup Gallery/       the gallery PSDs (subfolders are groups). Copying a PSD here is enough.
  Flows/                .mwf workflow files
  data/mockups/         metadata and thumbnail of each mockup
  data/designs/         uploaded reference designs (PNG + metadata)
  data/runs/<id>/       results of each run;  data/runs.json: history
  data/workflow.json    autosave of the open workflow
Workflows are saved as .mwf files (Mockup Workflow, XML) with the designs embedded.
"""
import base64
import hashlib
import io
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import uuid
import xml.etree.ElementTree as ET
import zipfile

from flask import Flask, Response, abort, jsonify, request, send_file, send_from_directory
from PIL import Image

import engine
from version import APP_NAME, FLOW_EXT, FLOW_FORMAT, __author__, __copyright__, __email__, __license__, __version__

# Code and interface: next to this file, or inside the packaged .app.
CODE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
# Work folder (gallery, workflows, results): MW_HOME (or the legacy MS_HOME), or the project folder from source.
ROOT = os.path.abspath(os.environ.get('MW_HOME') or os.environ.get('MS_HOME') or os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
FLOWS = os.path.join(ROOT, 'Flows')
GALLERY = os.path.join(ROOT, 'Mockup Gallery')
MOCKUPS = os.path.join(DATA, 'mockups')
DESIGNS = os.path.join(DATA, 'designs')
RUNS = os.path.join(DATA, 'runs')
RUNS_DB = os.path.join(DATA, 'runs.json')
WORKFLOW = os.path.join(DATA, 'workflow.json')
PSD_EXT = ('.psd', '.psb')

# Mockup Studio (Spanish) names, migrated on startup.
LEGACY_FOLDERS = {'Galería de mockups': 'Mockup Gallery', 'Flujos': 'Flows'}
LEGACY_GROUPS = {'Exterior': 'Outdoor', 'Merchandising': 'Merchandise', 'Otros': 'Other'}

app = Flask(__name__, static_folder=os.path.join(CODE, 'static'), static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 ** 3
lock = threading.Lock()
scan_lock = threading.Lock()
jobs = queue.Queue()


# ================================================================ utilities
def slug(name):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', os.path.splitext(name)[0]).strip('-').lower()
    return s or 'mockup'


def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def unique_path(folder, filename):
    base, ext = os.path.splitext(filename)
    path, i = os.path.join(folder, filename), 2
    while os.path.exists(path):
        path = os.path.join(folder, f'{base} ({i}){ext}')
        i += 1
    return path


def rel(path):
    """Path relative to the work folder when it is inside it (so the folder can be moved)."""
    p = os.path.abspath(path)
    return os.path.relpath(p, ROOT) if p.startswith(ROOT + os.sep) else p


def absolute(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def move_to_trash(path):
    """Moves a file to the macOS Trash (or to data/trash on other systems)."""
    trash = os.path.expanduser('~/.Trash')
    if not os.path.isdir(trash):
        trash = os.path.join(DATA, 'trash')
        os.makedirs(trash, exist_ok=True)
    shutil.move(path, unique_path(trash, os.path.basename(path)))


# ================================================================ migration from Mockup Studio
def migrate_from_studio():
    """
    Mockup Studio used Spanish folder and group names. Renames them (Galería de mockups → Mockup Gallery,
    Flujos → Flows, Exterior → Outdoor, Merchandising → Merchandise, Otros → Other) and updates the paths stored in
    the mockup metadata, the designs and the open workflow, so nothing breaks. Profiles are converted later, when
    the gallery is scanned.
    """
    renames = {}   # old absolute path → new absolute path
    for old, new in LEGACY_FOLDERS.items():
        src, dst = os.path.join(ROOT, old), os.path.join(ROOT, new)
        if os.path.isdir(src) and not os.path.exists(dst):
            os.rename(src, dst)
            renames[src] = dst
            if new == 'Mockup Gallery':
                for g_old, g_new in LEGACY_GROUPS.items():
                    gs, gd = os.path.join(dst, g_old), os.path.join(dst, g_new)
                    if os.path.isdir(gs) and not os.path.exists(gd):
                        os.rename(gs, gd)
                        renames[os.path.join(src, g_old)] = gd
    if not renames:
        return
    # Longest prefixes first, so a group folder wins over its gallery.
    pairs = sorted(renames.items(), key=lambda kv: -len(kv[0]))
    pairs += [(os.path.relpath(o, ROOT), os.path.relpath(n, ROOT)) for o, n in pairs]

    def fix(p):
        if not isinstance(p, str):
            return p
        for o, n in pairs:
            if p == o or p.startswith(o + os.sep):
                return n + p[len(o):]
        return p

    for f in os.listdir(MOCKUPS) if os.path.isdir(MOCKUPS) else []:
        if f.endswith('.json'):
            m = read_json(os.path.join(MOCKUPS, f), None)
            if m:
                m['path'], m['profilePath'] = fix(m.get('path')), fix(m.get('profilePath'))
                m['category'] = LEGACY_GROUPS.get(m.get('category'), m.get('category'))
                write_json(os.path.join(MOCKUPS, f), m)
    for f in os.listdir(DESIGNS) if os.path.isdir(DESIGNS) else []:
        if f.endswith('.json'):
            m = read_json(os.path.join(DESIGNS, f), None)
            if m and m.get('source'):
                m['source'] = fix(m['source'])
                write_json(os.path.join(DESIGNS, f), m)
    wf = read_json(WORKFLOW, None)
    if wf and wf.get('filePath'):
        wf['filePath'] = fix(wf['filePath'])
        write_json(WORKFLOW, wf)
    print('Migrated Mockup Studio folders:', ', '.join(f'{os.path.basename(o)} → {os.path.basename(n)}'
                                                         for o, n in renames.items()), flush=True)


os.makedirs(DATA, exist_ok=True)
migrate_from_studio()
for d in (GALLERY, MOCKUPS, DESIGNS, RUNS, FLOWS):
    os.makedirs(d, exist_ok=True)


# ================================================================ mockups (gallery)
def all_metas():
    metas = [read_json(os.path.join(MOCKUPS, f), None) for f in os.listdir(MOCKUPS) if f.endswith('.json')]
    return [m for m in metas if m]


def mockup_meta(mid):
    meta = read_json(os.path.join(MOCKUPS, mid + '.json'), None)
    if meta is None:
        abort(404, 'Mockup not found')
    return meta


def psd_path(meta):
    return absolute(meta['path'])


def category_of(path):
    folder = os.path.dirname(os.path.abspath(path))
    if folder.startswith(GALLERY + os.sep):
        return os.path.relpath(folder, GALLERY)
    return ''


# ================================================================ mockup profiles (.mockup.json)
DEFAULT_GROUPS = ['Outdoor', 'Merchandise', 'Other']
PROFILE_EXT = '.mockup.json'
PROFILE_FORMAT = 1
LOGO_TINT = {'light': '#ffffff', 'dark': '#1c2030', 'original': None}
BACKGROUNDS = ('transparent', 'full-bleed')
FITS = ('contain', 'cover', 'stretch')


def groups():
    """Gallery groups: the default ones plus any folder created in the gallery."""
    extra = sorted(d for d in os.listdir(GALLERY) if os.path.isdir(os.path.join(GALLERY, d))
                   and not d.startswith('.') and d not in DEFAULT_GROUPS)
    return DEFAULT_GROUPS + extra


def clean_group(name):
    """A group name that is valid as a folder name (no slashes or leading dots), or None."""
    name = re.sub(r'[\\/:*?"<>|]+', ' ', (name or '')).strip().strip('.').strip()[:40]
    return name or None


def profile_path(psd):
    return os.path.splitext(psd)[0] + PROFILE_EXT


def is_current(profile):
    return bool(profile) and 'format' in profile and profile['format'] >= PROFILE_FORMAT


def from_studio_profile(p):
    """
    Converts a Mockup Studio profile (Spanish keys) to the current schema, keeping what the user edited: name,
    group, and the logo, background, fit and rotation of each object. The rest is re-analyzed from the PSD.
    """
    logo = {'claro': 'light', 'oscuro': 'dark'}
    background = {'con fondo': 'full-bleed', 'transparente': 'transparent'}
    return {
        'name': p.get('nombre'), 'group': LEGACY_GROUPS.get(p.get('grupo'), p.get('grupo')), 'created': p.get('creado'),
        'objects': [{'id': o.get('id'), 'logo': logo.get(o.get('logo'), o.get('logo')),
                     'background': background.get(o.get('fondo'), o.get('fondo')), 'fit': o.get('ajuste'),
                     'rotate': o.get('giro')} for o in p.get('objetos', [])],
    }


def default_group(path):
    cat = category_of(path).split(os.sep)[0]
    return next((g for g in groups() if g.lower() == cat.lower()), cat or 'Other')


def build_profile(path, analysis, previous=None, name=None):
    """Mockup profile: what was detected in the PSD, keeping anything the user changed before."""
    prev = previous or {}
    prev_objs = {o.get('id'): o for o in prev.get('objects', [])}
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    objs = []
    for o in analysis['objects']:
        p = prev_objs.get(o['uid'], {})
        background = p.get('background') if p.get('background') in BACKGROUNDS else \
            ('full-bleed' if o['withBackground'] else 'transparent')
        objs.append({
            'id': o['uid'], 'name': o['name'], 'canvas': o['inner'], 'ratio': o['ratio'], 'aspect': o['aspect'],
            'logo': p.get('logo') if p.get('logo') in LOGO_TINT else o['logo'], 'background': background,
            'fit': p.get('fit') if p.get('fit') in FITS else ('cover' if background == 'full-bleed' else 'contain'),
            'rotate': int(p.get('rotate') or 0), 'visible': o['visible'],
            'warp': o.get('warp'), 'perspective': o.get('perspective'), 'instances': o.get('instances', []),
            'analysis': {'surface': o['surface'], 'sample': o['sample'], 'coverage': o['coverage']},
        })
    return {
        'format': PROFILE_FORMAT, 'app': f'{APP_NAME} {__version__}',
        'name': name or prev.get('name') or os.path.splitext(os.path.basename(path))[0],
        'file': os.path.basename(path),
        'group': prev.get('group') or default_group(path),
        'size': analysis['size'], 'objects': objs, 'layers': analysis.get('layers', []),
        'created': prev.get('created') or now, 'updated': now,
    }


def objects_from_profile(profile):
    return [{'uid': o['id'], 'name': o['name'], 'inner': o['canvas'], 'ratio': o.get('ratio', ''),
             'aspect': o.get('aspect'), 'visible': o.get('visible', True), 'logo': o.get('logo', 'original'),
             'background': o.get('background', 'transparent'), 'fit': o.get('fit', 'contain'),
             'rotate': int(o.get('rotate') or 0), 'tint': LOGO_TINT.get(o.get('logo')),
             'surface': (o.get('analysis') or {}).get('surface')}
            for o in profile.get('objects', [])]


def mockup_id(path):
    return f'{slug(os.path.basename(path))}-{hashlib.sha1(rel(path).encode()).hexdigest()[:6]}'


def write_meta(path, profile, mid=None):
    path = os.path.abspath(path)
    mid = mid or mockup_id(path)
    old = read_json(os.path.join(MOCKUPS, mid + '.json'), {}) or {}
    meta = {
        'id': mid, 'name': profile['name'], 'file': os.path.basename(path), 'path': rel(path),
        'profilePath': rel(profile_path(path)), 'category': profile['group'],
        'bytes': os.path.getsize(path), 'mtime': os.path.getmtime(path), 'size': profile['size'],
        'smartObjects': objects_from_profile(profile), 'added': old.get('added') or time.time(),
    }
    write_json(os.path.join(MOCKUPS, mid + '.json'), meta)
    return meta


def register_mockup(path, name=None, mid=None, reanalyze=True):
    """Inspects a PSD and creates or updates its profile (.mockup.json, next to the PSD), metadata and thumbnail."""
    path = os.path.abspath(path)
    prev = read_json(profile_path(path), None)
    if prev and not is_current(prev):
        # Mockup Studio profile: re-analyzed in English, keeping what the user edited.
        prev = from_studio_profile(prev) if 'objetos' in prev else None
        reanalyze = True
    if prev and not reanalyze:
        profile = prev
    else:
        analysis = engine.analyze(path)
        if not analysis['objects']:
            raise ValueError('This PSD has no Smart Object to place the design in')
        profile = build_profile(path, analysis, prev, name)
        write_json(profile_path(path), profile)
    mid = mid or mockup_id(path)
    engine.preview(path).save(os.path.join(MOCKUPS, mid + '.jpg'), quality=86)
    return write_meta(path, profile, mid)


def drop_meta(mid):
    for ext in ('.json', '.jpg'):
        p = os.path.join(MOCKUPS, mid + ext)
        if os.path.exists(p):
            os.remove(p)


def migrate_legacy():
    """Very early versions kept the PSD in data/mockups: it is moved to the gallery."""
    for m in all_metas():
        if 'path' in m:
            continue
        old = os.path.join(MOCKUPS, m['id'] + '.psd')
        if not os.path.exists(old):
            drop_meta(m['id'])
            continue
        dest = unique_path(GALLERY, m['name'] + '.psd')
        shutil.move(old, dest)
        m.update(path=rel(dest), file=os.path.basename(dest), category='', mtime=os.path.getmtime(dest))
        write_json(os.path.join(MOCKUPS, m['id'] + '.json'), m)


def scan_gallery():
    """Registers new gallery PSDs, creates missing profiles and forgets PSDs that are gone."""
    with scan_lock:
        metas = all_metas()
        known = {os.path.abspath(psd_path(m)): m for m in metas}
        # PSDs no longer at their path: if they reappear in another gallery folder (same file and size), they keep
        # their identity so the workflows that use them don't break.
        orphans = [m for p, m in known.items() if not os.path.exists(p)]
        for folder, _, files in os.walk(GALLERY):
            for f in files:
                p = os.path.abspath(os.path.join(folder, f))
                if p in known or not f.lower().endswith(PSD_EXT):
                    continue
                size = os.path.getsize(p)
                m = next((o for o in orphans if o.get('bytes') == size and (o.get('file') == f or len(orphans) == 1)), None) \
                    or next((o for o in orphans if o.get('bytes') == size), None)
                if m:
                    orphans.remove(m)
                    m.update(path=rel(p), file=f, mtime=os.path.getmtime(p))
                    write_json(os.path.join(MOCKUPS, m['id'] + '.json'), m)
                    known[p] = m
        for m in orphans:
            if not os.path.isabs(m['path']) or not os.path.exists(psd_path(m)):
                drop_meta(m['id'])
        added, errors = [], []
        for folder, dirs, files in os.walk(GALLERY):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
            for f in sorted(files):
                if f.startswith('.') or not f.lower().endswith(PSD_EXT):
                    continue
                p = os.path.abspath(os.path.join(folder, f))
                m = known.get(p)
                fresh = m and abs(m.get('mtime', 0) - os.path.getmtime(p)) < 1
                prof = read_json(profile_path(p), None) if fresh else None
                if fresh and is_current(prof) and m.get('profilePath') and 'background' in (m['smartObjects'] or [{}])[0]:
                    continue
                try:
                    meta = register_mockup(p, name=m['name'] if m else None, mid=m['id'] if m else None,
                                           reanalyze=not fresh or not os.path.exists(profile_path(p)))
                    if not m:
                        added.append(meta)
                except Exception as e:
                    errors.append({'file': os.path.relpath(p, GALLERY), 'error': str(e)})
        return added, errors


def update_profile(meta, changes):
    """Applies the user's changes to the profile. If the group changes, moves the PSD and its profile there."""
    path = psd_path(meta)
    profile = read_json(profile_path(path), None)
    if not is_current(profile):
        prev = from_studio_profile(profile) if profile and 'objetos' in profile else None
        profile = build_profile(path, engine.analyze(path), prev, name=meta['name'])
    if (changes.get('name') or '').strip():
        profile['name'] = changes['name'].strip()[:80]
    by_id = {o['id']: o for o in profile['objects']}
    for c in changes.get('objects') or []:
        o = by_id.get(c.get('id'))
        if not o:
            continue
        if c.get('logo') in LOGO_TINT:
            o['logo'] = c['logo']
        if c.get('background') in BACKGROUNDS:
            o['background'] = c['background']
        if c.get('fit') in FITS:
            o['fit'] = c['fit']
        if 'rotate' in c:
            o['rotate'] = int(c['rotate']) % 360
    group = clean_group(changes.get('group'))
    if group and group != profile.get('group'):
        profile['group'] = group
        if path.startswith(GALLERY + os.sep):
            folder = os.path.join(GALLERY, group)
            os.makedirs(folder, exist_ok=True)
            dest = unique_path(folder, os.path.basename(path))
            old_profile = profile_path(path)
            shutil.move(path, dest)
            if os.path.exists(old_profile):
                os.remove(old_profile)
            path = dest
    profile['updated'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    write_json(profile_path(path), profile)
    return write_meta(path, profile, meta['id'])


# ================================================================ designs
def design_meta(did):
    meta = read_json(os.path.join(DESIGNS, did + '.json'), None)
    p = os.path.join(DESIGNS, did + '.png')
    if not os.path.exists(p):
        return None
    if meta is None:   # old designs without metadata
        with Image.open(p) as img:
            meta = dict(id=did, name=did + '.png', width=img.width, height=img.height,
                        transparent=img.getextrema()[3][0] < 255, created=os.path.getmtime(p))
    meta['path'] = p
    return meta


def save_design(img, name, source=None):
    """
    Saves a design; if one with the same pixels already exists, reuses it (for example when reopening a .mwf).
    `source` is the path of the original file when it is known (Mac app, .mwf).
    """
    img.load()
    rgba = img.convert('RGBA')
    sha = hashlib.sha1(rgba.tobytes() + f'{rgba.width}x{rgba.height}'.encode()).hexdigest()
    for f in os.listdir(DESIGNS):
        if f.endswith('.json'):
            m = read_json(os.path.join(DESIGNS, f), None)
            if m and m.get('sha') == sha and os.path.exists(os.path.join(DESIGNS, m['id'] + '.png')):
                m['created'] = time.time()          # moves up in "recent"
                if name and m.get('name') != name and not name.startswith(m['id']):
                    m['name'] = name
                if source:
                    m['source'] = source
                write_json(os.path.join(DESIGNS, f), m)
                return design_meta(m['id'])
    did = uuid.uuid4().hex[:10]
    rgba.save(os.path.join(DESIGNS, did + '.png'))
    meta = dict(id=did, name=name, width=rgba.width, height=rgba.height, sha=sha,
                transparent=rgba.getextrema()[3][0] < 255, created=time.time(), source=source)
    write_json(os.path.join(DESIGNS, did + '.json'), meta)
    return design_meta(did)


# ================================================================ history and worker
def runs_load():
    return read_json(RUNS_DB, [])


def run_update(run_id, fn):
    with lock:
        runs = runs_load()
        for r in runs:
            if r['id'] == run_id:
                fn(r)
        write_json(RUNS_DB, runs)


def worker():
    while True:
        run_id = jobs.get()
        try:
            process_run(run_id)
        except Exception:
            traceback.print_exc()
        jobs.task_done()


def process_run(run_id):
    run = next(r for r in runs_load() if r['id'] == run_id)
    out_dir = os.path.join(RUNS, run_id)
    os.makedirs(out_dir, exist_ok=True)
    cache = {}

    def design(did):
        if did not in cache:
            cache[did] = Image.open(os.path.join(DESIGNS, did + '.png')).convert('RGBA')
        return cache[did]

    fmt = run['output'].get('format', 'png')
    scale = float(run['output'].get('scale', 1))
    t_run = time.time()
    run_update(run_id, lambda r: r.update(status='running', started=t_run))

    failed = 0
    for i, step in enumerate(run['steps']):
        t0 = time.time()
        run_update(run_id, lambda r: r['steps'][i].update(status='running', started=t0))
        try:
            meta = read_json(os.path.join(MOCKUPS, step['mockupId'] + '.json'), None)
            if not meta or not os.path.exists(psd_path(meta)):
                raise FileNotFoundError('The PSD is no longer in the gallery')
            assignments = {l['uid']: {'design': design(l['designId']), 'fit': l.get('fit', 'contain'),
                                      'tint': l.get('tint'), 'rotate': int(l.get('rotate') or 0)}
                           for l in step['links']}
            img, warns = engine.render(psd_path(meta), assignments=assignments,
                                       log=lambda m: print(f'[{run_id}] {m}', flush=True))
            if scale != 1:
                img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
            base = f'{i + 1:02d}-{slug(step["name"])}'
            fname = base + ('.jpg' if fmt == 'jpg' else '.png')
            img.save(os.path.join(out_dir, fname), **({'quality': 92} if fmt == 'jpg' else {}))
            thumb = img.copy()
            thumb.thumbnail((720, 720), Image.LANCZOS)
            thumb.save(os.path.join(out_dir, base + '.thumb.jpg'), quality=84)
            done = dict(status='success', ms=int((time.time() - t0) * 1000), file=fname,
                        thumb=base + '.thumb.jpg', size=[img.width, img.height], warnings=warns)
        except Exception as e:
            traceback.print_exc()
            failed += 1
            done = dict(status='failed', ms=int((time.time() - t0) * 1000), error=str(e) or type(e).__name__)
        run_update(run_id, lambda r: r['steps'][i].update(**done))

    ok = len(run['steps']) - failed
    status = 'success' if failed == 0 else ('failed' if ok == 0 else 'partial')
    run_update(run_id, lambda r: r.update(status=status, ms=int((time.time() - t_run) * 1000), finished=time.time()))


# ================================================================ .mwf files
UNTITLED = 'Untitled workflow'


def flow_to_xml(state):
    """Workflow → .mwf XML: several designs, links per Smart Object, node positions and file paths."""
    root = ET.Element('mockupWorkflow', version=FLOW_FORMAT, app=f'{APP_NAME} {__version__}')
    ET.SubElement(root, 'title').text = state.get('title') or UNTITLED
    out = state.get('output') or {}
    ET.SubElement(root, 'output', format=str(out.get('format', 'png')), scale=str(out.get('scale', 1)))
    designs = ET.SubElement(root, 'designs')
    for dn in state.get('designNodes') or []:
        d = dn.get('design')
        meta = design_meta(d['id']) if d else None
        attrs = {'node': dn.get('id', ''), 'label': dn.get('label') or '', 'x': str(dn.get('x', 48)), 'y': str(dn.get('y', 56))}
        if meta:
            attrs.update(name=meta['name'], width=str(meta['width']), height=str(meta['height']),
                         path=meta['path'], source=meta.get('source') or '', encoding='base64', type='image/png')
        el = ET.SubElement(designs, 'design', attrs)
        if meta:
            with open(meta['path'], 'rb') as f:
                el.text = base64.b64encode(f.read()).decode()
    ep = state.get('exportPos') or {}
    ET.SubElement(root, 'export', x=str(ep.get('x', 900)), y=str(ep.get('y', 56)))
    nodes = ET.SubElement(root, 'mockups')
    for n in state.get('nodes') or []:
        meta = read_json(os.path.join(MOCKUPS, n.get('mockupId', '') + '.json'), None) or {}
        el = ET.SubElement(nodes, 'mockup', {
            'node': n.get('id', ''), 'label': n.get('label') or '', 'id': n.get('mockupId', ''), 'name': meta.get('name', ''),
            'file': meta.get('file', ''), 'path': psd_path(meta) if meta else '', 'category': meta.get('category', ''),
            'x': str(n.get('x', 0)), 'y': str(n.get('y', 0)),
        })
        so_names = {s['uid']: s['name'] for s in meta.get('smartObjects', [])}
        for uid, l in (n.get('links') or {}).items():
            ET.SubElement(el, 'link', {
                'smartObject': uid, 'name': so_names.get(uid, ''), 'design': l.get('design') or '',
                'fit': l.get('fit', 'contain'), 'tint': l.get('tint') or '', 'rotate': str(l.get('rotate') or 0),
            })
    ET.indent(root)
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='utf-8')


def _resolve_mockup(el, metas):
    """Finds the mockup of a node: by id, by path (registering it if needed), by file name and by name."""
    by_id = {m['id']: m for m in metas}
    if el.get('id') in by_id:
        return by_id[el.get('id')]
    path = el.get('path')
    if path:
        ap = os.path.abspath(path)
        m = next((m for m in metas if os.path.abspath(psd_path(m)) == ap), None)
        if m:
            return m
        if os.path.exists(ap) and ap.lower().endswith(PSD_EXT):
            try:
                with scan_lock:
                    return register_mockup(ap, name=el.get('name') or None)
            except Exception:
                pass
    return next((m for m in metas if el.get('file') and m['file'] == el.get('file')), None) \
        or next((m for m in metas if el.get('name') and m['name'] == el.get('name')), None)


def _load_design(el):
    """Design of a <design> element: embedded in base64, or read from its path if it is not embedded."""
    name = el.get('name') or 'design.png'
    source = el.get('source') or None
    if (el.text or '').strip():
        return save_design(Image.open(io.BytesIO(base64.b64decode(el.text.strip()))), name, source=source)
    for p in (source, el.get('path')):
        if p and os.path.exists(p):
            with Image.open(p) as img:
                return save_design(img, name, source=source)
    return None


def xml_to_flow(data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise ValueError(f'The file is not a valid workflow (malformed XML: {e})')
    if root.tag != 'mockupWorkflow':
        raise ValueError(f'The file is not a {APP_NAME} workflow (.mwf)')
    num = lambda v, d=0: float(v) if v not in (None, '') else d
    version = root.get('version', '1')
    state = {'title': (root.findtext('title') or UNTITLED).strip(), 'nodes': [], 'designNodes': [],
             'missing': [], 'version': version}
    out = root.find('output')
    state['output'] = {'format': out.get('format', 'png') if out is not None else 'png',
                       'scale': num(out.get('scale'), 1) if out is not None else 1}
    design_els = list(root.find('designs')) if root.find('designs') is not None else []
    for i, el in enumerate(design_els):
        state['designNodes'].append({'id': el.get('node') or f'd{i + 1}', 'label': el.get('label') or None,
                                     'design': _load_design(el),
                                     'x': num(el.get('x'), 48), 'y': num(el.get('y'), 56 + i * 420)})
    if not state['designNodes']:
        state['designNodes'].append({'id': 'd1', 'design': None, 'x': 48, 'y': 56})
    e = root.find('export')
    if e is not None:
        state['exportPos'] = {'x': num(e.get('x'), 900), 'y': num(e.get('y'), 56)}
    metas = all_metas()
    valid_designs = {d['id'] for d in state['designNodes']}
    for el in root.iter('mockup'):
        meta = _resolve_mockup(el, metas)
        if not meta:
            state['missing'].append(el.get('name') or el.get('file') or el.get('id'))
            continue
        uids = [s['uid'] for s in meta['smartObjects']]
        links = {}
        for l in el.findall('link'):
            if l.get('smartObject') in uids:
                d = l.get('design') or None
                links[l.get('smartObject')] = {'design': d if d in valid_designs else None, 'fit': l.get('fit', 'contain'),
                                               'tint': l.get('tint') or None, 'rotate': int(num(l.get('rotate')))}
        state['nodes'].append({'id': el.get('node') or 'n' + uuid.uuid4().hex[:6], 'mockupId': meta['id'],
                               'label': el.get('label') or None,
                               'x': num(el.get('x'), 470), 'y': num(el.get('y'), 56), 'links': links})
    return state


# ================================================================ routes
@app.get('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.get('/api/about')
def about():
    import platform
    import psd_tools
    return jsonify(name=APP_NAME, version=__version__, author=__author__, email=__email__, license=__license__,
                   copyright=__copyright__, flowFormat=FLOW_FORMAT, flowExt=FLOW_EXT, workFolder=ROOT, gallery=GALLERY,
                   python=platform.python_version(), psdTools=psd_tools.__version__, packaged=hasattr(sys, '_MEIPASS'))


def sorted_metas():
    g = groups()
    return sorted(all_metas(), key=lambda m: (g.index(m['category']) if m.get('category') in g else 99,
                                              m['name'].lower()))


@app.get('/api/groups')
def list_groups():
    return jsonify(groups())


@app.get('/api/mockups')
def list_mockups():
    return jsonify(sorted_metas())


@app.post('/api/gallery/scan')
def gallery_scan():
    added, errors = scan_gallery()
    return jsonify(added=[m['name'] for m in added], errors=errors, mockups=sorted_metas())


@app.post('/api/gallery/reveal')
def gallery_reveal():
    try:
        subprocess.Popen(['open', GALLERY])
    except Exception as e:
        return jsonify(error=f'Could not open the folder: {e}'), 500
    return jsonify(ok=True, path=GALLERY)


@app.post('/api/mockups')
def upload_mockup():
    f = request.files.get('file')
    if not f or not f.filename.lower().endswith(PSD_EXT):
        return jsonify(error='Upload a .psd or .psb file'), 400
    group = clean_group(request.form.get('category')) or 'Other'
    folder = os.path.join(GALLERY, group)   # each group is a gallery folder
    os.makedirs(folder, exist_ok=True)
    path = unique_path(folder, os.path.basename(f.filename))
    f.save(path)
    try:
        with scan_lock:
            meta = register_mockup(path)
    except Exception as e:
        os.remove(path)
        if os.path.exists(profile_path(path)):
            os.remove(profile_path(path))
        return jsonify(error=f'Could not use the PSD: {e}'), 400
    return jsonify(meta)


@app.patch('/api/mockups/<mid>')
def rename_mockup(mid):
    meta = mockup_meta(mid)
    name = (request.get_json(force=True).get('name') or '').strip()
    if not name:
        return jsonify(error='The name cannot be empty'), 400
    return jsonify(update_profile(meta, {'name': name}))


@app.get('/api/mockups/<mid>/profile')
def get_profile(mid):
    meta = mockup_meta(mid)
    profile = read_json(profile_path(psd_path(meta)), None)
    if not is_current(profile):
        with scan_lock:
            register_mockup(psd_path(meta), name=meta['name'], mid=mid)
        profile = read_json(profile_path(psd_path(meta)), {})
    return jsonify(profile=profile, path=profile_path(psd_path(meta)), groups=groups())


@app.put('/api/mockups/<mid>/profile')
def put_profile(mid):
    meta = mockup_meta(mid)
    try:
        with scan_lock:
            return jsonify(update_profile(meta, request.get_json(force=True) or {}))
    except Exception as e:
        return jsonify(error=f'Could not save the profile: {e}'), 400


@app.delete('/api/mockups/<mid>')
def delete_mockup(mid):
    meta = mockup_meta(mid)
    p = psd_path(meta)
    for f in (p, profile_path(p)):
        if os.path.exists(f) and (f == profile_path(p) or p.startswith(GALLERY + os.sep)):
            move_to_trash(f)
    drop_meta(mid)
    return jsonify(ok=True)


@app.get('/api/mockups/<mid>/thumb.jpg')
def mockup_thumb(mid):
    return send_from_directory(MOCKUPS, mid + '.jpg', max_age=3600)


def touch_designs(ids, field='used'):
    """Marks designs as used now (or hides them with field='hidden')."""
    for did in set(ids):
        path = os.path.join(DESIGNS, did + '.json')
        m = read_json(path, None)
        if m:
            m[field] = time.time() if field == 'used' else True
            if field == 'used':
                m['hidden'] = False
            write_json(path, m)


DEMO_NAME = 'Demo'
DEMO_LOGO = 'demo.png'
DEMO_MONOGRAM = 'demo.svg'


def demo_designs():
    """The two demo designs: demo.png (app logo) and demo.svg (white "MW" monogram, with its SVG in Flows/)."""
    with Image.open(os.path.join(CODE, 'static', 'demo-design.png')) as img:
        logo = save_design(img, DEMO_LOGO)
    svg_path = os.path.join(FLOWS, DEMO_MONOGRAM)
    bundled_svg = os.path.join(CODE, 'static', 'demo-monogram.svg')
    with open(bundled_svg, 'rb') as f:
        svg = f.read()
    if not os.path.exists(svg_path) or open(svg_path, 'rb').read() != svg:   # also replaces the old "MS" monogram
        with open(svg_path, 'wb') as f:
            f.write(svg)
    with Image.open(os.path.join(CODE, 'static', 'demo-monogram.png')) as img:
        mono = save_design(img, DEMO_MONOGRAM, source=svg_path)
    for d in (logo, mono):
        m = read_json(os.path.join(DESIGNS, d['id'] + '.json'), {})
        if m.get('hidden'):
            m['hidden'] = False
            write_json(os.path.join(DESIGNS, d['id'] + '.json'), m)
            d['hidden'] = False
    return logo, mono


def retire_old_demo():
    """
    The Mockup Studio demo designs (the "Mockup Studio" logo and the "MS" monogram) are replaced by the current ones:
    they leave the recent lists and the open workflow uses the new ones. Their files are kept.
    """
    old = [m for m in (read_json(os.path.join(DESIGNS, f), None) for f in os.listdir(DESIGNS) if f.endswith('.json'))
           if m and m.get('name') in (DEMO_LOGO, DEMO_MONOGRAM) and not m.get('hidden')]
    if not old:
        return
    logo, mono = demo_designs()
    new = {DEMO_LOGO: logo, DEMO_MONOGRAM: mono}
    swap = {}
    for m in old:
        if m['id'] != new[m['name']]['id']:
            m['hidden'] = True
            write_json(os.path.join(DESIGNS, m['id'] + '.json'), m)
            swap[m['id']] = new[m['name']]
    wf = read_json(WORKFLOW, None)
    if not wf or not swap:
        return
    for dn in wf.get('designNodes') or []:
        d = dn.get('design') or {}
        if d.get('id') in swap:
            dn['design'] = swap[d['id']]
            if dn.get('label') == 'Monograma MS':
                dn['label'] = 'MW monogram'
    if wf.get('title') == 'Flujo sin título':
        wf['title'] = UNTITLED
    write_json(WORKFLOW, wf)


@app.get('/api/designs')
def list_designs():
    """
    Recent designs: the last ones used (in a run) or uploaded, without those removed from the list. If none are
    left, the demo designs: demo.png and demo.svg.
    """
    metas = [design_meta(f[:-4]) for f in os.listdir(DESIGNS) if f.endswith('.png')]
    metas = sorted([m for m in metas if m and not m.get('hidden')],
                   key=lambda m: -max(m.get('used') or 0, m.get('created') or 0))
    seen, out = set(), []
    for m in metas:   # no duplicates of the same file (same name and size)
        key = (m['name'], m['width'], m['height'])
        if key not in seen:
            seen.add(key)
            out.append(m)
    if not out:
        out = [dict(m, demo=True) for m in demo_designs()]
    return jsonify(out[:12])


@app.patch('/api/designs/<did>')
def update_design(did):
    """Removes a design from the recent lists (hidden) or shows it again. The file is not deleted."""
    m = read_json(os.path.join(DESIGNS, did + '.json'), None)
    if m is None:
        abort(404)
    body = request.get_json(force=True) or {}
    if 'hidden' in body:
        m['hidden'] = bool(body['hidden'])
    write_json(os.path.join(DESIGNS, did + '.json'), m)
    return jsonify(design_meta(did))


@app.post('/api/designs')
def upload_design():
    f = request.files.get('file')
    if not f:
        return jsonify(error='No file was received'), 400
    try:
        img = Image.open(f.stream)
        # SVGs are rasterized in the interface; they arrive here as PNG with the original's name and path.
        meta = save_design(img, request.form.get('name') or f.filename, source=request.form.get('source') or None)
    except Exception:
        return jsonify(error='The file is not a valid image (use PNG, SVG, JPG or WebP)'), 400
    return jsonify(meta)


@app.post('/api/designs/from-path')
def design_from_path():
    """Design chosen with the native dialog of the Mac app: its original path is kept."""
    path = (request.get_json(force=True) or {}).get('path') or ''
    if not os.path.isfile(path):
        return jsonify(error='The design file cannot be found'), 400
    try:
        with Image.open(path) as img:
            return jsonify(save_design(img, os.path.basename(path), source=path))
    except Exception:
        return jsonify(error='The file is not a valid image (use PNG, SVG, JPG or WebP)'), 400


@app.get('/api/designs/<did>.png')
def design_file(did):
    return send_from_directory(DESIGNS, did + '.png', max_age=3600)


@app.get('/api/workflow')
def get_workflow():
    return jsonify(read_json(WORKFLOW, {}))


@app.put('/api/workflow')
def put_workflow():
    data = request.get_json(force=True)
    data['savedAt'] = time.time()
    write_json(WORKFLOW, data)
    return jsonify(savedAt=data['savedAt'])


def flow_file_name(name):
    """A safe .mwf file name."""
    name = re.sub(r'[\\/:*?"<>|]+', '-', (name or '').strip()) or 'Workflow'
    return name if name.lower().endswith(FLOW_EXT) else name + FLOW_EXT


@app.post('/api/flows/export')
def flow_export():
    state = request.get_json(force=True)
    name = flow_file_name(state.get('fileName') or state.get('title'))
    q = urllib.parse.quote(name)
    return Response(flow_to_xml(state), mimetype='application/xml',
                    headers={'Content-Disposition': f"attachment; filename*=UTF-8''{q}", 'X-File-Name': q})


GRID = dict(x0=470, y0=56, dx=400, dy=660, cols=2)   # same grid as "Arrange nodes" in the interface


def link_defaults(s, design=None):
    """
    Default settings of a Smart Object from its profile. If it expects a full-bleed piece (a poster) but the design
    is a transparent logo, the whole design is fitted inside and tinted to contrast with the surface.
    """
    fit, tint = s.get('fit', 'contain'), s.get('tint')
    if s.get('background') == 'full-bleed' and design and design.get('transparent'):
        fit = 'contain'
        tint = '#ffffff' if (s.get('surface') or 0.5) < 0.5 else '#1c2030'
    return {'fit': fit, 'tint': tint, 'rotate': s.get('rotate', 0)}


def default_links(meta, design_id, design=None):
    """Default links of a mockup: every Smart Object to the design, with the settings from its profile."""
    return {s['uid']: {'design': design_id, **link_defaults(s, design)} for s in meta['smartObjects']}


def demo_state():
    """
    Demo workflow: the app logo (design 1) and the white "MW" monogram as SVG (design 2) on every gallery mockup.
    In mockups with several Smart Objects, the smallest one (sides, awnings, backgrounds) gets the monogram and the
    rest get the logo. Each link takes the settings from the mockup profile.
    """
    # The monogram SVG is left in Flows/demo.svg so the user has the vector file; the engine uses its rasterized
    # version (generated from the same outline by scripts/make_icon.py).
    logo, mono = demo_designs()
    designs = {'d1': logo, 'd2': mono}
    nodes = []
    for i, m in enumerate(sorted_metas()):
        sos = m['smartObjects']
        area = lambda s: (s.get('inner') or [0, 0])[0] * (s.get('inner') or [0, 0])[1]
        small = min(sos, key=area)['uid'] if len(sos) > 1 else None
        links = {}
        for s in sos:
            did = 'd2' if s['uid'] == small else 'd1'
            links[s['uid']] = {'design': did, **link_defaults(s, designs[did])}
        nodes.append({'id': f'demo{i}', 'mockupId': m['id'], 'links': links,
                      'x': GRID['x0'] + (i % GRID['cols']) * GRID['dx'], 'y': GRID['y0'] + (i // GRID['cols']) * GRID['dy']})
    cols = min(len(nodes), GRID['cols']) or 1
    return {'title': DEMO_NAME, 'nodes': nodes, 'output': {'format': 'png', 'scale': 1},
            'designNodes': [{'id': 'd1', 'design': logo, 'x': 48, 'y': GRID['y0']},
                            {'id': 'd2', 'label': 'MW monogram', 'design': mono, 'x': 48, 'y': GRID['y0'] + 560}],
            'exportPos': {'x': GRID['x0'] + cols * GRID['dx'] + 40, 'y': GRID['y0']}, 'missing': []}


@app.post('/api/demo')
def demo():
    """Returns the Demo workflow and saves it as Flows/Demo.mwf (without overwriting an existing one)."""
    state = demo_state()
    path = os.path.join(FLOWS, DEMO_NAME + FLOW_EXT)
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(flow_to_xml(state))
    state.update(fileName=DEMO_NAME + FLOW_EXT, filePath=path)
    return jsonify(state)


@app.post('/api/flows/import')
def flow_import():
    f = request.files.get('file')
    data = f.read() if f else request.get_data()
    if not data:
        return jsonify(error='No file was received'), 400
    try:
        return jsonify(xml_to_flow(data))
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.delete('/api/runs')
def clear_runs():
    """Clears the history: the generated mockups go to the Trash (they can be recovered)."""
    with lock:
        runs = runs_load()
        if any(r['status'] in ('queued', 'running') for r in runs):
            return jsonify(error='A run is in progress. Wait for it to finish before clearing the history.'), 409
        folders = [os.path.join(RUNS, r['id']) for r in runs if os.path.isdir(os.path.join(RUNS, r['id']))]
        if folders:
            trash = os.path.join(DATA, f'{APP_NAME} history {time.strftime("%Y-%m-%d %H.%M")}')
            os.makedirs(trash, exist_ok=True)
            for f in folders:
                shutil.move(f, os.path.join(trash, os.path.basename(f)))
            move_to_trash(trash)
        write_json(RUNS_DB, [])
    return jsonify(ok=True, removed=len(runs))


@app.get('/api/runs')
def list_runs():
    return jsonify(list(reversed(runs_load()))[:30])


@app.post('/api/runs')
def create_run():
    body = request.get_json(force=True)
    nodes = body.get('nodes') or []
    if not nodes:
        return jsonify(error='Add at least one mockup to the canvas'), 400
    steps = []
    for n in nodes:
        meta = mockup_meta(n['mockupId'])
        uids = {s['uid'] for s in meta['smartObjects']}
        links = [dict(uid=l['uid'], designId=l['designId'], fit=l.get('fit', 'contain'), tint=l.get('tint'),
                      rotate=int(l.get('rotate') or 0))
                 for l in n.get('links') or [] if l.get('uid') in uids and l.get('designId')
                 and os.path.exists(os.path.join(DESIGNS, l['designId'] + '.png'))]
        if not links:
            return jsonify(error=f'"{meta["name"]}" has no linked design. Choose a design in its Smart Objects '
                                 f'or upload one in a design node.'), 400
        steps.append(dict(nodeId=n.get('nodeId'), mockupId=meta['id'], name=n.get('label') or meta['name'], links=links,
                          status='pending'))
    touch_designs([l['designId'] for st in steps for l in st['links']])   # "last used"
    run = dict(id=time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:4],
               kind=body.get('kind', 'full'), output=body.get('output') or {},
               status='queued', created=time.time(), steps=steps)
    with lock:
        runs = runs_load()
        runs.append(run)
        write_json(RUNS_DB, runs)
    jobs.put(run['id'])
    return jsonify(run)


@app.get('/api/runs/<rid>/files/<name>')
def run_file(rid, name):
    return send_from_directory(os.path.join(RUNS, rid), name, max_age=3600,
                               as_attachment=request.args.get('download') == '1')


@app.get('/api/runs/<rid>/zip')
def run_zip(rid):
    run = next((r for r in runs_load() if r['id'] == rid), None)
    if not run:
        abort(404)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_STORED) as z:
        for s in run['steps']:
            if s.get('file'):
                z.write(os.path.join(RUNS, rid, s['file']), s['file'])
    buf.seek(0)
    return send_file(buf, mimetype='application/zip', as_attachment=True, download_name=f'mockups-{rid}.zip')


def recover_interrupted():
    with lock:
        runs = runs_load()
        for r in runs:
            if r['status'] in ('queued', 'running'):
                r['status'] = 'failed'
                for s in r['steps']:
                    if s['status'] in ('pending', 'running'):
                        s.update(status='failed', error='The app was closed before the run finished')
        write_json(RUNS_DB, runs)


def start_background():
    migrate_legacy()
    retire_old_demo()
    recover_interrupted()
    threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=scan_gallery, daemon=True).start()


if __name__ == '__main__':
    start_background()
    port = int(os.environ.get('PORT', 5173))
    print(f'{APP_NAME} {__version__} → http://127.0.0.1:{port}')
    app.run(host='127.0.0.1', port=port, threaded=True, debug=False)
