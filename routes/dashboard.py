from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date, timedelta
from models import Expense, Category, Budget, SalaryEntry, SavingsGoal
from app import db

dashboard_bp = Blueprint("dashboard", __name__)

def get_period_range(period, ref_date=None):
    today = ref_date or date.today()
    if period == "daily":
        return today, today
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    else:
        return today.replace(day=1), today

def month_range(year, month):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) - timedelta(days=1) if month == 12 \
          else date(year, month + 1, 1) - timedelta(days=1)
    return start, end

def spending_by_category(user_id, start, end):
    return db.session.query(
        Category.name, Category.color, Category.icon,
        func.sum(Expense.amount).label("total")
    ).join(Expense, Expense.category_id == Category.id)\
     .filter(Expense.user_id == user_id, Expense.date.between(start, end))\
     .group_by(Category.id).all()

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    uid   = current_user.id
    today = date.today()

    sel_year  = request.args.get("year",  type=int, default=today.year)
    sel_month = request.args.get("month", type=int, default=today.month)
    if not (1 <= sel_month <= 12): sel_month = today.month
    if sel_year < 2000 or sel_year > today.year + 1: sel_year = today.year
    m_start, m_end = month_range(sel_year, sel_month)

    chart_period = request.args.get("chart_period", "monthly")
    if chart_period not in ("daily", "weekly", "monthly"): chart_period = "monthly"
    chart_start, chart_end = (m_start, m_end) if chart_period == "monthly" \
                              else get_period_range(chart_period)

    def total_between(start, end):
        r = db.session.query(func.sum(Expense.amount))\
            .filter(Expense.user_id == uid, Expense.date.between(start, end)).scalar()
        return float(r or 0)

    totals = {
        "daily":   total_between(*get_period_range("daily")),
        "weekly":  total_between(*get_period_range("weekly")),
        "monthly": total_between(m_start, m_end),
    }

    total_income = float(db.session.query(func.sum(SalaryEntry.amount))
        .filter(SalaryEntry.user_id == uid).scalar() or 0)
    total_expenses_all = float(db.session.query(func.sum(Expense.amount))
        .filter(Expense.user_id == uid).scalar() or 0)
    balance = total_income - total_expenses_all

    income_this_month = float(db.session.query(func.sum(SalaryEntry.amount))
        .filter(SalaryEntry.user_id == uid,
                SalaryEntry.date.between(m_start, m_end)).scalar() or 0)

    recent = Expense.query.filter_by(user_id=uid).order_by(Expense.date.desc()).limit(6).all()

    alerts = []
    for b in Budget.query.filter_by(user_id=uid).all():
        s, e = get_period_range(b.period)
        q = db.session.query(func.sum(Expense.amount))\
            .filter(Expense.user_id == uid, Expense.date.between(s, e))
        if b.category_id:
            q = q.filter(Expense.category_id == b.category_id)
        spent = float(q.scalar() or 0)
        limit = float(b.limit_amount)
        pct   = (spent / limit * 100) if limit > 0 else 0
        if pct >= 80:
            label = b.category.name if b.category_id else "Overall"
            alerts.append({"label": label, "period": b.period,
                           "pct": round(pct, 1), "spent": spent, "limit": limit})

    pie_data          = spending_by_category(uid, chart_start, chart_end)
    chart_labels      = [r.name  for r in pie_data]
    chart_values      = [float(r.total) for r in pie_data]
    chart_colors      = [r.color for r in pie_data]
    chart_category_ids = []
    for r in pie_data:
        cat = Category.query.filter_by(user_id=uid, name=r.name).first()
        chart_category_ids.append(cat.id if cat else None)

    trend_labels, trend_expenses, trend_income = [], [], []
    for i in range(5, -1, -1):
        m = sel_month - i
        y = sel_year
        while m <= 0: m += 12; y -= 1
        s, e = month_range(y, m)
        trend_labels.append(date(y, m, 1).strftime("%b %y"))
        trend_expenses.append(float(db.session.query(func.sum(Expense.amount))
            .filter(Expense.user_id == uid, Expense.date.between(s, e)).scalar() or 0))
        trend_income.append(float(db.session.query(func.sum(SalaryEntry.amount))
            .filter(SalaryEntry.user_id == uid, SalaryEntry.date.between(s, e)).scalar() or 0))

    line_labels, line_values = [], []
    cur = m_start
    while cur <= min(m_end, today):
        line_labels.append(cur.strftime("%-d %b"))
        line_values.append(float(db.session.query(func.sum(Expense.amount))
            .filter(Expense.user_id == uid, Expense.date == cur).scalar() or 0))
        cur += timedelta(days=1)

    months = [(m, date(2000, m, 1).strftime("%B")) for m in range(1, 13)]

    # Savings goals summary (top 3)
    goals = SavingsGoal.query.filter_by(user_id=uid)\
        .order_by(SavingsGoal.created_at.desc()).limit(3).all()

    # Smart insights
    from routes.insights import generate_insights
    insights = generate_insights(uid, sel_year, sel_month)

    # Categories for quick-add modal
    categories = Category.query.filter_by(user_id=uid).order_by(Category.name).all()

    return render_template("dashboard.html",
        totals=totals, recent=recent, alerts=alerts,
        chart_labels=chart_labels, chart_values=chart_values, chart_colors=chart_colors,
        chart_category_ids=chart_category_ids,
        chart_start=chart_start.isoformat(), chart_end=chart_end.isoformat(),
        trend_labels=trend_labels, trend_expenses=trend_expenses, trend_income=trend_income,
        line_labels=line_labels, line_values=line_values,
        chart_period=chart_period,
        balance=balance, total_income=total_income, total_expenses_all=total_expenses_all,
        income_this_month=income_this_month,
        sel_month=sel_month, sel_year=sel_year, months=months,
        today=today, goals=goals, insights=insights, categories=categories)
