# -*- coding: utf-8 -*-
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton


class SolunexDialog(QDialog):
    """
    Professional standard dialog:
    - Top header (title + close)
    - Body container frame for content
    """
    def __init__(self, title: str, parent=None, width: int = 720, height: int = 520):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 10, 14, 10)

        lab = QLabel(title)
        lab.setStyleSheet("font-weight: 800; font-size: 12pt;")
        h.addWidget(lab)

        h.addStretch(1)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        h.addWidget(btn_close)

        root.addWidget(header)

        self.body = QFrame()
        self.body.setObjectName("Panel")
        root.addWidget(self.body, 1)

        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(14, 14, 14, 14)
        self.body_layout.setSpacing(10)
