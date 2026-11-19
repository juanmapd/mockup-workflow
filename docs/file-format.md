# `.mwf` file format (Mockup Workflow file)

A `.mwf` file is a UTF-8 XML document that describes a workflow:
- the title;
- the reference designs, embedded and with their paths;
- the mockups, with their paths and the links of each Smart Object;
- the positions on the canvas;
- the export format.

Current format version: **1**.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mockupWorkflow version="1" app="Mockup Workflow 1.0.0">
  <title>Campaign</title>
  <output format="png" scale="1" />
  <designs>
    <design node="d1" x="48" y="56" name="logo.png" width="2400" height="2000"
            path="/…/data/designs/1a2b3c.png" source="/Users/…/Desktop/logo.png"
            encoding="base64" type="image/png">iVBORw0KGgo…</design>
    <design node="d2" x="48" y="640" name="monogram.png" … >…</design>
  </designs>
  <export x="1310" y="56" />
  <mockups>
    <mockup node="n1" id="square-sign-mockup-9f1e2d" name="Square sign" file="Square Sign Mockup.psd"
            path="/…/Mockup Gallery/Outdoor/Square Sign Mockup.psd" category="Outdoor" x="470" y="56">
      <link smartObject="98f4c8de-…" name="Place Your Design Here…" design="d1" fit="contain" tint="#ffffff" rotate="0" />
      <link smartObject="eab6fdec-…" name="Place Your Design Here…" design="d2" fit="contain" tint="#ffffff" rotate="0" />
    </mockup>
  </mockups>
</mockupWorkflow>
```

## Elements

| Element | Attributes | Notes |
| --- | --- | --- |
| `mockupWorkflow` | `version`, `app` | Root. `version` is the format version, not the app version. |
| `title` | — | Workflow name. |
| `output` | `format` (`png` or `jpg`), `scale` (`1`, `0.5` or `0.25`) | Export settings. |
| `designs/design` | see the table below | One design node per element. |
| `export` | `x`, `y` | Position of the Export node. |
| `mockups/mockup` | see the table below | One node per mockup. |
| `mockup/link` | see the table below | One link per Smart Object. |

`design` attributes:

| Attribute | Content |
| --- | --- |
| `node` | Node identifier (`d1`, `d2`…). |
| `label` | Name the user gave to the window (optional). |
| `x`, `y` | Node position. |
| `name`, `width`, `height` | Image name and size. |
| `path` | Path of the copy stored by the app. |
| `source` | Path of the original file, when known (in the Mac app, the file chosen in the macOS dialog). |
| `encoding`, `type` | `base64` and `image/png`: the PNG is the element's text. |

`mockup` attributes:

| Attribute | Content |
| --- | --- |
| `node` | Node identifier. |
| `label` | Name the user gave to the window (optional). |
| `id` | Mockup identifier in the gallery. |
| `name`, `file`, `category` | Name, file and group of the PSD. |
| `path` | Absolute path of the PSD. |
| `x`, `y` | Node position. |

`link` attributes:

| Attribute | Content |
| --- | --- |
| `smartObject` | `unique_id` of the Smart Object. |
| `name` | Name of the object (informational). |
| `design` | Linked design node, or empty to keep the PSD's original content. |
| `fit` | `contain`, `cover` or `stretch`. |
| `tint` | `#rrggbb` color, or empty for the original colors. |
| `rotate` | `0`, `90`, `180` or `270`. |

## How files are resolved on open

**Designs:** the embedded PNG is used. If there is none, the file at `source` or `path` is read. A design
identical to an existing one is not duplicated.

**Mockups:** looked up in this order:
1. By `id`.
2. By `path`. If the PSD exists at that path but is not in the gallery, it is registered where it is.
3. By file name (`file`).
4. By name (`name`).

Mockups that are not found are dropped and the app shows a warning. Links to Smart Objects that no longer exist
in the PSD are ignored.

## Compatibility

- New attributes: can be added without changing `version`. Readers ignore what they do not know and use default
  values for what is missing.
- Structural changes: the format version in `version.py` is bumped and reading of earlier versions is kept.
  Newer files do not open in older versions of the app.
