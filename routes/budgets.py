from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Budget, Category
from forms import BudgetForm
from app import db
from sqlalchemy.exc import IntegrityError

budgets_bp = Blueprint("budgets", __name__, url_prefix="/budgets")

def populate_budget_form(form):
    cats = Category.query.filter_by(user_id=current_user.id).all()
    form.category_id.choices = [(0, "Overall (all categories)")] + [(c.id, c.name) for c in cats]

@budgets_bp.route("/")
@login_required
def index():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template("budgets/index.html", budgets=budgets)

@budgets_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = BudgetForm()
    populate_budget_form(form)
    if form.validate_on_submit():
        cat_id = form.category_id.data if form.category_id.data != 0 else None
        budget = Budget(limit_amount=form.limit_amount.data, period=form.period.data,
                        category_id=cat_id, user_id=current_user.id)
        db.session.add(budget)
        try:
            db.session.commit()
            flash("Budget limit set.", "success")
            return redirect(url_for("budgets.index"))
        except IntegrityError:
            db.session.rollback()
            flash("A budget for this category/period already exists.", "danger")
    return render_template("budgets/form.html", form=form, title="Set Budget")

@budgets_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=budget)
    populate_budget_form(form)
    if form.validate_on_submit():
        budget.limit_amount = form.limit_amount.data
        budget.period = form.period.data
        budget.category_id = form.category_id.data if form.category_id.data != 0 else None
        try:
            db.session.commit()
            flash("Budget updated.", "success")
            return redirect(url_for("budgets.index"))
        except IntegrityError:
            db.session.rollback()
            flash("A budget for this category/period already exists.", "danger")
    return render_template("budgets/form.html", form=form, title="Edit Budget")

@budgets_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash("Budget removed.", "success")
    return redirect(url_for("budgets.index"))
