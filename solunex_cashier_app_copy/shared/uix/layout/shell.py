# -*- coding: utf-8 -*-
# shared/uix/layout/shell.py
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QFrame, QScrollArea,
)

from shared.uix.layout.sidebar import Sidebar
from shared.uix.layout.topbar import Topbar

# Patient Feature Imports
from apps.cashier_app.features.patients.views.patients_list import PatientsListView
from apps.cashier_app.features.patients.views.patient_profile import (
    PatientProfileView,
    PatientLite,
)
from apps.cashier_app.features.reports.views.reports_dashboard import (
    ReportsDashboardView,
)
from apps.cashier_app.features.online_bookings.views.online_bookings_tab import (
    OnlineBookingsTab,
)
from apps.cashier_app.features.settings.views.settings_view import SettingsView

# --- THE FIX: IMPORT THE MAIN VIEW (Entry + Directory) ---
from apps.cashier_app.features.referrals.views.referral_wizard import ReferralWizardView

class ShellWindow(QMainWindow):
    def __init__(self, app_role: str):
        super().__init__()
        self.setWindowTitle("I and E Cashier")
        self.resize(1280, 760)

        # ROOT CONTAINER
        root = QWidget()
        self.setCentralWidget(root)

        outer = QHBoxLayout(root)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(20)

        # SIDEBAR
        self.sidebar = Sidebar(
            items=[
                ("Patients", "patients"),
                ("Referrals", "referrals"), 
                ("Online Bookings", "online_bookings"),
                ("Reports", "reports"),
                ("Settings", "settings"),
                ("Logout", "logout"),
            ]
        )
        self.sidebar.setFixedWidth(230)
        self.sidebar.nav_clicked.connect(self._on_nav)
        outer.addWidget(self.sidebar)

        # MAIN PANEL
        main_panel = QFrame()
        main_panel.setObjectName("Panel")
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        outer.addWidget(main_panel, 1)

        # TOPBAR
        self.topbar = Topbar(app_name="I and E", role=app_role)
        self.topbar.refresh_clicked.connect(self._on_refresh)
        main_layout.addWidget(self.topbar)

        # SCROLLABLE CONTENT AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        self.scroll.setWidget(content_frame)
        main_layout.addWidget(self.scroll, 1)

        # CENTERED MAX-WIDTH CONTAINER
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignTop)
        center_layout.setContentsMargins(40, 32, 40, 40)
        center_layout.setSpacing(24)
        content_layout.addWidget(center_container, 0, Qt.AlignHCenter)
        center_container.setMaximumWidth(1250)

        # STACKED PAGES
        self.pages = QStackedWidget()
        center_layout.addWidget(self.pages)

        self.page_index: dict[str, int] = {}

        def add_page(key: str, widget: QWidget):
            self.page_index[key] = self.pages.count()
            self.pages.addWidget(widget)

        # PATIENTS SECTION (OWN STACK)
        self.patients_stack = QStackedWidget()
        self.patients_list = PatientsListView()
        self.patients_list.open_patient.connect(self._open_patient_profile)
        self.patients_stack.addWidget(self.patients_list)
        self.patients_profile: PatientProfileView | None = None

        # REGISTER PAGES
        add_page("patients", self.patients_stack)
        
        # --- REGISTERING THE FULL REFERRAL SUITE ---
        add_page("referrals", ReferralWizardView()) 
        
        add_page("online_bookings", OnlineBookingsTab())
        add_page("reports", ReportsDashboardView())
        add_page("settings", SettingsView())

        # DEFAULT PAGE
        self.sidebar.set_active("patients")
        self.pages.setCurrentIndex(self.page_index["patients"])

    # NAVIGATION
    def _on_nav(self, key: str) -> None:
        if key == "logout":
            self.close()
            return

        idx = self.page_index.get(key)
        if idx is not None:
            self.pages.setCurrentIndex(idx)
            self.sidebar.set_active(key)

    # PATIENT PROFILE NAVIGATION
    def _open_patient_profile(self, patient: PatientLite) -> None:
        if self.patients_profile is not None:
            w = self.patients_profile
            self.patients_stack.removeWidget(w)
            w.deleteLater()
            self.patients_profile = None

        self.patients_profile = PatientProfileView(patient)
        self.patients_profile.back_requested.connect(self._back_to_patients_list)

        self.patients_stack.addWidget(self.patients_profile)
        self.patients_stack.setCurrentWidget(self.patients_profile)

    def _back_to_patients_list(self) -> None:
        self.patients_stack.setCurrentWidget(self.patients_list)

    # REFRESH HANDLING
    def _on_refresh(self) -> None:
        w = self.pages.currentWidget()
        if hasattr(w, "refresh") and callable(getattr(w, "refresh")):
            w.refresh()

        if w is self.patients_stack:
            inner = self.patients_stack.currentWidget()
            if hasattr(inner, "refresh") and callable(getattr(inner, "refresh")):
                inner.refresh()