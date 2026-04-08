# -*- coding: utf-8 -*-
# apps/cashier_app/features/test_requests/views/test_requests_tab.py

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog
)

from apps.cashier_app.app_state import state
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.test_requests.views.request_test_dialog import RequestTestDialog

from apps.cashier_app.features.test_requests.api import (
    create_test_request,
    CreateTestRequestPayload,
    list_test_requests,
    list_test_types,
)

BACKEND_DOWN_TEXT = "backend is busy or not reachable, try reconnect from settings and try again later"


@dataclass(frozen=True)
class TestRequestLite:
    request_id: str
    test_name: str
    status: str
    created_at: str


class TestRequestsTab(QWidget):
    def __init__(self, patient: PatientLite):
        super().__init__()
        self.patient = patient

        # Backend-derived lists
        self._pending_backend: list[TestRequestLite] = []
        self._submitted_backend: list[TestRequestLite] = []

        # Cache: test_type_id -> display name
        self._test_type_name: dict[int, str] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        title = QLabel("Test Requests")
        title.setStyleSheet("font-size: 12pt; font-weight: 800;")
        h.addWidget(title)

        hint = QLabel("Pending requests require payment. Paid requests are visible in Lab App.")
        hint.setObjectName("Muted")
        h.addWidget(hint)

        h.addStretch(1)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh)
        h.addWidget(btn_refresh)

        btn_request = QPushButton("Request Test")
        btn_request.setObjectName("Primary")
        btn_request.clicked.connect(self._open_request_dialog)
        h.addWidget(btn_request)

        root.addWidget(header)

        # Pending (backend)
        pending_panel = QFrame()
        pending_panel.setObjectName("Panel")
        p = QVBoxLayout(pending_panel)
        p.setContentsMargins(14, 14, 14, 14)
        p.setSpacing(10)

        p.addWidget(self._section_title("Pending (Not Paid Yet)"))
        self.pending_table = self._make_table()
        p.addWidget(self.pending_table)
        root.addWidget(pending_panel, 1)

        # Submitted (backend)
        submitted_panel = QFrame()
        submitted_panel.setObjectName("Panel")
        pp = QVBoxLayout(submitted_panel)
        pp.setContentsMargins(14, 14, 14, 14)
        pp.setSpacing(10)

        pp.addWidget(self._section_title("Paid / Submitted to Lab (Backend / Lab Visible)"))
        self.submitted_table = self._make_table()
        pp.addWidget(self.submitted_table)
        root.addWidget(submitted_panel, 1)

        self.refresh()

    def refresh(self) -> None:
        try:
            if not getattr(self.patient, "id", None):
                raise RuntimeError("Patient.id missing. Ensure patient search/open uses backend patient id.")

            self._load_test_type_map()
            self._load_backend_requests()

            self._render()

        except Exception as e:
            # Placeholder rows, no crash
            self._pending_backend = []
            self._submitted_backend = []
            self._render_placeholder(self.pending_table, BACKEND_DOWN_TEXT)
            self._render_placeholder(self.submitted_table, BACKEND_DOWN_TEXT)

            # optional popup
            QMessageBox.warning(self, "Backend", f"Could not load requests.\n\n{e}")

    def _open_request_dialog(self) -> None:
        dlg = RequestTestDialog(patient=self.patient, parent=self)
        if dlg.exec() != QDialog.Accepted or not dlg.created_requests:
            return

        # Phase 3: always create backend requests as 'pending'
        for r in dlg.created_requests:
            try:
                create_test_request(
                    CreateTestRequestPayload(
                        patient_id=int(self.patient.id),
                        test_type_id=int(r.test_type_id),
                        requested_by=state.username,
                    )
                )
            except Exception as e:
                QMessageBox.critical(self, "Request Failed", str(e))

        self.refresh()

    # -------------------------
    # Backend loaders
    # -------------------------
    def _load_test_type_map(self) -> None:
        rows = list_test_types() or []
        m: dict[int, str] = {}
        for r in rows:
            try:
                tid = int(r.get("id"))
            except Exception:
                continue
            name = (r.get("name") or "").strip()
            code = (r.get("code") or "").strip()
            if not name:
                continue
            m[tid] = f"{name}" + (f" ({code})" if code else "")
        self._test_type_name = m

    def _load_backend_requests(self) -> None:
        rows = list_test_requests(patient_id=int(self.patient.id), limit=200) or []

        pending: list[TestRequestLite] = []
        submitted: list[TestRequestLite] = []

        for r in rows:
            rid = r.get("id")
            tid = r.get("test_type_id")
            status = (r.get("status") or "").strip().lower()
            created_at = str(r.get("created_at") or "")

            # keep date readable
            if "T" in created_at:
                created_at = created_at.split("T")[0]

            try:
                rid_s = str(int(rid))
            except Exception:
                rid_s = str(rid or "")

            # Map test name
            tname = "Unknown Test"
            try:
                tname = self._test_type_name.get(int(tid), f"TestType #{tid}")
            except Exception:
                tname = f"TestType #{tid}"

            tr = TestRequestLite(
                request_id=rid_s,
                test_name=tname,
                status=status or "pending",
                created_at=created_at,
            )

            if status == "pending":
                pending.append(tr)
            else:
                # includes paid/accepted/fulfilled/rejected
                submitted.append(tr)

        self._pending_backend = pending
        self._submitted_backend = submitted

    # -------------------------
    # Rendering
    # -------------------------
    def _render(self) -> None:
        self._fill_table(self.pending_table, self._pending_backend)
        self._fill_table(self.submitted_table, self._submitted_backend)

    def _make_table(self) -> QTableWidget:
        t = QTableWidget(0, 4)
        t.setHorizontalHeaderLabels(["Request ID", "Test", "Status", "Created At"])
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setSelectionMode(QTableWidget.SingleSelection)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        return t

    def _render_placeholder(self, table: QTableWidget, msg: str) -> None:
        table.setRowCount(0)
        table.insertRow(0)
        for col in range(table.columnCount()):
            item = QTableWidgetItem("" if col != 1 else msg)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            table.setItem(0, col, item)
        table.resizeColumnsToContents()

    def _fill_table(self, table: QTableWidget, rows: list[TestRequestLite]) -> None:
        table.setRowCount(0)
        if not rows:
            self._render_placeholder(table, "No records.")
            return

        for r in rows:
            i = table.rowCount()
            table.insertRow(i)

            def add(col: int, val: str):
                item = QTableWidgetItem(val)
                item.setData(Qt.UserRole, r)
                table.setItem(i, col, item)

            add(0, r.request_id)
            add(1, r.test_name)
            add(2, r.status)
            add(3, r.created_at)

        table.resizeColumnsToContents()

    def _section_title(self, text: str) -> QLabel:
        lab = QLabel(text)
        lab.setStyleSheet("font-weight: 800;")
        return lab