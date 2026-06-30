from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import re

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

    # Markdownをプレーンテキスト化するJinja2フィルター（一覧カード用）
    @app.template_filter('md_plain')
    def md_plain(text):
        """Markdown記号を除去してプレーンテキストに変換する。"""
        if not text:
            return ''
        # 見出し（# ## ###）
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 太字・斜体（** __ で囲まれた部分 → 中身だけ残す）
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # 残留した単独の * や _ を除去
        text = re.sub(r'\*+', '', text)
        # 箇条書き（行頭の - / * / + ）
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        # 行中に残った「 - 」区切り（箇条書きが改行なしで連結されたケース）
        text = re.sub(r'\s*-\s+', ' ', text)
        # インラインコード
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # リンク [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 複数スペース・改行を1スペースに正規化
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

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
