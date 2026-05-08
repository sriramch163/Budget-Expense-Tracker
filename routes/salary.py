from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import SalaryEntry
from forms import SalaryForm
from app import db
from datetime import date

salary_bp = Blueprint("salary", __name__, url_prefix="/salary")

SOURCE_EMOJIS = {
    "salary":    ("🎉", "Hurrah! Salary credited! 💰 Keep tracking your expenses wisely!"),
    "freelance": ("🚀", "Freelance income added! 💪 Great hustle!"),
    "bonus":     ("🥳", "Bonus credited! You earned it! 🌟"),
    "business":  ("📈", "Business income recorded! Keep growing! 🚀"),
    "gift":      ("🎁", "Gift money added! Lucky you! 😊"),
    "other":     ("✅", "Income credited to your account! 💸"),
}

def get_emoji_msg(source):
    key = source.lower().strip()
    for k, v in SOURCE_EMOJIS.items():
        if k in key:
            return v
    return SOURCE_EMOJIS["other"]

@salary_bp.route("/")
@login_required
def index():
    entries = SalaryEntry.query.filter_by(user_id=current_user.id)\
        .order_by(SalaryEntry.date.desc()).all()
    total = sum(float(e.amount) for e in entries)
    return render_template("salary/index.html", entries=entries, total=total)

@salary_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = SalaryForm()
    if form.validate_on_submit():
        entry = SalaryEntry(
            amount=form.amount.data,
            source=form.source.data,
            note=form.note.data,
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        emoji, msg = get_emoji_msg(form.source.data)
        flash(f"{emoji} {msg}", "success")
        return redirect(url_for("salary.index"))
    form.date.data = form.date.data or date.today()
    return render_template("salary/form.html", form=form, title="Add Income")

@salary_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    entry = SalaryEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SalaryForm(obj=entry)
    if form.validate_on_submit():
        entry.amount = form.amount.data
        entry.source = form.source.data
        entry.note = form.note.data
        entry.date = form.date.data
        db.session.commit()
        flash("✏️ Income entry updated!", "success")
        return redirect(url_for("salary.index"))
    return render_template("salary/form.html", form=form, title="Edit Income")

@salary_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    entry = SalaryEntry.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("🗑️ Income entry removed.", "info")
    return redirect(url_for("salary.index"))
