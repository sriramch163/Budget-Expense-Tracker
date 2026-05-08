import csv
import io
from flask import Blueprint, request, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Expense
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

export_bp = Blueprint("export", __name__, url_prefix="/export")

def get_filtered_expenses():
    q = Expense.query.filter_by(user_id=current_user.id)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    category_id = request.args.get("category_id", type=int)
    if date_from:
        q = q.filter(Expense.date >= date_from)
    if date_to:
        q = q.filter(Expense.date <= date_to)
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    return q.order_by(Expense.date.desc()).all()

@export_bp.route("/csv")
@login_required
def export_csv():
    expenses = get_filtered_expenses()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Description", "Category", "Amount (INR)", "Recurring"])
    for e in expenses:
        writer.writerow([e.date, e.description, e.category.name, float(e.amount), e.is_recurring])
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=expenses.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@export_bp.route("/pdf")
@login_required
def export_pdf():
    expenses = get_filtered_expenses()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Expense Report", styles["Title"])]

    data = [["Date", "Description", "Category", "Amount (₹)"]]
    for e in expenses:
        data.append([str(e.date), e.description, e.category.name, f"₹{float(e.amount):,.2f}"])

    table = Table(data, colWidths=[80, 180, 100, 70, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers["Content-Disposition"] = "attachment; filename=expenses.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response
