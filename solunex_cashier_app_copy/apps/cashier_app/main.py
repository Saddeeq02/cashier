# -*- coding: utf-8 -*-
#app
from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication, QDialog

from shared.uix.theme import apply_solunex_theme
from shared.uix.layout.shell import ShellWindow

from apps.cashier_app.features.auth.views.login_dialog import LoginDialog


def main() -> int:
    app = QApplication(sys.argv)
    apply_solunex_theme(app)

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