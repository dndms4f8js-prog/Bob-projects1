from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Record
from app.config import CATEGORIES
from datetime import datetime

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
def index():
    records = Record.query.order_by(Record.created_at.desc()).all()
    return render_template("admin/index.html", records=records)


@bp.route("/records/<int:record_id>/edit", methods=["GET", "POST"])
def edit(record_id):
    record = Record.query.get_or_404(record_id)
    current_year = datetime.utcnow().year
    years = list(range(current_year, current_year - 10, -1))

    if request.method == "POST":
        term = request.form.get("term", "").strip()
        if not term:
            flash("用語名は必須です。", "danger")
            return redirect(url_for("admin.edit", record_id=record_id))

        record.term = term
        record.full_name = request.form.get("full_name", "").strip() or None
        record.category = request.form.get("category", "")
        record.description = request.form.get("description", "")
        record.example = request.form.get("example", "").strip() or None
        record.keywords = request.form.get("keywords", "").strip() or None
        record.understanding = 3
        record.registered_year = int(request.form.get("registered_year"))
        record.registered_month = int(request.form.get("registered_month"))

        db.session.commit()
        flash(f"「{record.term}」を更新しました。", "success")
        return redirect(url_for("records.detail", record_id=record.id))

    return render_template(
        "records/edit.html", record=record, categories=CATEGORIES, years=years
    )


@bp.route("/records/<int:record_id>/delete", methods=["POST"])
def delete(record_id):
    record = Record.query.get_or_404(record_id)
    term = record.term
    db.session.delete(record)
    db.session.commit()
    flash(f"「{term}」を削除しました。", "success")
    return redirect(url_for("admin.index"))
