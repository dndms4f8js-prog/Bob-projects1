# IT学習アプリ 機能改善プラン

## 概要

機能の追加・削除・調整をリスク最小・効果最大の順で進める。
バグを避けるため、各サブタスクは独立して実施・確認する。

---

## 第1弾：削除系（⑤⑥）

### サブタスク A：「理解度」をフォーム・表示・クイズフィルターから完全削除

**Intent**
登録・編集フォームから「理解度」入力欄を削除し、一覧カード・詳細画面・管理画面・クイズ設定画面からも理解度の表示・フィルター機能を取り除く。
DBカラム（`understanding`）はマイグレーションリスクを避けるため残し、デフォルト値3で書き込み続ける。

**Expected Outcomes**
- 新規登録・編集フォームに理解度selectが表示されない
- 学習記録一覧カードに「理解度 x/5」バッジが表示されない
- 詳細画面の基本情報に理解度バッジが表示されない
- 管理ページのテーブルに理解度列が表示されない
- クイズ設定画面に「苦手優先」「得意のみ」ラジオボタンが表示されず、「すべて」のみになる
- クイズの動作（出題・採点・結果）には一切影響しない

**Todo List**
1. `app/templates/records/_form.html` — 理解度のselectブロック（47〜58行目）を削除
2. `app/templates/index.html` — 理解度バッジ（74行目）を削除
3. `app/templates/records/detail.html` — 理解度バッジ（24行目）を削除
4. `app/templates/admin/index.html` — 理解度列ヘッダー（20行目）と各行のtd（34行目）を削除
5. `app/templates/quiz/setup.html` — 「理解度フィルター」セクション全体（38〜74行目）を削除し、「すべて」のみになるよう簡素化
6. `app/routes/quiz.py` — `understanding_counts` の集計（19〜21行目）と `understanding_filter` のフィルター処理（33〜43行目）を削除。`all_records = Record.query.all()` に一本化
7. `app/routes/records.py` — `understanding=int(...)` のフォーム取得を `understanding=3`（固定値）に変更
8. `app/routes/admin.py` — `record.understanding = int(...)` の行を `record.understanding = 3`（固定値）に変更
9. `app/templates/base.html` — `.understanding-badge` のCSS（11行目）を削除

**Relevant Context**
- `app/templates/records/_form.html:47-58` — 理解度selectブロック
- `app/templates/index.html:74` — 一覧カードの理解度バッジ
- `app/templates/records/detail.html:24` — 詳細画面の理解度バッジ
- `app/templates/admin/index.html:20,34` — 管理テーブルの理解度列
- `app/templates/quiz/setup.html:38-74` — クイズ理解度フィルターセクション
- `app/routes/quiz.py:19-21,33-43` — 理解度集計・フィルター処理
- `app/routes/records.py:66` — 新規登録時のunderstanding取得
- `app/routes/admin.py:34` — 編集時のunderstanding取得
- `app/models.py:15` — DBカラム（変更しない）

**Status**: [x] done

---

## 第2弾：追加系（①③）

### サブタスク B：「続けて新規登録」ボタンの追加

**Intent**
新規登録完了後に表示される詳細画面に「続けて新規登録」ボタンを追加し、連続登録の手間を減らす。

**Expected Outcomes**
- 詳細画面の上部ボタンエリアに「続けて新規登録」ボタンが追加される
- ボタンクリックで新規登録フォーム（`/records/new`）へ遷移する
- 既存の「編集」「← 一覧へ」ボタンは変わらない

**Todo List**
1. `app/templates/records/detail.html` — ボタンエリア（7〜10行目）に「続けて新規登録」リンクボタンを追加

**Relevant Context**
- `app/templates/records/detail.html:7-10` — 現在のボタンエリア
- `url_for('records.new_record')` — 新規登録フォームへのURL

**Status**: [x] done

---

### サブタスク C：学習記録一覧のページネーション

**Intent**
用語数が増えた際にも一覧が見やすくなるよう、ページネーション機能を追加する。

**Expected Outcomes**
- 一覧ページが1ページあたり一定件数（例：20件）に分割される
- ページ送りのUIが一覧下部に表示される
- キーワード・カテゴリ・年月のフィルター条件を保持したままページ移動できる
- 検索結果が0件の場合はページネーションUIが表示されない

**Todo List**
1. `app/routes/records.py` — `Record.query.order_by(...).all()` を `.paginate(page, per_page=20)` に変更し、`page` パラメータをクエリストリングから取得する
2. `app/templates/index.html` — ページネーションUIを一覧下部に追加。フィルター条件（keyword, category, year, month）をページリンクに引き継ぐ

**Relevant Context**
- `app/routes/records.py:35` — 現在の全件取得クエリ
- Flask-SQLAlchemy の `.paginate()` APIを使用（追加パッケージ不要）
- `app/templates/index.html` — 一覧テンプレート

**Status**: [x] done

---

## 第3弾：UI・JS（②⑦）

### サブタスク D：説明文・例文入力欄のMarkdownツールバー追加

**Intent**
新規登録・編集フォームの「説明文」「例文」テキストエリアに、太字・箇条書きを挿入できる簡易ツールバーボタンを追加する。
（表示側はすでに `marked.js` でMarkdownレンダリング済みのため、入力補助のみ実装する）

**Expected Outcomes**
- 説明文・例文テキストエリアの上に「B（太字）」「リスト」ボタンが表示される
- ボタンクリックでMarkdown記法（`**テキスト**`、`- `）がカーソル位置に挿入される

**Todo List**
1. `app/templates/records/_form.html` — 説明文・例文テキストエリアの直前にツールバーHTML（ボタン2つ）を追加
2. `app/static/js/main.js` または `_form.html` インラインスクリプト — ツールバーのJS処理を実装（テキストエリアへのMarkdown記法挿入）

**Relevant Context**
- `app/templates/records/_form.html:28-37` — 説明文・例文テキストエリア
- `app/static/js/main.js` — 既存のJSファイル
- `base.html` にすでに `marked.js` が読み込まれている

**Status**: [x] done

---

### サブタスク E：学習記録一覧ページのUIリデザイン

**Intent**
学習記録一覧ページのUIをよりスタイリッシュなデザインに変更する。
詳細な変更点は実施前に別途確認する。

**Expected Outcomes**
- ユーザーが指定したデザイン仕様に沿ったUIになる
- 機能（検索・フィルター・カード表示）は変わらない

**Todo List**
1. 詳細デザイン要件を確認する（ユーザーとの合意）
2. `app/templates/index.html` および `app/templates/base.html` を更新

**Relevant Context**
- `app/templates/index.html` — 一覧テンプレート
- `app/templates/base.html` — 共通レイアウト・CSSリンク

**Status**: [x] done

---

## 第4弾：設計が必要（④）

### サブタスク F：学習進捗グラフの追加

**Intent**
Chart.jsを使用して学習の進捗を可視化するグラフを追加する。
グラフの内容（何を可視化するか）は実施前に別途確認する。

**Expected Outcomes**
- ユーザーが指定した集計内容をグラフで表示できる

**Todo List**
1. グラフの内容・表示場所を確認する（ユーザーとの合意）
2. 必要な集計クエリをrouteに追加
3. Chart.jsをbase.htmlに読み込み、グラフ表示テンプレートを実装

**Relevant Context**
- Chart.js CDN で追加パッケージ不要
- `app/routes/records.py` または新規route — 集計データ提供

**Status**: [ ] pending
