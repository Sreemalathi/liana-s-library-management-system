import streamlit as st
import pandas as pd
from sqlalchemy import text


def get_engine():
    return st.session_state["engine"]


def insert_book(isbn, title, author, genre, book_language):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO books (isbn, title, author, genre, book_language)
                     VALUES (:isbn, :title, :author, :genre, :lang)"""),
            {"isbn": isbn, "title": title, "author": author, "genre": genre, "lang": book_language}
        )


def get_book(isbn):
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT * FROM books WHERE isbn=:isbn"), {"isbn": isbn}
        ).mappings().first()


def get_all_books():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM books", conn)


def update_book(isbn, title, author, genre, book_language):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("""UPDATE books SET title=:title, author=:author, genre=:genre, book_language=:lang
                     WHERE isbn=:isbn"""),
            {"isbn": isbn, "title": title, "author": author, "genre": genre, "lang": book_language}
        )
        return result.rowcount


def delete_book(isbn):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text("DELETE FROM books WHERE isbn=:isbn"), {"isbn": isbn})
        return result.rowcount

def set_availability(isbn, is_available):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("UPDATE books SET is_available=:avail WHERE isbn=:isbn"),
            {"avail": is_available, "isbn": isbn}
        )
        return result.rowcount

def get_total_books():
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM books")).scalar()
