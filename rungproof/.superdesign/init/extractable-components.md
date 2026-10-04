# Extractable component candidates

RungProof has no HTML or React layout components suitable for conversion to
Superdesign DraftComponents. It is a native PySide6 QWidget application.

Conceptual reusable native primitives:

## ProductHeader
- Source: `tools/rungproof_native.py` in `_build_ui`
- Category: layout
- Description: RP mark, product title, menus, view badge, and PLC state badge
- Extractable props: none for HTML; state is owned by Qt actions/session
- Hardcoded: brand mark, menu labels, status semantics

## PanelBlock
- Source: `tools/rungproof_native.py` in `_new_panel`
- Category: basic
- Description: titled industrial panel with optional micro badge
- Extractable props: title, badge, static area role
- Hardcoded: spacing, border, typography

## MetricCard
- Source: `tools/rungproof_native.py` in `_new_metric`
- Category: basic
- Description: compact label/value telemetry card
- Extractable props: title, value
- Hardcoded: monospace value styling

Component extraction is skipped because these are native Qt objects, not
Petite-Vue/HTML templates.

