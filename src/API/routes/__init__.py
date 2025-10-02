"""Blueprint registrations for the API."""
from __future__ import annotations

from flask import Blueprint

from .auth import bp as auth_bp
from .inventory import bp as inventory_bp


def register_blueprints(app) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(inventory_bp, url_prefix="/api")
