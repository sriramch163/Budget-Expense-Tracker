from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Category
from forms import CategoryForm
from app import db
from sqlalchemy.exc import IntegrityError

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")

# ── 20 default categories seeded for every new user ──
DEFAULT_CATEGORIES = [
    ("Food & Dining",      "utensils",         "#ef4444"),
    ("Groceries",          "shopping-basket",  "#f97316"),
    ("Transport",          "car",              "#f59e0b"),
    ("Fuel",               "gas-pump",         "#eab308"),
    ("Home & Rent",        "home",             "#84cc16"),
    ("Electricity",        "bolt",             "#22c55e"),
    ("Water & Gas",        "tint",             "#10b981"),
    ("Internet & Phone",   "wifi",             "#14b8a6"),
    ("Health & Medical",   "heartbeat",        "#06b6d4"),
    ("Medicines",          "pills",            "#3b82f6"),
    ("Education",          "graduation-cap",   "#6366f1"),
    ("Shopping & Fashion", "tshirt",           "#8b5cf6"),
    ("Entertainment",      "film",             "#a855f7"),
    ("Travel",             "plane",            "#ec4899"),
    ("Fitness & Sports",   "dumbbell",         "#f43f5e"),
    ("Loans & EMI",        "money-bill-wave",  "#64748b"),
    ("Savings",            "piggy-bank",       "#0ea5e9"),
    ("Gifts & Donations",  "gift",             "#d946ef"),
    ("Kids & Family",      "child",            "#fb923c"),
    ("Miscellaneous",      "tag",              "#94a3b8"),
]

def seed_default_categories(user_id):
    """Insert any default categories the user doesn't already have."""
    existing_names = {
        c.name for c in Category.query.filter_by(user_id=user_id).all()
    }
    added = 0
    for name, icon, color in DEFAULT_CATEGORIES:
        if name not in existing_names:
            db.session.add(Category(name=name, icon=icon, color=color, user_id=user_id))
            added += 1
    if added:
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    return added


@categories_bp.route("/")
@login_required
def index():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template("categories/index.html", categories=categories)

@categories_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = Category(name=form.name.data, color=form.color.data,
                       icon=form.icon.data, user_id=current_user.id)
        db.session.add(cat)
        try:
            db.session.commit()
            flash("✅ Category created.", "success")
            return redirect(url_for("categories.index"))
        except IntegrityError:
            db.session.rollback()
            flash("Category name already exists.", "danger")
    return render_template("categories/form.html", form=form, title="New Category")

@categories_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    cat = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.color = form.color.data
        cat.icon = form.icon.data
        try:
            db.session.commit()
            flash("✏️ Category updated.", "success")
            return redirect(url_for("categories.index"))
        except IntegrityError:
            db.session.rollback()
            flash("Category name already exists.", "danger")
    return render_template("categories/form.html", form=form, title="Edit Category")

@categories_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    cat = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if cat.expenses:
        flash("Cannot delete a category that has expenses.", "danger")
        return redirect(url_for("categories.index"))
    db.session.delete(cat)
    db.session.commit()
    flash("🗑️ Category deleted.", "success")
    return redirect(url_for("categories.index"))
