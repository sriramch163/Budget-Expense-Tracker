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
    form.date.data = form.date.data or date.today()
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

@expenses_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses.index"))
