from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "finance_tracker_secret"

# Database setup
DATABASE = "finance_tracker.db"

def connect_db():
    return sqlite3.connect(DATABASE, check_same_thread=False)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS income (
                        id INTEGER PRIMARY KEY,
                        date TEXT,
                        description TEXT,
                        amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY,
                        date TEXT,
                        description TEXT,
                        amount REAL)''')
    conn.commit()
    conn.close()

create_tables()

@app.route("/")
def index():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM income")
    total_income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0] or 0

    balance = total_income - total_expenses
    conn.close()

    return render_template("index.html", income=total_income, expenses=total_expenses, balance=balance)

@app.route("/add_income", methods=["GET", "POST"])
def add_income():
    if request.method == "POST":
        date = request.form["date"]
        description = request.form["description"]
        amount = request.form["amount"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO income (date, description, amount) VALUES (?, ?, ?)", (date, description, amount))
        conn.commit()
        conn.close()

        flash("Income added successfully!")
        return redirect(url_for("index"))

    return render_template("add_income.html")

@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        date = request.form["date"]
        description = request.form["description"]
        amount = request.form["amount"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)", (date, description, amount))
        conn.commit()
        conn.close()

        flash("Expense added successfully!")
        return redirect(url_for("index"))

    return render_template("add_expense.html")

@app.route("/view_transactions")
def view_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM income")
    incomes = cursor.fetchall()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    conn.close()
    return render_template("view_transactions.html", incomes=incomes, expenses=expenses)

@app.route("/transactions_by_month", methods=["GET", "POST"])
def transactions_by_month():
    if request.method == "POST":
        month = request.form["month"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM income WHERE strftime('%Y-%m', date) = ?", (month,))
        incomes = cursor.fetchall()

        cursor.execute("SELECT * FROM expenses WHERE strftime('%Y-%m', date) = ?", (month,))
        expenses = cursor.fetchall()

        conn.close()
        return render_template("transactions_by_month.html", incomes=incomes, expenses=expenses, month=month)

    return render_template("transactions_by_month.html", incomes=None, expenses=None)

@app.route("/delete_all")
def delete_all():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM income")
    cursor.execute("DELETE FROM expenses")

    conn.commit()
    conn.close()

    flash("All data deleted successfully!")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
