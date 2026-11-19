'use strict';

/* ================================================================ icons (Lucide-style strokes) */
const ICONS = {
  logo: '<polygon points="3,16.5 6.2,14.9 12,17.8 17.8,14.9 21,16.5 12,21" fill="currentColor" stroke="none"/><polygon points="3,12 6.2,10.4 12,13.3 17.8,10.4 21,12 12,16.5" fill="currentColor" stroke="none"/><polygon points="3,7.5 12,3 21,7.5 12,12" fill="currentColor" stroke="none"/>',
  undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
  redo: '<path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/>',
  layers: '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>',
  save: '<path d="M5 3h11l5 5v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M7 3v5h8"/><path d="M7 21v-7h10v7"/>',
  play: '<path d="M7 4.5v15a1 1 0 0 0 1.5.86l12-7.5a1 1 0 0 0 0-1.72l-12-7.5A1 1 0 0 0 7 4.5Z" fill="currentColor"/>',
  upload: '<path d="M12 15V3"/><path d="m7 8 5-5 5 5"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>',
  mouse: '<path d="m4 4 7 17 2.5-7.5L21 11 4 4Z"/>',
  download: '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
  frame: '<rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 22h8"/><path d="M12 18v4"/><path d="m7 13 3-3 2 2 3-3 2 2"/>',
  package: '<path d="M21 8v8a2 2 0 0 1-1 1.7l-7 4a2 2 0 0 1-2 0l-7-4A2 2 0 0 1 3 16V8a2 2 0 0 1 1-1.7l7-4a2 2 0 0 1 2 0l7 4A2 2 0 0 1 21 8Z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
  ok: '<circle cx="12" cy="12" r="9.5"/><path d="m8 12.5 2.7 2.7L16 9.8"/>',
  fail: '<circle cx="12" cy="12" r="9.5"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
  warn: '<circle cx="12" cy="12" r="9.5"/><path d="M12 7.5v5.5"/><path d="M12 16.5h.01"/>',
  loader: '<path d="M21 12a9 9 0 1 1-6.2-8.56"/>',
  circle: '<circle cx="12" cy="12" r="9.5"/>',
  clock: '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3 2"/>',
  pencil: '<path d="M17 3a2.8 2.8 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  rotate: '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
  minus: '<path d="M5 12h14"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  'file-plus': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M12 12v6"/><path d="M9 15h6"/>',
  'folder-open': '<path d="m6 14 1.5-2.9A2 2 0 0 1 9.2 10H20a2 2 0 0 1 1.9 2.5l-1.5 6A2 2 0 0 1 18.4 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.7.9l.8 1.2a2 2 0 0 0 1.7.9H18a2 2 0 0 1 2 2v2"/>',
  folder: '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.7-.9l-.8-1.2A2 2 0 0 0 7.9 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M8 16H3v5"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.9 4.9 1.4 1.4"/><path d="m17.7 17.7 1.4 1.4"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.3 17.7-1.4 1.4"/><path d="m19.1 4.9-1.4 1.4"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  'image-plus': '<path d="M16 5h6"/><path d="M19 2v6"/><path d="M21 11.5V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7.5"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/><circle cx="9" cy="9" r="2"/>',
  sliders: '<path d="M4 21v-7"/><path d="M4 10V3"/><path d="M12 21v-9"/><path d="M12 8V3"/><path d="M20 21v-5"/><path d="M20 12V3"/><path d="M2 14h4"/><path d="M10 8h4"/><path d="M18 16h4"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
};
const svg = (n) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[n] || ''}</svg>`;
const icon = (n, cls = '') => `<span data-icon="${n}" class="${cls}" aria-hidden="true">${svg(n)}</span>`;
const hydrateIcons = (root = document) => root.querySelectorAll('[data-icon]').forEach((el) => { if (!el.firstChild) el.innerHTML = svg(el.dataset.icon); });

/* ================================================================ state */
const $ = (s, r = document) => r.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const S = {
  title: 'Untitled workflow',
  designNodes: [{ id: 'd1', design: null, x: 48, y: 56 }],   // designs (one per node)
  exportPos: { x: 900, y: 56 },
  nodes: [],
  output: { format: 'png', scale: 1 },
  savedAt: null,
  mockups: [],
  runs: [],
  designs: [],
  groups: ['Outdoor', 'Merchandise', 'Other'],
  open: new Set(),
  fileName: null,      // name of the open or saved .mwf
  fileHandle: null,    // file handle (Chrome/Edge) so "Save" doesn't ask again
  filePath: null,      // file path (Mac app with pywebview)
  fileDirty: false,
};
const FLOW_TYPES = [{ description: 'Mockup Workflow file', accept: { 'application/xml': ['.mwf'] } }];
const native = () => window.pywebview && window.pywebview.api;
const TINTS = [['', 'Original colors'], ['#1c2030', 'Black'], ['#ffffff', 'White']];
const FIT = [['contain', 'Contain'], ['cover', 'Cover'], ['stretch', 'Stretch']];
const STATUS = { queued: 'queued', running: 'running', success: 'completed', failed: 'failed', partial: 'partial' };
const mockupById = (id) => S.mockups.find((m) => m.id === id);
const activeRun = () => S.runs.find((r) => r.status === 'queued' || r.status === 'running');

/* ================================================================ utilities */
async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Error ${res.status}`);
  return data;
}
let toastTimer;
function toast(msg, err = false) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.toggle('err', err);
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), err ? 5200 : 2600);
}
function ago(ts) {
  if (!ts) return '';
  const s = Date.now() / 1000 - ts;
  if (s < 45) return 'just now';
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  if (s < 86400) return `${Math.round(s / 3600)} h ago`;
  return new Date(ts * 1000).toLocaleDateString('en-US', { day: 'numeric', month: 'short' });
}
const dur = (ms) => (ms == null ? '–' : ms < 1000 ? `${ms} ms` : `${(ms / 1000).toLocaleString('en-US', { maximumFractionDigits: 1 })} s`);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const fileUrl = (run, name, dl) => `/api/runs/${run.id}/files/${encodeURIComponent(name)}${dl ? '?download=1' : ''}`;

/** Last run step of a node (from the most recent run that includes it). */
function lastStep(nodeId) {
  for (const r of S.runs) {
    const st = r.steps.find((s) => s.nodeId === nodeId);
    if (st) return { run: r, step: st };
  }
  return null;
}

/* ================================================================ saving */
let saveTimer;
/* ---------- undo / redo: workflow snapshots; consecutive changes (<0.6 s) count as one ---------- */
const H = { undo: [], redo: [], last: null, t: 0, restoring: false };
const snapshot = () => JSON.stringify({ title: S.title, designNodes: S.designNodes, nodes: S.nodes, output: S.output, exportPos: S.exportPos });
function resetHistory() {
  H.undo = []; H.redo = []; H.last = snapshot(); H.t = 0;
  updateUndoButtons();
}
function recordHistory() {
  const snap = snapshot();
  if (H.last !== null && snap !== H.last && !H.restoring) {
    if (Date.now() - H.t > 600 || !H.undo.length) H.undo.push(H.last);
    if (H.undo.length > 80) H.undo.shift();
    H.redo = [];
    H.t = Date.now();
  }
  H.last = snap;
  updateUndoButtons();
}
function restoreSnapshot(json) {
  Object.assign(S, JSON.parse(json));
  H.restoring = true;
  $('#title').value = S.title;
  renderCanvas();
  scheduleSave();
  H.restoring = false;
  H.last = json;
  updateUndoButtons();
}
function undo() {
  if (!H.undo.length) return;
  H.redo.push(snapshot());
  restoreSnapshot(H.undo.pop());
  toast('Undone');
}
function redo() {
  if (!H.redo.length) return;
  H.undo.push(snapshot());
  restoreSnapshot(H.redo.pop());
  toast('Redone');
}
function updateUndoButtons() {
  const u = $('#btn-undo'), r = $('#btn-redo');
  if (u) u.disabled = !H.undo.length;
  if (r) r.disabled = !H.redo.length;
}

function scheduleSave() {
  recordHistory();
  S.fileDirty = true;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(save, 1200);
  renderSaved();
}
const flowState = () => {
  const { title, designNodes, exportPos, nodes, output, fileName, filePath } = S;
  return { title, designNodes, exportPos, nodes, output, fileName, filePath, fileDirty: S.fileDirty };
};
/** Autosave of the open workflow (to restore it when the app is reopened). */
async function save() {
  clearTimeout(saveTimer);
  try {
    const r = await api('/api/workflow', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(flowState()) });
    S.savedAt = r.savedAt;
    renderSaved();
  } catch (e) { toast('Couldn\'t autosave: ' + e.message, true); }
}
function renderSaved() {
  const el = $('#saved');
  if (S.fileName) {
    el.textContent = S.fileDirty ? `${S.fileName}, unsaved changes` : S.fileName;
    el.title = S.filePath || S.fileName;
  } else {
    el.textContent = S.savedAt ? `No file, autosaved ${ago(S.savedAt)}` : 'Not saved';
    el.title = 'Use "Save" to create a .mwf file';
  }
}

/* ================================================================ library */
const groupBy = (list) => list.reduce((acc, m) => ((acc[m.category || ''] ||= []).push(m), acc), {});
/** Group order: the Gallery's (Outdoor, Merchandise, Other and user-created ones), then the rest. */
const groupOrder = (names) => names.sort((a, b) => {
  const ia = S.groups.indexOf(a), ib = S.groups.indexOf(b);
  return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib) || a.localeCompare(b, 'en');
});
const soLabel = (m) => `${m.smartObjects.length} ${m.smartObjects.length === 1 ? 'Smart Object' : 'Smart Objects'}`;
function renderLibrary() {
  const box = $('#library');
  if (!S.mockups.length) {
    box.innerHTML = '<p class="lib-empty">The Gallery is empty. Add a PSD with a Smart Object, or copy it into the Gallery folder and press ↻.</p>';
    return;
  }
  const groups = groupBy(S.mockups);
  const names = groupOrder(Object.keys(groups));
  box.innerHTML = names.map((cat) => `<section class="lib-group">${names.length > 1 || cat ? `<h3>${esc(cat || 'Uncategorized')}</h3>` : ''}
    <ul class="lib-list" role="list">${groups[cat].map(libItemHtml).join('')}</ul></section>`).join('');
}
function libItemHtml(m) {
  return `<li class="lib-wrap">
      <button class="lib-item" type="button" draggable="true" data-mid="${m.id}" aria-label="Add ${esc(m.name)} to the canvas">
        <img src="/api/mockups/${m.id}/thumb.jpg" alt="" loading="lazy" width="64" height="48">
        <span><span class="lib-name">${esc(m.name)}</span>
        <span class="lib-meta">${m.size[0]}×${m.size[1]} px, ${soLabel(m)}</span></span>
      </button>
      <span class="lib-tools">
        <button class="icon-btn" type="button" data-profile="${m.id}" title="Mockup profile" aria-label="Profile of ${esc(m.name)}">${icon('sliders')}</button>
        <button class="icon-btn" type="button" data-rename="${m.id}" title="Rename" aria-label="Rename ${esc(m.name)}">${icon('pencil')}</button>
        <button class="icon-btn" type="button" data-del="${m.id}" title="Remove from Gallery" aria-label="Remove ${esc(m.name)} from the Gallery">${icon('trash')}</button>
      </span>
    </li>`;
}

