import streamlit as st
import pandas as pd
from sqlalchemy import text


def get_engine():
    return st.session_state["engine"]


def create_reservation(isbn, user_id):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO reservations (isbn, user_id, status)
                     VALUES (:isbn, :user_id, 'WAIT')"""),
            {"isbn": isbn, "user_id": user_id}
        )


def get_all_reservations():
    engine = get_engine()
    query = """
        SELECT r.reservation_id, r.isbn, b.title, r.user_id, u.user_name,
               r.reservation_date, r.ready_date, r.status
        FROM reservations r
        JOIN books b ON r.isbn = b.isbn
        JOIN users u ON r.user_id = u.user_id
        ORDER BY r.reservation_date ASC
    """
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def get_next_waiting_reservation(isbn):
    """Oldest WAIT reservation for a book — used when a copy becomes available."""
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("""SELECT * FROM reservations
                     WHERE isbn=:isbn AND status='WAIT'
                     ORDER BY reservation_date ASC
                     LIMIT 1"""),
            {"isbn": isbn}
        ).mappings().first()


def mark_ready(reservation_id):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("""UPDATE reservations
                     SET status='READY', ready_date=CURRENT_TIMESTAMP
                     WHERE reservation_id=:reservation_id AND status='WAIT'"""),
            {"reservation_id": reservation_id}
        )
        return result.rowcount


def fulfill_reservation(reservation_id):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("""UPDATE reservations SET status='FULFILLED'
                     WHERE reservation_id=:reservation_id AND status='READY'"""),
            {"reservation_id": reservation_id}
        )
        return result.rowcount


def cancel_reservation(reservation_id):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("""UPDATE reservations SET status='CANCELLED'
                     WHERE reservation_id=:reservation_id
                     AND status IN ('WAIT', 'READY')"""),
            {"reservation_id": reservation_id}
        )
        return result.rowcount