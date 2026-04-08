# -*- coding: utf-8 -*-
#apps/cashier_app/features/patients/views/patient_profile.py
from __future__ import annotations

from dataclasses import dataclass
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTabWidget, QPushButton
)
from apps.cashier_app.features.patients.models import PatientLite

from apps.cashier_app.features.test_requests.views.test_requests_tab import TestRequestsTab
from apps.cashier_app.features.patients.views.tabs.biodata_tab import BiodataTab
from apps.cashier_app.features.payments.views.payments_tab import PaymentsTab
from apps.cashier_app.features.results.views.results_tab import ResultsTab


class PatientProfileView(QWidget):
    back_requested = Signal()

    def __init__(self, patient: PatientLite):
        super().__init__()
        self.patient = patient

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)

        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        # Back arrow (professional navigation)
        btn_back = QPushButton("← Back")
        btn_back.clicked.connect(self.back_requested.emit)
        h.addWidget(btn_back)

        title = QLabel(f"Patient Profile — {patient.full_name}")
        title.setStyleSheet("font-size: 13pt; font-weight: 800;")
        h.addWidget(title)

        h.addStretch(1)

        meta = QLabel(f"{patient.patient_no}  |  {patient.phone}  |  {patient.sex}  |  {patient.age} yrs")
        meta.setObjectName("Muted")
        h.addWidget(meta)

        outer.addWidget(header)

        tabs_panel = QFrame()
        tabs_panel.setObjectName("Panel")
        tabs_layout = QVBoxLayout(tabs_panel)
        tabs_layout.setContentsMargins(14, 14, 14, 14)

        tabs = QTabWidget()
        tabs_layout.addWidget(tabs)


        tabs.addTab(BiodataTab(patient), "Biodata")
        tabs.addTab(TestRequestsTab(patient), "Test Requests")

        tabs.addTab(PaymentsTab(patient), "Payments")

        tabs.addTab(ResultsTab(patient), "Results")


        outer.addWidget(tabs_panel, 1)

    def _placeholder_tab(self, name: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 10, 10, 10)
        lab = QLabel(f"{name} — (Step 3 will design this tab professionally)")
        lab.setObjectName("Muted")
        lay.addWidget(lab)
        lay.addStretch(1)
        return w
