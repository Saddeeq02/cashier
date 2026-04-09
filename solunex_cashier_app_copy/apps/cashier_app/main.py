# -*- coding: utf-8 -*-
#app
from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication, QDialog

from shared.uix.theme import apply_solunex_theme
from shared.uix.layout.shell import ShellWindow
from shared.utils.config_manager import ConfigManager

from apps.cashier_app.features.auth.views.login_dialog import LoginDialog
from apps.cashier_app.app_state import state


def main() -> int:
    app = QApplication(sys.argv)
    apply_solunex_theme(app)

    # ----------------------------------
    # RUNTIME LAN CONFIG
    # ----------------------------------
    server_ip = ConfigManager.get_server_ip()
    state.set_api_base_url(server_ip)

    # ----------------------------------
    # FORCE LOGIN FIRST
    # ----------------------------------
    login = LoginDialog()

    if login.exec() != QDialog.Accepted:
        return 0

    # ----------------------------------
    # Launch Main Shell After Auth
    # ----------------------------------
    w = ShellWindow(app_role="cashier")
    w.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())