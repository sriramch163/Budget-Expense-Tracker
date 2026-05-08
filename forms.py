from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, DateField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(1, 80)])
    color = StringField("Color", validators=[DataRequired(), Length(7, 7)], default="#6366f1")
    icon = StringField("Icon", validators=[Optional(), Length(max=50)], default="tag")

class ExpenseForm(FlaskForm):
    amount = DecimalField("Amount (₹)", validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    description = StringField("Description", validators=[DataRequired(), Length(1, 255)])
    date = DateField("Date", validators=[DataRequired()])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    is_recurring = BooleanField("Recurring Expense")
    recurrence_interval = SelectField("Recurrence", choices=[("","None"),("daily","Daily"),("weekly","Weekly"),("monthly","Monthly")])

class SalaryForm(FlaskForm):
    amount = DecimalField("Amount (₹)", validators=[DataRequired(), NumberRange(min=1)], places=2)
    source = StringField("Source", validators=[DataRequired(), Length(1, 120)], default="Salary")
    note = StringField("Note (optional)", validators=[Optional(), Length(max=255)])
    date = DateField("Date", validators=[DataRequired()])

class SavingsGoalForm(FlaskForm):
    name          = StringField("Goal Name", validators=[DataRequired(), Length(1, 120)])
    target_amount = DecimalField("Target Amount (₹)", validators=[DataRequired(), NumberRange(min=1)], places=2)
    saved_amount  = DecimalField("Already Saved (₹)", validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    emoji         = StringField("Emoji", validators=[Optional(), Length(max=10)], default="🎯")
    target_date   = DateField("Target Date (optional)", validators=[Optional()])

class BudgetForm(FlaskForm):
    limit_amount = DecimalField("Budget Limit", validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    period = SelectField("Period", choices=[("daily","Daily"),("weekly","Weekly"),("monthly","Monthly")])
    category_id = SelectField("Category (optional)", coerce=int, validators=[Optional()])
