"""Dialog to capture Supabase/PostgreSQL connection settings."""
from __future__ import annotations

from typing import Optional

import psycopg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
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
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        self.setPalette(palette)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("Configurá tu conexión a Supabase")
        header.setObjectName("dbDialogTitle")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setStyleSheet("font-size: 20px; font-weight: 600; color: #223354;")

        subtitle = QLabel(
            "Copiá y pegá la cadena de conexión completa de PostgreSQL. "
            "La encontrás en el correo que te enviamos. (RECUERDA NO COMPRARTIRLA CON NADIE)"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #4e5d78; line-height: 1.4;")

        layout.addWidget(header)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("dbDialogCard")
        card.setStyleSheet(
            "#dbDialogCard {"
            "  background-color: #f8fafc;"
            "  border: 1px solid #d8e0ef;"
            "  border-radius: 12px;"
            "}"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        field_label = QLabel("Cadena de conexión")
        field_label.setStyleSheet("font-weight: 500; color: #223354;")

        self._conninfo_input.setPlaceholderText(
            "postgresql://usuario:password@host:puerto/base"
        )
        self._conninfo_input.setMinimumHeight(36)
        self._conninfo_input.setClearButtonEnabled(True)
        self._conninfo_input.setStyleSheet(
            "QLineEdit {"
            "  background: #ffffff;"
            "  border: 1px solid #c3d0ea;"
            "  border-radius: 8px;"
            "  padding: 6px 10px;"
            "  font-size: 14px;"
            "}"
            "QLineEdit:focus {"
            "  border-color: #4f6edb;"
            "  box-shadow: 0 0 0 2px rgba(79, 110, 219, 0.2);"
            "}"
        )

        example = QLabel(
            "Ejemplo: postgresql://postgres:secreto@db.supabase.co:5432/postgres"
        )
        example.setStyleSheet("color: #6b7a99; font-size: 12px;")

        card_layout.addWidget(field_label)
        card_layout.addWidget(self._conninfo_input)
        card_layout.addWidget(example)

        layout.addWidget(card)

        self._message_label.setStyleSheet("color: #c0392b; font-size: 13px;")
        self._message_label.setWordWrap(True)
        self._message_label.setVisible(False)
        layout.addWidget(self._message_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self._connect_button = QPushButton("Probar conexión")
        self._connect_button.setDefault(True)
        self._connect_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._connect_button.setStyleSheet(
            "QPushButton {"
            "  background-color: #4f6edb;"
            "  color: white;"
            "  padding: 8px 20px;"
            "  border: none;"
            "  border-radius: 8px;"
            "  font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "  background-color: #3f59b7;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #33478f;"
            "}"
        )

        self._connect_button.clicked.connect(self._validate_connection)
        button_box.rejected.connect(self.reject)

        btn_container = QHBoxLayout()
        btn_container.addWidget(button_box)
        btn_container.addStretch(1)
        btn_container.addWidget(self._connect_button)
        layout.addLayout(btn_container)

        self._conninfo_input.returnPressed.connect(self._validate_connection)

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
