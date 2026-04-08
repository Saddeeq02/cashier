# -*- coding: utf-8 -*-
# apps/cashier_app/features/patients/views/patient_create_dialog.py
from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QTextEdit, QPushButton, QFrame, QMessageBox
)

from shared.uix.widgets.dialogs import SolunexDialog
from apps.cashier_app.features.patients.api import create_patient, search_patients


def _derive_dob_from_age(age_years: int) -> str:
    """
    Backend wants date_of_birth. We only have age for now.
    Safe default: January 1st of (current_year - age).
    Returns ISO yyyy-mm-dd string.
    """
    today = date.today()
    y = today.year - int(age_years)
    dob = date(y, 1, 1)
    return dob.isoformat()


def _format_patient_no(n: int) -> str:
    # LPT-0001 format
    return f"LPT-{n:04d}"


class PatientCreateDialog(SolunexDialog):
    def __init__(self, parent=None):
        super().__init__("New Patient Registration", parent=parent, width=760, height=560)

        # Body content
        form = QFrame()
        form.setObjectName("Panel2")
        self.body_layout.addWidget(form)

        f = QVBoxLayout(form)
        f.setContentsMargins(14, 14, 14, 14)
        f.setSpacing(12)

        subtitle = QLabel("Enter basic biodata.")
        subtitle.setObjectName("Muted")
        f.addWidget(subtitle)

        # Row 1: Full name + Phone
        r1 = QHBoxLayout()
        r1.setSpacing(10)
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full name")
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone number")
        r1.addWidget(self._field("Full Name", self.full_name), 2)
        r1.addWidget(self._field("Phone", self.phone), 1)
        f.addLayout(r1)

        # Row 2: Sex + Age + Patient No (AUTO)
        r2 = QHBoxLayout()
        r2.setSpacing(10)

        self.sex = QComboBox()
        self.sex.addItems(["Select...", "Male", "Female"])

        self.age = QSpinBox()
        self.age.setRange(1, 120)          # ✅ force age
        self.age.setValue(1)

        self.patient_no = QLineEdit()
        self.patient_no.setReadOnly(True)  # ✅ force auto patient number
        self.patient_no.setPlaceholderText("Generating...")

        r2.addWidget(self._field("Sex", self.sex), 1)
        r2.addWidget(self._field("Age", self.age), 1)
        r2.addWidget(self._field("Patient No", self.patient_no), 1)
        f.addLayout(r2)

        # Address / Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Address / notes (optional)")
        f.addWidget(self._field("Notes", self.notes))

        # Footer actions
        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("Primary")
        self.btn_save.clicked.connect(self._save)
        actions.addWidget(self.btn_save)

        self.body_layout.addLayout(actions)




    def _save(self) -> None:
        full_name = self.full_name.text().strip()
        phone = self.phone.text().strip()
        sex = self.sex.currentText().strip()
        age_years = int(self.age.value() or 0)

        if not full_name or not phone:
            QMessageBox.warning(self, "Missing info", "Full name and phone are required.")
            return

        if sex not in ("Male", "Female"):
            QMessageBox.warning(self, "Missing info", "Please select sex (Male/Female).")
            return

        dob = _derive_dob_from_age(age_years)

        payload = {
            "full_name": full_name,
            "phone": phone,
            "gender": sex,
            "date_of_birth": dob,
            "address": (self.notes.toPlainText().strip() or None),
        }

        print("CREATE PATIENT PAYLOAD:", payload)

        try:
            create_patient(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def _field(self, label: str, widget: QWidget) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lab = QLabel(label)
        lab.setObjectName("Muted")
        lay.addWidget(lab)
        lay.addWidget(widget)
        return w