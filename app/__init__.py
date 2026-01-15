from flask import Flask

from app.config import AppConfig, load_config
from app.routes import register_routes


def create_app(config_path: str | None = None) -> Flask:
    app = Flask(__name__)
    config: AppConfig = load_config(config_path)
    app.config["APP_CONFIG"] = config
    register_routes(app)
    return app
