# apps/cashier_app/features/auth/views/login_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

from ..vm import AuthVM

class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("I and E Cashier - Secure Login")
        self.setFixedSize(450, 550)  # More substantial, centered presence
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint) # Optional: Remove title bar for custom look
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 1. Main Background Layout (Dark overlay or empty space)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # 2. Login Card (The centered "Professional" look)
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        self.card.setStyleSheet("""
            QFrame#LoginCard {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLabel#Header {
                color: #2c3e50;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#SubHeader {
                color: #7f8c8d;
                font-size: 13px;
            }
            QLineEdit {
                border: 2px solid #ecf0f1;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                background-color: #f9f9f9;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QPushButton#LoginBtn {
                background-color: #364fc7;
                color: white;
                border-radius: 6px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton#LoginBtn:hover {
                background-color: #364fc7;
            }
            QPushButton#LoginBtn:pressed {
                background-color: #364fc7;
            }
            QPushButton#CloseBtn {
                border: none;
                color: #364fc7;
                font-size: 12px;
            }
            QPushButton#CloseBtn:hover {
                color: #364fc7;
            }
        """)

        # Shadow effect for the card
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        # Content
        title = QLabel("Welcome Back")
        title.setObjectName("Header")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Please enter your cashier credentials")
        subtitle.setObjectName("SubHeader")
        subtitle.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(20)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(50)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.returnPressed.connect(self._handle_login)

        self.login_btn = QPushButton("SIGN IN")
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self._handle_login)

        # Close button (since we removed frame)
        self.close_btn = QPushButton("Cancel")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_btn)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.close_btn, 0, Qt.AlignCenter)

        self.main_layout.addWidget(self.card)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation", "Please provide both credentials.")
            return

        self.login_btn.setText("Authenticating...")
        self.login_btn.setEnabled(False)

        try:
            AuthVM.login(username, password)
            self.accept()
        except Exception as e:
            self.login_btn.setText("SIGN IN")
            self.login_btn.setEnabled(True)
            QMessageBox.critical(self, "Access Denied", str(e))