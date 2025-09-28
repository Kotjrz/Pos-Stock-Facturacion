"""Entry point for the PyQt6 PoS desktop client."""
from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
    QDialog,
    QMessageBox,
)

from .auth_service import AuthError, AuthService
from .login_window import AuthProvider, LoginWindow
from .db_connection_dialog import DBConnectionDialog


def request_database_connection(default_conninfo: str = "") -> Optional[AuthProvider]:
    """Shows the DB dialog until the connection is valid or the user cancels."""

    while True:
        conninfo = DBConnectionDialog.prompt(default_conninfo)
        if conninfo is None:
            return None
        try:
            return AuthService(conninfo)
        except AuthError as exc:
            QMessageBox.critical(
                None,
                "Error de conexión",
                f"No se pudo inicializar la conexión: {exc}",
            )
            default_conninfo = conninfo  # Keep last attempt for convenience


class MainWindow(QWidget):
    """Placeholder main window shown after successful login."""

    def __init__(self, user: dict):
        super().__init__()
        self.setWindowTitle("Vivero PoS")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome = QLabel(f"Bienvenido/a {user['username']} ({user.get('rol', '-')})")
        welcome.setObjectName("welcomeLabel")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(welcome)

        info = QLabel("Esta es la pantalla principal del PoS. Aquí irá el módulo de ventas.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)


def main() -> int:
    app = QApplication(sys.argv)

    auth_service = request_database_connection(os.getenv("DATABASE_URL", ""))
    if auth_service is None:
        return 0

    login = LoginWindow(auth_service)
    if login.exec() != QDialog.DialogCode.Accepted or not login.last_auth_result:
        return 0

    window = MainWindow(login.last_auth_result.user or {})
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
