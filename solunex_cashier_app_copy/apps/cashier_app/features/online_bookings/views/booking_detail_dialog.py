from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)


class BookingDetailDialog(QDialog):

    def __init__(self, booking, patients, vm):
        super().__init__()

        self.booking = booking
        self.patients = patients
        self.vm = vm

        self.setWindowTitle(f"Booking {booking['booking_code']}")
        self.resize(520, 360)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        header = QVBoxLayout()

        header.addWidget(QLabel(f"Referrer: {booking['referrer_name']}"))
        header.addWidget(QLabel(f"Status: {booking['status']}"))

        layout.addLayout(header)

        # --------------------------------------------------
        # PATIENT TABLE
        # --------------------------------------------------

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Patient", "Tests"])

        self.table.setRowCount(len(patients))

        for row, p in enumerate(patients):

            self.table.setItem(
                row, 0, QTableWidgetItem(p["patient_name"])
            )

            tests = ", ".join(p["tests"])

            self.table.setItem(
                row, 1, QTableWidgetItem(tests)
            )

        layout.addWidget(self.table)

        # --------------------------------------------------
        # ACTION BAR
        # --------------------------------------------------

        action_bar = QHBoxLayout()

        action_bar.addStretch()

        self.convert_btn = QPushButton("Convert to Request")
        self.convert_btn.clicked.connect(self.convert_patient)
        action_bar.addWidget(self.convert_btn)

        layout.addLayout(action_bar)


    def convert_patient(self):

        row = self.table.currentRow()

        if row < 0:
            return

        patient = self.patients[row]

        try:

            self.convert_btn.setEnabled(False)
            self.convert_btn.setText("Processing...")

            self.vm.convert(
                self.booking["id"],
                patient["patient_name"]
            )

        except Exception as e:

            msg = str(e)

            if "Nothing to convert" in msg:
                print("Already converted")

            else:
                print("Conversion failed:", msg)

            return

        self.accept()