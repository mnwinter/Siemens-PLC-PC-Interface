# Native theme

## Compact token summary

- Product: RungProof PLC Visual Simulator
- Mode: dark industrial control console
- Fonts: Segoe UI Variable / Segoe UI; Cascadia Mono / Consolas for PLC data
- Corners: 2-6 px, restrained; no pill-heavy consumer styling
- Shadows/gradients: none
- Accent semantics: cyan action/focus, green good/TRUE, amber warning or
  disconnected, red fault only
- Spacing: dense 3/5/7/9/13/15/18 px rhythm
- Borders: one-pixel blue-slate separators
- Panel hierarchy: subtle solid shade changes, never bright color blocks

## Raw source tokens

Source: `tools/rungproof_native.py`.

```python
PROOF_GREEN = "#16A34A"
SAFE_GREEN = "#3DD6A5"
BACKGROUND_DEEP = "#071015"
BACKGROUND = "#0B171D"
PANEL = "#101F26"
PANEL_ALT = "#152830"
LINE = "#29414B"
LINE_BRIGHT = "#3A5C67"
TEXT = "#EAF2F4"
MUTED = "#88A0A9"
MUTED_BRIGHT = "#ADC0C6"
CYAN = "#5FC5EC"
AMBER = "#F2B94B"
BAD = "#EF6A61"
```

The full QSS implementation is returned by
`RungProofWindow._application_stylesheet` in
`tools/rungproof_native.py:1294`. That source range is the authoritative raw
theme dump and should be passed directly to a design call.

