from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from shared.uix.widgets.dialogs import SolunexDialog
from apps.cashier_app.features.patients.models import PatientLite
from apps.cashier_app.features.results.results_api import get_result


class ReprintResultDialog(SolunexDialog):
    def __init__(self, patient: PatientLite, result_id: str, result_title: str, parent=None):
        super().__init__("Reprint Result", parent=parent, width=760, height=520)

        self.result_id = result_id  # ✅ FIXED

        head = QLabel(f"{patient.patient_no} — {patient.full_name} ({patient.phone})")
        head.setObjectName("Muted")
        self.body_layout.addWidget(head)

        self.panel = QFrame()
        self.panel.setObjectName("Panel2")
        self.body_layout.addWidget(self.panel, 1)

        lay = QVBoxLayout(self.panel)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        title = QLabel(result_title)
        title.setStyleSheet("font-size: 12pt; font-weight: 900;")
        lay.addWidget(title)

        hint = QLabel("Result will be fetched and re-rendered before printing.")
        hint.setObjectName("Muted")
        lay.addWidget(hint)

        lay.addStretch(1)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        actions.addWidget(btn_close)

        btn_print = QPushButton("Reprint")
        btn_print.setObjectName("Primary")
        btn_print.clicked.connect(self._handle_print)
        actions.addWidget(btn_print)

        self.body_layout.addLayout(actions)

    # ✅ CORRECT LOCATION
    def _handle_print(self):
        try:
            data = get_result(self.result_id)

            if data.get("status") != "released":
                QMessageBox.warning(self, "Blocked", "Only released results can be reprinted.")
                return

            snapshot = data.get("template_snapshot")
            values = data.get("values")

            if not snapshot or not values:
                QMessageBox.critical(self, "Error", "Result data incomplete.")
                return

            # 🔁 UIX RENDER (plug your renderer here)
            self._render_result(snapshot, values)

            # 🖨️ PRINT
            self._print_result(snapshot, values)

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Reprint Failed", str(e))