from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # --- 設定 ---
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    _db_uri = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(app.instance_path, "learning.db"),
    )
    # RenderのPostgreSQL URLは "postgres://" で始まる場合があるため修正
    if _db_uri.startswith("postgres://"):
        _db_uri = _db_uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = _db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # instance フォルダを確保
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    # Blueprint 登録
    from app.routes.records import bp as records_bp
    from app.routes.quiz import bp as quiz_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(records_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(admin_bp)

    # テーブル作成
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
