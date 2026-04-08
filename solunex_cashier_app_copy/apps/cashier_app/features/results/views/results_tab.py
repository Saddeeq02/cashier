# -*- coding: utf-8 -*-
# apps\cashier_app\features\results\views\results_tab.py
from __future__ import annotations

from dataclasses import dataclass
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem
)
import requests

from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.results.views.reprint_result_dialog import ReprintResultDialog
from apps.cashier_app.features.results.views.release_result_dialog import ReleaseResultDialog
from apps.cashier_app.features.results.results_api import release_result
from PySide6.QtWidgets import QMessageBox

from apps.cashier_app.app_state import state


@dataclass
class ResultLite:
    result_id: str
    test_name: str
    lab_status: str      # draft | pending_review | approved | released
    payment_status: str  # pending | paid
    created_at: str


class ResultsTab(QWidget):
    def __init__(self, patient: PatientLite):
        super().__init__()
        self.patient = patient

        # Backend Data Base rows
        self._rows: list[ResultLite] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        title = QLabel("Results")
        title.setStyleSheet("font-size: 12pt; font-weight: 800;")
        h.addWidget(title)

        hint = QLabel("Reprint and Release are dialog-based. Release is gated by status + payment.")
        hint.setObjectName("Muted")
        h.addWidget(hint)

        h.addStretch(1)

        self.btn_reprint = QPushButton("Reprint")
        self.btn_reprint.clicked.connect(self._reprint_selected)
        self.btn_reprint.setEnabled(False)
        h.addWidget(self.btn_reprint)

        self.btn_release = QPushButton("Release")
        self.btn_release.setObjectName("Primary")
        self.btn_release.clicked.connect(self._release_selected)
        self.btn_release.setEnabled(False)
        h.addWidget(self.btn_release)

        root.addWidget(header)

        panel = QFrame()
        panel.setObjectName("Panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(14, 14, 14, 14)
        p.setSpacing(10)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Result ID", "Test", "Lab Status", "Payment", "Created At"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_select)

        p.addWidget(self.table)
        root.addWidget(panel, 1)

        self._load_results()
        self._render()

    def _load_results(self):

        from apps.cashier_app.features.results.results_api import list_results

        data = list_results(self.patient.id)
        rows = []

        if not isinstance(data, dict):
            print("Unexpected API response:", data)
            self._rows = []
            return

        rows = []

        for r in data.get("value", []):
            actual_test_name = None
            
            # 1. Dig into the template_snapshot (This is where the name is hiding!)
            snapshot = r.get("template_snapshot") or {}
            
            # Just in case the backend sends the JSON as a raw string
            if isinstance(snapshot, str):
                import json
                try: 
                    snapshot = json.loads(snapshot)
                except: 
                    snapshot = {}
            
            # Extract the title from the snapshot structure
            actual_test_name = snapshot.get("title") or snapshot.get("name") or snapshot.get("test_name")

            # 2. Flat Key Fallback (just in case)
            if not actual_test_name:
                actual_test_name = r.get("test_name") or r.get("test_type") or r.get("request_test_name")
            
            # 3. Final ID Fallback
            if not actual_test_name:
                fallback_id = r.get("test_type_id", "Unknown")
                actual_test_name = f"Test #{fallback_id}"

            rows.append(
                ResultLite(
                    result_id=str(r.get("id", "")),
                    test_name=str(actual_test_name),
                    lab_status=str(r.get("status", "draft")),
                    payment_status="paid",
                    created_at=str(r.get("created_at", ""))[:10],
                )
            )

        self._rows = rows

    def refresh(self) -> None:
        self._load_results()
        self._render()

    def _render(self) -> None:
        self.table.setRowCount(0)
        for r in self._rows:
            i = self.table.rowCount()
            self.table.insertRow(i)

            def add(col: int, val: str):
                it = QTableWidgetItem(val)
                it.setData(Qt.UserRole, r)
                self.table.setItem(i, col, it)

            add(0, r.result_id)
            add(1, r.test_name)
            add(2, r.lab_status)
            add(3, r.payment_status)
            add(4, r.created_at)

        self.btn_reprint.setEnabled(False)
        self.btn_release.setEnabled(False)

    def _selected(self) -> ResultLite | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return items[0].data(Qt.UserRole)

    def _on_select(self) -> None:
        r = self._selected()
        if not r:
            self.btn_reprint.setEnabled(False)
            self.btn_release.setEnabled(False)
            return

        # Reprint allowed only when released
        self.btn_reprint.setEnabled(r.lab_status == "released")

        # Release allowed only when approved + paid, and not already released
        can_release = (r.lab_status != "released") and (r.payment_status == "paid")
        self.btn_release.setEnabled(can_release)


    def _reprint_selected(self) -> None:
        r = self._selected()
        if not r:
            return

        # token = self._get_token()  # <-- REMOVE this line

        url = f"{state.api_base_url}/api/results/{r.result_id}/reprint"
        headers = {"Authorization": f"Bearer {state.access_token}"}  # use state token

        try:
            res = requests.get(url, headers=headers)

            if res.status_code == 200:
                file_path = f"result_{r.result_id}.pdf"
                with open(file_path, "wb") as f:
                    f.write(res.content)

                QMessageBox.information(self, "Success", f"Saved: {file_path}")

            else:
                QMessageBox.warning(self, "Error", res.text)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    
    def _release_selected(self) -> None:
        r = self._selected()
        if not r:
            return

        # Allow release if paid and not already released
        if r.payment_status != "paid" or r.lab_status == "released":
            QMessageBox.warning(self, "Cannot Release", "Result must be paid and not already released.")
            return

        dlg = ReleaseResultDialog(self.patient, f"{r.test_name} — {r.result_id}", parent=self)

        if dlg.exec() == 1:
            try:
                release_result(r.result_id)

                # reload backend data
                self._load_results()

                # redraw UI table
                self._render()

            except Exception as e:
                QMessageBox.critical(self, "Release Failed", str(e))