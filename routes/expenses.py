from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Expense, Category
from forms import ExpenseForm
from app import db
from datetime import date

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")

def populate_category_choices(form):
    cats = Category.query.filter_by(user_id=current_user.id).all()
    form.category_id.choices = [(c.id, c.name) for c in cats]

@expenses_bp.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        try:
            amount = float(q)
            amount_filter = Expense.amount == amount
        except ValueError:
            amount_filter = None
        base = Expense.query.filter_by(user_id=current_user.id)
        desc_q = base.filter(Expense.description.ilike(f"%{q}%"))
        results = desc_q.order_by(Expense.date.desc()).limit(30).all()
        if amount_filter is not None:
            amt_results = base.filter(amount_filter).order_by(Expense.date.desc()).limit(10).all()
            seen = {e.id for e in results}
            results += [e for e in amt_results if e.id not in seen]
    return render_template("expenses/search.html", results=results, q=q)

@expenses_bp.route("/")
@login_required
def index():
    q = Expense.query.filter_by(user_id=current_user.id)

    # Filters
    period = request.args.get("period")
    category_id = request.args.get("category_id", type=int)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    search = request.args.get("search", "").strip()
    min_amount = request.args.get("min_amount", type=float)
    max_amount = request.args.get("max_amount", type=float)

    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if date_from:
        q = q.filter(Expense.date >= date_from)
    if date_to:
        q = q.filter(Expense.date <= date_to)
    if search:
        q = q.filter(Expense.description.ilike(f"%{search}%"))
    if min_amount is not None:
        q = q.filter(Expense.amount >= min_amount)
    if max_amount is not None:
        q = q.filter(Expense.amount <= max_amount)

    expenses = q.order_by(Expense.date.desc()).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template("expenses/index.html", expenses=expenses, categories=categories)

@expenses_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = ExpenseForm()
    populate_category_choices(form)
    if not form.category_id.choices:
        flash("Create a category first.", "warning")
        return redirect(url_for("categories.create"))
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
            period="daily",
            category_id=form.category_id.data,
            is_recurring=form.is_recurring.data,
            recurrence_interval=form.recurrence_interval.data or None,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash("Expense added.", "success")
        return redirect(url_for("expenses.index"))
    if request.method == "GET":
        form.amount.data = request.args.get("amount", type=float) or form.amount.data
        form.description.data = request.args.get("description") or form.description.data
        form.category_id.data = request.args.get("category_id", type=int) or form.category_id.data
        form.is_recurring.data = request.args.get("is_recurring") == "1"
        form.recurrence_interval.data = request.args.get("recurrence_interval") or form.recurrence_interval.data
        form.date.data = date.today()
    return render_template("expenses/form.html", form=form, title="Add Expense")

@expenses_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)
    populate_category_choices(form)
    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.description = form.description.data
        expense.date = form.date.data
        expense.category_id = form.category_id.data
        expense.is_recurring = form.is_recurring.data
        expense.recurrence_interval = form.recurrence_interval.data or None
        db.session.commit()
        flash("Expense updated.", "success")
        return redirect(url_for("expenses.index"))
    return render_template("expenses/form.html", form=form, title="Edit Expense")

@expenses_bp.route("/<int:id>/duplicate")
@login_required
def duplicate(id):
    e = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return redirect(url_for("expenses.create",
        amount=e.amount,
        description=e.description,
        category_id=e.category_id,
        is_recurring="1" if e.is_recurring else "0",
        recurrence_interval=e.recurrence_interval or ""
    ))

@expenses_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.index"))
