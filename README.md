# Mockup Workflow

Place a design (a logo or a PNG artwork) on several Photoshop mockups at once and export the results, without
opening Photoshop. It runs as a Mac app or in the browser, always locally.

- **Version:** the one in `version.py` (also shown in "About"). Changes in each version are listed in the [CHANGELOG](CHANGELOG.md).
- **Author:** Juanma PD (juanmapd@gmail.com).
- **License:** [MIT](LICENSE).

## Features

- **Mockup gallery.** A folder of PSDs organized in groups. Each PSD needs at least one Smart Object.
- **Visual workflow.** Design nodes (one or more), one node per mockup and one export node. Each Smart Object of a
  mockup is linked to a design (or left unchanged), with its own fit (contain, cover or stretch), rotation and
  color.
- **Mockup profile.** A `.mockup.json` file next to each PSD stores its characteristics and provides the
  defaults: aspect ratio, recommended logo color, transparent logo or full-bleed design, and group.
- **Photoshop-accurate compositing.** Reproduces perspective, warps, blend modes, masks, Levels, Curves, shadows
  and smart blur filters. Compared with the composite saved by Photoshop, the mean error is 0.3 to 0.5 out of 255
  on the mockups tested.
- **`.mwf` workflow files.** XML files you can save, share and reopen (by double-clicking them in the Mac app).
- **Interface.** Run history, .zip download, and light and dark mode.
- **Demo workflow.** When the app starts with no workflow open, it loads `Demo.mwf`: the Mockup Workflow logo and
  a white "MW" monogram on every mockup in the gallery.

## Requirements

- macOS (the app and the build script use system tools; the server runs on any system with Python).
- Python 3.9 or later. It comes with Xcode Command Line Tools: `xcode-select --install`.

## Installation

```bash
make setup
```

Creates `.venv` and installs the dependencies from `requirements*.txt`.

## Usage

| Mode | Command |
| --- | --- |
| Mac app | `make build` and open `dist/Mockup Workflow.app` (or copy it to Applications) |
| Browser | `make run` and open <http://127.0.0.1:5173>, or double-click `Open Mockup Workflow.command` |
| Native window without building | `make desktop` |
| Command line | `.venv/bin/python mockup.py mockup.psd design.png result.png [--fit contain\|cover\|stretch]` |

In the app:

1. **New:** pick mockups from the gallery and one or more designs. With several designs, the first Smart Object of
   each mockup gets design 1, the second gets design 2, and so on. The "Order" bar sets the order of the selected
   designs and mockups: drag them, or select one and use the arrow keys.
2. **Adjust each mockup:** for each Smart Object, set the linked design, fit, rotation and color.
   "Add design" creates another design node (PNG, SVG, JPG or WebP). Double-click a window title to rename it.
   ⌘Z undoes and ⇧⌘Z redoes (the canvas buttons do the same).
3. **Run workflow:** generates all the mockups. The ▶ button on a node generates only that one.
4. **Download the results:** from the Export node or the history (PNG or JPG, at 100, 50 or 25 %, or everything
   as a .zip).
5. **Save (⌘S):** creates a `.mwf` file. **Open (⌘O)** loads one; you can also drop it on the canvas.

### Work folder

The gallery, workflows and results are not stored with the code but in the **work folder**:

```
<work folder>/
├── Mockup Gallery/   PSDs; subfolders are groups. Copy your mockups here.
├── Flows/            .mwf files (and demo.svg)
└── data/             thumbnails, uploaded designs, run results and history
```

- **Mac app:** choose the folder in File > Change Work Folder…; it is stored in
  `~/Library/Application Support/Mockup Workflow/config.json`. On first launch the app creates
  `~/Documents/Mockup Workflow`.
- **From source:** the project folder, or the folder set in the `MW_HOME` environment variable.

You can move or rename PSDs inside the gallery without breaking the workflows that use them.

### Mockup profile

Next to each PSD there is a `<name>.mockup.json` with its characteristics. The app creates it when the PSD is
added (by analyzing it), and you can edit it with the settings button of each mockup in the gallery. Changing the
group moves the PSD and its profile to that folder. The format is described in
[docs/mockup-profile.md](docs/mockup-profile.md).

## Development

```bash
make help        # list of tasks
make test        # tests (add PSD=path.psd for the fidelity test with a real PSD)
make check PSD=path.psd   # compares a PSD's render with Photoshop's composite
```

| File | Purpose |
| --- | --- |
| `engine.py` | Compositing engine (psd-tools + NumPy + OpenCV) |
| `app.py` | Local server (Flask): API, gallery, `.mwf` workflows and run queue |
| `desktop.py` | Mac app: native window (pywebview), menus and dialogs |
| `static/` | Interface (HTML, CSS and JavaScript with no dependencies or build step) |
| `mockup.py` | Command line |
| `version.py` | Version, author and license: the single source used by the app, packaging and scripts |
| `MockupWorkflow.spec` | PyInstaller packaging |
| `scripts/` | Build (`build_app.sh`), release (`release.py`) and icon scripts |
| `tests/` | pytest tests |
| `docs/` | [Architecture](docs/architecture.md), [.mwf file format](docs/file-format.md) and [mockup profile](docs/mockup-profile.md) |

How to work on the project (branches, commits, versions): [CONTRIBUTING.md](CONTRIBUTING.md).

### Releasing a version

1. Note the changes in the `## [Unreleased]` section of the [CHANGELOG](CHANGELOG.md).
2. Run `make release VERSION=1.1.0`. This command:
   - Bumps the version in `version.py` and dates the CHANGELOG.
   - Runs the tests.
   - Builds the app and creates `releases/Mockup-Workflow-1.1.0-macOS.zip`.
   - Creates the commit and the `v1.1.0` tag.

### Signing

For personal use the app does not need to be signed: if macOS blocks it the first time, right-click > Open.
To distribute it to other people it must be signed and notarized with an Apple Developer account.

## Known limitations

- **Photoshop features that are not reproduced:**
  - Smart filters other than blurs (Gaussian, motion or box).
  - Some adjustments, such as Hue/Saturation or Gradient Map.
  - Preset warps such as Arc or Flag. "Cylinder" is reproduced, approximately.

  If a PSD uses them, the mockup is still generated and the history shows a warning.
- **Opening another `.mwf` while the app is running:** a double-click only brings the app to the front; use
  File > Open.
- **Typography:** loaded from Google Fonts. Without a connection the system font is used.

## License

[MIT](LICENSE) © 2026 Juanma PD.
