# 📚 Liana's Library

A simple library management system built to turn an informal book-lending process into a structured workflow for tracking books, borrowers, loans, and reservations.

## Business Case

Liana was informally lending books to people she knew, there was no track of who had a book, when it was due, or whether a book was already promised to someone else. This system provides a structured lending workflow with real-time availability, borrower and due-date tracking, and reservations for books that are currently on loan.

## Features

- **Dashboard** — at-a-glance stats for total books, total users, currently loaned books, and overdue loans, plus a "Most Popular Books" view based on loan history.
- **Books** — add, search, update, and delete books, with real-time availability tracking.
- **Users** — manage the borrower registry (name, phone, email, max loans), with search-and-select editing.
- **Loans** — borrow, extend, and return books, with automatic availability tracking and overdue detection.
- **Reservations** — reserve books that are currently on loan, get notified when they become ready, and fulfill or cancel reservations.
- **Access Control** — simple username/password login for application access.

**Demo login:** `admin` / `pswd1234` (hardcoded for this project's current scope — not intended for production use).

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io/) |
| Database | MySQL |
| Database Access | SQLAlchemy + PyMySQL |
| Data Handling | pandas |
| Configuration | python-dotenv |

## Project Structure

The app follows a simple modular structure. **`app.py` handles the UI and page routing**, while each database table has its own module (`books.py`, `users.py`, `loan.py`, `reservation.py`) responsible for its CRUD operations and business logic.

`app.py` does not interact with the database directly. It calls functions from these modules, keeping the UI and database logic separated.

Database setup is maintained in **`sql_files/`**, while **`con_lib.py`** manages the shared database connection configuration.

## Repository Structure

```
liana-s-library-management-system/
├── src/
│   ├── app.py            # Page routing, layout, and UI for every page
│   ├── login.py          # Login screen and session auth
│   ├── books.py          # Book CRUD + availability logic
│   ├── users.py          # User (borrower) CRUD
│   ├── loan.py           # Borrow / extend / return + loan stats
│   ├── reservation.py    # Reserve / fulfill / cancel reservations
│   └── assets/           # Images used in the UI
├── sql_files/
│   ├── mylibrary_schema.sql       # Database schema (tables + foreign keys)
│   └── my_library_dataupdate.sql  # Sample seed data
├── notebook/
│   └── crud_workflow.py  # Exploratory data-access workflow
├── con_lib.py             # Builds the SQLAlchemy connection string from .env
├── requirements.txt
└── .gitignore
```

## Database Schema

Four related tables:

- **books** (`isbn` PK) — title, author, genre, language, availability
- **users** (`user_id` PK) — name, phone, email, max loans
- **loans** (`loan_id` PK) — FKs to `books.isbn` and `users.user_id`, loan/due/return dates, extension tracking
- **reservations** (`reservation_id` PK) — FKs to `books.isbn` and `users.user_id`, status (`WAIT` / `READY` / `FULFILLED` / `CANCELLED` / `EXPIRED`)

Deleting a user or book with existing loan/reservation history is blocked by the foreign key constraints, so lending history is never silently lost.

## Author

Sree Malathi — [LinkedIn](https://linkedin.com/in/sree-malathik)
