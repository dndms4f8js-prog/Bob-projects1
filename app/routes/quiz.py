import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import Record

bp = Blueprint("quiz", __name__, url_prefix="/quiz")

# セッションキー
SESSION_QUESTIONS = "quiz_questions"
SESSION_INDEX = "quiz_index"
SESSION_RESULTS = "quiz_results"
SESSION_MODE = "quiz_mode"


@bp.route("/", methods=["GET"])
def setup():
    total = Record.query.count()
    return render_template(
        "quiz/setup.html",
        total=total,
    )


@bp.route("/start", methods=["POST"])
def start():
    mode = request.form.get("mode", "term")       # "term" or "desc"
    count = int(request.form.get("count", 10))    # 10 or 30

    all_records = Record.query.all()

    if len(all_records) < 4:
        flash("フィルター条件に合う記録が4件未満です。条件を変えてお試しください。", "danger")
        return redirect(url_for("quiz.setup"))

    count = min(count, len(all_records))
    questions = _generate_questions(all_records, mode, count)

    session[SESSION_QUESTIONS] = questions
    session[SESSION_INDEX] = 0
    session[SESSION_RESULTS] = []
    session[SESSION_MODE] = mode
    session.modified = True

    return redirect(url_for("quiz.run"))


@bp.route("/abort", methods=["POST"])
def abort():
    """クイズを中断してセッションをクリアし設定画面へ戻る。"""
    session.pop(SESSION_QUESTIONS, None)
    session.pop(SESSION_INDEX, None)
    session.pop(SESSION_RESULTS, None)
    session.pop(SESSION_MODE, None)
    session.modified = True
    flash("クイズを中断しました。", "warning")
    return redirect(url_for("quiz.setup"))


@bp.route("/run", methods=["GET"])
def run():
    questions = session.get(SESSION_QUESTIONS)
    index = session.get(SESSION_INDEX, 0)

    if not questions:
        return redirect(url_for("quiz.setup"))

    if index >= len(questions):
        return redirect(url_for("quiz.result"))

    q = questions[index]
    mode = session.get(SESSION_MODE, "term")
    return render_template(
        "quiz/run.html",
        question=q,
        index=index,
        total=len(questions),
        mode=mode,
        answered=False,
        is_correct=None,
        selected=None,
    )


@bp.route("/answer", methods=["POST"])
def answer():
    questions = session.get(SESSION_QUESTIONS)
    index = session.get(SESSION_INDEX, 0)

    if not questions or index >= len(questions):
        return redirect(url_for("quiz.setup"))

    q = questions[index]
    selected = request.form.get("choice", "")
    is_correct = selected == q["correct_text"]

    # DB更新
    record = Record.query.get(q["correct_id"])
    if record:
        record.quiz_total += 1
        if is_correct:
            record.quiz_correct += 1
        else:
            record.quiz_incorrect += 1
        db.session.commit()

    # 結果を保存
    results = session.get(SESSION_RESULTS, [])
    results.append(
        {
            "term": q["term"],
            "correct_text": q["correct_text"],
            "selected": selected,
            "is_correct": is_correct,
            "question_text": q["question_text"],
        }
    )
    session[SESSION_RESULTS] = results
    session[SESSION_INDEX] = index + 1
    session.modified = True

    mode = session.get(SESSION_MODE, "term")
    return render_template(
        "quiz/run.html",
        question=q,
        index=index,
        total=len(questions),
        mode=mode,
        answered=True,
        is_correct=is_correct,
        selected=selected,
    )


@bp.route("/result", methods=["GET"])
def result():
    results = session.get(SESSION_RESULTS, [])
    if not results:
        return redirect(url_for("quiz.setup"))

    total = len(results)
    correct_count = sum(1 for r in results if r["is_correct"])
    accuracy = round(correct_count / total * 100, 1) if total > 0 else 0
    wrong_items = [r for r in results if not r["is_correct"]]

    return render_template(
        "quiz/result.html",
        results=results,
        total=total,
        correct_count=correct_count,
        accuracy=accuracy,
        wrong_items=wrong_items,
    )


# ───────────────────────────────
# ヘルパー関数
# ───────────────────────────────

def _generate_questions(all_records, mode, count):
    """
    count問分のクイズデータを生成する。

    mode="term"  : 説明文を提示し、用語名を選択させる
    mode="desc"  : 用語名を提示し、説明文を選択させる

    戻り値: list of dict
      {
        correct_id: int,
        term: str,
        question_text: str,   # 問題文（提示するテキスト）
        correct_text: str,    # 正解の選択肢テキスト
        choices: [str, ...],  # 4択（ランダム並び替え済み）
      }
    """
    selected_corrects = random.sample(all_records, count)
    questions = []

    for correct in selected_corrects:
        distractors_pool = [r for r in all_records if r.id != correct.id]
        distractors = random.sample(distractors_pool, min(3, len(distractors_pool)))

        if mode == "term":
            question_text = correct.description[:300]  # 長すぎる場合は省略
            correct_text = correct.term
            wrong_texts = [r.term for r in distractors]
        else:  # mode == "desc"
            question_text = correct.term
            correct_text = correct.description[:200]
            wrong_texts = [r.description[:200] for r in distractors]

        choices = wrong_texts + [correct_text]
        random.shuffle(choices)

        questions.append(
            {
                "correct_id": correct.id,
                "term": correct.term,
                "question_text": question_text,
                "correct_text": correct_text,
                "choices": choices,
            }
        )

    return questions
