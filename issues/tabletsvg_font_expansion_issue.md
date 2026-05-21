# tabletsvg Font Expansion Issue

## Summary

Diagrams that rendered correctly under flatland 2.0.15 (PyQt backend) now exceed
their diagram width boundaries under the current flatland (tabletsvg backend). The root
cause is a change in how text width is measured, combined with a secondary difference in
how the "A2" sheet size was interpreted.

---

## Root Cause: Fixed Character-Width Approximation

The old flatland used **PyQt** for rendering. Qt measures text using actual font metrics
via `QFontMetrics.horizontalAdvance()` — the real rendered width of each character in the
chosen typeface. Qt uses its own independent rendering stack (QPainter, QFont, FreeType,
HarfBuzz), entirely separate from Cairo/Pango.

The new flatland uses the **tabletsvg** library, which replaced Qt font measurement with a
fixed approximation in:

```
tabletsvg/graphics/text_element.py, line 85:

    width = int(style.size * 0.6 * len(text_line))
```

This estimates every character as **0.6 × font_size** wide, regardless of the actual
character shape. For proportional fonts like Verdana (used throughout Flatland diagrams),
this tends to **overestimate** text width because narrow characters (`i`, `l`, `r`, space)
are counted the same as wide characters (`W`, `M`, `m`).

The overestimated text width flows directly into node size calculations:

1. `TextElement.line_size()` → overestimates line width
2. `TextElement.text_block_size()` → takes the max line width as block width
3. `Compartment.Text_block_size` → adds compartment padding to block width
4. Node size → drives how wide a grid column must be
5. Wider columns → rightmost column boundary exceeds `Diagram.Size.width` → `sys.exit(1)`

---

## Evidence: the cabin State Machine Diagram

The `cabin.mls` layout specifies `sheet A2`, `orientation landscape`, `padding l150 b150`.

### Old flatland (2.0.15) output — `flatland_2_0_15/cabin.pdf`

```
MediaBox: 1584 × 1224 pt  (22.0" × 17.0")
```

The diagram fits within this page with the 150pt left padding applied.

### New flatland output — `flatland_svg/cabin.svg` (left padding removed from mls to force a successful run)

```
SVG canvas: 1684 × 1191 pt  (ISO A2 landscape)
Diagram boundary rect: x=10, y=10, width=1664, height=1021
```

Grid column boundaries extracted from SVG vertical grid lines:

| Boundary | x (pt) | Column width (pt) |
|----------|--------|-------------------|
| 0 (left edge) | 10.0 | — |
| 1 | 239.0 | 229.0 |
| 2 | 349.0 | 110.0 |
| 3 | 525.0 | 176.0 |
| 4 | 874.3 | 349.3 |
| 5 | 1041.6 | 167.3 |
| 6 | 1400.6 | 359.0 |
| 7 | 1742.6 | 342.0 |
| **Total grid width** | | **1732.6 pt** |

The rightmost grid boundary (1742.6 pt) exceeds the page width (1684 pt) by **58.6 pt**,
and exceeds the diagram area right edge (1674 pt) by **68.6 pt** — even without the 150pt
left padding.

With the 150pt left padding restored, the test fails:

```
ERROR  flatland.node_subsystem.grid:grid.py:222
       Max diagram width exceeded by 130pt at col 8
```

---

## Secondary Factor: Sheet Size Interpretation Changed

The old flatland produced output at **1584 × 1224 pt** for an `A2` sheet in landscape.
This is **22" × 17"** — a US engineering "C-size" sheet, not ISO A2.

The current `sheet.yaml` correctly defines A2 as ISO A2:

```yaml
A2: {standard: int, height: 420, width: 594, size_group: medium}
```

ISO A2 landscape = 594mm × 420mm = **1684 × 1191 pt**.

The new page is actually **100 pt wider** than the old page. Despite this, the diagram
still overflows — confirming that the font approximation issue, not the page size, is the
primary driver.

---

## Potential Fixes

### Option 1 — Reduce the 0.6× coefficient in tabletsvg (upstream fix)
Lower the multiplier in `text_element.py` to better match actual Pango-rendered widths
for the fonts in use. The correct value would need to be empirically determined by
comparing measured vs. rendered widths for representative node label text.

### Option 2 — Reduce font sizes in the style sheets
Smaller font sizes produce narrower text estimates and smaller nodes. This is a
workaround that affects visual appearance.

### Option 3 — Increase sheet size in the `.mls` files
Wider sheets absorb the overestimate. For `cabin`, the diagram needs approximately
1733 pt of grid width (plus left padding of 150 pt), requiring a sheet wider than
~1900 pt. This is what the iterative fix attempts during test runs have been doing.

### Option 4 — Switch to actual font metric measurement in tabletsvg
Re-introduce real font metric measurement (e.g. via cairocffi + pangocffi, which are
already installed in the Flatland312 environment) so that node sizes match what the
renderer actually produces.

---

## Files Referenced

| File | Role |
|------|------|
| `working/compare_size/flatland_2_0_15/cabin.pdf` | Old flatland output (PyQt, 1584×1224 pt) |
| `working/compare_size/flatland_svg/cabin.pdf` | New flatland PDF (tabletsvg, no left padding) |
| `working/compare_size/flatland_svg/cabin.svg` | New flatland SVG (tabletsvg, no left padding) |
| `tests/model_style_sheets/xUML_smd/cabin.mls` | Layout spec: A2 landscape, l150 b150 padding |
| `~/.config/flatland/sheet.yaml` | Sheet size definitions |
| `tabletsvg/graphics/text_element.py` | Fixed 0.6× width approximation (line 85) |
| `src/flatland/node_subsystem/grid.py` | Width overflow check (lines 222–223, 411–412) |
