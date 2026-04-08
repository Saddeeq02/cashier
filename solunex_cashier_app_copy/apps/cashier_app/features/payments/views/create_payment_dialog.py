# -*- coding: utf-8 -*-
# apps/cashier_app/features/payments/views/create_payment_dialog.py
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QPushButton, QMessageBox, QCheckBox
)

from shared.uix.widgets.dialogs import SolunexDialog
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.payments.api import list_pending_test_requests, create_payment

from app.services.cashier_receipt_service import CashierReceiptService
from apps.cashier_app.app_state import state

BACKEND_DOWN_TEXT = "backend is busy or not reachable, try reconnect from settings and try again later"


@dataclass(frozen=True)
class PaymentLite:
    payment_id: str
    purpose: str
    amount: float
    method: str
    status: str
    created_at: str


class CreatePaymentDialog(SolunexDialog):
    def __init__(self, patient: PatientLite, parent=None):
        super().__init__("Create Payment", parent=parent, width=780, height=560)
        self.patient = patient
        self.created_payment: PaymentLite | None = None

        head = QLabel(f"{patient.patient_no} — {patient.full_name} ({patient.phone})")
        head.setObjectName("Muted")
        self.body_layout.addWidget(head)

        panel = QFrame()
        panel.setObjectName("Panel2")
        self.body_layout.addWidget(panel, 1)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        # --- Header with Select All ---
        header_row = QHBoxLayout()
        self.hint = QLabel("Select pending request(s) to pay for:")
        
        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.stateChanged.connect(self._toggle_select_all)
        
        header_row.addWidget(self.hint)
        header_row.addStretch()
        header_row.addWidget(self.select_all_cb)
        lay.addLayout(header_row)

        self.requests = QListWidget()
        # Connect signal for individual item toggles
        self.requests.itemChanged.connect(self._recompute_amount)
        lay.addWidget(self.requests, 1)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.amount = QLineEdit()
        self.amount.setPlaceholderText("0.00")
        self.amount.setReadOnly(True)
        self.method = QComboBox()
        self.method.addItems(["Cash", "Transfer", "POS", "USSD"])

        row.addWidget(self._field("Total Amount (₦)", self.amount), 1)
        row.addWidget(self._field("Payment Method", self.method), 1)
        lay.addLayout(row)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        self.btn_save = QPushButton("Save & Print Receipt")
        self.btn_save.setObjectName("Primary")
        self.btn_save.clicked.connect(self._save)
        actions.addWidget(self.btn_save)

        self.body_layout.addLayout(actions)

        # load from backend now
        self._load_pending_requests()

    def _field(self, label: str, widget):
        w = QFrame()
        w.setStyleSheet("background: transparent; border: none;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        lab = QLabel(label)
        lab.setObjectName("Muted")
        v.addWidget(lab)
        v.addWidget(widget)
        return w

    def _toggle_select_all(self, state_val: int):
        """Checks or unchecks all available requests."""
        self.requests.blockSignals(True)
        
        target_state = Qt.Checked if state_val == Qt.Checked.value else Qt.Unchecked
        
        for i in range(self.requests.count()):
            item = self.requests.item(i)
            # Only toggle items that have actual request data
            if item.data(Qt.UserRole):
                item.setCheckState(target_state)
        
        self.requests.blockSignals(False)
        self._recompute_amount()

    def _load_pending_requests(self) -> None:
        self.requests.clear()
        self.select_all_cb.setChecked(False)

        pid = int(getattr(self.patient, "id", 0) or 0)
        if pid <= 0:
            self._render_placeholder("Cannot load requests: patient id missing.")
            self.btn_save.setEnabled(False)
            self.select_all_cb.setEnabled(False)
            return

        try:
            reqs = list_pending_test_requests(pid) or []
            if not reqs:
                self._render_placeholder("No pending requests found for this patient.")
                self.btn_save.setEnabled(False)
                self.select_all_cb.setEnabled(False)
                return

            self.requests.blockSignals(True)
            for r in reqs:
                rid = r.get("id") or r.get("request_id") or r.get("uuid")
                test_name = r.get("test_name") or "Unknown Test"
                price = float(r.get("price") or 0)

                label = f"{test_name}  —  ₦{price:,.2f}"

                item = QListWidgetItem(label)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, {
                    "id": rid,
                    "test_name": test_name,
                    "price": price
                })
                self.requests.addItem(item)
            
            self.requests.blockSignals(False)
            self.btn_save.setEnabled(True)
            self.select_all_cb.setEnabled(True)

        except Exception:
            self._render_placeholder(BACKEND_DOWN_TEXT)
            self.btn_save.setEnabled(False)
            self.select_all_cb.setEnabled(False)

    def _render_placeholder(self, text: str) -> None:
        item = QListWidgetItem(text)
        item.setFlags(Qt.ItemIsEnabled)  # not selectable/checkable
        self.requests.addItem(item)

    def _recompute_amount(self):
        total = 0.0
        for i in range(self.requests.count()):
            item = self.requests.item(i)
            if item.checkState() == Qt.Checked:
                meta = item.data(Qt.UserRole) or {}
                total += float(meta.get("price") or 0)

        self.amount.setText(f"{total:.2f}")

    def _save(self) -> None:
        request_ids = []
        purpose_names = []
        selected_meta = []

        for i in range(self.requests.count()):
            item = self.requests.item(i)
            if item.checkState() != Qt.Checked:
                continue

            meta = item.data(Qt.UserRole) or {}
            rid = meta.get("id")
            if rid:
                request_ids.append(rid)
                purpose_names.append(str(meta.get("test_name") or "Test"))
                selected_meta.append({
                    "name": meta.get("test_name"),
                    "price": float(meta.get("price") or 0)
                })

        if not request_ids:
            QMessageBox.warning(self, "Selection Required", "Please select at least one item to pay for.")
            return

        try:
            amt_str = self.amount.text().strip()
            amt = float(amt_str) if amt_str else 0.0
            if amt <= 0:
                raise ValueError()
        except Exception:
            QMessageBox.warning(self, "Invalid Amount", "The total amount must be greater than zero.")
            return

        method = self.method.currentText().strip()
        pid = int(getattr(self.patient, "id", 0) or 0)

        payload = {
            "patient_id": pid,
            "amount": amt,
            "method": method,
            "request_ids": request_ids,
        }

        try:
            self.btn_save.setEnabled(False)
            res = create_payment(payload) or {}

            # Format Payment ID for UI display
            raw_id = res.get("payment_id") or res.get("id") or ""
            payment_id = f"PAY-{int(raw_id):06d}" if str(raw_id).isdigit() else str(raw_id or "PAY")

            self.created_payment = PaymentLite(
                payment_id=payment_id,
                purpose=", ".join(purpose_names),
                amount=float(res.get("amount") or amt),
                method=str(res.get("method") or method),
                status=str(res.get("status") or "completed"),
                created_at=str(res.get("created_at") or date.today().isoformat())[:10],
            )
            
            self._generate_receipt(selected_meta)
            self.accept()

        except Exception as e:
            self.btn_save.setEnabled(True)
            QMessageBox.critical(self, "Transaction Failed", f"Could not save payment: {str(e)}")

    def _generate_receipt(self, selected):
        try:
            # 1. Prepare data (Matching the Service keys exactly)
            receipt_data = {
                "patient_no": self.patient.patient_no,
                "patient_name": self.patient.full_name,
                "phone": self.patient.phone,
                "created_by": state.username,  # Ensure state.username is available
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tests": selected,  # List of {"name": "X", "price": 0.0}
            }

            # 2. Setup Folder Logic (FIX APPLIED HERE)
            # os.path.expanduser("~") safely gets the current Windows user's home directory (e.g., C:\Users\Rafawa)
            user_documents = os.path.join(os.path.expanduser("~"), "Documents")
            folder = os.path.join(user_documents, "IECashier_Receipts")
            
            if not os.path.exists(folder):
                os.makedirs(folder)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"REC_{receipt_data['patient_no']}_{timestamp}.pdf"
            path = os.path.abspath(os.path.join(folder, filename))

            # 3. Generate the PDF (Optimized for Thermal)
            CashierReceiptService.generate(
                receipt_data=receipt_data,
                output_path=path,
                paper_width="80mm" 
            )

            # 4. TRIGGER SILENT PRINT 
            print_success = CashierReceiptService.print_to_windows_printer(path)

            # 5. Fallback: If print fails or for preview, open the file
            if not print_success:
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        except Exception as e:
            QMessageBox.warning(self, "Receipt Error", f"Receipt generated but could not print: {str(e)}")
            print(f"Receipt generation/print failed: {e}")