"""PyQt6 dialog used as the login screen for the PoS desktop client."""
from __future__ import annotations

from typing import Optional, Protocol

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .auth_service import AuthError, AuthResult


class AuthProvider(Protocol):
    """Protocol that any authentication provider must follow."""

    def authenticate(self, username: str, password: str) -> AuthResult:
        ...


class LoginWindow(QDialog):
    """Login dialog that validates credentials against ``AuthService``."""

    authenticated = pyqtSignal(dict)

    def __init__(self, auth_service: AuthProvider, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._auth_service: AuthProvider = auth_service

        self.setWindowTitle("Vivero PoS - Iniciar sesión")
        self.setModal(True)
        self.setFixedWidth(360)
        self._last_auth_result: Optional[AuthResult] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QLabel("Ingresá con tu usuario del sistema")
        header.setObjectName("loginHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setWordWrap(True)
        layout.addWidget(header)

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Usuario")
        self._username_input.setClearButtonEnabled(True)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Contraseña")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form.addWidget(QLabel("Usuario"), 0, 0)
        form.addWidget(self._username_input, 0, 1)
        form.addWidget(QLabel("Contraseña"), 1, 0)
        form.addWidget(self._password_input, 1, 1)

        layout.addLayout(form)

        self._message_label = QLabel("")
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet("color: #c0392b;")
        self._message_label.setVisible(False)
        layout.addWidget(self._message_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        self._login_button = QPushButton("Ingresar")
        self._login_button.clicked.connect(self._handle_login)
        btn_layout.addWidget(self._login_button)

        layout.addLayout(btn_layout)

        self._username_input.returnPressed.connect(self._focus_password)
        self._password_input.returnPressed.connect(self._handle_login)

    def _focus_password(self) -> None:
        self._password_input.setFocus()

    def _set_error(self, message: str) -> None:
        self._message_label.setText(message)
        self._message_label.setVisible(bool(message))

    def _clear_error(self) -> None:
        self._set_error("")

    def _handle_login(self) -> None:
        self._clear_error()
        username = self._username_input.text()
        password = self._password_input.text()

        try:
            result: AuthResult = self._auth_service.authenticate(username, password)
        except AuthError as exc:
            self._set_error(str(exc))
            return

        if not result.success:
            self._set_error(result.message)
            self._password_input.selectAll()
            self._password_input.setFocus()
            return

        self._message_label.setStyleSheet("color: #27ae60;")
        self._set_error(result.message)
        self.authenticated.emit(result.user or {})
        QMessageBox.information(
            self,
            "Sesión iniciada",
            f"Bienvenido/a {result.user['username']}!",
        )
        self._last_auth_result = result
        self.accept()

    @staticmethod
    def prompt(auth_service: AuthProvider) -> Optional[dict]:
        """Helper to show the dialog and return the authenticated user."""

        dialog = LoginWindow(auth_service)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog._last_auth_result:
            return dialog._last_auth_result.user
        return None

    @property
    def last_auth_result(self) -> Optional[AuthResult]:
        """Expose the last positive authentication result."""

        return self._last_auth_result
