from sqlalchemy import func
from datetime import date, timedelta
from models import Expense, Category, SalaryEntry, Budget
from app import db


def month_range(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def generate_insights(uid, sel_year, sel_month):
    insights = []
    today = date.today()
    m_start, m_end = month_range(sel_year, sel_month)

    # prev month
    pm = sel_month - 1 or 12
    py = sel_year if sel_month > 1 else sel_year - 1
    pm_start, pm_end = month_range(py, pm)

    def total_exp(start, end, cat_id=None):
        q = db.session.query(func.sum(Expense.amount))\
            .filter(Expense.user_id == uid, Expense.date.between(start, end))
        if cat_id:
            q = q.filter(Expense.category_id == cat_id)
        return float(q.scalar() or 0)

    this_total = total_exp(m_start, m_end)
    prev_total = total_exp(pm_start, pm_end)

    # 1. Overall month vs last month
    if prev_total > 0:
        diff_pct = (this_total - prev_total) / prev_total * 100
        if diff_pct > 15:
            insights.append({"type": "warning", "emoji": "📈",
                "text": f"You spent <strong>₹{this_total:,.0f}</strong> this month — {abs(diff_pct):.0f}% more than last month (₹{prev_total:,.0f}). Try to cut back!"})
        elif diff_pct < -15:
            insights.append({"type": "success", "emoji": "📉",
                "text": f"Great job! You spent <strong>{abs(diff_pct):.0f}% less</strong> this month (₹{this_total:,.0f}) vs last month (₹{prev_total:,.0f}). Keep it up! 🌟"})

    # 2. Income vs spending this month
    income_m = float(db.session.query(func.sum(SalaryEntry.amount))
        .filter(SalaryEntry.user_id == uid, SalaryEntry.date.between(m_start, m_end)).scalar() or 0)
    if income_m > 0:
        savings_rate = (income_m - this_total) / income_m * 100
        if savings_rate >= 30:
            insights.append({"type": "success", "emoji": "🏦",
                "text": f"Excellent! You saved <strong>{savings_rate:.0f}%</strong> of your income this month. Financial goals incoming! 🚀"})
        elif savings_rate < 0:
            insights.append({"type": "danger", "emoji": "🚨",
                "text": f"You've spent <strong>₹{abs(income_m - this_total):,.0f} more</strong> than your income this month. Time to review your expenses!"})
        elif savings_rate < 10:
            insights.append({"type": "warning", "emoji": "⚠️",
                "text": f"You're saving only <strong>{savings_rate:.0f}%</strong> of income this month. Aim for at least 20%."})

    # 3. Top spending category this month
    top = db.session.query(Category.name, Category.icon, func.sum(Expense.amount).label("t"))\
        .join(Expense, Expense.category_id == Category.id)\
        .filter(Expense.user_id == uid, Expense.date.between(m_start, m_end))\
        .group_by(Category.id).order_by(func.sum(Expense.amount).desc()).first()
    if top and this_total > 0:
        top_name, top_icon, top_total = top[0], top[1], float(top[2] or 0)
        top_pct = top_total / this_total * 100
        if top_pct > 40:
            insights.append({"type": "info", "emoji": "🔍",
                "text": f"<strong>{top_name}</strong> is your biggest expense at <strong>{top_pct:.0f}%</strong> of total spending (₹{top_total:,.0f}). Is this expected?"})

    # 4. Category spike vs last month
    cats = db.session.query(Category).filter_by(user_id=uid).all()
    for cat in cats:
        this_c = total_exp(m_start, m_end, cat.id)
        prev_c = total_exp(pm_start, pm_end, cat.id)
        if prev_c > 500 and this_c > prev_c * 1.5:
            insights.append({"type": "warning", "emoji": "⚡",
                "text": f"<strong>{cat.name}</strong> spending jumped <strong>{(this_c/prev_c-1)*100:.0f}%</strong> vs last month (₹{this_c:,.0f} vs ₹{prev_c:,.0f})."})
            break  # only show one spike

    # 5. Budget health
    budgets_ok = 0
    budgets_total = 0
    for b in Budget.query.filter_by(user_id=uid).all():
        from routes.dashboard import get_period_range
        s, e = get_period_range(b.period)
        q = db.session.query(func.sum(Expense.amount))\
            .filter(Expense.user_id == uid, Expense.date.between(s, e))
        if b.category_id:
            q = q.filter(Expense.category_id == b.category_id)
        spent = float(q.scalar() or 0)
        budgets_total += 1
        if spent <= float(b.limit_amount):
            budgets_ok += 1
    if budgets_total > 0 and budgets_ok == budgets_total:
        insights.append({"type": "success", "emoji": "✅",
            "text": f"You're within budget on all <strong>{budgets_total}</strong> budget categories. Fantastic discipline! 🎯"})

    # 6. No expenses logged nudge
    last_exp = Expense.query.filter_by(user_id=uid).order_by(Expense.date.desc()).first()
    if last_exp:
        days_ago = (today - last_exp.date).days
        if days_ago >= 3:
            insights.append({"type": "info", "emoji": "📝",
                "text": f"You haven't logged any expenses in <strong>{days_ago} days</strong>. Don't forget to keep your tracker up to date!"})

    return insights[:5]  # max 5 insights