$('#library').addEventListener('click', async (e) => {
  const del = e.target.closest('[data-del]');
  if (del) {
    const m = mockupById(del.dataset.del);
    if (!confirm(`Remove "${m.name}" from the Gallery?\n\nThe PSD (${m.file}) is moved to the Trash; you can restore it from there.`)) return;
    await api(`/api/mockups/${m.id}`, { method: 'DELETE' });
    S.mockups = S.mockups.filter((x) => x.id !== m.id);
    S.nodes = S.nodes.filter((n) => n.mockupId !== m.id);
    renderLibrary(); renderCanvas(); scheduleSave();
    return;
  }
  const prof = e.target.closest('[data-profile]');
  if (prof) { openProfile(prof.dataset.profile); return; }
  const ren = e.target.closest('[data-rename]');
  if (ren) {
    const m = mockupById(ren.dataset.rename);
    const name = prompt('Mockup name', m.name);
    if (!name || !name.trim() || name.trim() === m.name) return;
    try {
      Object.assign(m, await api(`/api/mockups/${m.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name.trim() }) }));
      renderLibrary(); renderCanvas();
    } catch (err) { toast(err.message, true); }
    return;
  }
  const item = e.target.closest('[data-mid]');
  if (item) addNode(item.dataset.mid);
});
$('#library').addEventListener('dragstart', (e) => {
  const item = e.target.closest('[data-mid]');
  if (!item) return;
  e.dataTransfer.setData('text/mockup', item.dataset.mid);
  e.dataTransfer.effectAllowed = 'copy';
});

async function uploadPsds(files) {
  const card = $('#psd-drop');
  const status = $('#psd-status');
  for (const f of files) {
    card.classList.add('busy');
    status.textContent = `Copying and analyzing ${f.name}…`;
    try {
      const fd = new FormData();
      fd.append('file', f);
      const meta = await api('/api/mockups', { method: 'POST', body: fd });
      S.mockups.push(meta);
      renderLibrary();
      addNode(meta.id);
      toast(`${meta.name} added. Check its profile.`);
      await openProfile(meta.id, true);
    } catch (e) { toast(e.message, true); }
  }
  card.classList.remove('busy');
  status.textContent = 'Copied to the Gallery folder';
}

async function scanGallery(quiet = false) {
  const btn = $('#btn-scan');
  btn.classList.add('busy');
  btn.querySelector('[data-icon]')?.classList.add('spin');
  try {
    const r = await api('/api/gallery/scan', { method: 'POST' });
    S.mockups = r.mockups;
    S.groups = await api('/api/groups').catch(() => S.groups);
    renderLibrary(); renderCanvas(false);
    if ($('#new-dialog').open) renderGallery();
    if (r.added.length) toast(`${r.added.length === 1 ? 'New mockup' : 'New mockups'} in the Gallery: ${r.added.join(', ')}`);
    else if (!quiet) toast('The Gallery is up to date');
    if (r.errors.length) toast(`Couldn't use ${r.errors.map((e) => e.file).join(', ')}: ${r.errors[0].error}`, true);
  } catch (e) { if (!quiet) toast(e.message, true); }
  btn.classList.remove('busy');
  btn.querySelector('[data-icon]')?.classList.remove('spin');
}
$('#btn-scan').addEventListener('click', () => scanGallery());
$('#btn-reveal').addEventListener('click', () => api('/api/gallery/reveal', { method: 'POST' }).catch((e) => toast(e.message, true)));
$('#psd-input').addEventListener('change', (e) => { uploadPsds([...e.target.files]); e.target.value = ''; });
const psdDrop = $('#psd-drop');
psdDrop.addEventListener('dragover', (e) => { if (e.dataTransfer.types.includes('Files')) { e.preventDefault(); psdDrop.classList.add('drag'); } });
psdDrop.addEventListener('dragleave', () => psdDrop.classList.remove('drag'));
psdDrop.addEventListener('drop', (e) => { e.preventDefault(); psdDrop.classList.remove('drag'); uploadPsds([...e.dataTransfer.files]); });

/* ================================================================ designs (several) */
const IMG_ACCEPT = 'image/png,image/jpeg,image/webp,image/svg+xml,.svg';
const IMG_RE = /\.(png|jpe?g|webp|svg)$/i;
const IMG_ERR = 'The design must be a PNG, SVG, JPG or WebP image';

/**
 * SVG → PNG in the browser (WebKit renders the vector), up to 4000 px on the long side, with a transparent
 * background. The engine works with pixels; the original SVG's name and path are kept.
 */
async function rasterizeSvg(blob, name) {
  const text = await blob.text();
  const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
  const root = doc.documentElement;
  if (!root || root.nodeName.toLowerCase() !== 'svg') throw new Error(`"${name}" is not a valid SVG`);
  const vb = (root.getAttribute('viewBox') || '').split(/[\s,]+/).map(Number);
  let w = parseFloat(root.getAttribute('width')) || vb[2] || 1000;
  let h = parseFloat(root.getAttribute('height')) || vb[3] || 1000;
  if (vb.length === 4 && vb[2] > 0 && vb[3] > 0) h = w * vb[3] / vb[2];
  const scale = 4000 / Math.max(w, h);
  const W = Math.round(w * scale), H = Math.round(h * scale);
  root.setAttribute('width', W); root.setAttribute('height', H);
  if (!root.getAttribute('viewBox')) root.setAttribute('viewBox', `0 0 ${w} ${h}`);
  const url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(root)], { type: 'image/svg+xml' }));
  try {
    const img = await new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => rej(new Error(`Couldn't render "${name}"`)); i.src = url; });
    const c = Object.assign(document.createElement('canvas'), { width: W, height: H });
    c.getContext('2d').drawImage(img, 0, 0, W, H);
    const png = await new Promise((res) => c.toBlob(res, 'image/png'));
    return new File([png], name.replace(/\.svg$/i, '.png'), { type: 'image/png' });
  } finally { URL.revokeObjectURL(url); }
}
/** Uploads a design file (SVGs are rasterized first). Returns the design metadata. */
async function postDesign(file, source = null) {
  if (!IMG_RE.test(file.name)) throw new Error(IMG_ERR);
  const isSvg = /\.svg$/i.test(file.name);
  const fd = new FormData();
  fd.append('file', isSvg ? await rasterizeSvg(file, file.name) : file);
  fd.append('name', file.name);
  if (source) fd.append('source', source);
  return api('/api/designs', { method: 'POST', body: fd });
}
const dnById = (id) => S.designNodes.find((d) => d.id === id);
const dnDefault = (dn) => `Design ${S.designNodes.indexOf(dn) + 1}`;
const dnLabel = (dn) => (dn && dn.label) || dnDefault(dn);
function newDesignNode(design = null) {
  const n = S.designNodes.reduce((m, d) => Math.max(m, +String(d.id).replace(/\D/g, '') || 0), 0) + 1;
  const last = S.designNodes[S.designNodes.length - 1];
  const lastH = last ? document.getElementById('n-' + last.id)?.offsetHeight || 520 : 0;
  const dn = { id: 'd' + n, design, x: 48, y: last ? last.y + lastH + 40 : GRID.y0 };
  S.designNodes.push(dn);
  return dn;
}
function rememberDesign(d) {
  S.designs = [d, ...S.designs.filter((x) => x.id !== d.id && !(x.name === d.name && x.width === d.width))].slice(0, 12);
}
function setDesign(dnId, d) {
  const dn = dnById(dnId) || newDesignNode();
  dn.design = d;
  rememberDesign(d);
  renderCanvas(); scheduleSave();
}
async function uploadDesign(file, dnId) {
  if (!file) return;
  try {
    const d = await postDesign(file);
    setDesign(dnId, d);
    toast(`${dnLabel(dnById(dnId) || S.designNodes[S.designNodes.length - 1])}: ${d.name}`);
    return d;
  } catch (e) { toast(e.message, true); }
}
/** In the Mac app the design is picked with the native dialog, so its path is kept in the .mwf. */
async function pickDesignNative(dnId) {
  try {
    const path = await native().pick_design();
    if (!path) return;
    let d;
    if (/\.svg$/i.test(path)) {          // the SVG is rendered here; the server stores the PNG and the original path
      const b64 = await native().read_file(path);
      const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
      d = await postDesign(new File([bytes], baseName(path), { type: 'image/svg+xml' }), path);
    } else {
      d = await api('/api/designs/from-path', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path }) });
    }
    setDesign(dnId, d);
  } catch (e) { toast(e.message, true); }
}
/** Images dropped on the canvas fill empty designs and, if there are none, create new designs. */
async function dropDesigns(files) {
  for (const f of files) {
    const empty = S.designNodes.find((d) => !d.design);
    await uploadDesign(f, (empty || newDesignNode()).id);
  }
}
function addDesignNode() {
  const dn = newDesignNode();
  placeExport();
  renderCanvas(); scheduleSave();
  document.getElementById('n-' + dn.id)?.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' });
}
function removeDesignNode(id) {
  if (S.designNodes.length < 2) return;
  S.designNodes = S.designNodes.filter((d) => d.id !== id);
  for (const n of S.nodes) for (const l of Object.values(n.links || {})) if (l.design === id) l.design = null;
  renderCanvas(); scheduleSave();
}

