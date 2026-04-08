# apps/cashier_app/features/test_requests/views/request_test_dialog.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QPushButton, QFrame, QLineEdit
)

from shared.uix.widgets.dialogs import SolunexDialog
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.test_requests.api import list_test_types


@dataclass(frozen=True)
class CreatedRequest:
    request_id: str
    test_type_id: int
    test_name: str
    price: float  
    status: str
    created_at: str


class RequestTestDialog(SolunexDialog):

    def __init__(self, patient: PatientLite, parent=None):
        super().__init__("Request Test", parent=parent, width=760, height=620)

        self.patient = patient
        self.created_requests: list[CreatedRequest] = []

        # DATA STORAGE
        self._all_tests: list[dict] = []  # Full master list from backend
        self._selected_ids: set[int] = set()  # PERSISTENT STORAGE for selected test IDs

        # -----------------------------
        # Patient header
        # -----------------------------
        head = QLabel(f"{patient.patient_no} — {patient.full_name} ({patient.phone})")
        head.setObjectName("Muted")
        self.body_layout.addWidget(head)

        panel = QFrame()
        panel.setObjectName("Panel2")
        self.body_layout.addWidget(panel)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        # -----------------------------
        # Search Bar
        # -----------------------------
        search_row = QHBoxLayout()
        search_label = QLabel("Search Test:")
        search_row.addWidget(search_label)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Type test name or code...")
        self.search.textChanged.connect(self._apply_filter)
        search_row.addWidget(self.search)

        lay.addLayout(search_row)

        # -----------------------------
        # Test List
        # -----------------------------
        self.list = QListWidget()
        # Connect to our new state-tracking method
        self.list.itemChanged.connect(self._on_item_toggled)
        lay.addWidget(self.list, 1)

        # -----------------------------
        # Total display
        # -----------------------------
        self.total_label = QLabel("Total: ₦0.00")
        self.total_label.setStyleSheet("font-weight:800; font-size:12pt;")
        lay.addWidget(self.total_label)

        # -----------------------------
        # Status
        # -----------------------------
        self.status_label = QLabel("")
        self.status_label.setObjectName("Muted")
        lay.addWidget(self.status_label)

        # -----------------------------
        # Options & Actions
        # -----------------------------
        self.mark_paid = QCheckBox("Mark as PAID (demo UI)")
        self.mark_paid.setChecked(False)
        lay.addWidget(self.mark_paid)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        btn_save = QPushButton("Save")
        btn_save.setObjectName("Primary")
        btn_save.clicked.connect(self._save)
        actions.addWidget(btn_save)

        self.body_layout.addLayout(actions)

        # Initialize loading
        self._load_test_types()

    def _load_test_types(self):
        """Fetch test types and store them in the master list."""
        try:
            rows = list_test_types()
            if not rows:
                self.status_label.setText("No test types found.")
                return

            self._all_tests.clear()
            for r in rows:
                tid = r.get("id")
                name = (r.get("name") or "").strip()
                code = (r.get("code") or "").strip()
                price = float(r.get("price", 0))

                if tid is not None and name:
                    self._all_tests.append({
                        "id": int(tid),
                        "name": name,
                        "code": code,
                        "price": price
                    })

            self._render_tests(self._all_tests)
            self.status_label.setText(f"Loaded {len(self._all_tests)} test types.")

        except Exception as e:
            self.status_label.setText(f"Failed to load: {e}")

    def _render_tests(self, rows: list[dict]):
        """Render specific rows while preserving selection state from the ID set."""
        self.list.blockSignals(True)  # Prevent itemChanged triggering during build
        self.list.clear()

        for r in rows:
            tid = r["id"]
            price = r["price"]
            name = r["name"]
            
            label = f"{name} — ₦{price:,.2f}"
            if r["code"]:
                label += f" ({r['code']})"

            item = QListWidgetItem(label)
            
            # THE FIX: Check if this ID exists in our persistent selection set
            if tid in self._selected_ids:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

            # Store metadata
            item.setData(Qt.UserRole, tid)
            item.setData(Qt.UserRole + 1, name)
            item.setData(Qt.UserRole + 2, price)

            self.list.addItem(item)

        self.list.blockSignals(False)

    def _on_item_toggled(self, item: QListWidgetItem):
        """Update the Source of Truth (self._selected_ids) whenever a user clicks."""
        tid = item.data(Qt.UserRole)
        if tid is None:
            return

        if item.checkState() == Qt.Checked:
            self._selected_ids.add(tid)
        else:
            self._selected_ids.discard(tid)
        
        self._recompute_total()

    def _apply_filter(self, text: str):
        """Filter the master list and re-render."""
        query = text.strip().lower()
        if not query:
            self._render_tests(self._all_tests)
            return

        filtered = [
            r for r in self._all_tests 
            if query in r["name"].lower() or query in (r["code"] or "").lower()
        ]
        self._render_tests(filtered)

    def _recompute_total(self):
        """Calculate total based on selected IDs, regardless of current visibility."""
        total = 0.0
        for r in self._all_tests:
            if r["id"] in self._selected_ids:
                total += r["price"]
        
        self.total_label.setText(f"Total: ₦{total:,.2f}")

    def _save(self):
        """Finalize and create requests based on the selected ID set."""
        if not self._selected_ids:
            return

        status = "paid" if self.mark_paid.isChecked() else "pending"
        today = date.today().isoformat()
        base_id = 2000
        
        # Cross-reference selected IDs with the master data
        count = 1
        for r in self._all_tests:
            if r["id"] in self._selected_ids:
                self.created_requests.append(
                    CreatedRequest(
                        request_id=f"R-{base_id + count}",
                        test_type_id=r["id"],
                        test_name=r["name"],
                        price=r["price"],
                        status=status,
                        created_at=today
                    )
                )
                count += 1

        self.accept()