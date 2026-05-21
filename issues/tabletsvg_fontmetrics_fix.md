# tabletsvg Font Metrics Fix

## Summary

Replaced the fixed 0.6× character-width approximation in `tabletsvg` with accurate
Pillow-based font metrics. Text widths are now measured using the actual TTF/TTC font
files, matching what the SVG renderer produces. A graceful fallback to the 0.6×
approximation is retained for any typeface not configured in `font_paths.yaml`.

---

## Problem

`TextElement.line_size()` in `tabletsvg/graphics/text_element.py` estimated text width as:

```python
width = int(style.size * 0.6 * len(text_line))
```

This treats every character as 0.6× the font size wide, regardless of the actual
character shape. For proportional fonts like Gill Sans and Verdana:

- **All-caps text** (e.g. "EMERGENCY BRAKING") is significantly **wider** than the
  approximation — capital letters average wider than 0.6×
- **Mixed-case text** (e.g. "Are we already there?") is significantly **narrower** —
  lowercase letters average narrower than 0.6×

Measured examples using Gill Sans at the sizes used in Flatland state machine diagrams:

| Text | Font | Actual (pt) | 0.6× Approx (pt) | Difference |
|------|------|-------------|------------------|------------|
| EMERGENCY BRAKING | GillSans Bold 12 | 152 | 122 | +30pt |
| SECURING DOORS | GillSans Bold 12 | 119 | 100 | +19pt |
| Are we already there? | GillSans Normal 9 | 83 | 113 | −30pt |
| Notify transfer | GillSans Normal 9 | 55 | 80 | −25pt |
| Request destination | GillSans Normal 9 | 73 | 102 | −29pt |

These inaccuracies cause node sizes — and therefore grid column widths — to diverge
from what the renderer actually produces, leading to either wasted space or overflow
errors.

---

## Changes

### New file: `src/tabletsvg/configuration/font_paths.yaml`

Maps each typeface alias (from `typefaces.yaml`) to its font file path(s) on disk,
one entry per style variant. TrueType Collection (`.ttc`) files include an `index:`
field to select the correct variant within the collection.

```yaml
Gill_Sans:
  normal:      {path: /System/Library/Fonts/Supplemental/GillSans.ttc, index: 0}
  bold:        {path: /System/Library/Fonts/Supplemental/GillSans.ttc, index: 1}
  italic:      {path: /System/Library/Fonts/Supplemental/GillSans.ttc, index: 2}
  bold_italic: {path: /System/Library/Fonts/Supplemental/GillSans.ttc, index: 3}

Verdana:
  normal:      {path: /System/Library/Fonts/Supplemental/Verdana.ttf}
  bold:        {path: "/System/Library/Fonts/Supplemental/Verdana Bold.ttf"}
  italic:      {path: "/System/Library/Fonts/Supplemental/Verdana Italic.ttf"}
  bold_italic: {path: "/System/Library/Fonts/Supplemental/Verdana Bold Italic.ttf"}

Courier:
  normal:      {path: "/System/Library/Fonts/Supplemental/Courier New.ttf"}
  bold:        {path: "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"}
  italic:      {path: "/System/Library/Fonts/Supplemental/Courier New Italic.ttf"}
  bold_italic: {path: "/System/Library/Fonts/Supplemental/Courier New Bold Italic.ttf"}
```

Any typeface without an entry (e.g. `Helvetica`) silently falls back to the 0.6×
approximation.

### Modified: `src/tabletsvg/graphics/text_element.py`

**New import:**
```python
import yaml
```

**New class attributes on `TextElement`:**
```python
_font_paths: dict = {}         # loaded from font_paths.yaml
_font_paths_loaded: bool = False
_font_cache: dict = {}         # (font_path, ttc_index, size) -> PIL ImageFont or None
```

**New private classmethods:**

`_load_font_paths()` — Loads `font_paths.yaml` lazily on first use. Logs a warning
and continues with the 0.6× fallback if the file is missing.

`_get_pil_font(typeface_alias, weight, slant, size)` — Resolves the correct font
variant, loads the PIL `ImageFont` via Pillow's `truetype()`, caches it by
`(path, ttc_index, size)`, and returns it. Returns `None` on any failure so the
caller can fall back gracefully.

**Updated `line_size()`:**
```python
pil_font = cls._get_pil_font(
    typeface_alias=style.typeface,
    weight=style.weight,
    slant=style.slant,
    size=style.size,
)

if pil_font is not None:
    width = int(pil_font.getlength(text_line))
else:
    # Fallback: fixed approximation (0.6x font size per character)
    width = int(style.size * 0.6 * len(text_line))
```

---

## Dependencies

- **Pillow** — already a transitive dependency of `tabletsvg` via `CairoSVG`; no new
  package required.
- **PyYAML** — already present in the environment; used for loading `font_paths.yaml`.

---

## Fallback Behavior

The fix degrades gracefully at every failure point:

| Condition | Behavior |
|-----------|----------|
| `font_paths.yaml` missing | Warning logged; all typefaces use 0.6× approximation |
| Typeface not in `font_paths.yaml` | That typeface uses 0.6× approximation |
| Font file path not found on disk | Warning logged; that typeface uses 0.6× approximation |
| PIL fails to load the font | Warning logged; that typeface uses 0.6× approximation |

---

## Effect on Layout

Switching to accurate font metrics does not eliminate all diagram overflow errors.
Diagrams that were tuned for the 0.6× approximation may need `.mls` sheet size
adjustments because the accurate measurements differ — sometimes larger, sometimes
smaller — from what was assumed. In particular:

- All-caps bold node labels (common in state machine diagrams) measure **wider** with
  actual font metrics, potentially increasing column widths.
- Mixed-case labels measure **narrower**, potentially reducing column widths.

The net effect on any given diagram depends on the specific text content and layout.
Accurate measurement is the correct foundation; `.mls` sheet sizes should be adjusted
to match actual content rather than an approximation.

---

## Files Changed

| File | Change |
|------|--------|
| `src/tabletsvg/configuration/font_paths.yaml` | New — typeface alias → font file path mapping |
| `src/tabletsvg/graphics/text_element.py` | Modified — Pillow-based `line_size()` with fallback |
