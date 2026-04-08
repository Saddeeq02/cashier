# -*- coding: utf-8 -*-
"""
Runtime application state for Solunex Cashier.
JWT-based session state + UI preferences.
"""

class AppState:
    def __init__(self):
        # ----------------------------------
        # Backend Configuration
        # ----------------------------------
        self.api_base_url: str = "https://api.iandelaboratory.com"
        self.api_timeout: int = 15

        # ----------------------------------
        # Authenticated Session (LOCKED)
        # ----------------------------------
        self.access_token: str | None = None
        self.user_id: int | None = None
        self.username: str | None = None
        self.role: str | None = None
        self.branch_id: int | None = None

        # ----------------------------------
        # UI / Operator Preferences (NEW)
        # ----------------------------------
        self.operator_display_name: str | None = None
        self.operator_role: str = "cashier"

        # ----------------------------------
        # Branding (Receipt / Reports)
        # ----------------------------------
        self.facility_name: str = ""
        self.facility_phone: str = ""
        self.facility_address: str = ""
        self.footer_note: str = ""
        self.printer_name: str = ""

    # ----------------------------------
    # Session Management
    # ----------------------------------
    def set_session(self, token: str, user: dict):
        self.access_token = token
        self.user_id = user.get("id")
        self.username = user.get("username")
        self.role = user.get("role")
        self.branch_id = user.get("branch_id")

    def clear_session(self):
        self.access_token = None
        self.user_id = None
        self.username = None
        self.role = None
        self.branch_id = None

    def is_authenticated(self) -> bool:
        return self.access_token is not None

    # ----------------------------------
    # Derived UI Identity
    # ----------------------------------
    @property
    def operator_name(self) -> str:
        """
        Priority:
        1. Custom display name (Settings)
        2. Username (auth)
        """
        return self.operator_display_name or self.username or "Operator"


# singleton
state = AppState()