"""Dialog to capture Supabase/PostgreSQL connection settings."""
from __future__ import annotations

from typing import Optional

import psycopg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class DBConnectionDialog(QDialog):
    """Collects a PostgreSQL connection string and validates it."""

    def __init__(self, default_conninfo: str = "", parent: Optional[QDialog] = None):
        super().__init__(parent)
        self.setWindowTitle("Conectar a la base de datos")
        self.setModal(True)
        self.setFixedSize(460, 340)
        self._conninfo_input = QLineEdit(default_conninfo)
        self._message_label = QLabel("")
        self._setup_palette()
        self._build_ui()

    def _setup_palette(self) -> None:
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#f6f8fb'))
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#eef2fb'))
        palette.setColor(QPalette.ColorRole.WindowText, QColor('#1f2937'))
        palette.setColor(QPalette.ColorRole.Text, QColor('#1f2937'))
        palette.setColor(QPalette.ColorRole.Button, QColor('#edf1f9'))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('#1f2937'))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor('#6b7a99'))
        self.setPalette(palette)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QLabel("Configura tu conexion a Supabase")
        header.setObjectName("dbDialogTitle")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)

        subtitle = QLabel(
            "Copia y pega la cadena de conexion completa de PostgreSQL. "
            "La encontras en el correo que te enviamos. (RECUERDA NO COMPRARTIRLA CON NADIE)"
        )
        subtitle.setObjectName("dbDialogSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("dbDialogCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        field_label = QLabel("Cadena de conexi�n")
        field_label.setObjectName("dbDialogFieldLabel")

        self._conninfo_input.setPlaceholderText(
            "postgresql://usuario:password@host:puerto/base"
        )
        self._conninfo_input.setMinimumHeight(40)
        self._conninfo_input.setClearButtonEnabled(True)

        example = QLabel(
            "Ejemplo: postgresql://postgres:secreto@db.supabase.co:5432/postgres"
        )
        example.setObjectName("dbDialogHint")
        example.setWordWrap(True)

        card_layout.addWidget(field_label)
        card_layout.addWidget(self._conninfo_input)
        card_layout.addWidget(example)

        layout.addWidget(card)

        self._message_label.setObjectName("dbDialogMessage")
        self._message_label.setWordWrap(True)
        self._message_label.setVisible(False)
        layout.addWidget(self._message_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_button:
            cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_button.setObjectName("cancelButton")

        self._connect_button = QPushButton("Probar conexion")
        self._connect_button.setObjectName("primaryButton")
        self._connect_button.setDefault(True)
        self._connect_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self._connect_button.clicked.connect(self._validate_connection)
        button_box.rejected.connect(self.reject)

        btn_container = QHBoxLayout()
        btn_container.addWidget(button_box)
        btn_container.addStretch(1)
        btn_container.addWidget(self._connect_button)
        layout.addLayout(btn_container)

        self._conninfo_input.returnPressed.connect(self._validate_connection)

        self._apply_styles()
    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f6f8fb;
                color: #1f2937;
            }
            QLabel {
                color: #1f2937;
            }
            QLabel#dbDialogTitle {
                font-size: 20px;
                font-weight: 600;
                color: #1d2a53;
            }
            QLabel#dbDialogSubtitle {
                color: #4b5d7d;
                line-height: 1.4;
            }
            QLabel#dbDialogFieldLabel {
                font-weight: 600;
                color: #1f2937;
            }
            QLabel#dbDialogHint {
                color: #5c6f92;
                font-size: 12px;
            }
            QFrame#dbDialogCard {
                background-color: #ffffff;
                border: 1px solid #d8e0ef;
                border-radius: 16px;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #c4d0e9;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #4f6edb;
            }
            QLabel#dbDialogMessage {
                font-size: 13px;
            }
            QPushButton {
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
            }
            QPushButton#cancelButton {
                background-color: #f1f4fa;
                color: #1f2937;
                border: 1px solid #d1d9e9;
            }
            QPushButton#cancelButton:hover {
                background-color: #e3e8f5;
            }
            QPushButton#cancelButton:pressed {
                background-color: #d7deef;
            }
            QPushButton#primaryButton {
                background-color: #4f6edb;
                color: #ffffff;
                border: none;
            }
            QPushButton#primaryButton:hover {
                background-color: #3f59b7;
            }
            QPushButton#primaryButton:pressed {
                background-color: #324796;
            }
            """
        )

    def _set_message(self, message: str, success: bool = False) -> None:
        color = "#27ae60" if success else "#c0392b"
        self._message_label.setStyleSheet(f"color: {color};")
        self._message_label.setText(message)
        self._message_label.setVisible(bool(message))

    def _validate_connection(self) -> None:
        conninfo = self.connection_info.strip()
        if not conninfo:
            self._set_message("La cadena de conexión es obligatoria.")
            return

        try:
            with psycopg.connect(conninfo) as conn:
                conn.execute("SELECT 1")
        except psycopg.Error as exc:
            message = getattr(exc, "pgerror", None)
            if not message and getattr(exc, "diag", None):
                message = getattr(exc.diag, "message_primary", None)
            if not message:
                message = str(exc)
            self._set_message(f"No se pudo conectar: {message}")
            return
        except Exception as exc:  # pragma: no cover - errores no esperados
            self._set_message(str(exc))
            return

        self._set_message("Conexión verificada.", success=True)
        self.accept()

    @property
    def connection_info(self) -> str:
        return self._conninfo_input.text()

    @staticmethod
    def prompt(default_conninfo: str = "") -> Optional[str]:
        dialog = DBConnectionDialog(default_conninfo=default_conninfo)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.connection_info.strip()
        return None
