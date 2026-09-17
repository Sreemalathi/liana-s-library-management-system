import streamlit as st
import pandas as pd
from sqlalchemy import text


def get_engine():
    return st.session_state["engine"]


def insert_user(user_name, phone_number, email, max_loans):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO users (user_name, phone_number, email, max_loans)
                     VALUES (:user_name, :phone_number, :email, :max_loans)"""),
            {"user_name": user_name, "phone_number": phone_number, "email": email, "max_loans": max_loans}
        )


def get_user(user_id):
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT * FROM users WHERE user_id=:user_id"), {"user_id": user_id}
        ).mappings().first()

def get_all_users():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM users", conn)


def update_user(user_id, user_name, phone_number, email, max_loans):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("""UPDATE users SET user_name=:user_name, phone_number=:phone_number,
                     email=:email, max_loans=:max_loans WHERE user_id=:user_id"""),
            {"user_id": user_id, "user_name": user_name, "phone_number": phone_number,
             "email": email, "max_loans": max_loans}
        )
        return result.rowcount


def delete_user(user_id):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text("DELETE FROM users WHERE user_id=:user_id"), {"user_id": user_id})
        return result.rowcount

def get_total_users():
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
