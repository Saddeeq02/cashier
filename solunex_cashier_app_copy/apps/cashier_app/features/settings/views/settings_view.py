# -*- coding: utf-8 -*-
# apps/cashier_app/features/settings/views/settings_view.py

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox
)

from shared.api.client import client, APIError
from apps.cashier_app.app_state import state


class SettingsView(QWidget):

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        # -------------------------
        # HEADER
        # -------------------------
        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 13pt; font-weight: 800;")
        h.addWidget(title)

        hint = QLabel("System configuration, connectivity, branding and operator preferences.")
        hint.setObjectName("Muted")
        h.addWidget(hint)

        h.addStretch(1)

        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setObjectName("Primary")
        self.btn_save.clicked.connect(self._save)
        h.addWidget(self.btn_save)

        root.addWidget(header)

        # -------------------------
        # PANELS
        # -------------------------
        root.addWidget(self._connection_panel())
        root.addWidget(self._operator_panel())
        root.addWidget(self._branding_panel(), 1)
        root.addWidget(self._about_panel())

        self._load_state()

    # ==========================================================
    # STATE SYNC
    # ==========================================================
    def _load_state(self):
        self.base_url.setText(state.api_base_url)
        self.timeout.setText(str(state.api_timeout))

        self.operator_name.setText(state.operator_name or "")
        self.role.setCurrentText(state.operator_role or "cashier")

    # ==========================================================
    # SAVE
    # ==========================================================
    def _save(self):

        self._set_loading(True)

        try:
            # -------------------------
            # Validate inputs
            # -------------------------
            base_url = self.base_url.text().strip()
            timeout = int(self.timeout.text() or 15)

            if not base_url.startswith("http"):
                raise ValueError("Invalid Base URL")

            # -------------------------
            # Apply state
            # -------------------------
            state.api_base_url = base_url
            state.api_timeout = timeout

            state.operator_name = self.operator_name.text().strip()
            state.operator_role = self.role.currentText()

            # Branding (for receipt engine)
            state.facility_name = self.facility_name.text().strip()
            state.facility_phone = self.facility_phone.text().strip()
            state.facility_address = self.facility_address.toPlainText().strip()
            state.footer_note = self.footer_note.text().strip()
            state.printer_name = self.printer_name.text().strip()

            QMessageBox.information(self, "Saved", "Settings updated successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        self._set_loading(False)

    # ==========================================================
    # CONNECTION TEST
    # ==========================================================
    def _test_connection(self):

        self._set_loading(True)

        try:
            # lightweight ping
            client.get("/openapi.json")

            QMessageBox.information(self, "Connection OK", "Backend is reachable.")

        except APIError as e:
            QMessageBox.critical(self, "Connection Failed", str(e))

        self._set_loading(False)

    # ==========================================================
    # PANELS
    # ==========================================================
    def _connection_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(12)

        t = QLabel("Connection")
        t.setStyleSheet("font-weight: 900; font-size: 12pt;")
        lay.addWidget(t)

        sub = QLabel("Backend API connectivity (Solunex Core).")
        sub.setObjectName("Muted")
        lay.addWidget(sub)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.base_url = QLineEdit()
        self.base_url.setPlaceholderText("https://api.iandelaboratory.com")

        self.timeout = QLineEdit()
        self.timeout.setPlaceholderText("15")

        row.addWidget(self._field("Base URL", self.base_url), 3)
        row.addWidget(self._field("Timeout (s)", self.timeout), 1)
        lay.addLayout(row)

        btns = QHBoxLayout()
        btns.addStretch(1)

        btn_test = QPushButton("Test Connection")
        btn_test.clicked.connect(self._test_connection)
        btns.addWidget(btn_test)

        lay.addLayout(btns)

        return panel

    def _operator_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(12)

        t = QLabel("Operator / Session")
        t.setStyleSheet("font-weight: 900; font-size: 12pt;")
        lay.addWidget(t)

        sub = QLabel("Display identity used across receipts and logs.")
        sub.setObjectName("Muted")
        lay.addWidget(sub)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.operator_name = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["cashier", "receptionist"])

        row.addWidget(self._field("Display Name", self.operator_name), 2)
        row.addWidget(self._field("Role", self.role), 1)
        lay.addLayout(row)

        return panel

    def _branding_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(12)

        t = QLabel("Branding / Printing")
        t.setStyleSheet("font-weight: 900; font-size: 12pt;")
        lay.addWidget(t)

        sub = QLabel("Used by receipt & report engine.")
        sub.setObjectName("Muted")
        lay.addWidget(sub)

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.facility_name = QLineEdit()
        self.facility_phone = QLineEdit()

        row1.addWidget(self._field("Facility Name", self.facility_name), 2)
        row1.addWidget(self._field("Facility Phone", self.facility_phone), 1)
        lay.addLayout(row1)

        self.facility_address = QTextEdit()
        lay.addWidget(self._field("Facility Address", self.facility_address))

        row2 = QHBoxLayout()
        row2.setSpacing(10)

        self.footer_note = QLineEdit()
        self.printer_name = QLineEdit()

        row2.addWidget(self._field("Footer Note", self.footer_note), 2)
        row2.addWidget(self._field("Printer", self.printer_name), 1)
        lay.addLayout(row2)

        return panel

    def _about_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Panel2")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 12, 14, 12)

        t = QLabel("About")
        t.setStyleSheet("font-weight: 900;")
        lay.addWidget(t)

        info = QLabel("Solunex Cashier — Enterprise UIX Layer\nVersion: 1.0")
        info.setObjectName("Muted")
        lay.addWidget(info)

        return panel

    # ==========================================================
    # UTIL
    # ==========================================================
    def _set_loading(self, state: bool):
        self.btn_save.setEnabled(not state)
        self.btn_save.setText("Saving..." if state else "Save Settings")

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