# -*- coding: utf-8 -*-
# apps/cashier_app/features/payments/views/force_push_dialog.py

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox
)

from shared.uix.widgets.dialogs import SolunexDialog
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.payments.api import list_pending_test_requests
from shared.api.client import client


def _format_force_note(reason: str) -> str:
    r = (reason or "").strip()
    return f"[FORCE_PUSH] {r}" if r else "[FORCE_PUSH]"


class ForcePushDialog(SolunexDialog):
    """
    Force Push:
    - Select backend PENDING test_requests
    - PATCH each: status='paid' + requested_note='[FORCE_PUSH] ...'
    Result:
    - Lab can see/work (paid)
    - Cashier can still identify them via requested_note flag
    """
    def __init__(self, patient: PatientLite, parent=None):
        super().__init__("Force Push Pending Tests", parent=parent, width=780, height=560)
        self.patient = patient
        self.pushed_count = 0

        head = QLabel(f"{patient.patient_no} — {patient.full_name} ({patient.phone})")
        head.setObjectName("Muted")
        self.body_layout.addWidget(head)

        panel = QFrame()
        panel.setObjectName("Panel2")
        self.body_layout.addWidget(panel, 1)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        warn = QLabel(
            "Warning: Force Push is ONLY for trusted customers.\n"
            "Lab may start work, but payment confirmation is still required before final release."
        )
        warn.setStyleSheet("font-weight: 800;")
        lay.addWidget(warn)

        lay.addWidget(QLabel("Select pending test request(s) to force-push:"))

        self.requests = QListWidget()
        lay.addWidget(self.requests, 1)

        note = QLabel("Force push note (audit trail):")
        note.setObjectName("Muted")
        lay.addWidget(note)

        self.reason = QTextEdit()
        self.reason.setPlaceholderText("e.g., Customer promised to pay on pickup. Approved by Admin.")
        lay.addWidget(self.reason, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        self.btn_confirm = QPushButton("Confirm Force Push")
        self.btn_confirm.setObjectName("Primary")
        self.btn_confirm.clicked.connect(self._do_force_push)
        actions.addWidget(self.btn_confirm)

        self.body_layout.addLayout(actions)

        self._load_pending()

    def _load_pending(self) -> None:
        self.requests.clear()

        if not getattr(self.patient, "id", None):
            QMessageBox.warning(self, "Missing patient id", "Backend patient id is missing for this profile.")
            self.btn_confirm.setEnabled(False)
            return

        try:
            rows = list_pending_test_requests(int(self.patient.id)) or []
        except Exception as e:
            QMessageBox.warning(self, "Backend Unreachable", str(e))
            self.btn_confirm.setEnabled(False)
            return

        if not rows:
            item = QListWidgetItem("(No pending requests)")
            item.setFlags(Qt.NoItemFlags)
            self.requests.addItem(item)
            self.btn_confirm.setEnabled(False)
            return

        self.btn_confirm.setEnabled(True)

        for r in rows:
            rid = r.get("id")
            ttid = r.get("test_type_id")
            # If backend has test_name later, use it. For now:
            label = f"TR-{rid}  |  TestType-{ttid}  |  status=pending"
            it = QListWidgetItem(label)
            it.setData(Qt.UserRole, int(rid))
            it.setCheckState(Qt.Unchecked)
            self.requests.addItem(it)

    def _selected_ids(self) -> list[int]:
        ids: list[int] = []
        for i in range(self.requests.count()):
            it = self.requests.item(i)
            if it.flags() == Qt.NoItemFlags:
                continue
            if it.checkState() == Qt.Checked:
                rid = it.data(Qt.UserRole)
                if rid:
                    ids.append(int(rid))
        return ids

    def _do_force_push(self) -> None:
        ids = self._selected_ids()
        if not ids:
            QMessageBox.information(self, "No selection", "Select at least one pending request.")
            return

        reason = _format_force_note(self.reason.toPlainText())

        # Confirm
        ok = QMessageBox.question(
            self,
            "Confirm Force Push",
            f"Force push {len(ids)} request(s) to Lab as PAID?\n\nThey will be flagged as FORCE_PUSH in audit notes.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ok != QMessageBox.Yes:
            return

        self.btn_confirm.setEnabled(False)

        failed: list[str] = []
        pushed = 0

        for rid in ids:
            try:
                # PATCH /api/test-requests/{id}/status
                r = client.patch(
                    f"/api/test-requests/{int(rid)}/status",
                    json={"status": "paid", "requested_note": reason},
                )
                r.raise_for_status()
                pushed += 1
            except Exception as e:
                failed.append(f"TR-{rid}: {e}")

        self.pushed_count = pushed

        if failed:
            QMessageBox.warning(
                self,
                "Force Push Partial",
                f"Pushed: {pushed}\nFailed: {len(failed)}\n\n" + "\n".join(failed[:8])
            )
        else:
            QMessageBox.information(self, "Force Push Complete", f"Pushed {pushed} request(s) to Lab as PAID.")

        self.accept()
