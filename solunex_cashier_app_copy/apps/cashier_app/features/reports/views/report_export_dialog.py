# -*- coding: utf-8 -*-
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox

from shared.uix.widgets.dialogs import SolunexDialog


class ReportExportDialog(SolunexDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent=parent, width=720, height=420)

        panel = QFrame()
        panel.setObjectName("Panel2")
        self.body_layout.addWidget(panel, 1)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        info = QLabel(
            "Export is UI-only for now.\n"
            "Step 4 will connect this to backend report generation and file download."
        )
        info.setObjectName("Muted")
        lay.addWidget(info)

        self.format = QComboBox()
        self.format.addItems(["PDF", "Excel (XLSX)"])
        lay.addWidget(self._field("Format", self.format))

        lay.addStretch(1)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        btn_export = QPushButton("Export (UI Only)")
        btn_export.setObjectName("Primary")
        btn_export.clicked.connect(self.accept)
        actions.addWidget(btn_export)

        self.body_layout.addLayout(actions)

    def _field(self, label: str, widget):
        w = QFrame()
        w.setStyleSheet("background: transparent; border: none;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        lab = QLabel(label)
        lab.setObjectName("Muted")
        v.addWidget(lab)
        v.addWidget(widget)
        return w
