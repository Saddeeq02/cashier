# -*- coding: utf-8 -*-
# shared/uix/layout/topbar.py

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from apps.cashier_app.app_state import state


class Topbar(QWidget):
    refresh_clicked = Signal()

    def __init__(self, app_name: str, role: str):
        super().__init__()

        panel = QFrame()
        panel.setObjectName("HeaderBar")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(panel)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.setSpacing(16)

        # ------------------------------------------------------
        # LEFT: Application Identity
        # ------------------------------------------------------
        brand_block = QWidget()
        brand_layout = QHBoxLayout(brand_block)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(10)

        title = QLabel(f"{app_name} — Cashier Portal")
        title.setObjectName("SectionTitle")
        brand_layout.addWidget(title)

        layout.addWidget(brand_block)

        layout.addStretch(1)

        # ------------------------------------------------------
        # RIGHT: Status + Identity
        # ------------------------------------------------------

        # Online dot
        self.dot = QLabel()
        self.dot.setFixedSize(10, 10)
        self.dot.setStyleSheet("background:#059669;border-radius:5px;")
        layout.addWidget(self.dot)

        self.status = QLabel("Online")
        self.status.setObjectName("Muted")
        layout.addWidget(self.status)

        # Role badge
        self.role = QLabel(role.upper())
        self.role.setStyleSheet("""
            padding: 6px 14px;
            border-radius: 14px;
            background: #F1F5F9;
            border: 1px solid #E2E8F0;
            font-weight: 600;
        """)
        layout.addWidget(self.role)

        # Username
        self.user = QLabel(state.username or "—")
        self.user.setStyleSheet("font-weight:600;")
        layout.addWidget(self.user)

        # Refresh button
        btn = QPushButton("Refresh")
        btn.setObjectName("Primary")
        btn.clicked.connect(self.refresh_clicked.emit)
        layout.addWidget(btn)