# Mockup profile (`.mockup.json`)

Each PSD in the gallery has a `<PSD name>.mockup.json` file next to it with its characteristics. For example,
`Mockup Gallery/Outdoor/Square Sign Mockup.psd` has `Square Sign Mockup.mockup.json` next to it.

- **When it is created:** when the PSD is added, or when scanning for new mockups if it is missing.
- **What it contains:** what is detected by analyzing the PSD.
- **How to edit it:** from the gallery (the mockup's settings button) or by hand.
- **If the PSD changes:** the app analyzes it again but keeps what you edited.
- **Profiles from Mockup Studio:** profiles with Spanish keys (`formato`, `nombre`, `objetos`…) are converted to
  this schema automatically, keeping the values you edited.

```json
{
 "format": 1,
 "app": "Mockup Workflow 1.0.0",
 "name": "Square sign",
 "file": "Square Sign Mockup.psd",
 "group": "Outdoor",
 "size": [4000, 3000],
 "objects": [
  {
   "id": "98f4c8de-…",
   "name": "Place Your Design Here (Double Click to Edit)",
   "canvas": [1969, 1969],
   "ratio": "1:1",
   "aspect": 1.0,
   "logo": "light",
   "background": "transparent",
   "fit": "contain",
   "rotate": 0,
   "visible": true,
   "warp": "none",
   "perspective": "perspective",
   "instances": [
    {
     "name": "Place Your Design Here (Double Click to Edit)",
     "visible": true,
     "opacity": 100,
     "fill": 100,
     "blend": "normal",
     "mask": false,
     "effects": [],
     "filters": [],
     "clippedLayers": [{ "name": "Shadow", "blend": "multiply", "visible": true }]
    }
   ],
   "analysis": { "surface": 0.09, "sample": 1.0, "coverage": 0.083 }
  }
 ],
 "layers": [
  {
   "name": "Place Your Design Here (Double Click to Edit)",
   "type": "smartobject",
   "depth": 0,
   "group": "",
   "visible": true,
   "blend": "normal",
   "opacity": 100,
   "fill": 100,
   "clipping": false,
   "mask": false,
   "effects": [],
   "filters": [],
   "warnings": []
  }
 ],
 "created": "2026-11-19T15:52:43",
 "updated": "2026-11-19T15:52:43"
}
```

## Fields

| Field | Content |
| --- | --- |
| `format` | Profile format version. |
| `app` | App and version that wrote the profile. |
| `name`, `file` | Mockup name and PSD file name. |
| `group` | `Outdoor`, `Merchandise`, `Other` or any group created by the user. It is the gallery folder: changing it in the app (or creating a new one) moves the PSD and its profile. |
| `size` | Document size `[width, height]` in pixels. |
| `objects[]` | One element per Smart Object (`id` = the PSD's `unique_id`). |
| `layers[]` | All the PSD's layers, top to bottom: `name`, `type`, `depth`, `group`, `visible`, `blend`, `opacity`, `fill`, `clipping`, `mask`, `effects`, `filters` and `warnings` (what the engine does not reproduce). |
| `created`, `updated` | Timestamps. |

Fields of each `objects` element:

| Field | Content |
| --- | --- |
| `name` | Smart Object layer name. |
| `canvas`, `ratio`, `aspect` | Inner canvas size and its aspect ratio (simplified and decimal). |
| `logo` | `light` (the design is tinted white), `dark` (tinted near-black) or `original` (not tinted). |
| `background` | `transparent`: the layer expects a logo. `full-bleed`: it expects artwork that fills the area, such as a poster. |
| `fit` | Default fit: `contain`, `cover` or `stretch`. |
| `rotate` | Default rotation: 0, 90, 180 or 270. |
| `visible` | Whether the Smart Object is visible. |
| `warp` | `none`, `custom mesh`, `quilt`, `cylinder`, `arc`… |
| `perspective` | `rectangular` or `perspective`. |
| `instances` | Each layer that uses the object: `name`, `visible`, `opacity`, `fill`, `blend`, `mask`, `effects`, `filters` (for example "Gaussian Blur 3 px") and `clippedLayers` (shadows and reflections clipped above it: `name`, `blend`, `visible`). |
| `analysis` | Measured data (informational only). |

`analysis` data:

| Value | What it measures |
| --- | --- |
| `surface` | Median luminance of the object's visible area with an empty design (0 black, 1 white). |
| `sample` | Luminance of the PSD's sample content. |
| `coverage` | Fraction of the canvas covered by the sample content. |

## Detection rules

- **`background`:** `full-bleed` if the sample content covers more than 90 % of the canvas.
- **`logo`:** if the object expects full-bleed artwork, `original`. Otherwise the color of the PSD's sample is
  used, because its author already chose one that works on that surface: light sample → `light`, dark sample →
  `dark`. If the PSD has no sample, the surface decides: dark → `light`, light → `dark`.
- **`fit`:** `cover` for full-bleed artwork and `contain` for logos.

## How it is used

When a mockup is added to a workflow, each Smart Object takes its fit, rotation and color from the profile. There
is one exception: if the object expects full-bleed artwork but the linked design is a transparent logo, the
design is fitted whole and tinted to contrast with the surface. Everything can be changed later in the node.
