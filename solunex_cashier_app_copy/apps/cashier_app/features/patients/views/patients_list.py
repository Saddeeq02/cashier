# -*- coding: utf-8 -*-
# apps/cashier_app/features/patients/views/patients_list.py
from __future__ import annotations
from datetime import date

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QMessageBox, QDialog
)

from apps.cashier_app.features.patients.api import search_patients
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.patients.views.patient_create_dialog import PatientCreateDialog

BACKEND_DOWN_TEXT = "Backend unreachable. Check connection from Settings."
EMPTY_SEARCH_TEXT = "No patients registered today."

print("USING CASHIER PatientsListView (LIVE) FROM:", __file__)

def _age_from_dob(dob_value) -> int:
    if not dob_value:
        return 0
    s = str(dob_value).strip()
    if not s:
        return 0
    s = s[:10]  # YYYY-MM-DD
    try:
        y, m, d = map(int, s.split("-"))
        dob = date(y, m, d)
        today = date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
    except Exception:
        return 0

class PatientsListView(QWidget):
    # Emit when a patient is opened (Shell will route)
    open_patient = Signal(object)  # PatientLite

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        # Header controls
        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        title = QLabel("Daily Queue")
        title.setStyleSheet("font-size: 13pt; font-weight: 800;")
        h.addWidget(title)

        h.addStretch(1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search all or leave empty for Today...")
        self.search.setClearButtonEnabled(True)
        h.addWidget(self.search, 2)

        # Timers for search debouncing and live refreshing
        self._search_timer = QTimer(self)
        self._search_timer.setInterval(400)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh)
        
        self.search.textChanged.connect(lambda: self._search_timer.start())

        self.live_timer = QTimer(self)
        self.live_timer.timeout.connect(self._auto_refresh)
        self.live_timer.start(60000) # 1 minute refresh

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh)
        h.addWidget(self.btn_refresh)

        self.btn_new = QPushButton("New Patient")
        self.btn_new.setObjectName("Primary")
        self.btn_new.clicked.connect(self._new_patient_stub)
        h.addWidget(self.btn_new)

        self.btn_open = QPushButton("Open Profile")
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self._open_selected)
        h.addWidget(self.btn_open)

        root.addWidget(header)

        # Table
        table_panel = QFrame()
        table_panel.setObjectName("Panel")
        tlay = QVBoxLayout(table_panel)
        tlay.setContentsMargins(14, 14, 14, 14)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Patient No", "Full Name", "Phone", "Sex", "Age", "Registered At"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self._on_select_change)
        self.table.cellDoubleClicked.connect(lambda *_: self._open_selected())

        tlay.addWidget(self.table)
        root.addWidget(table_panel, 1)

        self._all: list[PatientLite] = []
        self._filtered: list[PatientLite] = []
        
        # Initial load
        QTimer.singleShot(100, self.refresh)

    def _auto_refresh(self):
        """Only auto-refreshes if user is not currently typing."""
        if not self.search.text().strip():
            self.refresh()

    def refresh(self) -> None:
        q = self.search.text().strip()
        today_str = date.today().isoformat()

        try:
            # If search is empty, we pass created_date. 
            # If search has text, we pass q (The API router we fixed handles this).
            if not q:
                rows = search_patients(created_date=today_str) or []
            else:
                rows = search_patients(q=q) or []

            self._all = []
            for r in rows:
                dob = r.get("date_of_birth") or r.get("dob")
                computed_age = _age_from_dob(dob)

                self._all.append(
                    PatientLite(
                        id=r["id"],
                        patient_no=r.get("patient_no") or "",
                        full_name=r.get("full_name") or "",
                        phone=r.get("phone") or "",
                        sex=((r.get("gender") or "")[:1].upper() or "-"),
                        age=computed_age,
                        created_at=str(r.get("created_at") or "")[:16].replace("T", " "),
                    )
                )

            self._filtered = list(self._all)
            
            if not self._filtered:
                msg = EMPTY_SEARCH_TEXT if not q else f"No results for '{q}'"
                self._render_placeholder(msg)
            else:
                self._render()

        except Exception as e:
            print(f"CASHIER LIST ERROR: {e}")
            self._filtered = []
            self._render_placeholder(BACKEND_DOWN_TEXT)

    def _render_placeholder(self, message: str) -> None:
        self.table.setRowCount(0)
        self.table.insertRow(0)
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("" if col != 1 else message)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(0, col, item)
        self.btn_open.setEnabled(False)

    def _render(self) -> None:
        self.table.setRowCount(0)
        for p in self._filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)

            def add(col: int, val: str):
                item = QTableWidgetItem(val)
                item.setData(Qt.UserRole, p)
                self.table.setItem(row, col, item)

            add(0, p.patient_no)
            add(1, p.full_name)
            add(2, p.phone)
            add(3, p.sex)
            add(4, str(p.age))
            add(5, p.created_at)

        self.btn_open.setEnabled(False) # Wait for click

    def _on_select_change(self) -> None:
        p = self._selected_patient()
        self.btn_open.setEnabled(p is not None)

    def _selected_patient(self) -> PatientLite | None:
        items = self.table.selectedItems()
        if not items:
            return None
        p = items[0].data(Qt.UserRole)
        return p if isinstance(p, PatientLite) else None

    def _open_selected(self) -> None:
        p = self._selected_patient()
        if not p:
            return
        self.open_patient.emit(p)

    def _new_patient_stub(self) -> None:
        dlg = PatientCreateDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            # Clear search and refresh to show the new patient at the top of the queue
            self.search.clear()
            self.refresh()