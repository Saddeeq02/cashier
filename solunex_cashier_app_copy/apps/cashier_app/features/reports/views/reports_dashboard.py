# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import date, timedelta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem
)

from apps.cashier_app.features.reports.models import ReportRow
from apps.cashier_app.features.reports.views.report_export_dialog import ReportExportDialog
from shared.api.client import client, APIError

class ReportsDashboardView(QWidget):
    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)
        
        # Header / controls
        header = QFrame()
        header.setObjectName("Panel2")
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(10)

        title = QLabel("Reports")
        title.setStyleSheet("font-size: 13pt; font-weight: 800;")
        h.addWidget(title)

        hint = QLabel("Generated from per-test transactions (requests, payments, releases).")
        hint.setObjectName("Muted")
        h.addWidget(hint)

        h.addStretch(1)

        self.period = QComboBox()
        self.period.addItems(["Daily", "Weekly", "Monthly"])
        h.addWidget(self._field_inline("Period", self.period))

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)

        today = date.today()
        self.date_to.setDate(today)
        self.date_from.setDate(today - timedelta(days=7))

        h.addWidget(self._field_inline("From", self.date_from))
        h.addWidget(self._field_inline("To", self.date_to))

        btn_generate = QPushButton("Generate")
        btn_generate.setObjectName("Primary")
        btn_generate.clicked.connect(self._generate_ui_only)
        h.addWidget(btn_generate)

        btn_export = QPushButton("Export")
        btn_export.clicked.connect(self._export_selected)
        h.addWidget(btn_export)

        root.addWidget(header)

        # Summary cards
        cards = QHBoxLayout()
        cards.setSpacing(10)
        self.card_tests = self._card("Total Tests", "0")
        self.card_rev = self._card("Total Revenue", "₦ 0")
        self.card_pending = self._card("Pending Payments", "₦ 0")
        cards.addWidget(self.card_tests)
        cards.addWidget(self.card_rev)
        cards.addWidget(self.card_pending)
        root.addLayout(cards)

        # Table
        panel = QFrame()
        panel.setObjectName("Panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(14, 14, 14, 14)
        p.setSpacing(10)

        lab = QLabel("Generated Reports")
        lab.setStyleSheet("font-weight: 800;")
        p.addWidget(lab)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Report ID", "Period", "From", "To",
            "Total Tests", "Revenue", "Pending", "Created At"
        ])
        self.table.itemDoubleClicked.connect(self._on_row_double_clicked)
        self.table.itemDoubleClicked.connect(self._export_selected)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        p.addWidget(self.table)

        root.addWidget(panel, 1)

        # UI-only history
        self._history: list[ReportRow] = []
        self._render()

    def refresh(self) -> None:
        # Step R1: UI-only
        self._render()


    def _generate_ui_only(self) -> None:
        d1 = self.date_from.date().toString("yyyy-MM-dd")
        d2 = self.date_to.date().toString("yyyy-MM-dd")

        self._set_loading(True)

        try:
            res = client.get("/api/reports/generate", params={
                "date_from": d1,
                "date_to": d2
            })
            total_tests = res["total_tests"]
            revenue = res["total_revenue"]
            pending = res["pending"]

        except APIError as e:
            print("Report fetch failed:", e)
            self._set_loading(False)
            return

        rid = f"REP-{1000 + len(self._history) + 1}"
        created_at = date.today().isoformat()

        row = ReportRow(
            report_id=rid,
            period=self.period.currentText().lower(),
            date_from=d1,
            date_to=d2,
            total_tests=total_tests,
            total_revenue=revenue,
            pending_payments=pending,
            created_at=created_at
        )

        self._history.insert(0, row)

        self._render()
        self._set_summary(total_tests, revenue, pending)
        self._set_loading(False)

    def _set_loading(self, state: bool):
        btn = self.findChild(QPushButton, "")
        # better: store reference if needed

        for w in self.findChildren(QPushButton):
            if w.text().startswith("Generate"):
                w.setEnabled(not state)
                w.setText("Generating..." if state else "Generate")

    def _export_selected(self) -> None:
        row = self._selected()
        if not row:
            return
        dlg = ReportExportDialog(f"Export {row.report_id}", parent=self)
        dlg.exec()

    def _selected(self) -> ReportRow | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return items[0].data(Qt.UserRole)

    def _render(self) -> None:
        self.table.setRowCount(0)
        for r in self._history:
            i = self.table.rowCount()
            self.table.insertRow(i)

            def add(col: int, val: str):
                it = QTableWidgetItem(val)
                it.setData(Qt.UserRole, r)
                self.table.setItem(i, col, it)

            add(0, r.report_id)
            add(1, r.period)
            add(2, r.date_from)
            add(3, r.date_to)
            add(4, str(r.total_tests))
            add(5, f"₦ {r.total_revenue:,.0f}")
            add(6, f"₦ {r.pending_payments:,.0f}")
            add(7, r.created_at)

        if not self._history:
            self.table.setRowCount(1)
            it = QTableWidgetItem("No reports generated yet")
            it.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(0, 0, 1, self.table.columnCount())
            self.table.setItem(0, 0, it)

    def _set_summary(self, tests: int, revenue: float, pending: float) -> None:
        self._set_card_value(self.card_tests, str(tests))
        self._set_card_value(self.card_rev, f"₦ {revenue:,.0f}")
        self._set_card_value(self.card_pending, f"₦ {pending:,.0f}")

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

    def _set_card_value(self, card: QWidget, value: str) -> None:
        # card layout: [title, value]
        lay = card.layout()
        if lay and lay.count() >= 2:
            lab = lay.itemAt(1).widget()
            if isinstance(lab, QLabel):
                lab.setText(value)

    def _field_inline(self, label: str, widget: QWidget) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        lab = QLabel(label)
        lab.setObjectName("Muted")
        lay.addWidget(lab)
        lay.addWidget(widget)
        return w
    

    def _on_row_double_clicked(self, item):
        row = item.row()
        r = self.table.item(row, 0).data(Qt.UserRole)
        if not r:
            return

        dlg = ReportExportDialog(f"Export {r.report_id}", parent=self)
        dlg.exec()