/* ================================================================ nodes */
const GRID = { x0: 470, y0: 56, dx: 400, dy: 660, cols: 2 };
const slot = (i) => ({ x: GRID.x0 + (i % GRID.cols) * GRID.dx, y: GRID.y0 + Math.floor(i / GRID.cols) * GRID.dy });
function freeSlot() {
  // Below whatever is in the least occupied grid column.
  const cols = Array.from({ length: GRID.cols }, (_, j) => GRID.x0 + j * GRID.dx);
  const bottom = (x) => Math.max(GRID.y0 - 48, ...S.nodes.filter((n) => Math.abs(n.x - x) < 200)
    .map((n) => n.y + (document.getElementById('n-' + n.id)?.offsetHeight || 620)));
  const x = cols.reduce((a, b) => (bottom(b) < bottom(a) ? b : a));
  return { x, y: bottom(x) + 48 };
}
/** Places designs in a column and mockups in a grid, measuring each node's real height so they don't overlap. */
function autoLayout() {
  renderCanvas();
  const h = (id) => document.getElementById('n-' + id)?.offsetHeight || 520;
  let y = GRID.y0;
  for (const d of S.designNodes) { Object.assign(d, { x: 48, y }); y += h(d.id) + 40; }
  let rowY = GRID.y0;
  for (let i = 0; i < S.nodes.length; i += GRID.cols) {
    const row = S.nodes.slice(i, i + GRID.cols);
    row.forEach((n, j) => Object.assign(n, { x: GRID.x0 + j * GRID.dx, y: rowY }));
    rowY += Math.max(...row.map((n) => h(n.id))) + 48;
  }
  S.exportPos = { x: 0, y: GRID.y0 };
  placeExport();
  renderCanvas();
  requestAnimationFrame(fitZoom);
}
function arrange() {
  autoLayout();
  scheduleSave();
}
/** Default links: each Smart Object to a design, with the fit, rotation and color from its profile. */
function linkDefaults(s, design) {
  // Full-bleed piece (poster) + transparent logo: fit it whole and color it according to the surface.
  if (s.background === 'full-bleed' && design?.transparent) {
    return { fit: 'contain', tint: (s.surface ?? 0.5) < 0.5 ? '#ffffff' : '#1c2030', rotate: s.rotate || 0 };
  }
  return { fit: s.fit || 'contain', tint: s.tint ?? null, rotate: s.rotate || 0 };
}
function defaultLinks(m, designIds) {
  const ids = designIds.length ? designIds : [S.designNodes[0]?.id || null];
  return Object.fromEntries(m.smartObjects.map((s, i) => {
    const design = ids[Math.min(i, ids.length - 1)];
    return [s.uid, { design, ...linkDefaults(s, dnById(design)?.design) }];
  }));
}
function addNode(mockupId, x, y) {
  const m = mockupById(mockupId);
  if (!m) return;
  if (x == null) ({ x, y } = freeSlot());
  if (!S.designNodes.length) newDesignNode();
  const node = { id: 'n' + Math.random().toString(36).slice(2, 8), mockupId, x, y, links: defaultLinks(m, [S.designNodes[0].id]) };
  S.nodes.push(node);
  placeExport();
  renderCanvas();
  scheduleSave();
  document.getElementById('n-' + node.id)?.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' });
}
/** Readable name of each Smart Object ("Place Your Design Here (Double Click…)" → "Place Your Design Here 1"). */
function soLabels(m) {
  const base = m.smartObjects.map((s) => (s.name || 'Object').replace(/\s*\(.*?\)\s*/g, ' ').trim() || 'Object');
  return base.map((b, i) => (base.filter((x) => x === b).length > 1 ? `${b} ${base.slice(0, i + 1).filter((x) => x === b).length}` : b));
}

function designNodeHtml(dn) {
  const d = dn.design;
  const recents = S.designs.filter((x) => x.id !== d?.id).slice(0, 5);
  const input = `<input type="file" accept="${IMG_ACCEPT}" hidden data-design-input="${dn.id}">`;
  const body = d
    ? `<div class="design-drop" data-ddrop="${dn.id}">
         <div class="preview checker"><img src="/api/designs/${d.id}.png" alt="${esc(dnLabel(dn))}: ${esc(d.name)}"></div>
         <div class="drop-hint">Drop to replace the design</div>
       </div>
       <div class="design-meta"><strong title="${esc(d.source || d.name)}">${esc(d.name)}</strong><span>${d.width}×${d.height} px</span></div>
       ${d.transparent ? '' : '<p class="note warn">The image has no transparency: its background will also appear in the mockup.</p>'}
       <div class="design-actions">
         <label class="btn btn-outline btn-sm" data-pick-native="${dn.id}">${icon('upload')}Replace design${input}</label>
       </div>`
    : `<label class="drop design-drop" data-ddrop="${dn.id}" data-pick-native="${dn.id}">
         ${input}
         <span><span class="circle">${svg('image')}</span><strong>Upload a design</strong>Transparent PNG or SVG. Select it or drag it here.</span>
       </label>`;
  const rec = recents.length
    ? `<div><span class="field-label">Recent designs</span><div class="recents">${recents.map((r) =>
        `<button type="button" class="recent" data-pick-design="${r.id}" data-for="${dn.id}" title="${esc(r.name)}" aria-label="Use ${esc(r.name)} in ${esc(dnLabel(dn))}"><img src="/api/designs/${r.id}.png" alt="" loading="lazy"></button>`).join('')}</div></div>`
    : '';
  const uses = S.nodes.reduce((c, n) => c + Object.values(n.links || {}).filter((l) => l.design === dn.id).length, 0);
  return `<div class="node design-node" id="n-${dn.id}" data-dnode="${dn.id}" style="left:${dn.x}px;top:${dn.y}px">
    <div class="node-head" data-drag="dn:${dn.id}">
      <span class="node-icon">${svg('image')}</span>
      <span class="node-title"><span data-rename="dn:${dn.id}" title="Double-click to rename">${esc(dnLabel(dn))}</span><span class="node-sub">${uses} ${uses === 1 ? 'link' : 'links'}${dn.label ? ', ' + esc(dnDefault(dn)) : ''}</span></span>
      ${S.designNodes.length > 1 ? `<button class="icon-btn" type="button" data-remove-design="${dn.id}" title="Remove this design" aria-label="Remove ${esc(dnLabel(dn))}">${icon('x')}</button>` : ''}
    </div>
    <div class="node-body">${body}${rec}</div>
    <span class="port out"></span>
  </div>`;
}

function linkControlsHtml(n, uid, l) {
  const custom = l.tint && !TINTS.some(([v]) => v === l.tint);
  return `<div class="so-ctrl">
      <div class="seg seg-sm" role="group" aria-label="Fit">
        ${FIT.map(([v, lab]) => `<button type="button" data-fit="${v}" aria-pressed="${l.fit === v}">${lab}</button>`).join('')}
      </div>
      <button type="button" class="rot-btn rot-sm" data-rotate title="Rotate design 90°" aria-label="Rotate design 90°, currently ${l.rotate || 0} degrees">${icon('rotate')}<span>${l.rotate || 0}°</span></button>
    </div>
    <div class="tint tint-sm" role="group" aria-label="Design color">
      ${TINTS.map(([v, lab]) => `<button type="button" class="swatch ${v ? '' : 'orig'}" data-tint="${v}" aria-pressed="${(l.tint || '') === v}" title="${lab}" aria-label="${lab}" style="${v ? `--sw:${v}` : ''}"></button>`).join('')}
      <label class="swatch custom ${custom ? 'on' : ''}" title="Custom color" style="${custom ? `--sw:${l.tint}` : ''}">
        <input type="color" data-tint-custom value="${l.tint || '#4a43e6'}" aria-label="Pick a custom color">
      </label>
    </div>`;
}

function mockupNodeHtml(n) {
  const m = mockupById(n.mockupId);
  const last = lastStep(n.id);
  const st = last?.step;
  const running = st && (st.status === 'running' || (st.status === 'pending' && last.run.status !== 'failed'));
  let preview;
  if (!m) {
    preview = '<p class="note err">This mockup is no longer in the Gallery. Remove the node or add the PSD again.</p>';
  } else {
    const showResult = st?.status === 'success';
    const src = showResult ? fileUrl(last.run, st.thumb) : `/api/mockups/${m.id}/thumb.jpg`;
    preview = `<div class="preview">
      <img src="${src}" alt="${showResult ? 'Result' : 'Original mockup'}: ${esc(m.name)}" loading="lazy">
      <span class="tag ${showResult ? 'ok' : ''}">${showResult ? 'Result' : 'Original'}</span>
      ${showResult ? `<button class="zoom" type="button" data-view="${last.run.id}|${st.file}" aria-label="View result of ${esc(m.name)} at full size"></button>` : ''}
      ${running ? `<div class="veil">${icon('loader', 'spin')}${st.status === 'running' ? 'Compositing…' : 'Queued'}</div>` : ''}
    </div>`;
    if (st?.status === 'failed') preview += `<p class="note err">${esc(st.error || 'Couldn\'t generate')}</p>`;
    else if (st?.warnings?.length) preview += `<p class="note warn">${esc(st.warnings.join('. '))}</p>`;
  }
  const sos = m?.smartObjects || [];
  const labels = m ? soLabels(m) : [];
  const rows = sos.map((s, i) => {
    const l = n.links?.[s.uid] || { design: null, fit: s.fit || 'contain', tint: s.tint ?? null, rotate: s.rotate || 0 };
    const linked = !!l.design;
    return `<div class="so-row ${linked ? 'linked' : ''}" data-so="${s.uid}">
      <span class="port in so-port ${linked ? 'on' : ''}"></span>
      <div class="so-head">
        <span class="so-name" title="${esc(s.name)}">${esc(labels[i])}</span>
        <span class="so-meta">${s.ratio ? esc(s.ratio) + ', ' : ''}${s.inner ? `${s.inner[0]}×${s.inner[1]}` : ''}</span>
      </div>
      <select class="select select-sm" data-link-design aria-label="Design for ${esc(labels[i])}">
        <option value="" ${!linked ? 'selected' : ''}>Keep original</option>
        ${S.designNodes.map((dn) => `<option value="${dn.id}" ${l.design === dn.id ? 'selected' : ''}>${esc(dnLabel(dn))}${dn.design ? ': ' + esc(dn.design.name) : ' (empty)'}</option>`).join('')}
      </select>
      ${linked ? linkControlsHtml(n, s.uid, l) : ''}
    </div>`;
  }).join('');
  return `<div class="node ${running ? 'active' : ''} ${st?.status === 'failed' ? 'errored' : ''}" id="n-${n.id}" data-node="${n.id}" style="left:${n.x}px;top:${n.y}px">
    <div class="node-head" data-drag="${n.id}">
      <span class="node-icon">${svg('frame')}</span>
      <span class="node-title" title="${esc(m?.name)}"><span data-rename="${n.id}" title="Double-click to rename">${esc(n.label || m?.name || 'Mockup unavailable')}</span>${m ? `<span class="node-sub">${esc(m.category || 'Other')}${n.label ? ', ' + esc(m.name) : ''}</span>` : ''}</span>
      ${m ? `<button class="icon-btn run" type="button" data-run-one="${n.id}" title="Run only this mockup" aria-label="Run only ${esc(m.name)}">${icon('play')}</button>` : ''}
      <button class="icon-btn" type="button" data-remove="${n.id}" title="Remove from canvas" aria-label="Remove ${esc(m?.name || 'node')} from the canvas">${icon('x')}</button>
    </div>
    <div class="node-body">
      ${rows ? `<div><span class="field-label">${sos.length === 1 ? 'Smart Object' : `Smart Objects (${sos.length})`}</span><div class="so-list">${rows}</div></div>` : ''}
      ${preview}
    </div>
    <span class="port out"></span>
  </div>`;
}

function exportNodeHtml() {
  const ids = new Set(S.nodes.map((n) => n.id));
  const run = S.runs.find((r) => r.steps.some((s) => s.file && ids.has(s.nodeId))) || null;
  const done = run ? run.steps.filter((s) => s.file && ids.has(s.nodeId)) : [];
  return `<div class="node" id="n-export" style="left:${S.exportPos.x}px;top:${S.exportPos.y}px">
    <div class="node-head" data-drag="export">
      <span class="node-icon">${svg('package')}</span><span class="node-title">Export</span>
    </div>
    <div class="node-body">
      <div class="two">
        <label><span class="field-label">Format</span>
          <select class="select" data-out="format">
            <option value="png" ${S.output.format === 'png' ? 'selected' : ''}>PNG</option>
            <option value="jpg" ${S.output.format === 'jpg' ? 'selected' : ''}>JPG</option>
          </select></label>
        <label><span class="field-label">Size</span>
          <select class="select" data-out="scale">
            ${[[1, '100 %'], [0.5, '50 %'], [0.25, '25 %']].map(([v, l]) => `<option value="${v}" ${+S.output.scale === v ? 'selected' : ''}>${l}</option>`).join('')}
          </select></label>
      </div>
      ${done.length
        ? `<div><span class="field-label">Last run of this workflow, ${ago(run.finished || run.created)}</span>
            <div class="results">${done.map((s) => `<button type="button" data-view="${run.id}|${s.file}" aria-label="View ${esc(s.name)}"><img src="${fileUrl(run, s.thumb)}" alt="" loading="lazy"></button>`).join('')}</div></div>
           <a class="btn btn-outline btn-sm" href="/api/runs/${run.id}/zip">${icon('download')}Download all (.zip)</a>`
        : '<p class="note">Composites will appear here when you run the workflow.</p>'}
    </div>
    <span class="port in"></span>
  </div>`;
}

