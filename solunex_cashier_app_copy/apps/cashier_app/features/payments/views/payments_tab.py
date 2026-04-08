# -*- coding: utf-8 -*-
# apps/cashier_app/features/payments/views/payments_tab.py
from __future__ import annotations

import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog

from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.payments.views.create_payment_dialog import CreatePaymentDialog, PaymentLite
from apps.cashier_app.features.payments.views.force_push_dialog import ForcePushDialog
from apps.cashier_app.features.payments.api import list_patient_payments

# Add the imports needed for receipt generation
from app.services.cashier_receipt_service import CashierReceiptService
from apps.cashier_app.app_state import state

BACKEND_DOWN_TEXT = "backend is busy or not reachable, try reconnect from settings and try again later"


class PaymentsTab(QWidget):
    def __init__(self, patient: PatientLite):
        super().__init__()
        self.patient = patient
        self._history: list[PaymentLite] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        title = QLabel("Payments")
        title.setStyleSheet("font-size: 12pt; font-weight: 800;")
        h.addWidget(title)

        h.addStretch(1)

        btn_force = QPushButton("Force Push")
        btn_force.clicked.connect(self._force_push)
        h.addWidget(btn_force)

        # --- REPRINT BUTTON SETUP ---
        self.btn_reprint = QPushButton("Reprint Receipt")
        self.btn_reprint.setEnabled(False) # Disabled until a row is selected
        self.btn_reprint.clicked.connect(self._reprint_receipt)
        h.addWidget(self.btn_reprint)

        btn_pay = QPushButton("Create Payment")
        btn_pay.setObjectName("Primary")
        btn_pay.clicked.connect(self._create_payment)
        h.addWidget(btn_pay)

        root.addWidget(header)

        # Summary cards
        cards = QHBoxLayout()
        cards.setSpacing(10)

        self.card_payable = self._card("Total Payable", "—")
        self.card_paid = self._card("Total Paid", "—")
        self.card_due = self._card("Balance Due", "—")

        cards.addWidget(self.card_payable)
        cards.addWidget(self.card_paid)
        cards.addWidget(self.card_due)

        root.addLayout(cards)

        # History
        panel = QFrame()
        panel.setObjectName("Panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(14, 14, 14, 14)
        p.setSpacing(10)

        lab = QLabel("Payment History")
        lab.setStyleSheet("font-weight: 800;")
        p.addWidget(lab)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Payment ID", "Purpose", "Amount", "Method", "Status", "Created At"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        
        # Connect row selection to toggle the reprint button
        self.table.itemSelectionChanged.connect(self._on_table_selection)
        
        p.addWidget(self.table)

        root.addWidget(panel, 1)

        self.refresh()

    def _on_table_selection(self):
        """Enable reprint button only if a row is selected."""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_reprint.setEnabled(has_selection)

    def _reprint_receipt(self):
        """Gathers data from the selected row and regenerates the PDF."""
        row = self.table.currentRow()
        if row < 0: return
        
        item = self.table.item(row, 0)
        if not item: return
        
        pay: PaymentLite = item.data(Qt.UserRole)
        if not pay: return

        try:
            # 1. Prepare data mapping (Adapting history data to receipt format)
            receipt_data = {
                "patient_no": self.patient.patient_no,
                "patient_name": self.patient.full_name,
                "phone": self.patient.phone,
                "created_by": getattr(state, "username", "System"), 
                "created_at": pay.created_at,
                "tests": [{"name": pay.purpose, "price": pay.amount}], 
            }

            # 2. Setup Folder Logic
            user_documents = os.path.join(os.path.expanduser("~"), "Documents")
            folder = os.path.join(user_documents, "IECashier_Receipts")
            if not os.path.exists(folder):
                os.makedirs(folder)

            # Clean the Payment ID for the filename to prevent OS errors
            safe_pay_id = "".join(c for c in pay.payment_id if c.isalnum() or c in "-_")
            filename = f"REC_{receipt_data['patient_no']}_{safe_pay_id}_REPRINT.pdf"
            path = os.path.abspath(os.path.join(folder, filename))

            # 3. Generate and Print
            CashierReceiptService.generate(
                receipt_data=receipt_data,
                output_path=path,
                paper_width="80mm"
            )

            print_success = CashierReceiptService.print_to_windows_printer(path)

            if not print_success:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        except Exception as e:
            QMessageBox.warning(self, "Reprint Error", f"Could not reprint receipt: {str(e)}")
            print(f"Reprint failed: {e}")

    def refresh(self) -> None:
        pid = int(getattr(self.patient, "id", 0) or 0)
        if pid <= 0:
            self._render_placeholder("Cannot load payments: patient id missing.")
            self._set_totals(None, None, None)
            return

        try:
            rows = list_patient_payments(pid) or []
            self._history = []

            total_paid = 0.0
            for r in rows:
                payment_id = str(r.get("payment_id") or r.get("id") or "")
                amount = float(r.get("amount") or 0.0)
                method = str(r.get("method") or "")
                status = str(r.get("status") or "completed")
                created_at = str(r.get("created_at") or "")[:10]

                # purpose can be free text or derived from request/test
                purpose = str(r.get("purpose") or "")
                if not purpose:
                    test_name = (r.get("test_name") or r.get("request_test_name") or "")
                    req_code = (r.get("request_code") or r.get("request_no") or r.get("request_id") or "")
                    purpose = f"{test_name} ({req_code})" if test_name and req_code else (test_name or "Payment")

                self._history.append(PaymentLite(
                    payment_id=payment_id,
                    purpose=purpose,
                    amount=amount,
                    method=method,
                    status=status,
                    created_at=created_at,
                ))
                total_paid += amount

            self._render()

            # We can only compute paid reliably here without extra endpoints.
            # Payable/Due can be added once backend provides totals per patient.
            self._set_totals("—", f"₦ {total_paid:,.0f}", "—")

        except Exception:
            self._render_placeholder(BACKEND_DOWN_TEXT)
            self._set_totals("—", "—", "—")

    def _set_totals(self, payable, paid, due):
        self._set_card_value(self.card_payable, str(payable))
        self._set_card_value(self.card_paid, str(paid))
        self._set_card_value(self.card_due, str(due))

    def _set_card_value(self, card: QFrame, value: str):
        # card layout: [Muted title, big value]
        lay = card.layout()
        if lay and lay.count() >= 2:
            v = lay.itemAt(1).widget()
            if isinstance(v, QLabel):
                v.setText(value)

    def _card(self, title: str, value: str) -> QWidget:
        w = QFrame()
        w.setObjectName("Panel2")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        t = QLabel(title)
        t.setObjectName("Muted")
        lay.addWidget(t)

        v = QLabel(value)
        v.setStyleSheet("font-size: 12pt; font-weight: 900;")
        lay.addWidget(v)
        return w

    def _render_placeholder(self, message: str) -> None:
        self.table.setRowCount(0)
        self.table.insertRow(0)
        for col in range(self.table.columnCount()):
            item = QTableWidgetItem("" if col != 1 else message)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(0, col, item)

    def _render(self) -> None:
        self.table.setRowCount(0)
        for pay in self._history:
            r = self.table.rowCount()
            self.table.insertRow(r)

            def add(c: int, val: str):
                it = QTableWidgetItem(val)
                it.setData(Qt.UserRole, pay)
                self.table.setItem(r, c, it)

            add(0, pay.payment_id)
            add(1, pay.purpose)
            add(2, f"{pay.amount:,.2f}")
            add(3, pay.method)
            add(4, pay.status)
            add(5, pay.created_at)

    def _create_payment(self) -> None:
        dlg = CreatePaymentDialog(patient=self.patient, parent=self)
        if dlg.exec() == QDialog.Accepted:
            # Always refresh from backend (no local append)
            self.refresh()

    def _force_push(self) -> None:
        dlg = ForcePushDialog(patient=self.patient, parent=self)
        dlg.exec()