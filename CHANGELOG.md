# Changelog

All notable changes to Mockup Workflow are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/):

- **MAJOR:** breaking changes, such as an older `.mwf` file that no longer opens.
- **MINOR:** new features.
- **PATCH:** fixes.

## [Unreleased]

### Changed

- **Install instructions:** since macOS 15, an app that is not notarized is allowed in System Settings >
  Privacy & Security > Open Anyway (right-click > Open no longer works). Updated in the README and the project page.

## [1.0.0] - 2026-11-19

First release.

### Added

- **Compositing engine without Photoshop:**
  - Smart Object replacement with perspective and warps: classic custom mesh, quilt (grid) warp and an
    approximation of the Cylinder preset.
  - Blend modes, layer and vector masks, clipping masks and fill layers.
  - Levels, Curves and Brightness/Contrast adjustments, including in pass-through groups.
  - Drop shadow, inner shadow, outer glow and inner glow.
  - Color overlay applied before compositing the layer, as in Photoshop.
  - Smart blur filters (Gaussian, motion and box) on Smart Objects. Other filters are reported in the history.
- **Multiple designs per workflow:** each Smart Object of a mockup is linked to any design, or left unchanged,
  with its own fit (contain, cover or stretch), rotation and color.
- **SVG designs:** rasterized to PNG up to 4000 px with a transparent background, keeping their name and path.
- **Mockup profiles** (`<PSD name>.mockup.json` next to each PSD): aspect ratio, recommended logo color,
  transparent logo or full-bleed design, default fit and rotation, warp, perspective, instances, clipped layers
  and the full layer list. Created by analyzing the PSD and editable from the gallery.
- **Gallery and groups:** a folder of PSDs where each subfolder is a group (Outdoor, Merchandise, Other, or any
  new group). New PSDs are detected, and PSDs can be moved or renamed without breaking workflows.
- **`.mwf` workflow files (XML):** embedded designs, file paths of designs and PSDs, per-Smart-Object links and
  node positions. Save, Save As, Open and drop on the canvas.
- **Workflow interface:**
  - Node canvas with zoom, "Arrange nodes" and window renaming (double-click a title).
  - New workflow dialog with an order bar: drag the selected designs and mockups (or use the arrow keys) to choose
    the order they are loaded in.
  - Undo and redo with canvas buttons and ⌘Z, ⇧⌘Z and ⌘Y.
  - Full run or single-mockup run, live history, full-size viewer and .zip download.
  - Clear history (results go to the Trash).
  - Recent designs sorted by last use, with a button to remove them from the list. When none are left, the demo
    designs are offered.
  - Prompt to save unsaved changes when choosing New.
  - Light and dark mode.
  - Splash screen.
- **Demo workflow** (`Flows/Demo.mwf`): the app logo and a white "MW" monogram (SVG) on every mockup in the
  gallery.
- **Mac app:**
  - Native window with native menus and macOS dialogs.
  - `.mwf` file association.
  - Configurable work folder.
  - Log file and diagnostic mode (`MW_DIAG=1`).
  - "About" dialog with version, author and license.
- **Command line:** `mockup.py`, with `--check` to compare with Photoshop.
- **Maintenance:** pytest tests, `Makefile`, release script and documentation.

[Unreleased]: #
[1.0.0]: #
