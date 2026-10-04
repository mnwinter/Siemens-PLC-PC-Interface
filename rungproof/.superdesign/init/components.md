# Shared UI primitives

RungProof is a native PySide6 desktop application. It does not use React,
Vue, Tailwind, or an HTML component library. The shipped window is assembled
from Qt Widgets in `tools/rungproof_native.py`.

## Button factory

Source: `tools/rungproof_native.py`

```python
def _button(
    QtWidgets: Any,
    text: str,
    *,
    object_name: str,
) -> Any:
    button = QtWidgets.QPushButton(text)
    button.setObjectName(object_name)
    button.setMinimumHeight(38)
    return button
```

## Panel primitive

Source: `RungProofWindow._new_panel` in `tools/rungproof_native.py`.

```python
def _new_panel(
    self,
    title: str,
    *,
    badge: str | None = None,
) -> tuple[Any, Any]:
    panel = QtWidgets.QFrame()
    panel.setObjectName("panelBlock")
    layout = QtWidgets.QVBoxLayout(panel)
    layout.setContentsMargins(15, 13, 15, 14)
    layout.setSpacing(9)
    heading = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(title)
    label.setObjectName("sectionLabel")
    heading.addWidget(label)
    heading.addStretch(1)
    if badge:
        badge_label = QtWidgets.QLabel(badge)
        badge_label.setObjectName("microBadge")
        heading.addWidget(badge_label)
    layout.addLayout(heading)
    return panel, layout
```

## Metric-card primitive

Source: `RungProofWindow._new_metric` in `tools/rungproof_native.py`.

```python
def _new_metric(
    self,
    title: str,
    initial: str = "--",
) -> tuple[Any, Any]:
    card = QtWidgets.QFrame()
    card.setObjectName("metricCard")
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(8, 7, 8, 7)
    layout.setSpacing(3)
    small = QtWidgets.QLabel(title)
    small.setObjectName("metricLabel")
    value = QtWidgets.QLabel(initial)
    value.setObjectName("metricValue")
    layout.addWidget(small)
    layout.addWidget(value)
    return card, value
```

## Rail primitive

Source: `RungProofWindow._new_rail` in `tools/rungproof_native.py`.

```python
def _new_rail(self) -> tuple[Any, Any]:
    scroll = QtWidgets.QScrollArea()
    scroll.setObjectName("rail")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(
        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    content = QtWidgets.QWidget()
    content.setObjectName("railContent")
    layout = QtWidgets.QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    scroll.setWidget(content)
    return scroll, layout
```

