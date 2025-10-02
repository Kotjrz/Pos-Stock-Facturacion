"""Authentication routes."""
from __future__ import annotations

from datetime import datetime

import bcrypt
from flask import Blueprint, jsonify, request
from sqlalchemy import select

from ..db import get_session
from ..models import Usuario

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son obligatorios"}), 400

    with get_session() as session:
        user = session.execute(
            select(Usuario).where(Usuario.username == username)
        ).scalar_one_or_none()

        if not user or not user.activo:
            return jsonify({"error": "Usuario no encontrado o deshabilitado"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return jsonify({"error": "Credenciales inválidas"}), 401

        user.ultimo_login = datetime.utcnow()
        session.add(user)

    return jsonify(
        {
            "user": {
                "id": user.idusuario,
                "username": user.username,
                "rol": user.rol,
                "email": user.email,
            }
        }
    )
