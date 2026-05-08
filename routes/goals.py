from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import SavingsGoal, SalaryEntry
from forms import SavingsGoalForm
from app import db
from sqlalchemy import func

goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

@goals_bp.route("/")
@login_required
def index():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).order_by(SavingsGoal.created_at.desc()).all()
    return render_template("goals/index.html", goals=goals)

@goals_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = SavingsGoalForm()
    if form.validate_on_submit():
        goal = SavingsGoal(
            name=form.name.data,
            target_amount=form.target_amount.data,
            saved_amount=form.saved_amount.data or 0,
            emoji=form.emoji.data or "🎯",
            target_date=form.target_date.data,
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        flash(f"{goal.emoji} Goal '{goal.name}' created! Let's crush it! 💪", "success")
        return redirect(url_for("goals.index"))
    return render_template("goals/form.html", form=form, title="New Savings Goal")

@goals_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SavingsGoalForm(obj=goal)
    if form.validate_on_submit():
        was_complete = goal.pct >= 100
        goal.name          = form.name.data
        goal.target_amount = form.target_amount.data
        goal.saved_amount  = form.saved_amount.data or 0
        goal.emoji         = form.emoji.data or "🎯"
        goal.target_date   = form.target_date.data
        db.session.commit()
        if not was_complete and goal.pct >= 100:
            flash(f"🎉 Congratulations! You've reached your '{goal.name}' goal! 🥳", "success")
        else:
            flash("✏️ Goal updated!", "success")
        return redirect(url_for("goals.index"))
    return render_template("goals/form.html", form=form, title="Edit Goal")

@goals_bp.route("/<int:id>/add", methods=["POST"])
@login_required
def add_savings(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    try:
        amount = float(request.form.get("amount", 0))
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Enter a valid amount.", "danger")
        return redirect(url_for("goals.index"))
    was_complete = goal.pct >= 100
    goal.saved_amount = float(goal.saved_amount) + amount
    db.session.commit()
    if not was_complete and goal.pct >= 100:
        flash(f"🎉🎊 WOW! You've completed your '{goal.name}' goal! Amazing work! 🏆", "success")
    else:
        flash(f"💰 ₹{amount:,.0f} added to '{goal.name}'! {goal.pct}% done!", "success")
    return redirect(url_for("goals.index"))

@goals_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash("🗑️ Goal removed.", "info")
    return redirect(url_for("goals.index"))
