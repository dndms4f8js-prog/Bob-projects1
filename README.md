# IT学習記録 & クイズ生成 Webアプリ

新入社員がIT知識を記録・検索・復習・クイズ形式でアウトプットできるWebアプリです。

## 技術スタック

- **フロントエンド**: HTML / Bootstrap 5 / JavaScript (marked.js)
- **バックエンド**: Python + Flask
- **DB**: SQLite (Flask-SQLAlchemy)
- **デプロイ**: Render (無料プラン)

## ページ構成

| ページ | URL |
|---|---|
| 学習記録一覧 | `/` |
| 記録登録 | `/records/new` |
| 記録詳細 | `/records/<id>` |
| クイズ設定 | `/quiz` |
| クイズ実行 | `/quiz/run` |
| 管理ページ | `/admin` |

---

## ローカル開発環境のセットアップ

### 前提条件
- Python 3.10 以上

### 手順

```bash
# 1. リポジトリをクローン（またはディレクトリに移動）
cd it-learning-app

# 2. 仮想環境を作成・有効化
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. アプリを起動
python app.py
```

ブラウザで `http://localhost:5000` にアクセス。

---

## Render へのデプロイ手順

1. [Render](https://render.com) にサインアップ・ログイン
2. **New > Web Service** を選択
3. GitHubリポジトリを連携する
4. 以下の設定を入力：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3
5. **Environment Variables** に以下を設定：
   - `SECRET_KEY` = （任意のランダム文字列）
6. **Create Web Service** をクリック

> ⚠️ Render無料プランはファイルシステムが永続化されないため、デプロイのたびにDBがリセットされます。

---

## カテゴリの追加方法

`app/config.py` の `CATEGORIES` リストに追記するだけでUIに反映されます。

```python
CATEGORIES = [
    "IT用語",
    "IBM用語",
    "営業用語",
    "製品",
    "新しいカテゴリ",  # ← ここに追記
]
```
