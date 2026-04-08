from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView
)
import requests
from apps.cashier_app.app_state import state


class ReferrerDashboardDialog(QDialog):
    def __init__(self, referrer_id, name, parent=None):
        super().__init__(parent)
        self.referrer_id = referrer_id
        self.setWindowTitle(f"{name} - Dashboard")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        self.lbl_total = QLabel("Total Credit: ₦0.00")
        layout.addWidget(self.lbl_total)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "BOOKING CODE", "PATIENTS", "AMOUNT", "DATE"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.table.cellDoubleClicked.connect(self._open_booking)

        layout.addWidget(self.table)

        self._load()

    def _load(self):
        url = f"{state.api_base_url}/api/referrer/dashboard?referrer_id={self.referrer_id}"
        headers = {"Authorization": f"Bearer {state.access_token}"}

        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            return

        data = resp.json()

        self.lbl_total.setText(f"Total Credit: ₦{data['total_credit']:,.2f}")

        self.table.setRowCount(0)

        for r, b in enumerate(data["bookings"]):
            self.table.insertRow(r)

            self.table.setItem(r, 0, QTableWidgetItem(b["booking_code"]))
            self.table.setItem(r, 1, QTableWidgetItem(str(b["patients_count"])))
            self.table.setItem(r, 2, QTableWidgetItem(f"₦{b['booking_total']:,.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(str(b["created_at"])))

    def _open_booking(self, row, col):
        code = self.table.item(row, 0).text()

        dlg = BookingDetailsDialog(self.referrer_id, code, self)
        dlg.exec()





class BookingDetailsDialog(QDialog):
    def __init__(self, referrer_id, booking_code, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Booking {booking_code}")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "PATIENT", "PHONE", "AMOUNT", "DATE"
        ])

        layout.addWidget(self.table)

        url = f"{state.api_base_url}/api/referrer/booking/{booking_code}?referrer_id={referrer_id}"
        headers = {"Authorization": f"Bearer {state.access_token}"}

        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            return

        data = resp.json()

        for r, p in enumerate(data):
            self.table.insertRow(r)

            self.table.setItem(r, 0, QTableWidgetItem(p["full_name"]))
            self.table.setItem(r, 1, QTableWidgetItem(p["phone"]))
            self.table.setItem(r, 2, QTableWidgetItem(f"₦{p['amount']:,.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(str(p["created_at"])))