let canvasSig = '';
function canvasSignature() {
  return JSON.stringify([S.designNodes.map((d) => [d.id, d.design?.id]), S.designs.length, S.nodes.map((n) => [n.id, n.mockupId, n.links]),
    S.output, S.mockups.map((m) => [m.id, m.name, m.category]), S.runs.slice(0, 6).map((r) => [r.id, r.status, r.steps.map((s) => s.status)])]);
}
let dragging = null;
function renderCanvas(force = true) {
  const sig = canvasSignature();
  if (!force && sig === canvasSig) return;
  if (dragging) { canvasSig = ''; return; }
  canvasSig = sig;
  const world = $('#world');
  world.querySelectorAll('.node').forEach((el) => el.remove());
  world.insertAdjacentHTML('beforeend', S.designNodes.map(designNodeHtml).join('') + S.nodes.map(mockupNodeHtml).join('') + exportNodeHtml());
  $('#canvas-hint').hidden = S.nodes.length > 0;
  bindDesignInputs();
  requestAnimationFrame(() => { sizeWorld(); drawEdges(); });
}

function bindDesignInputs() {
  document.querySelectorAll('[data-design-input]').forEach((input) =>
    input.addEventListener('change', (e) => uploadDesign(e.target.files[0], input.dataset.designInput)));
  document.querySelectorAll('[data-ddrop]').forEach((drop) => {
    drop.addEventListener('dragover', (e) => { if (e.dataTransfer.types.includes('Files')) { e.preventDefault(); e.stopPropagation(); drop.classList.add('drag'); hideVeil(); } });
    drop.addEventListener('dragleave', () => drop.classList.remove('drag'));
    drop.addEventListener('drop', (e) => { e.preventDefault(); e.stopPropagation(); drop.classList.remove('drag'); hideVeil(); uploadDesign(e.dataTransfer.files[0], drop.dataset.ddrop); });
  });
}

/** Center of a port in canvas coordinates (works for ports nested in rows). */
function portXY(p) {
  if (!p) return null;
  const w = $('#world').getBoundingClientRect();
  const r = p.getBoundingClientRect();
  return { x: (r.left + r.width / 2 - w.left) / S.zoom, y: (r.top + r.height / 2 - w.top) / S.zoom };
}
function curve(a, b) {
  const dx = Math.max(60, Math.abs(b.x - a.x) / 2);
  return `M${a.x},${a.y} C${a.x + dx},${a.y} ${b.x - dx},${b.y} ${b.x},${b.y}`;
}
function drawEdges() {
  const paths = [];
  const to = portXY($('#n-export .port.in'));
  const outs = Object.fromEntries(S.designNodes.map((d) => [d.id, portXY(document.querySelector(`#n-${d.id} .port.out`))]));
  for (const n of S.nodes) {
    const el = document.getElementById('n-' + n.id);
    if (!el) continue;
    const live = el.classList.contains('active') ? ' live' : '';
    for (const [uid, l] of Object.entries(n.links || {})) {
      if (!l.design || !outs[l.design]) continue;
      const p = portXY(el.querySelector(`.so-row[data-so="${CSS.escape(uid)}"] .so-port`));
      if (p) paths.push(`<path class="edge${live}${dnById(l.design)?.design ? '' : ' empty'}" d="${curve(outs[l.design], p)}"/>`);
    }
    const o = portXY(el.querySelector(':scope > .port.out'));
    if (o && to) paths.push(`<path class="edge${live}" d="${curve(o, to)}"/>`);
  }
  $('#edges').innerHTML = paths.join('');
}
function sizeWorld() {
  const world = $('#world');
  let w = 0, h = 0;
  world.querySelectorAll('.node').forEach((el) => {
    w = Math.max(w, el.offsetLeft + el.offsetWidth);
    h = Math.max(h, el.offsetTop + el.offsetHeight);
  });
  S.worldW = w + 160;
  S.worldH = h + 160;
  world.style.width = S.worldW + 'px';
  world.style.height = S.worldH + 'px';
  applyZoom();
}

/* ---------- zoom ---------- */
S.zoom = 1;
function applyZoom() {
  const z = S.zoom;
  $('#world').style.transform = `scale(${z})`;
  const sizer = $('#sizer');
  sizer.style.width = Math.ceil((S.worldW || 0) * z) + 'px';
  sizer.style.height = Math.ceil((S.worldH || 0) * z) + 'px';
  $('#zoom-label').textContent = Math.round(z * 100) + ' %';
}
function setZoom(z, anchor) {
  const c = $('#canvas');
  const old = S.zoom;
  S.zoom = Math.min(1.5, Math.max(0.25, Math.round(z * 100) / 100));
  const ax = anchor ? anchor.x : c.clientWidth / 2, ay = anchor ? anchor.y : c.clientHeight / 2;
  const wx = (c.scrollLeft + ax) / old, wy = (c.scrollTop + ay) / old;
  applyZoom();
  c.scrollLeft = wx * S.zoom - ax;
  c.scrollTop = wy * S.zoom - ay;
}
function fitZoom() {
  const c = $('#canvas');
  sizeWorld();
  S.zoom = Math.min(1, Math.max(0.25, Math.min((c.clientWidth - 24) / (S.worldW - 100), (c.clientHeight - 70) / (S.worldH - 100))));
  applyZoom();
  c.scrollTo({ left: 0, top: 0 });
  drawEdges();
}
$('#zoom-in').addEventListener('click', () => { setZoom(S.zoom + 0.1); drawEdges(); });
$('#zoom-out').addEventListener('click', () => { setZoom(S.zoom - 0.1); drawEdges(); });
$('#zoom-fit').addEventListener('click', fitZoom);
$('#canvas').addEventListener('wheel', (e) => {
  if (!e.ctrlKey && !e.metaKey) return;          // trackpad pinch or Ctrl + wheel
  e.preventDefault();
  const r = $('#canvas').getBoundingClientRect();
  setZoom(S.zoom * Math.exp(-e.deltaY * 0.01), { x: e.clientX - r.left, y: e.clientY - r.top });
}, { passive: false });

/* automatic position of the Export node: to the right of the mockups */
function placeExport() {
  const maxRight = Math.max(...S.designNodes.map((d) => d.x + 360), ...S.nodes.map((n) => n.x + 360), 408);
  if (S.exportPos.x < maxRight + 60) S.exportPos.x = maxRight + 80;
}

/* ---------- canvas interaction ---------- */
const world = $('#world');
const nodeOf = (el) => S.nodes.find((x) => x.id === el.closest('[data-node]')?.dataset.node);
const linkOf = (el) => {
  const n = nodeOf(el);
  const uid = el.closest('[data-so]')?.dataset.so;
  return n && uid ? n.links?.[uid] : null;
};
world.addEventListener('click', (e) => {
  const rm = e.target.closest('[data-remove]');
  if (rm) {
    S.nodes = S.nodes.filter((n) => n.id !== rm.dataset.remove);
    renderCanvas(); scheduleSave();
    return;
  }
  const rmd = e.target.closest('[data-remove-design]');
  if (rmd) { removeDesignNode(rmd.dataset.removeDesign); return; }
  const nat = e.target.closest('[data-pick-native]');
  if (nat && native()?.pick_design && !e.target.closest('input')) { e.preventDefault(); pickDesignNative(nat.dataset.pickNative); return; }
  const fit = e.target.closest('[data-fit]');
  if (fit) {
    const l = linkOf(fit);
    if (l) { l.fit = fit.dataset.fit; renderCanvas(); scheduleSave(); }
    return;
  }
  const rot = e.target.closest('[data-rotate]');
  if (rot) {
    const l = linkOf(rot);
    if (l) { l.rotate = ((l.rotate || 0) + 90) % 360; renderCanvas(); scheduleSave(); }
    return;
  }
  const tint = e.target.closest('[data-tint]');
  if (tint) {
    const l = linkOf(tint);
    if (l) { l.tint = tint.dataset.tint || null; renderCanvas(); scheduleSave(); }
    return;
  }
  const pick = e.target.closest('[data-pick-design]');
  if (pick) { const d = S.designs.find((x) => x.id === pick.dataset.pickDesign); if (d) setDesign(pick.dataset.for, d); return; }
  const one = e.target.closest('[data-run-one]');
  if (one) { runWorkflow('single', [one.dataset.runOne]); return; }
  const view = e.target.closest('[data-view]');
  if (view) openViewer(...view.dataset.view.split('|'));
});
world.addEventListener('change', (e) => {
  const ld = e.target.closest('[data-link-design]');
  if (ld) {
    const n = nodeOf(ld);
    const uid = ld.closest('[data-so]').dataset.so;
    const s = mockupById(n.mockupId)?.smartObjects.find((x) => x.uid === uid) || {};
    n.links = n.links || {};
    const prev = n.links[uid];
    // When a design is linked for the first time, the profile values are applied; existing settings are kept.
    n.links[uid] = prev?.design ? { ...prev, design: ld.value || null }
      : { ...linkDefaults(s, dnById(ld.value)?.design), design: ld.value || null };
    renderCanvas(); scheduleSave();
    return;
  }
  const tc = e.target.closest('[data-tint-custom]');
  if (tc) {
    const l = linkOf(tc);
    if (l) { l.tint = tc.value; renderCanvas(); scheduleSave(); }
  }
  const o = e.target.closest('[data-out]');
  if (o) {
    S.output[o.dataset.out] = o.dataset.out === 'scale' ? +o.value : o.value;
    canvasSig = canvasSignature();
    scheduleSave();
  }
});

world.addEventListener('pointerdown', (e) => {
  const head = e.target.closest('[data-drag]');
  if (!head || e.target.closest('button, label, input, select') || e.button !== 0) return;
  const key = head.dataset.drag;
  const el = head.closest('.node');
  const pos = key.startsWith('dn:') ? dnById(key.slice(3)) : key === 'export' ? S.exportPos : S.nodes.find((n) => n.id === key);
  if (!pos) return;
  dragging = { el, pos, sx: e.clientX, sy: e.clientY, ox: pos.x, oy: pos.y };
  el.classList.add('dragging');
  head.setPointerCapture(e.pointerId);
});
world.addEventListener('pointermove', (e) => {
  if (!dragging) return;
  const { el, pos, sx, sy, ox, oy } = dragging;
  pos.x = Math.max(8, Math.round(ox + (e.clientX - sx) / S.zoom));
  pos.y = Math.max(8, Math.round(oy + (e.clientY - sy) / S.zoom));
  el.style.left = pos.x + 'px';
  el.style.top = pos.y + 'px';
  drawEdges();
});
function endDrag() {
  if (!dragging) return;
  dragging.el.classList.remove('dragging');
  dragging = null;
  sizeWorld();
  scheduleSave();
  renderCanvas(false);
}
world.addEventListener('pointerup', endDrag);
world.addEventListener('pointercancel', endDrag);

