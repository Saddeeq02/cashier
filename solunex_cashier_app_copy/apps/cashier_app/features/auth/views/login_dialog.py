# apps/cashier_app/features/auth/views/login_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

from ..vm import AuthVM
from shared.utils.config_manager import ConfigManager
from apps.cashier_app.app_state import state

class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("I and E Cashier - Secure Login")
        self.setFixedSize(450, 650)  # Increased height for Server IP field
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ... [UI Styles remain same] ...
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setStyleSheet("""
            QFrame#LoginCard { background-color: #ffffff; border-radius: 12px; }
            QLabel#Header { color: #2c3e50; font-size: 24px; font-weight: 800; }
            QLabel#SubHeader { color: #7f8c8d; font-size: 13px; }
            QLineEdit { border: 2px solid #ecf0f1; border-radius: 6px; padding: 10px; font-size: 14px; background-color: #f9f9f9; color: #2c3e50; }
            QLineEdit:focus { border: 2px solid #3498db; background-color: #ffffff; }
            QPushButton#LoginBtn { background-color: #364fc7; color: white; border-radius: 6px; padding: 12px; font-size: 15px; font-weight: bold; }
            QPushButton#VerifyBtn { background-color: #f1f3f5; color: #495057; border-radius: 6px; padding: 8px; font-size: 12px; font-weight: bold; border: 1px solid #dee2e6; }
            QPushButton#VerifyBtn:hover { background-color: #e9ecef; }
            QPushButton#CloseBtn { border: none; color: #364fc7; font-size: 12px; }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(12)

        title = QLabel("Welcome Back")
        title.setObjectName("Header")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Please enter your cashier credentials")
        subtitle.setObjectName("SubHeader")
        subtitle.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(15)

        # --- SERVER IP SECTION ---
        server_label = QLabel("Server Configuration (LAN/Hub)")
        server_label.setStyleSheet("color: #adb5bd; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        card_layout.addWidget(server_label)

        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("e.g. 192.168.1.15 or localhost:8000")
        self.server_input.setText(ConfigManager.get_server_ip())
        card_layout.addWidget(self.server_input)

        self.verify_btn = QPushButton("Verify Hub Connection")
        self.verify_btn.setObjectName("VerifyBtn")
        self.verify_btn.setCursor(Qt.PointingHandCursor)
        self.verify_btn.clicked.connect(self._handle_verify_connection)
        card_layout.addWidget(self.verify_btn)

        card_layout.addSpacing(10)

        # --- AUTH SECTION ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(45)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self._handle_login)

        self.login_btn = QPushButton("SIGN IN")
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self._handle_login)

        self.close_btn = QPushButton("Cancel")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_btn)
        card_layout.addSpacing(5)
        card_layout.addWidget(self.close_btn, 0, Qt.AlignCenter)

        self.main_layout.addWidget(self.card)

    def _handle_verify_connection(self):
        server_url = self.server_input.text().strip()
        if not server_url:
            QMessageBox.warning(self, "Error", "Please enter a Server IP or URL.")
            return

        self.verify_btn.setEnabled(False)
        self.verify_btn.setText("Verifying Hub...")

        try:
            state.set_api_base_url(server_url)
            from shared.api.client import client
            # Simple health check if available or just URL test
            health = client.get("/health", silent=True)
            if health and health.get("status") == "ok":
                QMessageBox.information(self, "Success", f"Successfully connected to Hub at {server_url}")
            else:
                QMessageBox.warning(self, "Warning", "Hub reached but health check failed. Check if port 8000 is open.")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", f"Could not reach Hub: {e}")
        finally:
            self.verify_btn.setEnabled(True)
            self.verify_btn.setText("Verify Hub Connection")

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        server_url = self.server_input.text().strip()

        if not server_url:
            QMessageBox.warning(self, "Error", "Server IP is required for offline setup.")
            return

        if not username or not password:
            QMessageBox.warning(self, "Validation", "Please provide both credentials.")
            return

        self.login_btn.setText("Connecting...")
        self.login_btn.setEnabled(False)

        try:
            # ✅ Apply Server IP and Save for next time
            state.set_api_base_url(server_url)
            ConfigManager.save_config({"server_ip": server_url})
            
            AuthVM.login(username, password)
            self.accept()
        except Exception as e:
            self.login_btn.setText("SIGN IN")
            self.login_btn.setEnabled(True)
            QMessageBox.critical(self, "Access Denied", str(e))