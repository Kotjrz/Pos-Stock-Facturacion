"""Authentication service used by the PyQt6 PoS login window.

The implementation is intentionally simple so it can run locally while still
being easy to plug into a future FastAPI/Django backend.  It reads the
PostgreSQL connection string from environment variables and validates the user
against the ``usuarios`` table using bcrypt hashed passwords.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import psycopg
from psycopg.rows import dict_row

try:
    import bcrypt
except ImportError as exc:  # pragma: no cover - makes the dependency obvious
    raise RuntimeError(
        "Missing dependency 'bcrypt'. Install it with 'pip install bcrypt'."
    ) from exc


class AuthError(Exception):
    """Raised when authentication cannot proceed (e.g., connectivity issues)."""


@dataclass
class AuthResult:
    """Represents the outcome of an authentication attempt."""

    success: bool
    message: str
    user: Optional[dict] = None


class AuthService:
    """Simple authentication service targeting the ``usuarios`` table."""

    def __init__(self, conninfo: str):
        if not conninfo:
            raise AuthError("DATABASE_URL env var is required for authentication")
        self._conninfo = conninfo

    @classmethod
    def from_env(cls) -> "AuthService":
        """Factory that creates the service from ``DATABASE_URL`` env var."""

        return cls(os.getenv("DATABASE_URL", ""))

    def authenticate(self, username: str, password: str) -> AuthResult:
        """Validate the user credentials against the database.

        The ``usuarios`` table is expected to have columns:
        ``username``, ``password_hash``, ``activo`` and ``rol``.
        """

        username = username.strip()
        if not username or not password:
            return AuthResult(
                success=False,
                message="Usuario y contraseña son obligatorios.",
            )

        try:
            with psycopg.connect(self._conninfo, row_factory=dict_row) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT idusuario, username, password_hash, rol, activo
                        FROM public.usuarios
                        WHERE username = %s
                        LIMIT 1
                        """,
                        (username,),
                    )
                    row = cur.fetchone()
        except psycopg.Error as exc:
            raise AuthError(
                "No se pudo conectar a la base de datos Supabase/PostgreSQL"
            ) from exc

        if not row:
            return AuthResult(success=False, message="Usuario no encontrado.")

        if not row["activo"]:
            return AuthResult(
                success=False,
                message="El usuario está deshabilitado. Contactá al administrador.",
            )

        stored_hash = row["password_hash"].encode("utf-8")
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return AuthResult(success=False, message="Contraseña incorrecta.")

        return AuthResult(
            success=True,
            message="Ingreso correcto.",
            user={
                "id": row["idusuario"],
                "username": row["username"],
                "rol": row["rol"],
            },
        )
