from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import select

from src.config.env_utils import ensureDatabaseUrl

from .db import get_session, init_db
from .routes import register_blueprints


def create_app() -> Flask:
    """Create and configure a Flask application instance."""

    app = Flask(__name__)
    app.config["DATABASE_URL"] = ensureDatabaseUrl()
    app.config["JSON_SORT_KEYS"] = False

    # Enable CORS so the React frontend can call the API during development.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)
    register_blueprints(app)

    @app.get("/api/health")
    def healthcheck():
        try:
            with get_session() as session:
                session.execute(select(1))
        except Exception:  # pragma: no cover - defensive logging
            app.logger.exception("Database health check failed")
            return (
                jsonify({"status": "error", "database": "unreachable"}),
                500,
            )

        return jsonify({"status": "ok", "database": "ok"})

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.get("/")
    def index():
        return jsonify({"name": "Vivero API", "endpoints": ["/api/health", "..."]})

    return app


# Allow "flask --app src.API.app run" usage by exposing a module-level app.
app = create_app()
