from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from ..vm import OnlineBookingsVM
from .booking_detail_dialog import BookingDetailDialog
from PySide6.QtWidgets import QAbstractItemView


class OnlineBookingsTab(QWidget):

    def __init__(self):
        super().__init__()

        self.vm = OnlineBookingsVM()

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        # store bookings list
        self.bookings = []

        # connect double-click event
        self.table.cellDoubleClicked.connect(self._open_booking)

        self.load_data()

    def load_data(self):

        # fetch latest bookings from server
        self.bookings = self.vm.load()

        # reset table structure
        self.table.clear()
        self.table.setColumnCount(3)
        self.table.setRowCount(len(self.bookings))

        self.table.setHorizontalHeaderLabels(
            ["Booking Code", "Referrer", "Status"]
        )

        # table behavior (professional UI)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        for row, b in enumerate(self.bookings):

            self.table.setItem(row, 0, QTableWidgetItem(b["booking_code"]))
            self.table.setItem(row, 1, QTableWidgetItem(b["referrer_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(b["status"]))

        # adjust column sizing
        self.table.resizeColumnsToContents()

    def _open_booking(self, row, column):

        booking = self.bookings[row]

        booking_id = booking["id"]
        booking_code = booking["booking_code"]

        print("Opening booking:", booking_code)

        # fetch patients inside this booking
        patients = self.vm.get_patients(booking_id)

        dlg = BookingDetailDialog(booking, patients, self.vm)
        if dlg.exec():
            # dialog accepted → conversion likely happened
            self.load_data()