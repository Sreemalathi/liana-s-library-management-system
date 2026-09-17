import streamlit as st
from sqlalchemy import text
import pandas as pd
from datetime import date, timedelta

def get_engine():
    return st.session_state["engine"]

def create_loan(isbn, user_id, loan_days=14):
    due_date = date.today() + timedelta(days=loan_days)
    with get_engine().begin() as conn:
        conn.execute(
            text("""INSERT INTO loans (isbn, user_id, due_date)
                    VALUES (:isbn, :user_id, :due_date)"""),
            {"isbn": isbn, "user_id": user_id, "due_date": due_date}
        )

def get_active_loan(isbn):
    with get_engine().connect() as conn:
        return conn.execute(
            text("""SELECT * FROM loans
                    WHERE isbn=:isbn AND return_date IS NULL"""),
            {"isbn": isbn}
        ).mappings().first()

def extend_loan(loan_id, extra_days=14):
    with get_engine().begin() as conn:
        result = conn.execute(
            text("""UPDATE loans
                    SET extended_due_date=DATE_ADD(
                        COALESCE(extended_due_date, due_date),
                        INTERVAL :days DAY
                    ),
                    extension_count=extension_count+1
                    WHERE loan_id=:loan_id AND extension_count<2"""),
            {"loan_id": loan_id, "days": extra_days}
        )
        return result.rowcount

def return_loan(loan_id):
    with get_engine().begin() as conn:
        result = conn.execute(
            text("""UPDATE loans
                    SET return_date=CURRENT_DATE()
                    WHERE loan_id=:loan_id AND return_date IS NULL"""),
            {"loan_id": loan_id}
        )
        return result.rowcount

def get_all_loans():
    engine = get_engine()
    query = """
        SELECT l.loan_id, l.isbn, b.title, l.user_id, u.user_name,
               l.loan_date, l.due_date, l.extended_due_date, l.extension_count, l.return_date
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        JOIN users u ON l.user_id = u.user_id
        ORDER BY l.loan_id DESC
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

def get_loaned_count():
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT COUNT(*) FROM loans WHERE return_date IS NULL")
        ).scalar()


def get_overdue_count():
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("""SELECT COUNT(*) FROM loans
                    WHERE return_date IS NULL
                    AND COALESCE(extended_due_date, due_date) < CURRENT_DATE()""")
        ).scalar()


def get_most_borrowed_books(limit=3):
    engine = get_engine()
    query = text("""
        SELECT b.isbn, b.title, b.author, COUNT(l.loan_id) AS times_borrowed
        FROM loans l
        JOIN books b ON l.isbn = b.isbn
        GROUP BY b.isbn, b.title, b.author
        ORDER BY times_borrowed DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"limit": limit})
