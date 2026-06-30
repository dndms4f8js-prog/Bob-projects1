from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Record
from app.config import CATEGORIES
from datetime import datetime

bp = Blueprint("records", __name__)

PER_PAGE = 20


@bp.route("/")
def index():
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "").strip()
    year = request.args.get("year", "").strip()
    month = request.args.get("month", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Record.query

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Record.term.ilike(like),
                Record.description.ilike(like),
                Record.keywords.ilike(like),
            )
        )
    if category:
        query = query.filter(Record.category == category)
    if year:
        query = query.filter(Record.registered_year == int(year))
    if month:
        query = query.filter(Record.registered_month == int(month))

    pagination = query.order_by(Record.created_at.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )
    current_year = datetime.utcnow().year
    years = list(range(current_year, current_year - 10, -1))

    return render_template(
        "index.html",
        pagination=pagination,
        records=pagination.items,
        categories=CATEGORIES,
        years=years,
        selected_keyword=keyword,
        selected_category=category,
        selected_year=year,
        selected_month=month,
    )


@bp.route("/records/new", methods=["GET", "POST"])
def new_record():
    if request.method == "POST":
        term = request.form.get("term", "").strip()
        if not term:
            flash("用語名は必須です。", "danger")
            return redirect(url_for("records.new_record"))

        record = Record(
            term=term,
            full_name=request.form.get("full_name", "").strip() or None,
            category=request.form.get("category", ""),
            description=request.form.get("description", ""),
            example=request.form.get("example", "").strip() or None,
            keywords=request.form.get("keywords", "").strip() or None,
            understanding=3,
            registered_year=int(request.form.get("registered_year")),
            registered_month=int(request.form.get("registered_month")),
        )
        db.session.add(record)
        db.session.commit()
        flash(f"「{record.term}」を登録しました。", "success")
        return redirect(url_for("records.detail", record_id=record.id))

    now = datetime.utcnow()
    current_year = now.year
    years = list(range(current_year, current_year - 10, -1))
    return render_template(
        "records/new.html",
        categories=CATEGORIES,
        years=years,
        now_year=now.year,
        now_month=now.month,
    )


@bp.route("/records/<int:record_id>")
def detail(record_id):
    record = Record.query.get_or_404(record_id)
    return render_template("records/detail.html", record=record)
