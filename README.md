# 💰 Budget & Expense Tracker

A full-featured personal finance web app built with **Flask**. Track expenses, set budgets, manage savings goals, log income, and visualize your spending — all in one place.

---

## 🗂️ Project Structure

```
budget expense tracker/
├── app.py              # App factory — initializes Flask, DB, blueprints, CSRF
├── config.py           # Config (secret key, DB URI via .env)
├── models.py           # SQLAlchemy models
├── forms.py            # WTForms form definitions
├── run.py              # Entry point
├── routes/
│   ├── auth.py         # Register / Login / Logout
│   ├── dashboard.py    # Main dashboard with charts & insights
│   ├── expenses.py     # CRUD for expenses
│   ├── categories.py   # CRUD for categories
│   ├── budgets.py      # CRUD for budgets
│   ├── salary.py       # Income / salary entries
│   ├── goals.py        # Savings goals with progress tracking
│   ├── report.py       # Monthly reports & spending heatmap
│   ├── export.py       # Export expenses as CSV or PDF
│   └── insights.py     # Smart spending insights generator
├── templates/          # Jinja2 HTML templates
├── static/
│   ├── css/style.css
│   └── js/main.js      # Dark mode, charts, animations, confetti
└── instance/
    └── budget.db       # SQLite database (auto-created)
```

---

## 🔄 Application Workflow

### 1. Authentication
- Users **register** with a username, email, and password (hashed with PBKDF2-SHA256).
- On **login**, Flask-Login manages the session.
- All routes are protected with `@login_required`.

### 2. Categories
- Before adding expenses, create **categories** (e.g., Food, Rent, Travel) with a custom color and icon.
- Each category belongs to the logged-in user.

### 3. Expenses
- Add expenses with amount, description, date, category, and optional recurrence.
- Filter by category, date range, keyword, or amount range.
- Edit or delete any expense.

### 4. Budgets
- Set spending limits per category or overall, for daily / weekly / monthly periods.
- The dashboard shows **budget alerts** when spending reaches ≥ 80% of the limit.

### 5. Salary / Income
- Log income entries with source, amount, date, and optional note.
- Used to calculate **net balance** (total income − total expenses).

### 6. Savings Goals
- Create goals with a target amount, emoji, and optional deadline.
- Add savings incrementally; a **confetti animation** fires when a goal is completed.
- Dashboard shows the top 3 active goals.

### 7. Dashboard
- Displays daily / weekly / monthly spending totals.
- Interactive **doughnut**, **line**, and **bar charts** (Chart.js) with dark/light theme support.
- Smart insights, budget alerts, and recent transactions at a glance.
- Month/year selector to browse historical data.

### 8. Reports
- **Monthly report**: income vs expenses, savings rate, top 5 categories, biggest single expense, day-wise breakdown.
- **Spending heatmap**: GitHub-style calendar view of daily spending for any year.

### 9. Export
- Download filtered expenses as **CSV** or **PDF** (with date range and category filters).

---

## 🚀 How to Run

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone the repository
git clone <repo-url>
cd "budget expense tracker"

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Create a .env file for custom config
echo "SECRET_KEY=your-secret-key" > .env
echo "DATABASE_URL=sqlite:///budget.db" >> .env

# 5. Run the app
python run.py
```

Open your browser at **http://127.0.0.1:5000**

> The SQLite database (`instance/budget.db`) is created automatically on first run.

---

## ⚙️ Environment Variables

| Variable       | Default                    | Description                  |
|----------------|----------------------------|------------------------------|
| `SECRET_KEY`   | `dev-secret-change-in-prod`| Flask session secret key     |
| `DATABASE_URL` | `sqlite:///budget.db`      | SQLAlchemy database URI      |

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Flask, Flask-Login, Flask-WTF       |
| Database   | SQLite + SQLAlchemy                 |
| Frontend   | Jinja2, Chart.js, Font Awesome      |
| Export     | ReportLab (PDF), Python csv (CSV)   |
| Auth       | Werkzeug password hashing, CSRF     |

---

## 👤 Credits

**Developed by Sriram Chandika**

- Built as a personal finance management project using Flask and SQLite.
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Icons by [Font Awesome](https://fontawesome.com/)
- PDF generation by [ReportLab](https://www.reportlab.com/)
