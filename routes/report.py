from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date, timedelta
import json
from models import Expense, Category, SalaryEntry
from app import db

report_bp = Blueprint("report", __name__)

def month_range(year, month):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) - timedelta(days=1) if month == 12 \
          else date(year, month + 1, 1) - timedelta(days=1)
    return start, end

@report_bp.route("/report")
@login_required
def index():
    uid   = current_user.id
    today = date.today()

    sel_year  = request.args.get("year",  type=int, default=today.year)
    sel_month = request.args.get("month", type=int, default=today.month)
    if not (1 <= sel_month <= 12): sel_month = today.month
    if sel_year < 2000 or sel_year > today.year + 1: sel_year = today.year

    m_start, m_end = month_range(sel_year, sel_month)

    total_income = float(db.session.query(func.sum(SalaryEntry.amount))
        .filter(SalaryEntry.user_id == uid,
                SalaryEntry.date.between(m_start, m_end)).scalar() or 0)

    total_expenses = float(db.session.query(func.sum(Expense.amount))
        .filter(Expense.user_id == uid,
                Expense.date.between(m_start, m_end)).scalar() or 0)

    savings = total_income - total_expenses
    savings_rate = round((savings / total_income * 100), 1) if total_income > 0 else 0
    if savings_rate >= 20:
        savings_emoji = "😊"
    elif savings_rate >= 5:
        savings_emoji = "😐"
    else:
        savings_emoji = "😟"

    # Top 5 categories
    top_cats = db.session.query(
        Category.name, Category.color, Category.icon,
        func.sum(Expense.amount).label("total")
    ).join(Expense, Expense.category_id == Category.id)\
     .filter(Expense.user_id == uid, Expense.date.between(m_start, m_end))\
     .group_by(Category.id)\
     .order_by(func.sum(Expense.amount).desc())\
     .limit(5).all()

    # Biggest single expense
    biggest = Expense.query\
        .filter_by(user_id=uid)\
        .filter(Expense.date.between(m_start, m_end))\
        .order_by(Expense.amount.desc())\
        .first()

    # Day-wise spending
    day_rows = db.session.query(
        Expense.date,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count")
    ).filter(Expense.user_id == uid, Expense.date.between(m_start, m_end))\
     .group_by(Expense.date)\
     .order_by(Expense.date).all()

    months = [(m, date(2000, m, 1).strftime("%B")) for m in range(1, 13)]
    years  = list(range(today.year - 3, today.year + 1))
    categories = Category.query.filter_by(user_id=uid).order_by(Category.name).all()

    return render_template("report/index.html",
        categories=categories,
        sel_month=sel_month, sel_year=sel_year, months=months, years=years,
        m_start=m_start, m_end=m_end,
        total_income=total_income, total_expenses=total_expenses,
        savings=savings, savings_rate=savings_rate, savings_emoji=savings_emoji,
        top_cats=top_cats, biggest=biggest, day_rows=day_rows,
        today=today)


@report_bp.route("/heatmap")
@login_required
def heatmap():
    uid   = current_user.id
    today = date.today()

    sel_year = request.args.get("year", type=int, default=today.year)
    if sel_year < 2000 or sel_year > today.year + 1:
        sel_year = today.year

    y_start = date(sel_year, 1, 1)
    y_end   = date(sel_year, 12, 31)

    rows = db.session.query(
        Expense.date,
        func.sum(Expense.amount).label("total")
    ).filter(Expense.user_id == uid, Expense.date.between(y_start, y_end))\
     .group_by(Expense.date).all()

    spend_map = {str(r.date): float(r.total) for r in rows}
    max_spend = max(spend_map.values(), default=1)

    # Build weeks: list of 7-day columns starting from Mon of week containing Jan 1
    grid_start = y_start - timedelta(days=y_start.weekday())  # Monday
    weeks = []
    cur = grid_start
    while cur <= y_end or len(weeks) < 53:
        week = []
        for _ in range(7):
            week.append(cur)
            cur += timedelta(days=1)
        weeks.append(week)
        if cur > y_end and len(weeks) >= 53:
            break

    years = list(range(today.year - 3, today.year + 1))
    categories = Category.query.filter_by(user_id=uid).order_by(Category.name).all()

    return render_template("report/heatmap.html",
        sel_year=sel_year, years=years,
        weeks=weeks, spend_map=spend_map, max_spend=max_spend,
        y_start=y_start, y_end=y_end, today=today,
        spend_map_json=json.dumps(spend_map),
        categories=categories)
