from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    categories = db.relationship("Category", backref="user", lazy=True, cascade="all, delete-orphan")
    expenses   = db.relationship("Expense",  backref="user", lazy=True, cascade="all, delete-orphan")
    budgets    = db.relationship("Budget",   backref="user", lazy=True, cascade="all, delete-orphan")
    goals      = db.relationship("SavingsGoal", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = "categories"
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(80), nullable=False)
    color   = db.Column(db.String(7),  default="#6366f1")
    icon    = db.Column(db.String(50), default="tag")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    expenses = db.relationship("Expense", backref="category", lazy=True)
    budgets  = db.relationship("Budget",  backref="category", lazy=True)
    __table_args__ = (db.UniqueConstraint("name", "user_id"),)


class Expense(db.Model):
    __tablename__ = "expenses"
    id          = db.Column(db.Integer, primary_key=True)
    amount      = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date        = db.Column(db.Date, nullable=False, default=date.today)
    period      = db.Column(db.String(10), nullable=False, default="daily")
    is_recurring        = db.Column(db.Boolean, default=False)
    recurrence_interval = db.Column(db.String(10))
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class Budget(db.Model):
    __tablename__ = "budgets"
    id           = db.Column(db.Integer, primary_key=True)
    limit_amount = db.Column(db.Numeric(10, 2), nullable=False)
    period       = db.Column(db.String(10), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id  = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    __table_args__ = (db.UniqueConstraint("user_id", "category_id", "period"),)


class SalaryEntry(db.Model):
    __tablename__ = "salary_entries"
    id         = db.Column(db.Integer, primary_key=True)
    amount     = db.Column(db.Numeric(10, 2), nullable=False)
    source     = db.Column(db.String(120), nullable=False, default="Salary")
    note       = db.Column(db.String(255))
    date       = db.Column(db.Date, nullable=False, default=date.today)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("salary_entries", lazy=True, cascade="all, delete-orphan"))


class SavingsGoal(db.Model):
    __tablename__ = "savings_goals"
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    target_amount= db.Column(db.Numeric(10, 2), nullable=False)
    saved_amount = db.Column(db.Numeric(10, 2), default=0)
    emoji        = db.Column(db.String(10), default="🎯")
    target_date  = db.Column(db.Date, nullable=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def pct(self):
        t = float(self.target_amount)
        return min(round(float(self.saved_amount) / t * 100, 1), 100) if t > 0 else 0

    @property
    def remaining(self):
        return max(float(self.target_amount) - float(self.saved_amount), 0)

    @property
    def months_left(self):
        if not self.target_date:
            return None
        today = date.today()
        months = (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month)
        return max(months, 1)

    @property
    def monthly_needed(self):
        m = self.months_left
        if not m:
            return None
        return round(self.remaining / m, 2)
