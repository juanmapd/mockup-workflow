# Architecture

```
┌────────────────────────── Mockup Workflow.app (or browser) ─────────────────────────────┐
│  Interface: static/index.html + app.css + app.js                                        │
│  Node canvas, gallery, history, dialogs. Talks to the server over HTTP (JSON).          │
│  In the Mac app it also calls window.pywebview.api (native dialogs).                    │
└───────────────┬───────────────────────────────────────────────────┬─────────────────────┘
                │ HTTP 127.0.0.1                                    │ js_api
┌───────────────▼───────────────────────────────┐   ┌───────────────▼─────────────────────┐
│ app.py (Flask)                                │   │ desktop.py (pywebview)              │
│ · gallery, design, workflow and run API       │   │ · WebKit window, menus              │
│ · .mwf format (XML)                           │   │ · save/open .mwf, downloads         │
│ · run queue (one worker thread)               │   │ · work folder (config.json)         │
└───────────────┬───────────────────────────────┘   └─────────────────────────────────────┘
                │
┌───────────────▼───────────────────────────────┐
│ engine.py                                     │
│ · inspect(): Smart Objects of a PSD           │
│ · render(): composite with the new design     │
└───────────────────────────────────────────────┘
```

## Compositing engine (`engine.py`)

1. **Prepare the design.** `render()` receives `assignments`: one design (with its fit, rotation and color) per
   Smart Object `unique_id`. Smart Objects that are not listed keep their original content. Each design is
   prepared with `prepare_design` (rotate, recolor and fit to the inner canvas).
2. **Project it.** For each instance of the Smart Object (every layer with the same `unique_id`), the design is
   projected onto the document:
   - **No warp:** homography from the four corners to the transform box (`transform_box`).
   - **Classic warp (`warp`):** 4×4 Bézier mesh in the original placement space.
   - **Quilt warp (`quiltWarp`):** several Bézier patches. Note: in this case the transform box wraps the
     already warped mesh, not the inner canvas.

   Meshes are rasterized as triangles with affine transforms (OpenCV), using premultiplied alpha.
3. **Composite.** The psd-tools compositor is used, extended by the `_Compositor` subclass:
   - The content of replaced Smart Objects comes from the projection above.
   - Levels, Curves and Brightness/Contrast adjustment layers are applied to what lies below. In a
     pass-through group the adjustment extends the group's shape so it affects the whole background.
   - Added effects: drop shadow, inner shadow, outer glow and inner glow, approximated with offset and Gaussian
     blur.
   - Each effect's blend mode is translated to the compositor's internal key (`_fx_mode`).
4. **Export.** The result is composited over white where the PSD is transparent.

The psd-tools compositor is replaced at module level during `render()`; a lock (`_LOCK`) ensures that only one
composite runs at a time.

**Validation.** `mockup.py --check` and `make test PSD=…` render the PSD with its original content and compare
it with the composite saved by Photoshop.

**Profile analysis.** `analyze()` composites the mockup with an empty design to measure the surface under each
object (respecting its layer mask), measures the luminance and coverage of the sample content, and recommends a
light or dark logo. See [mockup-profile.md](mockup-profile.md).

## Server (`app.py`)

- **Paths.** `CODE` is where the code lives (inside the `.app` when packaged). `ROOT` is the work folder:
  `MW_HOME`, or the project folder.
- **Gallery.** `Mockup Gallery/` is scanned (`scan_gallery`). A moved or renamed PSD keeps its identifier if the
  file name and size match, or just the size if only one of them is missing.
- **Runs.** Stored in `data/runs.json` and processed in order by a single thread. If the app closes midway, they
  are marked as failed on the next start. Each step carries its links (`links`: `uid`, `designId`, fit, color
  and rotation).
- **Designs.** Identified by a hash of their pixels, so reopening a `.mwf` does not duplicate the design. They
  store the path of the copy (`path`) and, when known, the path of the original (`source`).
- **Profiles.** `register_mockup` creates or updates the `.mockup.json` of each PSD. `update_profile` applies the
  user's changes and, if the group changes, moves the PSD and its profile.

## Interface (`static/`)

- **No dependencies or build step.**
- **State:** lives in the `S` object in `app.js` (`designNodes`, and `nodes` with their per-Smart-Object
  `links`) and is saved automatically to `data/workflow.json`. `migrateFlow` converts workflows from earlier
  versions.
- **Canvas drawing:** the canvas is fully redrawn only when its "signature" (`canvasSignature`) changes, which
  avoids flicker while the history is polled.
- **Themes:** colors are CSS variables in `:root`, with their equivalents in `:root[data-theme="dark"]`.
