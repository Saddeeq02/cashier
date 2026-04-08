# -*- coding: utf-8 -*-
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QTextEdit, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

# Assuming you have an API function for updating patients
from apps.cashier_app.features.patients.api import update_patient 
from apps.cashier_app.features.patients.views.patient_profile import PatientLite


class BiodataTab(QWidget):
    def __init__(self, patient: PatientLite):
        super().__init__()
        self.patient = patient

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        # --- Summary Card (Top) ---
        self.summary_card = QFrame()
        self.summary_card.setObjectName("Panel2")
        self.summary_card.setProperty("card", "true") # Use your enterprise CSS
        s = QHBoxLayout(self.summary_card)
        s.setContentsMargins(14, 14, 14, 14)

        left = QVBoxLayout()
        self.lbl_full_name = QLabel(patient.full_name)
        self.lbl_full_name.setStyleSheet("font-size: 14pt; font-weight: 800; color: #0F172A;")
        left.addWidget(self.lbl_full_name)

        self.lbl_meta = QLabel(f"{patient.patient_no} • {patient.phone} • {patient.sex} • {patient.age} yrs")
        self.lbl_meta.setObjectName("Muted")
        left.addWidget(self.lbl_meta)

        s.addLayout(left)
        s.addStretch(1)

        badge = QLabel("ACTIVE PATIENT")
        badge.setStyleSheet(
            "padding: 6px 12px; background: #F0F9FF; color: #1E40AF; "
            "border: 1px solid #BEE3F8; border-radius: 6px; font-weight: 800; font-size: 10px;"
        )
        s.addWidget(badge, 0, Qt.AlignVCenter)
        root.addWidget(self.summary_card)

        # --- Form Card (Main) ---
        form = QFrame()
        form.setObjectName("Panel")
        form.setProperty("card", "true")
        f = QVBoxLayout(form)
        f.setContentsMargins(20, 20, 20, 20)
        f.setSpacing(15)

        title = QLabel("Edit Patient Information")
        title.setStyleSheet("font-size: 12pt; font-weight: 700; color: #1E293B;")
        f.addWidget(title)

        # Row 1: Name & Phone
        r1 = QHBoxLayout()
        r1.setSpacing(15)
        self.full_name = QLineEdit(patient.full_name)
        self.phone = QLineEdit(patient.phone)
        r1.addWidget(self._field("Full Name", self.full_name), 2)
        r1.addWidget(self._field("Phone Number", self.phone), 1)
        f.addLayout(r1)

        # Row 2: Sex, Age, No
        r2 = QHBoxLayout()
        r2.setSpacing(15)
        self.sex = QComboBox()
        self.sex.addItems(["Male", "Female", "Other"])
        self.sex.setCurrentText(patient.sex)

        self.age = QSpinBox()
        self.age.setRange(0, 150)
        self.age.setValue(int(patient.age or 0))

        self.patient_no = QLineEdit(patient.patient_no)
        self.patient_no.setReadOnly(True)
        self.patient_no.setStyleSheet("background-color: #F1F5F9; color: #64748B;")

        r2.addWidget(self._field("Gender", self.sex), 1)
        r2.addWidget(self._field("Current Age", self.age), 1)
        r2.addWidget(self._field("Record Number (Static)", self.patient_no), 1)
        f.addLayout(r2)

        # Row 3: Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Enter address or clinical notes...")
        self.notes.setMaximumHeight(100)
        f.addWidget(self._field("Address / Internal Notes", self.notes))

        # Actions
        actions = QHBoxLayout()
        actions.addStretch(1)

        self.btn_save = QPushButton("Save Changes")
        self.btn_save.setObjectName("Primary")
        self.btn_save.setProperty("variant", "primary") # Enterprise CSS
        self.btn_save.setMinimumWidth(150)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setEnabled(False) 
        self.btn_save.clicked.connect(self._on_save_clicked)
        actions.addWidget(self.btn_save)

        f.addLayout(actions)
        root.addWidget(form, 1)

        # --- Change Tracking Listeners ---
        # When any widget changes, we check if we should enable the save button
        self.full_name.textChanged.connect(self._check_dirty)
        self.phone.textChanged.connect(self._check_dirty)
        self.sex.currentTextChanged.connect(self._check_dirty)
        self.age.valueChanged.connect(self._check_dirty)
        self.notes.textChanged.connect(self._check_dirty)

    def _field(self, label: str, widget: QWidget) -> QWidget:
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        lab = QLabel(label.upper())
        lab.setStyleSheet("font-size: 9px; font-weight: 700; color: #64748B;")
        lay.addWidget(lab)
        lay.addWidget(widget)
        return container

    def _check_dirty(self):
        """Enables the save button only if data differs from the original patient object."""
        name_changed = self.full_name.text().strip() != self.patient.full_name
        phone_changed = self.phone.text().strip() != self.patient.phone
        sex_changed = self.sex.currentText() != self.patient.sex
        
        # Ensure we compare int to int
        age_changed = int(self.age.value()) != int(self.patient.age)

        has_changed = name_changed or phone_changed or sex_changed or age_changed
        self.btn_save.setEnabled(has_changed)

    def _update_summary_ui(self):
        """Forcefully pushes the local patient object data to the top labels."""
        self.lbl_full_name.setText(self.patient.full_name)
        
        # Build string using the object to confirm the object itself was updated
        meta = f"{self.patient.patient_no} • {self.patient.phone} • {self.patient.sex} • {self.patient.age} yrs"
        self.lbl_meta.setText(meta)
        
        # Force a repaint of the summary card to ensure pixels refresh
        self.summary_card.update()

    def _on_save_clicked(self):
        from dataclasses import replace
        
        # 1. Prepare Payload
        try:
            current_ui_age = int(self.age.value())
            payload = {
                "full_name": self.full_name.text().strip(),
                "phone": self.phone.text().strip(),
                "gender": self.sex.currentText(), 
                "age": current_ui_age,
                "notes": self.notes.toPlainText().strip()
            }
        except ValueError: return

        try:
            self.btn_save.setEnabled(False)
            self.btn_save.setText("Saving...")

            # 2. Backend Call
            success = update_patient(self.patient.id, payload)
            
            if success:
                # 3. Object Update
                # We replace the frozen dataclass instance entirely
                self.patient = replace(
                    self.patient,
                    full_name=payload["full_name"],
                    phone=payload["phone"],
                    sex=payload["gender"], 
                    age=payload["age"]
                )
                
                # 4. UI Refresh
                self.setUpdatesEnabled(False) # Prevent flickering
                self._update_summary_ui()
                self.setUpdatesEnabled(True)
                
                print(f"UI SYNC: Age refreshed to {self.patient.age}")
                QMessageBox.information(self, "Success", "Patient record updated.")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Update failed: {str(e)}")
        finally:
            self.btn_save.setText("Save Changes")
            self._check_dirty()