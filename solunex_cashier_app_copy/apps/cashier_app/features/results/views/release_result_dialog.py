# -*- coding: utf-8 -*-
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from shared.uix.widgets.dialogs import SolunexDialog
from apps.cashier_app.features.patients.models import PatientLite


class ReleaseResultDialog(SolunexDialog):
    def __init__(self, patient: PatientLite, result_title: str, parent=None):
        super().__init__("Release Result", parent=parent, width=760, height=520)

        head = QLabel(f"{patient.patient_no} — {patient.full_name} ({patient.phone})")
        head.setObjectName("Muted")
        self.body_layout.addWidget(head)

        panel = QFrame()
        panel.setObjectName("Panel2")
        self.body_layout.addWidget(panel, 1)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        title = QLabel(result_title)
        title.setStyleSheet("font-size: 12pt; font-weight: 900;")
        lay.addWidget(title)

        warn = QLabel(
            "Confirm Release:\n"
            "• This will sync the result to Patient Portal for download.\n"
            "• Release should only happen when lab status is APPROVED and payment is PAID.\n"
            "• Full enforcement will be backed by server rules."
        )
        warn.setStyleSheet("font-weight: 800;")
        lay.addWidget(warn)

        lay.addStretch(1)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        btn_confirm = QPushButton("Confirm Release")
        btn_confirm.setObjectName("Primary")
        btn_confirm.clicked.connect(self.accept)
        actions.addWidget(btn_confirm)

        self.body_layout.addLayout(actions)
