# -*- coding: utf-8 -*-
from __future__ import annotations
import requests

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget,
    QComboBox, QDateTimeEdit, QPushButton, QMessageBox,
    QDoubleSpinBox, QTabWidget, QHeaderView, QTableWidgetItem, QFrame
)

from apps.cashier_app.features.test_requests.views.request_test_dialog import RequestTestDialog
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.app_state import state
from apps.cashier_app.features.referrals.views.referrer_dashboard_dialog import ReferrerDashboardDialog


class ReferralWizardView(QWidget):

    def __init__(self):
        super().__init__()

        self.active_referrer_id = None
        self.row_test_map = {}
        self.current_gross = 0.0
        self.current_net = 0.0

        self._init_ui()

    # ==========================================================
    # UI ROOT
    # ==========================================================

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(15)

        # HEADER
        header = QFrame()
        header.setObjectName("HeaderBar")
        header.setFixedHeight(60)

        h = QHBoxLayout(header)

        title = QLabel("REFERRAL BATCH MANAGEMENT")
        title.setObjectName("Title")

        self.status_pill = QLabel("READY")
        self.status_pill.setObjectName("StatusNormal")

        h.addWidget(title)
        h.addStretch()
        h.addWidget(self.status_pill)

        root.addWidget(header)

        # TABS
        self.tabs = QTabWidget()
        self.tab_list = QWidget()   # NEW
        self.tab_reg = QWidget()
        self.tab_log = QWidget()
        self.tab_req = QWidget()
        self.tab_pay = QWidget()
        
        self._referrer_list_tab()
        self._step_1()
        self._step_2()
        self._step_3()
        self._step_4()

        

        self.tabs.addTab(self.tab_list, "REFERRERS")  # FIRST TAB
        self.tabs.addTab(self.tab_reg, "01 PROFILE")
        self.tabs.addTab(self.tab_log, "02 INTAKE")
        self.tabs.addTab(self.tab_req, "03 MAPPING")
        self.tabs.addTab(self.tab_pay, "04 SETTLEMENT")

        for i in range(1, 4):
            self.tabs.setTabEnabled(i, False)

        root.addWidget(self.tabs)

    # ==========================================================
    # STEP 1 — PROFILE
    # ==========================================================


    def _referrer_list_tab(self):
        layout = QVBoxLayout(self.tab_list)

        # TABLE
        self.ref_table = QTableWidget(0, 3)
        self.ref_table.setHorizontalHeaderLabels(["NAME", "PHONE", ""])
        self.ref_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.ref_table.cellDoubleClicked.connect(self._open_referrer_dashboard)

        layout.addWidget(self.ref_table)

        # LOAD BUTTON
        btn = QPushButton("REFRESH")
        btn.clicked.connect(self._load_referrers)
        layout.addWidget(btn)

        self._load_referrers()


    def _load_referrers(self):
        try:
            url = f"{state.api_base_url}/api/referrer/list"
            headers = {"Authorization": f"Bearer {state.access_token}"}

            resp = requests.get(url, headers=headers)

            if resp.status_code != 200:
                QMessageBox.critical(self, "Error", resp.text)
                return

            data = resp.json()

            self.ref_table.setRowCount(0)

            for r, ref in enumerate(data):
                self.ref_table.insertRow(r)

                self.ref_table.setItem(r, 0, QTableWidgetItem(ref["name"]))
                self.ref_table.setItem(r, 1, QTableWidgetItem(ref["phone"]))

                # Store ID internally
                self.ref_table.setRowHeight(r, 42)
                self.ref_table.setVerticalHeaderItem(r, QTableWidgetItem(str(ref["id"])))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def _open_referrer_dashboard(self, row, col):
        ref_id = int(self.ref_table.verticalHeaderItem(row).text())
        name = self.ref_table.item(row, 0).text()

        dlg = ReferrerDashboardDialog(ref_id, name, self)
        dlg.exec()

    def _step_1(self):
        layout = QVBoxLayout(self.tab_reg)
        layout.setContentsMargins(60, 40, 60, 40)

        form = QFrame()
        form.setObjectName("Panel")

        f = QVBoxLayout(form)
        f.setSpacing(15)

        self.ref_name = QLineEdit()
        self.ref_phone = QLineEdit()
        self.ref_code = QLineEdit()
        self.ref_code.setReadOnly(True)

        f.addWidget(self._label_input("FACILITY / SOURCE NAME", self.ref_name))
        f.addWidget(self._label_input("CONTACT PHONE NUMBER", self.ref_phone))
        f.addWidget(self._label_input("SYSTEM BATCH UID", self.ref_code))

        layout.addWidget(form)
        layout.addStretch()

        btn = QPushButton("CREATE BATCH SESSION →")
        btn.setObjectName("Primary")
        btn.setFixedHeight(45)
        btn.clicked.connect(self._to_step_2)

        layout.addWidget(btn)

    # ==========================================================
    # STEP 2 — INTAKE
    # ==========================================================

    def _step_2(self):
        layout = QVBoxLayout(self.tab_log)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 10, 20, 10)

        # ===============================
        # TOP BAR (BETTER SPACING)
        # ===============================
        bar = QFrame()
        bar.setObjectName("PanelAlt")

        b = QHBoxLayout(bar)
        b.setContentsMargins(15, 10, 15, 10)
        b.setSpacing(10)

        self.date_rec = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_eta = QDateTimeEdit(QDateTime.currentDateTime().addDays(1))

        self.date_rec.setFixedHeight(34)
        self.date_eta.setFixedHeight(34)

        b.addWidget(QLabel("RECEIVED"))
        b.addWidget(self.date_rec)
        b.addSpacing(20)
        b.addWidget(QLabel("EXPECTED"))
        b.addWidget(self.date_eta)
        b.addStretch()

        layout.addWidget(bar)

        # ===============================
        # TABLE (PROFESSIONAL DENSITY)
        # ===============================
        self.batch_table = QTableWidget(0, 3)
        self.batch_table.setHorizontalHeaderLabels(
            ["PATIENT FULL NAME", "SAMPLE TYPE", ""]
        )

        # Column sizing
        self.batch_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.batch_table.setColumnWidth(1, 160)
        self.batch_table.setColumnWidth(2, 60)

        # 🔥 CRITICAL: ROW HEIGHT
        self.batch_table.verticalHeader().setDefaultSectionSize(44)

        # Remove ugly row numbers
        self.batch_table.verticalHeader().setVisible(False)

        # Slight breathing space
        self.batch_table.setShowGrid(True)
        self.batch_table.setAlternatingRowColors(True)

        layout.addWidget(self.batch_table)

        # ===============================
        # FOOTER
        # ===============================
        btn_add = QPushButton("+ ADD PATIENT")
        btn_add.setFixedHeight(36)
        btn_add.clicked.connect(self._add_row)

        btn_next = QPushButton("NEXT → MAP TESTS")
        btn_next.setObjectName("Primary")
        btn_next.setFixedHeight(40)
        btn_next.clicked.connect(self._to_step_3)

        foot = QHBoxLayout()
        foot.setContentsMargins(5, 5, 5, 5)
        foot.addWidget(btn_add)
        foot.addStretch()
        foot.addWidget(btn_next)

        layout.addLayout(foot)

    # ==========================================================
    # STEP 3 — MAPPING
    # ==========================================================

    def _step_3(self):
        layout = QVBoxLayout(self.tab_req)

        self.req_table = QTableWidget(0, 3)
        self.req_table.setHorizontalHeaderLabels(
            ["PATIENT", "ASSIGNED TESTS", ""]
        )
        self.req_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addWidget(self.req_table)

        btn = QPushButton("VALIDATE FINANCIALS →")
        btn.setObjectName("Primary")
        btn.clicked.connect(self._to_step_4)

        layout.addWidget(btn, alignment=Qt.AlignRight)

    # ==========================================================
    # STEP 4 — PAYMENT
    # ==========================================================

    def _step_4(self):
        layout = QVBoxLayout(self.tab_pay)
        layout.setContentsMargins(100, 20, 100, 20)

        card = QFrame()
        card.setObjectName("Panel")

        v = QVBoxLayout(card)

        self.lbl_gross = QLabel("₦0.00")
        self.lbl_net = QLabel("₦0.00")

        self.discount = QDoubleSpinBox()
        self.discount.setRange(0, 100)
        self.discount.setSuffix("% DISCOUNT")
        self.discount.valueChanged.connect(self._recompute)

        v.addWidget(QLabel("SUBTOTAL"))
        v.addWidget(self.lbl_gross)
        v.addWidget(self.discount)

        v.addSpacing(15)

        v.addWidget(QLabel("TOTAL PAYABLE"))
        v.addWidget(self.lbl_net)

        layout.addWidget(card)
        layout.addStretch()

        self.btn_submit = QPushButton("AUTHORIZE & DISPATCH")
        self.btn_submit.setObjectName("Primary")
        self.btn_submit.setFixedHeight(55)
        self.btn_submit.clicked.connect(self._submit)

        layout.addWidget(self.btn_submit)

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _label_input(self, label, widget):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setObjectName("FormLabel")

        v.addWidget(lbl)
        v.addWidget(widget)

        return w

    def _add_row(self):
        r = self.batch_table.rowCount()
        self.batch_table.insertRow(r)

        # -----------------------------
        # PATIENT NAME INPUT
        # -----------------------------
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter patient full name")
        name_input.setFixedHeight(34)

        self.batch_table.setCellWidget(r, 0, name_input)

        # -----------------------------
        # SAMPLE TYPE
        # -----------------------------
        combo = QComboBox()
        combo.addItems(["Blood", "Urine", "Swab", "Stool"])
        combo.setFixedHeight(34)

        self.batch_table.setCellWidget(r, 1, combo)

        # -----------------------------
        # REMOVE BUTTON
        # -----------------------------
        btn = QPushButton("✕")
        btn.setFixedSize(30, 30)
        btn.clicked.connect(lambda _, row=r: self.batch_table.removeRow(row))

        self.batch_table.setCellWidget(r, 2, btn)

    # ==========================================================
    # FLOW
    # ==========================================================

    def _to_step_2(self):
        if not self.ref_name.text():
            return

        try:
            url = f"{state.api_base_url}/api/referrer/create"
            headers = {"Authorization": f"Bearer {state.access_token}"}

            resp = requests.post(
                url,
                json={
                    "name": self.ref_name.text(),
                    "phone": self.ref_phone.text()
                },
                headers=headers
            )

            if resp.status_code == 200:
                self.active_referrer_id = int(resp.json()["id"])
                self.ref_code.setText(
                    f"REF-{QDateTime.currentDateTime().toString('yyMMdd-hhmmss')}"
                )

                self.tabs.setTabEnabled(1, True)
                self.tabs.setCurrentIndex(1)

                self.status_pill.setText("BATCH OPEN")

            else:
                QMessageBox.critical(self, "Error", resp.text)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _map_tests(self, row_idx):
        name = self.req_table.item(row_idx, 0).text()

        dlg = RequestTestDialog(
            PatientLite(0, "B", name, "", "M", "0", ""),
            self
        )

        if dlg.exec():
            tests = dlg.created_requests or []
            self.row_test_map[row_idx] = tests

            display = ", ".join([t.test_name for t in tests])
            self.req_table.setItem(row_idx, 1, QTableWidgetItem(display))

            self._recompute()

    def _recompute(self):
        self.current_gross = 0.0

        for tests in self.row_test_map.values():
            for t in tests:
                self.current_gross += float(getattr(t, "price", 0.0))

        self.current_net = self.current_gross * (1 - self.discount.value() / 100)

        self.lbl_gross.setText(f"₦{self.current_gross:,.2f}")
        self.lbl_net.setText(f"₦{self.current_net:,.2f}")

    def _to_step_3(self):
        self.req_table.setRowCount(0)

        for r in range(self.batch_table.rowCount()):
            name_widget = self.batch_table.cellWidget(r, 0)
            name = name_widget.text() or f"Patient {r+1}"

            self.req_table.insertRow(r)
            self.req_table.setItem(r, 0, QTableWidgetItem(name))

            btn = QPushButton("MAP")
            btn.clicked.connect(lambda _, i=r: self._map_tests(i))

            self.req_table.setCellWidget(r, 2, btn)

        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentIndex(2)

    def _to_step_4(self):
        self.tabs.setTabEnabled(3, True)
        self.tabs.setCurrentIndex(3)

    def _submit(self):
        QMessageBox.information(self, "Info", "Submit logic unchanged")