const canvas = $('#canvas');
const wrap = $('.canvas-wrap');
const hideVeil = () => { $('#drop-veil').hidden = true; };
wrap.addEventListener('dragover', (e) => {
  if (e.dataTransfer.types.includes('text/mockup')) { e.preventDefault(); canvas.classList.add('drop-target'); }
  else if (e.dataTransfer.types.includes('Files')) { e.preventDefault(); $('#drop-veil').hidden = false; }
});
wrap.addEventListener('dragleave', (e) => { if (!wrap.contains(e.relatedTarget)) { canvas.classList.remove('drop-target'); hideVeil(); } });
wrap.addEventListener('drop', (e) => {
  e.preventDefault();
  canvas.classList.remove('drop-target');
  hideVeil();
  const mid = e.dataTransfer.getData('text/mockup');
  const r = world.getBoundingClientRect();
  if (mid) { addNode(mid, Math.max(8, Math.round((e.clientX - r.left) / S.zoom - 180)), Math.max(8, Math.round((e.clientY - r.top) / S.zoom - 30))); return; }
  const files = [...e.dataTransfer.files];
  const psds = files.filter((f) => /\.(psd|psb)$/i.test(f.name));
  const imgs = files.filter((f) => IMG_RE.test(f.name));
  const flow = files.find((f) => /\.mwf$/i.test(f.name));
  if (flow) { loadFlowFile(flow); return; }
  if (psds.length) uploadPsds(psds);
  if (imgs.length) dropDesigns(imgs);
  if (!psds.length && !imgs.length && files.length) toast('That file type can\'t be used here. Drop a PNG, a PSD or a .mwf workflow.', true);
});

/* ================================================================ runs */
function runPayloadNodes(nodes) {
  return nodes.map((n) => ({
    nodeId: n.id, mockupId: n.mockupId, label: n.label || null,
    links: Object.entries(n.links || {}).filter(([, l]) => l.design && dnById(l.design)?.design)
      .map(([uid, l]) => ({ uid, designId: dnById(l.design).design.id, fit: l.fit, tint: l.tint || null, rotate: l.rotate || 0 })),
  }));
}
async function runWorkflow(kind = 'full', only = null) {
  if (!S.designNodes.some((d) => d.design)) { toast('First upload a design to a "Design" node', true); return; }
  const nodes = S.nodes.filter((n) => mockupById(n.mockupId) && (!only || only.includes(n.id)));
  if (!nodes.length) { toast('Add at least one mockup to the canvas', true); return; }
  const payload = runPayloadNodes(nodes);
  const empty = payload.filter((n) => !n.links.length).map((n) => mockupById(n.mockupId).name);
  if (empty.length === payload.length) { toast('No Smart Object is linked to a design with an image', true); return; }
  try {
    const run = await api('/api/runs', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind, output: S.output, nodes: payload.filter((n) => n.links.length) }),
    });
    S.runs.unshift(run);
    S.open.add(run.id);
    renderRuns(); renderCanvas(false); updateRunButton();
    poll();
    if (empty.length) toast(`Skipped (no linked design): ${empty.join(', ')}`);
    if (window.matchMedia('(max-width: 1280px)').matches) document.body.classList.add('show-history');
  } catch (e) { toast(e.message, true); }
}
$('#btn-run').addEventListener('click', () => runWorkflow('full'));
$('#btn-add-design').addEventListener('click', addDesignNode);
$('#btn-undo').addEventListener('click', undo);
$('#btn-redo').addEventListener('click', redo);

/* ---------- rename nodes (double-click the title) ---------- */
$('#world').addEventListener('dblclick', (e) => {
  const t = e.target.closest('[data-rename]');
  if (!t || t.querySelector('input')) return;
  const key = t.dataset.rename;
  const isDesign = key.startsWith('dn:');
  const item = isDesign ? dnById(key.slice(3)) : S.nodes.find((n) => n.id === key);
  if (!item) return;
  const def = isDesign ? dnDefault(item) : (mockupById(item.mockupId)?.name || '');
  const input = Object.assign(document.createElement('input'), { className: 'title-edit', value: item.label || def, maxLength: 60 });
  input.setAttribute('aria-label', 'Node name');
  t.replaceChildren(input);
  input.focus(); input.select();
  let done = false;
  const finish = (save) => {
    if (done) return;
    done = true;
    if (save) {
      const v = input.value.trim();
      item.label = v && v !== def ? v : null;
      scheduleSave();
    }
    renderCanvas();
  };
  input.addEventListener('keydown', (ev) => { if (ev.key === 'Enter') finish(true); else if (ev.key === 'Escape') finish(false); ev.stopPropagation(); });
  input.addEventListener('blur', () => finish(true));
});
$('#btn-arrange').addEventListener('click', arrange);
$('#btn-save').addEventListener('click', (e) => saveFlowFile(e.shiftKey || e.altKey));
$('#btn-open').addEventListener('click', openFlow);
$('#btn-new').addEventListener('click', requestNew);
$('#flow-input').addEventListener('change', (e) => { const f = e.target.files[0]; e.target.value = ''; if (f) loadFlowFile(f); });
document.addEventListener('keydown', (e) => {
  const mod = e.metaKey || e.ctrlKey;
  if (!mod) return;
  const k = e.key.toLowerCase();
  const typing = e.target.closest?.('input, textarea, select, [contenteditable]');
  if (!typing && !document.querySelector('dialog[open]')) {
    if (k === 'z' && !e.shiftKey) { e.preventDefault(); undo(); return; }
    if ((k === 'z' && e.shiftKey) || k === 'y') { e.preventDefault(); redo(); return; }
  }
  if (k === 's') { e.preventDefault(); saveFlowFile(e.shiftKey); }
  else if (k === 'o') { e.preventDefault(); openFlow(); }
});
$('#btn-panels').addEventListener('click', () => document.body.classList.toggle('show-history'));
$('#btn-close-history').addEventListener('click', () => document.body.classList.remove('show-history'));
$('#title').addEventListener('input', (e) => { S.title = e.target.value; scheduleSave(); });

function updateRunButton() {
  const busy = !!activeRun();
  const b = $('#btn-run');
  b.disabled = busy;
  b.innerHTML = busy ? `${icon('loader', 'spin')}Running…` : `${icon('play')}<span>Run<span class="run-label"> workflow</span></span>`;
}

let pollTimer;
async function poll() {
  clearTimeout(pollTimer);
  try {
    S.runs = await api('/api/runs');
  } catch { /* the server may be busy; retry */ }
  const wasBusy = $('#btn-run').disabled;
  renderRuns(); renderCanvas(false); updateRunButton();
  const busy = activeRun();
  if (busy) pollTimer = setTimeout(poll, 900);
  else if (wasBusy && S.runs[0]) {
    const r = S.runs[0];
    const ok = r.steps.filter((s) => s.status === 'success').length;
    toast(r.status === 'success' ? `Done: ${ok} ${ok === 1 ? 'composite generated' : 'composites generated'}` : `${ok} of ${r.steps.length} composites generated. Check the History.`, r.status !== 'success');
  }
}

function stepIcon(status) {
  if (status === 'success') return icon('ok', 'st success');
  if (status === 'failed') return icon('fail', 'st failed');
  if (status === 'running') return icon('loader', 'st running spin');
  return icon('circle', 'st pending');
}
function runIcon(r) {
  if (r.status === 'success') return icon('ok', 'st success');
  if (r.status === 'failed') return icon('fail', 'st failed');
  if (r.status === 'partial') return icon('warn', 'st partial');
  return icon('loader', 'st running spin');
}
function renderRuns() {
  $('#run-count').textContent = `${S.runs.length} ${S.runs.length === 1 ? 'run' : 'runs'}`;
  const box = $('#runs');
  if (!S.runs.length) {
    box.innerHTML = `<div class="hist-empty">${icon('history')}<p>You haven't run the workflow yet. Upload your design, add mockups and press "Run workflow".</p></div>`;
    return;
  }
  const now = Date.now() / 1000;
  box.innerHTML = S.runs.map((r) => {
    const live = r.status === 'running' || r.status === 'queued';
    const ms = r.ms ?? (r.started ? Math.round((now - r.started) * 1000) : null);
    const files = r.steps.filter((s) => s.file);
    const open = S.open.has(r.id) || live;
    return `<article class="run ${open ? 'open' : ''}">
      <button class="run-head" type="button" data-toggle="${r.id}" aria-expanded="${open}">
        ${runIcon(r)}
        <span><span class="run-title">${r.kind === 'single' ? 'Single run' : 'Full run'}<span class="pill ${r.status}">${STATUS[r.status] || r.status}</span></span>
        <span class="run-sub">${icon('clock')}${cap(ago(r.created))} · ${dur(ms)} · ${r.steps.length} ${r.steps.length === 1 ? 'mockup' : 'mockups'}</span></span>
        ${icon('chevron', 'chev')}
      </button>
      <div class="run-body">
        <ol class="steps">${r.steps.map((s) => `<li class="step"><span class="dot"></span><span class="name" title="${esc(s.name)}">${esc(s.name)}</span>
          <span class="time">${s.status === 'running' && s.started ? dur(Math.round((now - s.started) * 1000)) : s.ms != null ? dur(s.ms) : '–'}</span>${stepIcon(s.status)}
          ${s.status === 'failed' ? `<span class="step-err">${esc(s.error)}</span>` : ''}</li>`).join('')}</ol>
        ${files.length ? `<div class="results" style="margin-top:10px">${files.map((s) => `<button type="button" data-view="${r.id}|${s.file}" aria-label="View ${esc(s.name)}"><img src="${fileUrl(r, s.thumb)}" alt="" loading="lazy"></button>`).join('')}</div>
          <div class="run-actions"><a class="btn btn-outline btn-sm" href="/api/runs/${r.id}/zip">${icon('download')}Download .zip</a></div>` : ''}
      </div>
    </article>`;
  }).join('');
}
$('#btn-clear-runs').addEventListener('click', async () => {
  if (!S.runs.length) { toast('The History is already empty'); return; }
  if (activeRun()) { toast('A run is in progress. Wait for it to finish before clearing the History.', true); return; }
  if (!confirm(`Clear the History (${S.runs.length} ${S.runs.length === 1 ? 'run' : 'runs'})?\n\nGenerated composites are moved to the Trash; you can restore them from there.`)) return;
  try {
    await api('/api/runs', { method: 'DELETE' });
    S.runs = [];
    renderRuns(); renderCanvas();
    toast('History cleared');
  } catch (err) { toast(err.message, true); }
});
$('#runs').addEventListener('click', (e) => {
  const t = e.target.closest('[data-toggle]');
  if (t) {
    const id = t.dataset.toggle;
    S.open.has(id) ? S.open.delete(id) : S.open.add(id);
    renderRuns();
    return;
  }
  const view = e.target.closest('[data-view]');
  if (view) openViewer(...view.dataset.view.split('|'));
});

