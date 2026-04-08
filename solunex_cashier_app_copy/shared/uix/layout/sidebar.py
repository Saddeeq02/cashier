# -*- coding: utf-8 -*-
# shared/uix/layout/sidebar.py

from __future__ import annotations

from typing import List, Tuple
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from apps.cashier_app.app_state import state


class Sidebar(QWidget):
    nav_clicked = Signal(str)

    def __init__(self, items: List[Tuple[str, str]]):
        super().__init__()

        self.setObjectName("Sidebar")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        panel = QFrame()
        panel.setObjectName("Panel")
        root.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ------------------------------------------------------
        # BRAND AREA
        # ------------------------------------------------------
        brand = QLabel("I and E")
        brand.setObjectName("Brand")
        layout.addWidget(brand)

        subtitle = QLabel("Lab Cashier System")
        subtitle.setObjectName("Muted")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Divider feel
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background:#E2E8F0;")
        layout.addWidget(divider)

        layout.addSpacing(6)

        # ------------------------------------------------------
        # NAVIGATION
        # ------------------------------------------------------
        self.buttons = {}

        for label, key in items:
            btn = QPushButton(label)
            btn.setObjectName("NavItem")
            btn.setProperty("active", False)
            btn.clicked.connect(lambda _, k=key: self.nav_clicked.emit(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        layout.addStretch(1)

        # ------------------------------------------------------
        # FOOTER INFO
        # ------------------------------------------------------
        footer = QLabel(f"User: {state.username or '—'}")
        footer.setObjectName("Muted")
        layout.addWidget(footer)

    def set_active(self, key: str) -> None:
        for k, btn in self.buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()