/* ================================================================ viewer */
const viewer = $('#viewer');
function openViewer(runId, file) {
  const run = S.runs.find((r) => r.id === runId);
  const step = run?.steps.find((s) => s.file === file);
  if (!step) return;
  $('#viewer-title').textContent = step.name;
  $('#viewer-meta').textContent = `${step.size?.[0]}×${step.size?.[1]} px, ${file.split('.').pop().toUpperCase()}`;
  $('#viewer-dl').href = fileUrl(run, file, true);
  const frame = $('#viewer-frame');
  frame.innerHTML = `<p class="loading-line">${icon('loader', 'spin')}Loading the full-size composite…</p>`;
  const img = new Image();
  img.alt = `Final composite: ${step.name}`;
  img.onload = () => { frame.innerHTML = ''; frame.appendChild(img); };
  img.onerror = () => { frame.innerHTML = '<p class="loading-line">Couldn\'t load the image. Try downloading it.</p>'; };
  img.src = fileUrl(run, file);
  viewer.showModal();
}
viewer.addEventListener('click', (e) => { if (e.target === viewer || e.target.closest('[data-close]')) viewer.close(); });

/* ================================================================ theme */
function syncThemeSwitch() {
  const dark = document.documentElement.dataset.theme === 'dark';
  const b = $('#btn-theme');
  b.setAttribute('aria-checked', dark);
  b.title = dark ? 'Switch to light mode' : 'Switch to dark mode';
}
$('#btn-theme').addEventListener('click', () => {
  const t = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem('mw-theme', t); } catch { /* no storage: this session only */ }
  syncThemeSwitch();
});

/* ================================================================ .mwf files */
const baseName = (p) => String(p || '').split(/[\\/]/).pop();
async function exportXml() {
  const res = await fetch('/api/flows/export', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(flowState()) });
  if (!res.ok) throw new Error('Couldn\'t prepare the workflow file');
  return { xml: await res.text(), suggested: decodeURIComponent(res.headers.get('X-File-Name') || 'Workflow.mwf') };
}
/** Save: reuses the open file if there is one; "Save as" (⇧⌘S) always asks. */
async function saveFlowFile(saveAs = false) {
  try {
    const { xml, suggested } = await exportXml();
    if (native()?.save_flow) {                                  // Mac app (pywebview): native dialog
      const path = await native().save_flow(xml, saveAs ? null : S.filePath, S.fileName || suggested);
      if (!path) return;
      S.filePath = path; S.fileName = baseName(path);
    } else if (window.showSaveFilePicker) {                     // Chrome / Edge
      let h = saveAs ? null : S.fileHandle;
      if (!h) {
        try { h = await window.showSaveFilePicker({ suggestedName: S.fileName || suggested, types: FLOW_TYPES }); }
        catch (e) { if (e.name === 'AbortError') return; throw e; }
      }
      const w = await h.createWritable();
      await w.write(xml);
      await w.close();
      S.fileHandle = h; S.fileName = h.name;
    } else {                                                    // Safari / Firefox: download
      const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(new Blob([xml], { type: 'application/xml' })), download: S.fileName || suggested });
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      S.fileName = a.download;
    }
    S.fileDirty = false;
    renderSaved(); save();
    toast(`Workflow saved to ${S.fileName}`);
    return true;
  } catch (e) { toast('Couldn\'t save the workflow: ' + e.message, true); }
  return false;
}
async function openFlow() {
  try {
    if (native()?.open_flow) {
      const r = await native().open_flow();
      if (!r) return;
      const state = await api('/api/flows/import', { method: 'POST', headers: { 'Content-Type': 'application/xml' }, body: r.xml });
      return applyFlow(state, baseName(r.path), null, r.path);
    }
    if (window.showOpenFilePicker) {
      let h;
      try { [h] = await window.showOpenFilePicker({ types: FLOW_TYPES, multiple: false }); }
      catch (e) { if (e.name === 'AbortError') return; throw e; }
      return loadFlowFile(await h.getFile(), h);
    }
    $('#flow-input').click();
  } catch (e) { toast('Couldn\'t open the workflow: ' + e.message, true); }
}
async function loadFlowFile(file, handle = null) {
  if (!/\.mwf$/i.test(file.name)) { toast('Choose a .mwf workflow file', true); return; }
  try {
    const fd = new FormData();
    fd.append('file', file);
    applyFlow(await api('/api/flows/import', { method: 'POST', body: fd }), file.name, handle);
  } catch (e) { toast('Couldn\'t open the workflow: ' + e.message, true); }
}
function applyFlow(st, fileName, handle, path = null, layout = false) {
  const m = migrateFlow(st);
  Object.assign(S, {
    title: m.title, designNodes: m.designNodes, nodes: m.nodes, output: m.output || { format: 'png', scale: 1 },
    exportPos: m.exportPos || { x: 900, y: 56 }, fileName, fileHandle: handle, filePath: path, fileDirty: false,
  });
  S.designNodes.forEach((d) => d.design && rememberDesign(d.design));
  placeExport();
  refreshAll();
  if (layout) autoLayout();
  resetHistory();
  save();
  if (st.missing?.length) toast(`Opened, but missing from the Gallery: ${st.missing.join(', ')}. Add them and open the workflow again.`, true);
  else toast(`Workflow opened: ${fileName}`);
}
/** Welcome workflow: the app logo on every mockup in the Gallery (the Demo workflow file). */
async function openDemo() {
  try {
    const st = await api('/api/demo', { method: 'POST' });
    applyFlow(st, st.fileName, null, native() ? st.filePath : null, true);
  } catch (e) { toast('Couldn\'t load the Demo workflow: ' + e.message, true); openNewDialog(); }
}
function refreshAll() {
  $('#title').value = S.title;
  renderLibrary(); renderSaved(); renderCanvas();
  setTimeout(fitZoom, 40);
}

/**
 * Converts workflows from earlier versions (a single design; uid/fit/tint/rotate per node) to the current model
 * (several design nodes and links per Smart Object). Current workflows pass through unchanged.
 */
function migrateFlow(st) {
  const out = { ...st };
  if (!Array.isArray(st.designNodes) || !st.designNodes.length) {
    out.designNodes = [{ id: 'd1', design: st.design || null, x: st.designPos?.x ?? 48, y: st.designPos?.y ?? 56 }];
  }
  const first = out.designNodes[0].id;
  out.nodes = (st.nodes || []).map((n) => {
    if (n.links) return n;
    const m = mockupById(n.mockupId);
    const links = {};
    for (const s of m?.smartObjects || []) {
      links[s.uid] = { design: !n.uid || n.uid === s.uid ? first : null, fit: n.fit || 'contain', tint: n.tint || null, rotate: n.rotate || 0 };
    }
    const { uid, fit, tint, rotate, ...rest } = n;
    return { ...rest, links };
  });
  return out;
}

/* ================================================================ new workflow */
const dlg = $('#new-dialog');
const NF = { designs: [], mockups: [], filter: '' };   // designs and mockups: ids in the chosen order
/** "New": if the open workflow has unsaved changes, ask first (Save / Don't save / Cancel). */
async function requestNew() {
  const hasContent = S.nodes.length || S.designNodes.some((d) => d.design);
  if (S.fileDirty && hasContent) {
    const choice = await askSave();
    if (choice === 'cancel') return;
    if (choice === 'save' && !(await saveFlowFile(false))) return;
  }
  openNewDialog();
}
function askSave() {
  const d = $('#save-dialog');
  $('#save-title').textContent = `Save changes to "${S.title}"?`;
  $('#save-text').textContent = S.fileName
    ? `${S.fileName} has unsaved changes. If you create a new workflow without saving, they will be lost.`
    : 'This workflow isn\'t saved to a file. If you create a new one without saving it, it will be lost.';
  return new Promise((resolve) => {
    const done = (v) => { d.close(); resolve(v); };
    d.onclick = (e) => {
      const b = e.target.closest('[data-choice]');
      if (b) done(b.dataset.choice); else if (e.target === d) done('cancel');
    };
    d.oncancel = (e) => { e.preventDefault(); done('cancel'); };
    d.showModal();
    $('#save-dialog [data-choice="save"]').focus();
  });
}
async function openNewDialog() {
  S.designs = await api('/api/designs').catch(() => S.designs);
  // Selected by default: the most recently used design or, if only the demo is there, its two designs.
  NF.designs = S.designs.some((d) => d.demo) ? S.designs.map((d) => d.id) : S.designs.slice(0, 1).map((d) => d.id);
  NF.mockups = [];
  NF.filter = '';
  $('#new-name').value = 'Untitled workflow';
  $('#gal-search').value = '';
  $('#new-note').hidden = !(S.nodes.length || S.designNodes.some((d) => d.design));
  renderNewDesigns(); renderGallery();
  dlg.showModal();
  $('#new-name').select();
  scanGallery(true);
}
function renderNewDesigns() {
  const box = $('#new-designs');
  box.innerHTML = `<label class="dp-card upload" id="new-design-drop">
      <input type="file" accept="${IMG_ACCEPT}" hidden id="new-design-input">
      <span class="thumb">${icon('upload')}</span><span>Upload or drag a PNG or SVG</span>
    </label>
    <button type="button" class="dp-card none" data-pick="" aria-pressed="${!NF.designs.length}"><span class="thumb">I'll choose later</span><span class="name">No design</span></button>` +
    S.designs.map((d) => {
      const i = NF.designs.indexOf(d.id);
      return `<div class="dp-wrap"><button type="button" class="dp-card" data-pick="${d.id}" aria-pressed="${i >= 0}" title="${esc(d.source || d.name)}">
      ${i >= 0 ? `<span class="dp-order">${i + 1}</span>` : ''}
      <span class="thumb"><img src="/api/designs/${d.id}.png" alt="" loading="lazy"></span><span class="name">${esc(d.name)}</span></button>
      ${d.demo ? '' : `<button type="button" class="dp-remove" data-hide-design="${d.id}" title="Remove from this list" aria-label="Remove ${esc(d.name)} from the list">${icon('x')}</button>`}</div>`;
    }).join('');
  $('#new-design-input').addEventListener('change', async (e) => { const f = e.target.files[0]; if (f) await newDesignUpload(f); });
  renderOrder();
  const drop = $('#new-design-drop');
  drop.addEventListener('dragover', (e) => { if (e.dataTransfer.types.includes('Files')) { e.preventDefault(); drop.classList.add('drag'); } });
  drop.addEventListener('dragleave', () => drop.classList.remove('drag'));
  drop.addEventListener('drop', (e) => { e.preventDefault(); drop.classList.remove('drag'); if (e.dataTransfer.files[0]) newDesignUpload(e.dataTransfer.files[0]); });
}
async function newDesignUpload(file) {
  try {
    const d = await postDesign(file);
    rememberDesign(d);
    if (!NF.designs.includes(d.id)) NF.designs.push(d.id);
    renderNewDesigns();
  } catch (e) { toast(e.message, true); }
}
function renderGallery() {
  const box = $('#gallery');
  const q = NF.filter.trim().toLowerCase();
  const list = S.mockups.filter((m) => !q || `${m.name} ${m.category} ${m.file}`.toLowerCase().includes(q));
  if (!S.mockups.length) {
    box.innerHTML = '<p class="gal-empty">The Gallery is empty. Copy your PSDs into the Gallery folder (folder button in the left column) or add them with "Add PSD mockup".</p>';
  } else if (!list.length) {
    box.innerHTML = `<p class="gal-empty">No mockup matches "${esc(NF.filter)}".</p>`;
  } else {
    const groups = groupBy(list);
    const names = groupOrder(Object.keys(groups));
    box.innerHTML = names.map((cat) => `<section class="gal-group">${names.length > 1 || cat ? `<h4>${esc(cat || 'Uncategorized')}</h4>` : ''}
      <div class="gal-grid">${groups[cat].map((m) => `<label class="gal-card">
        <input type="checkbox" value="${m.id}" ${NF.mockups.includes(m.id) ? 'checked' : ''} aria-label="${esc(m.name)}">
        <img src="/api/mockups/${m.id}/thumb.jpg" alt="" loading="lazy">
        <span class="check">${icon('check')}${checkNum(m.id)}</span>
        <span class="name" title="${esc(m.name)}">${esc(m.name)}</span>
        <span class="meta">${m.size[0]}×${m.size[1]} px, ${soLabel(m)}</span>
      </label>`).join('')}</div></section>`).join('');
  }
  updateNewButton();
}
function updateNewButton() {
  const n = NF.mockups.length;
  $('#new-create').textContent = n ? `Create workflow with ${n} ${n === 1 ? 'mockup' : 'mockups'}` : 'Create empty workflow';
  const visible = [...$('#gallery').querySelectorAll('input')];
  $('#gal-all').textContent = visible.length && visible.every((i) => i.checked) ? 'Deselect all' : 'Select all';
}
$('#gallery').addEventListener('change', (e) => {
  if (e.target.type !== 'checkbox') return;
  toggleMockup(e.target.value, e.target.checked);
  selectionChanged();
});
$('#gal-search').addEventListener('input', (e) => { NF.filter = e.target.value; renderGallery(); });
$('#gal-all').addEventListener('click', () => {
  const inputs = [...$('#gallery').querySelectorAll('input')];
  const all = inputs.every((i) => i.checked);
  inputs.forEach((i) => { i.checked = !all; toggleMockup(i.value, !all); });
  selectionChanged();
});
$('#new-designs').addEventListener('click', async (e) => {
  const hide = e.target.closest('[data-hide-design]');
  if (hide) {
    // Only removed from the recents list; the file and the workflows that use it don't change.
    const id = hide.dataset.hideDesign;
    try {
      await api(`/api/designs/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ hidden: true }) });
      S.designs = await api('/api/designs');
      NF.designs = NF.designs.filter((x) => x !== id);
      if (!NF.designs.length && S.designs.every((d) => d.demo)) NF.designs = S.designs.map((d) => d.id);
      renderNewDesigns(); renderCanvas();
    } catch (err) { toast(err.message, true); }
    return;
  }
  const b = e.target.closest('[data-pick]');
  if (!b) return;
  const id = b.dataset.pick;
  if (!id) NF.designs = [];
  else NF.designs = NF.designs.includes(id) ? NF.designs.filter((x) => x !== id) : [...NF.designs, id];
  renderNewDesigns();
});
dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.closest('[data-close]')) dlg.close(); });

/* ---- order of the selected designs and mockups: drag, or arrow keys on a focused item ---- */
const checkNum = (id) => { const i = NF.mockups.indexOf(id); return i >= 0 ? `<span class="check-num">${i + 1}</span>` : ''; };
function toggleMockup(id, on) {
  if (on && !NF.mockups.includes(id)) NF.mockups.push(id);
  if (!on) NF.mockups = NF.mockups.filter((x) => x !== id);
}
/** After the mockup selection or its order changes: numbers on the gallery cards, the order bar and the button. */
function selectionChanged() {
  $('#gallery').querySelectorAll('.gal-card').forEach((card) => {
    const id = card.querySelector('input').value;
    card.querySelector('.check').innerHTML = icon('check') + checkNum(id);
  });
  renderOrder();
  updateNewButton();
}
function orderItems(kind) {
  return kind === 'designs'
    ? NF.designs.map((id) => S.designs.find((d) => d.id === id)).filter(Boolean)
      .map((d) => ({ id: d.id, name: d.name, img: `/api/designs/${d.id}.png`, contain: true }))
    : NF.mockups.map(mockupById).filter(Boolean).map((m) => ({ id: m.id, name: m.name, img: `/api/mockups/${m.id}/thumb.jpg` }));
}
function renderOrder(kind = null, moved = null) {
  let shown = 0;
  for (const k of ['designs', 'mockups']) {
    const items = orderItems(k);
    const row = $(`#order-${k}-row`);
    row.hidden = items.length < 2;   // a single item has no order to choose
    if (row.hidden) continue;
    shown++;
    const list = $(`#order-${k}`);
    list.innerHTML = items.map((it, i) => `<li class="order-chip${k === kind && it.id === moved ? ' moved' : ''}" draggable="true" tabindex="0"
        data-id="${it.id}" title="${esc(it.name)}" aria-label="${esc(it.name)}, ${i + 1} of ${items.length}">
        <span class="order-num" aria-hidden="true">${i + 1}</span>
        <img src="${it.img}" alt="" class="${it.contain ? 'contain' : ''}" loading="lazy" draggable="false">
        <span class="order-name" aria-hidden="true">${esc(it.name)}</span></li>`).join('');
  }
  $('#new-order').hidden = !shown;
}
/** Moves an item of the designs or mockups list to position `to` and refreshes everything that shows the order. */
function moveItem(kind, id, to) {
  const arr = kind === 'designs' ? NF.designs : NF.mockups;
  const from = arr.indexOf(id);
  to = Math.max(0, Math.min(arr.length - 1, to));
  if (from < 0 || from === to) return;
  arr.splice(to, 0, arr.splice(from, 1)[0]);
  if (kind === 'designs') renderNewDesigns(); else selectionChanged();
  renderOrder(kind, id);
  const name = orderItems(kind)[to]?.name || '';
  $('#order-live').textContent = `${name} moved to position ${to + 1} of ${arr.length}`;
}
const ORDER = { kind: null, id: null };
$('#new-order').addEventListener('keydown', (e) => {
  const chip = e.target.closest('.order-chip');
  if (!chip) return;
  const kind = chip.parentElement.dataset.kind;
  const arr = kind === 'designs' ? NF.designs : NF.mockups;
  const i = arr.indexOf(chip.dataset.id);
  const to = { ArrowLeft: i - 1, ArrowUp: i - 1, ArrowRight: i + 1, ArrowDown: i + 1, Home: 0, End: arr.length - 1 }[e.key];
  if (to === undefined) return;
  e.preventDefault();
  moveItem(kind, chip.dataset.id, to);
  $(`#order-${kind} [data-id="${chip.dataset.id}"]`)?.focus();
});
$('#new-order').addEventListener('dragstart', (e) => {
  const chip = e.target.closest('.order-chip');
  if (!chip) return;
  Object.assign(ORDER, { kind: chip.parentElement.dataset.kind, id: chip.dataset.id });
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', chip.dataset.id);
  requestAnimationFrame(() => chip.classList.add('dragging'));
});
const clearDropMarks = () => $('#new-order').querySelectorAll('.drop-before, .drop-after')
  .forEach((c) => c.classList.remove('drop-before', 'drop-after'));
/** Where a drop lands: before or after the chip under the pointer, in the same list as the dragged chip. */
function dropTarget(e) {
  const chip = e.target.closest('.order-chip');
  if (!ORDER.id || !chip || chip.parentElement.dataset.kind !== ORDER.kind) return null;
  const r = chip.getBoundingClientRect();
  return { chip, after: e.clientX > r.left + r.width / 2 };
}
$('#new-order').addEventListener('dragover', (e) => {
  const t = dropTarget(e);
  if (!t) return;
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  clearDropMarks();
  if (t.chip.dataset.id !== ORDER.id) t.chip.classList.add(t.after ? 'drop-after' : 'drop-before');
});
$('#new-order').addEventListener('drop', (e) => {
  const t = dropTarget(e);
  clearDropMarks();
  if (!t) return;
  e.preventDefault();
  const arr = (ORDER.kind === 'designs' ? NF.designs : NF.mockups).filter((x) => x !== ORDER.id);
  const at = arr.indexOf(t.chip.dataset.id);
  const to = t.chip.dataset.id === ORDER.id ? -1 : at + (t.after ? 1 : 0);
  if (to >= 0) moveItem(ORDER.kind, ORDER.id, to);
});
$('#new-order').addEventListener('dragend', () => {
  clearDropMarks();
  $('#new-order').querySelectorAll('.dragging').forEach((c) => c.classList.remove('dragging'));
  ORDER.id = ORDER.kind = null;
});
$('#new-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const ids = NF.mockups.filter((id) => mockupById(id));   // in the chosen order
  const chosen = NF.designs.map((id) => S.designs.find((d) => d.id === id)).filter(Boolean);
  const designNodes = (chosen.length ? chosen : [null]).map((d, i) => ({ id: 'd' + (i + 1), design: d, x: 48, y: GRID.y0 + i * 470 }));
  Object.assign(S, {
    title: $('#new-name').value.trim() || 'Untitled workflow',
    designNodes,
    // With several designs, each Smart Object of a mockup gets the next one (1st → design 1, 2nd → design 2…).
    nodes: ids.map((mockupId, i) => ({ id: 'n' + Math.random().toString(36).slice(2, 8), mockupId, ...slot(i),
      links: defaultLinks(mockupById(mockupId), designNodes.map((d) => d.id)) })),
    exportPos: { x: 0, y: GRID.y0 },
    fileName: null, fileHandle: null, filePath: null,
  });
  placeExport();
  dlg.close();
  refreshAll();
  autoLayout();
  resetHistory();
  scheduleSave();
  toast(ids.length ? `New workflow with ${ids.length} ${ids.length === 1 ? 'mockup' : 'mockups'}` : 'New workflow. Drag mockups from the Gallery.');
});

/* ================================================================ mockup profile */
const profDlg = $('#profile-dialog');
const PROF = { id: null, groups: ['Outdoor', 'Merchandise', 'Other'] };
const LOGO_OPTS = [['light', 'Light (white)'], ['dark', 'Dark (black)'], ['original', 'Original colors']];
const BG_OPTS = [['transparent', 'Transparent logo'], ['full-bleed', 'Full-bleed design']];
const opt = (list, v) => list.map(([k, l]) => `<option value="${k}" ${k === v ? 'selected' : ''}>${l}</option>`).join('');
async function openProfile(mid, isNew = false) {
  try {
    const r = await api(`/api/mockups/${mid}/profile`);
    const p = r.profile;
    PROF.id = mid;
    S.groups = r.groups || S.groups;
    const m = mockupById(mid);
    const labels = m ? soLabels(m) : p.objects.map((o) => o.name);
    $('#profile-title').textContent = isNew ? `Profile of "${p.name}"` : 'Mockup profile';
    $('#profile-lead').textContent = isNew
      ? 'The PSD has been analyzed. Choose its group (or create one) and review what was detected; it will be used when you add it to a workflow.'
      : 'Mockup characteristics. They are used as defaults when you add it to a workflow.';
    const chips = (o) => {
      const out = [`<span class="chip">Warp: ${esc(o.warp || 'none')}</span>`,
        `<span class="chip">${o.perspective === 'rectangular' ? 'No perspective' : 'Perspective'}</span>`];
      const inst = o.instances || [];
      if (inst.length > 1) out.push(`<span class="chip">${inst.length} instances</span>`);
      for (const i of inst) {
        const bits = [];
        if (i.opacity < 100) bits.push(`opacity ${i.opacity} %`);
        if (i.fill < 100) bits.push(`fill ${i.fill} %`);
        if (i.blend !== 'Normal') bits.push(i.blend);
        bits.push(...(i.effects || []), ...(i.filters || []));
        if ((i.clippedLayers || []).length) bits.push('clipped: ' + i.clippedLayers.map((c) => `${c.name} (${c.blend})`).join(', '));
        if (bits.length) out.push(`<span class="chip" title="${esc(i.name)}">${esc(i.visible ? '' : 'hidden: ')}${esc(bits.join(', '))}</span>`);
      }
      return out.join('');
    };
    const groupOpts = S.groups.map((g) => `<option ${g === p.group ? 'selected' : ''}>${esc(g)}</option>`).join('') +
      (S.groups.includes(p.group) ? '' : `<option selected>${esc(p.group)}</option>`) + '<option value="__new__">New group…</option>';
    const layers = p.layers || [];
    $('#profile-body').innerHTML = `
      <div class="two prof-top">
        <label class="field"><span class="field-label">Name</span><input class="input" name="nombre" value="${esc(p.name)}" maxlength="80"></label>
        <div class="field"><label><span class="field-label">Group</span><select class="select" name="grupo" id="prof-group">${groupOpts}</select></label>
          <input class="input new-group" id="prof-new-group" name="nuevoGrupo" placeholder="New group name" maxlength="40" hidden></div>
      </div>
      <p class="note">${esc(p.file)}, ${p.size[0]}×${p.size[1]} px. Each group is a Gallery folder: changing it moves the PSD and its profile.</p>
      ${p.objects.map((o, i) => `<fieldset class="prof-obj" data-obj="${esc(o.id)}">
        <legend>${esc(labels[i] || o.name)}<span class="so-meta">${o.ratio ? esc(o.ratio) + ', ' : ''}${o.canvas[0]}×${o.canvas[1]} px${o.visible ? '' : ', hidden'}</span></legend>
        <div class="prof-summary">${chips(o)}</div>
        <div class="prof-grid">
          <label><span class="field-label">Logo color</span><select class="select" name="logo">${opt(LOGO_OPTS, o.logo)}</select></label>
          <label><span class="field-label">Design layer</span><select class="select" name="fondo">${opt(BG_OPTS, o.background)}</select></label>
          <label><span class="field-label">Fit</span><select class="select" name="ajuste">${opt(FIT, o.fit)}</select></label>
          <label><span class="field-label">Rotation</span><select class="select" name="giro">${opt([[0, '0°'], [90, '90°'], [180, '180°'], [270, '270°']], o.rotate)}</select></label>
        </div>
        ${o.analysis ? `<p class="note">Detected: ${o.analysis.surface < 0.5 ? 'dark' : 'light'} surface (${Math.round(o.analysis.surface * 100)} %)${o.analysis.sample != null ? `, ${o.analysis.sample > 0.5 ? 'light' : 'dark'} PSD sample` : ''}; the sample content covers ${Math.round(o.analysis.coverage * 100)} % of the canvas.</p>` : ''}
      </fieldset>`).join('')}
      ${layers.length ? `<section class="prof-section"><h3>PSD layers (${layers.length})</h3>
        <div class="layers-wrap"><table class="layers">
          <thead><tr><th>Layer</th><th>Type</th><th>Blend</th><th class="num">Opacity</th><th>Details</th></tr></thead>
          <tbody>${layers.map((l) => {
            const det = [l.clipping ? 'clipping' : '', l.mask ? 'mask' : '', ...(l.effects || []), ...(l.filters || [])].filter(Boolean);
            return `<tr class="${l.visible ? '' : 'hidden-layer'} ${l.type === 'Smart Object' ? 'is-so' : ''}">
              <td><span class="lname" style="padding-left:${l.depth * 16}px">${esc(l.name)}</span>${l.visible ? '' : ' <span class="muted">(hidden)</span>'}</td>
              <td>${esc(l.type)}</td><td>${esc(l.blend)}</td>
              <td class="num">${l.opacity} %${l.fill < 100 ? ` / ${l.fill} %` : ''}</td>
              <td>${esc(det.join(', '))}${(l.warnings || []).map((a) => ` <span class="chip warn">${esc(a)}</span>`).join('')}</td></tr>`;
          }).join('')}</tbody></table></div></section>` : ''}`;
    $('#prof-group').addEventListener('change', (e) => {
      const ng = $('#prof-new-group');
      ng.hidden = e.target.value !== '__new__';
      if (!ng.hidden) ng.focus();
    });
    $('#profile-file').textContent = `File: ${baseName(r.path)}`;
    $('#profile-file').title = r.path;
    profDlg.showModal();
  } catch (e) { toast('Couldn\'t open the profile: ' + e.message, true); }
}
profDlg.addEventListener('click', (e) => { if (e.target === profDlg || e.target.closest('[data-close]')) profDlg.close(); });
$('#profile-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = e.target;
  const body = {
    name: f.elements.nombre.value,
    group: f.elements.grupo.value === '__new__' ? f.elements.nuevoGrupo.value.trim() : f.elements.grupo.value,
    objects: [...f.querySelectorAll('[data-obj]')].map((fs) => ({
      id: fs.dataset.obj, logo: fs.querySelector('[name=logo]').value, background: fs.querySelector('[name=fondo]').value,
      fit: fs.querySelector('[name=ajuste]').value, rotate: +fs.querySelector('[name=giro]').value,
    })),
  };
  try {
    const meta = await api(`/api/mockups/${PROF.id}/profile`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    S.mockups = S.mockups.map((m) => (m.id === meta.id ? meta : m));
    S.groups = await api('/api/groups').catch(() => S.groups);
    profDlg.close();
    renderLibrary(); renderCanvas();
    toast(`Profile of "${meta.name}" saved`);
  } catch (err) { toast(err.message, true); }
});

/* ================================================================ about */
const aboutDlg = $('#about-dialog');
async function openAbout() {
  try {
    const a = await api('/api/about');
    $('#about-version').textContent = `Version ${a.version}${a.packaged ? '' : ' (from source)'}`;
    $('#about-facts').innerHTML = [
      ['Author', `${esc(a.author)} · <a href="mailto:${esc(a.email)}">${esc(a.email)}</a>`],
      ['License', esc(a.license)],
      ['Work folder', esc(a.workFolder)],
      ['Workflow format', `.mwf version ${esc(a.flowFormat)}`],
      ['Engine', `psd-tools ${esc(a.psdTools)}, Python ${esc(a.python)}`],
    ].map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
    $('#about-legal').textContent = `${a.copyright}. License ${a.license}.`;
    aboutDlg.showModal();
  } catch (e) { toast(e.message, true); }
}
$('#btn-about').addEventListener('click', openAbout);
aboutDlg.addEventListener('click', (e) => { if (e.target === aboutDlg || e.target.closest('[data-close]')) aboutDlg.close(); });

/* ================================================================ Mac app (pywebview) */
// Downloads: in the native window they are saved with the macOS dialog instead of the browser download.
document.addEventListener('click', async (e) => {
  const a = e.target.closest('a[href^="/api/runs/"]');
  if (!a || !native()?.download) return;
  e.preventDefault();
  const url = a.getAttribute('href');
  const name = url.includes('/zip') ? `mockups-${url.split('/')[3]}.zip` : decodeURIComponent(url.split('/').pop().split('?')[0]);
  try {
    const path = await native().download(url, name);
    if (path) toast(`Saved to ${baseName(path)}`);
  } catch (err) { toast('Couldn\'t save the file: ' + err, true); }
});
/** Workflow passed when opening the app (double-click on a .mwf or "Open with"). */
async function openFromLaunch() {
  const path = new URLSearchParams(location.search).get('open');
  if (!path || !native()?.read_flow) return false;
  history.replaceState(null, '', '/');
  try {
    const r = await native().read_flow(path);
    const st = await api('/api/flows/import', { method: 'POST', headers: { 'Content-Type': 'application/xml' }, body: r.xml });
    applyFlow(st, baseName(r.path), null, r.path);
    return true;
  } catch (e) { toast('Couldn\'t open the workflow: ' + e.message, true); return false; }
}
const nativeReady = new Promise((res) => {
  if (window.pywebview?.api) res(true);
  else { window.addEventListener('pywebviewready', () => res(true)); setTimeout(() => res(false), 1500); }
});

/* ================================================================ startup */
const SPLASH_T0 = performance.now();
/** Removes the splash screen when the app is ready, letting the animation (≈0.9 s) finish. */
function hideSplash() {
  const el = $('#splash');
  if (!el) return;
  const wait = Math.max(0, 950 - (performance.now() - SPLASH_T0));
  setTimeout(() => { el.classList.add('done'); setTimeout(() => el.remove(), 400); }, wait);
}
async function init() {
  hydrateIcons();
  syncThemeSwitch();
  const [mockups, wf, runs, designs, groups] = await Promise.all([api('/api/mockups'), api('/api/workflow'), api('/api/runs'),
    api('/api/designs'), api('/api/groups').catch(() => S.groups)]);
  S.groups = groups;
  S.mockups = mockups;
  S.runs = runs;
  S.designs = designs;
  const firstRun = !(wf && wf.savedAt);
  if (!firstRun) {
    const m = migrateFlow(wf);
    Object.assign(S, { title: m.title || S.title, designNodes: m.designNodes, nodes: m.nodes, output: m.output || S.output,
      exportPos: m.exportPos || S.exportPos, savedAt: wf.savedAt,
      fileName: wf.fileName || null, filePath: wf.filePath || null, fileDirty: !!wf.fileDirty });
  }
  placeExport();
  $('#title').value = S.title;
  renderLibrary(); renderRuns(); renderSaved(); updateRunButton();
  renderCanvas();
  setTimeout(fitZoom, 60);
  if (activeRun()) poll();
  setInterval(() => { renderSaved(); if (!activeRun()) renderRuns(); }, 30000);
  document.body.classList.toggle('is-native', await nativeReady && !!native());
  const launched = await openFromLaunch();
  if (firstRun && !launched) await openDemo();
  resetHistory();
  hideSplash();
  setTimeout(() => scanGallery(true), 1500);   // picks up PSDs copied to the folder while the app was closed
}
init().catch((e) => { hideSplash(); toast('Couldn\'t load the app: ' + e.message, true); });
