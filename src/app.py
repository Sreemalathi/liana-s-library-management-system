import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, exc

from login import login
from books import insert_book, get_book, update_book, delete_book, get_all_books, set_availability, get_total_books
from users import insert_user, get_user, update_user, delete_user, get_all_users, get_total_users
from loan import create_loan, get_active_loan, extend_loan, return_loan, get_all_loans, get_loaned_count, get_overdue_count, get_most_borrowed_books
from reservation import create_reservation, get_all_reservations, get_next_waiting_reservation, mark_ready, fulfill_reservation, cancel_reservation

st.set_page_config(page_title="Liana's Library", page_icon="📚", layout="wide")


def get_title_options():
    return [""] + sorted(get_all_books()["title"].dropna().unique().tolist())


def get_user_name_options():
    return [""] + sorted(get_all_users()["user_name"].dropna().unique().tolist())


# ---------- DASHBOARD PAGE ----------

DASHBOARD_CARD_CSS = """
<style>
div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    height: 170px;
}
div[data-testid="column"] > div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
</style>
"""


def show_dashboard_page():
    st.markdown(DASHBOARD_CARD_CSS, unsafe_allow_html=True)

    st.subheader("Overview")
    stat_cols = st.columns(4)
    stats = [
        ("Total Books", get_total_books()),
        ("Total Users", get_total_users()),
        ("Loaned Books", get_loaned_count()),
        ("Overdue", get_overdue_count()),
    ]
    for col, (label, value) in zip(stat_cols, stats):
        with col:
            with st.container(border=True):
                st.metric(label, value)

    st.divider()
    st.subheader("Most Popular Books")

    popular_df = get_most_borrowed_books(limit=3)

    if popular_df.empty:
        st.info("No loan history yet — lend a book out to see popularity stats here.")
    else:
        pop_cols = st.columns(3)
        for col, (_, row) in zip(pop_cols, popular_df.iterrows()):
            with col:
                with st.container(border=True):
                    st.markdown(f"<span style='font-size:1.3em; font-weight:bold'>{row['title']}</span>", unsafe_allow_html=True)
                    st.write(f"by {row['author']}")
                    st.write(f"Borrowed {row['times_borrowed']} time(s)")


# ---------- USERS PAGE ----------

def show_users_page():
    st.subheader("All Users")
    st.dataframe(get_all_users(), hide_index=True, use_container_width=True)
    st.divider()

    if "user_op" not in st.session_state:
        st.session_state.user_op = None

    op_cols = st.columns(3)
    if op_cols[0].button("Insert", use_container_width=True, key="user_insert_btn"):
        st.session_state.user_op = "Insert"
    if op_cols[1].button("Update", use_container_width=True, key="user_update_btn"):
        st.session_state.user_op = "Update"
    if op_cols[2].button("Delete", use_container_width=True, key="user_delete_btn"):
        st.session_state.user_op = "Delete"

    operation = st.session_state.user_op

    if operation == "Insert":
        with st.form("insert_user_form"):
            user_name = st.text_input("User Name")
            phone_number = st.text_input("Phone Number")
            email = st.text_input("Email")
            max_loans = st.number_input("Max Loans", min_value=1, value=5, step=1)
            submitted = st.form_submit_button("Insert")

        if submitted:
            try:
                insert_user(user_name, phone_number, email, max_loans)
                st.success(f"Added user '{user_name}'")
                st.rerun()
            except exc.IntegrityError:
                st.warning("This email address is already registered.")

    elif operation == "Update":
        col1, col2 = st.columns(2)
        id_search = col1.text_input("Search by User ID", key="user_update_id_search")
        name_search = col2.selectbox("Search by User Name", get_user_name_options(), key="user_update_name_search")

        if id_search or name_search:
            df = get_all_users()
            if id_search:
                df = df[df["user_id"].astype(str).str.contains(id_search, case=False, na=False)]
            if name_search:
                df = df[df["user_name"] == name_search]

            df = df.copy()
            df.insert(0, "Select", False)

            edited_df = st.data_editor(
                df,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=[col for col in df.columns if col != "Select"],
                hide_index=True,
                use_container_width=True,
                key="user_update_editor",
            )

            selected_ids = edited_df[edited_df["Select"]]["user_id"].tolist()
            if len(selected_ids) == 1:
                user = get_user(selected_ids[0])
                st.session_state["user_to_update"] = dict(user)
            elif len(selected_ids) > 1:
                st.warning("Select only one user to edit.")
                st.session_state.pop("user_to_update", None)
            else:
                st.session_state.pop("user_to_update", None)

            if "user_to_update" in st.session_state:
                user = st.session_state["user_to_update"]
                with st.form("update_user_form"):
                    st.write(f"**User ID:** {user['user_id']}")
                    user_name = st.text_input("User Name", value=user["user_name"])
                    phone_number = st.text_input("Phone Number", value=user["phone_number"] or "")
                    email = st.text_input("Email", value=user["email"])
                    max_loans = st.number_input("Max Loans", min_value=1, value=int(user["max_loans"]), step=1)
                    update_clicked = st.form_submit_button("Update User")

                if update_clicked:
                    try:
                        rowcount = update_user(user["user_id"], user_name, phone_number, email, max_loans)
                        if rowcount == 1:
                            st.success(f"User ID {user['user_id']} updated successfully!")
                            st.session_state.pop("user_to_update")
                            st.rerun()
                        else:
                            st.warning("User could not be updated")
                    except exc.IntegrityError:
                        st.warning("This email address is already registered.")

    elif operation == "Delete":
        col1, col2 = st.columns(2)
        id_search = col1.text_input("Search by User ID", key="user_delete_id_search")
        name_search = col2.selectbox("Search by User Name", get_user_name_options(), key="user_delete_name_search")

        df = get_all_users()
        if id_search:
            df = df[df["user_id"].astype(str).str.contains(id_search, case=False, na=False)]
        if name_search:
            df = df[df["user_name"] == name_search]

        df.insert(0, "Select", False)

        edited_df = st.data_editor(
            df,
            column_config={"Select": st.column_config.CheckboxColumn(required=True)},
            disabled=[col for col in df.columns if col != "Select"],
            hide_index=True,
            use_container_width=True,
        )

        if st.button("Delete Selected", key="user_delete_selected_btn"):
            selected_rows = edited_df[edited_df["Select"]][["user_id", "user_name"]]
            if selected_rows.empty:
                st.warning("No users selected.")
            else:
                deleted = []
                blocked = []
                for _, row in selected_rows.iterrows():
                    user_id, user_name = row["user_id"], row["user_name"]
                    try:
                        delete_user(user_id)
                        deleted.append(f"{user_name} (ID {user_id})")
                    except exc.IntegrityError:
                        blocked.append(f"{user_name} (ID {user_id})")

                st.session_state["user_delete_result"] = {"deleted": deleted, "blocked": blocked}
                st.rerun()

        if "user_delete_result" in st.session_state:
            result = st.session_state.pop("user_delete_result")
            if result["deleted"]:
                st.success(f"Deleted {len(result['deleted'])} user(s): {', '.join(result['deleted'])}")
            if result["blocked"]:
                st.warning(f"Could not delete (has loan/reservation history): {', '.join(result['blocked'])}")


# ---------- BOOKS PAGE ----------

def show_books_page():
    st.subheader("All Books")
    st.dataframe(get_all_books(), hide_index=True, use_container_width=True)
    st.divider()

    if "book_op" not in st.session_state:
        st.session_state.book_op = None

    op_cols = st.columns(3)
    if op_cols[0].button("Insert", use_container_width=True, key="book_insert_btn"):
        st.session_state.book_op = "Insert"
    if op_cols[1].button("Update", use_container_width=True, key="book_update_btn"):
        st.session_state.book_op = "Update"
    if op_cols[2].button("Delete", use_container_width=True, key="book_delete_btn"):
        st.session_state.book_op = "Delete"

    operation = st.session_state.book_op

    if operation == "Insert":
        with st.form("insert_book_form"):
            isbn = st.text_input("ISBN")
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            genre = st.selectbox("Genre", ["Fiction", "Non-fiction", "Literature", "Early Learning", "Childrens", "Education", "Programming", "Other"])
            book_language = st.selectbox("Language", ["English", "German", "French", "Spanish", "Italian", "Other"])
            submitted = st.form_submit_button("Insert")

        if submitted:
            insert_book(isbn, title, author, genre, book_language)
            st.success(f"Added '{title}'")
            st.rerun()

    elif operation == "Update":
        col1, col2 = st.columns(2)
        isbn_search = col1.text_input("Search by ISBN", key="book_update_isbn_search")
        title_search = col2.selectbox("Search by Book Title", get_title_options(), key="book_update_title_search")

        if isbn_search or title_search:
            df = get_all_books()
            if isbn_search:
                df = df[df["isbn"].str.contains(isbn_search, case=False, na=False)]
            if title_search:
                df = df[df["title"] == title_search]

            df = df.copy()
            df.insert(0, "Select", False)

            edited_df = st.data_editor(
                df,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=[col for col in df.columns if col != "Select"],
                hide_index=True,
                use_container_width=True,
                key="book_update_editor",
            )

            selected_isbns = edited_df[edited_df["Select"]]["isbn"].tolist()
            if len(selected_isbns) == 1:
                book = get_book(selected_isbns[0])
                st.session_state["book_to_update"] = dict(book)
            elif len(selected_isbns) > 1:
                st.warning("Select only one book to edit.")
                st.session_state.pop("book_to_update", None)
            else:
                st.session_state.pop("book_to_update", None)

            if "book_to_update" in st.session_state:
                book = st.session_state["book_to_update"]
                genre_options = ["Fiction", "Non-fiction", "Literature", "Early Learning", "Childrens", "Education", "Programming", "Other"]
                language_options = ["English", "German", "French", "Spanish", "Italian", "Other"]

                with st.form("update_book_form"):
                    st.write(f"**ISBN:** {book['isbn']}")
                    title = st.text_input("Book Title", value=book["title"])
                    author = st.text_input("Author", value=book["author"] or "")
                    genre = st.selectbox("Genre", genre_options, index=genre_options.index(book["genre"]) if book["genre"] in genre_options else 0)
                    book_language = st.selectbox("Language", language_options, index=language_options.index(book["book_language"]) if book["book_language"] in language_options else 0)
                    update_clicked = st.form_submit_button("Update Book")

                if update_clicked:
                    rowcount = update_book(book["isbn"], title, author, genre, book_language)
                    if rowcount == 1:
                        st.success(f"Book with ISBN {book['isbn']} updated successfully!")
                        st.session_state.pop("book_to_update")
                        st.rerun()
                    else:
                        st.warning("Book could not be updated")

    elif operation == "Delete":
        col1, col2 = st.columns(2)
        isbn_search = col1.text_input("Search by ISBN", key="book_delete_isbn_search")
        title_search = col2.selectbox("Search by Book Title", get_title_options(), key="book_delete_title_search")

        df = get_all_books()
        if isbn_search:
            df = df[df["isbn"].str.contains(isbn_search, case=False, na=False)]
        if title_search:
            df = df[df["title"] == title_search]

        df.insert(0, "Select", False)

        edited_df = st.data_editor(
            df,
            column_config={"Select": st.column_config.CheckboxColumn(required=True)},
            disabled=[col for col in df.columns if col != "Select"],
            hide_index=True,
            use_container_width=True,
        )

        if st.button("Delete Selected", key="book_delete_selected_btn"):
            selected_isbns = edited_df[edited_df["Select"]]["isbn"].tolist()
            if not selected_isbns:
                st.warning("No books selected.")
            else:
                deleted = []
                blocked = []
                for isbn in selected_isbns:
                    try:
                        delete_book(isbn)
                        deleted.append(isbn)
                    except exc.IntegrityError:
                        blocked.append(isbn)

                st.session_state["book_delete_result"] = {"deleted": deleted, "blocked": blocked}
                st.rerun()

        if "book_delete_result" in st.session_state:
            result = st.session_state.pop("book_delete_result")
            if result["deleted"]:
                st.success(f"Deleted {len(result['deleted'])} book(s): {', '.join(result['deleted'])}")
            if result["blocked"]:
                st.warning(f"Could not delete (has loan/reservation history): {', '.join(result['blocked'])}")


# ---------- LOANS PAGE ----------

def show_loans_page():
    operation = st.radio("Select Operation", ["Borrow", "Extend", "Return"], horizontal=True, key="loan_op")

    if operation == "Borrow":
        st.subheader("All Books")
        books_df = get_all_books().copy()
        books_df["status"] = books_df["is_available"].apply(lambda x: "Available" if x else "Unavailable")
        st.dataframe(
            books_df[["isbn", "title", "author", "genre", "book_language", "status"]],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.subheader("Loaned Books")
        loaned_df = get_all_loans()
        loaned_df = loaned_df[loaned_df["return_date"].isna()]
        st.dataframe(
            loaned_df[["loan_id", "isbn", "title", "user_id", "user_name", "due_date", "extension_count"]],
            hide_index=True,
            use_container_width=True,
        )
    st.divider()

    if operation == "Borrow":
        st.write("**Select Book(s)**")
        bcol1, bcol2 = st.columns(2)
        isbn_search = bcol1.text_input("Search by ISBN", key="borrow_isbn_search")
        title_search = bcol2.selectbox("Search by Book Title", get_title_options(), key="borrow_title_search")

        edited_books_df = pd.DataFrame(columns=["Select Book", "isbn", "title", "author", "genre", "book_language", "status"])

        if isbn_search or title_search:
            books_search_df = get_all_books()
            if isbn_search:
                books_search_df = books_search_df[books_search_df["isbn"].str.contains(isbn_search, case=False, na=False)]
            if title_search:
                books_search_df = books_search_df[books_search_df["title"] == title_search]

            books_search_df = books_search_df.copy()
            books_search_df["status"] = books_search_df["is_available"].apply(lambda x: "Available" if x else "Unavailable")
            books_search_df.insert(0, "Select Book", False)

            edited_books_df = st.data_editor(
                books_search_df[["Select Book", "isbn", "title", "author", "genre", "book_language", "status"]],
                column_config={"Select Book": st.column_config.CheckboxColumn(required=True)},
                disabled=[col for col in books_search_df.columns if col != "Select Book"],
                hide_index=True,
                use_container_width=True,
                key="borrow_books_editor",
            )

        st.write("**Select User**")
        ucol1, ucol2 = st.columns(2)
        id_search = ucol1.text_input("Search by User ID", key="borrow_user_id_search")
        name_search = ucol2.selectbox("Search by User Name", get_user_name_options(), key="borrow_user_name_search")

        edited_users_df = pd.DataFrame(columns=["Select User", "user_id", "user_name", "phone_number", "email", "max_loans"])

        if id_search or name_search:
            users_search_df = get_all_users()
            if id_search:
                users_search_df = users_search_df[users_search_df["user_id"].astype(str).str.contains(id_search, case=False, na=False)]
            if name_search:
                users_search_df = users_search_df[users_search_df["user_name"] == name_search]

            users_search_df = users_search_df.copy()
            users_search_df.insert(0, "Select User", False)

            edited_users_df = st.data_editor(
                users_search_df[["Select User", "user_id", "user_name", "phone_number", "email", "max_loans"]],
                column_config={"Select User": st.column_config.CheckboxColumn(required=True)},
                disabled=[col for col in users_search_df.columns if col != "Select User"],
                hide_index=True,
                use_container_width=True,
                key="borrow_users_editor",
            )

        if st.button("Borrow Selected", key="borrow_submit_btn"):
            selected_isbns = edited_books_df[edited_books_df["Select Book"]]["isbn"].tolist()
            selected_user_ids = edited_users_df[edited_users_df["Select User"]]["user_id"].tolist()

            if not selected_isbns:
                st.warning("Select at least one book.")
            elif len(selected_user_ids) != 1:
                st.warning("Select exactly one user.")
            else:
                user_id = selected_user_ids[0]
                borrowed = []
                unavailable = []
                for isbn in selected_isbns:
                    book = get_book(isbn)
                    if not book:
                        continue
                    if book["is_available"]:
                        create_loan(isbn, user_id)
                        set_availability(isbn, False)
                        borrowed.append(book["title"])
                    else:
                        unavailable.append({"isbn": isbn, "title": book["title"], "user_id": user_id})

                st.session_state["borrow_result"] = borrowed
                st.session_state["borrow_unavailable_list"] = unavailable
                st.rerun()

        if "borrow_result" in st.session_state:
            borrowed = st.session_state.pop("borrow_result")
            if borrowed:
                st.success(f"Borrowed: {', '.join(borrowed)}")

        if st.session_state.get("borrow_unavailable_list"):
            for item in list(st.session_state["borrow_unavailable_list"]):
                st.warning(f"'{item['title']}' is already loaned out.")
                if st.button(f"Reserve '{item['title']}'", key=f"reserve_{item['isbn']}"):
                    create_reservation(item["isbn"], item["user_id"])
                    st.success(f"Reservation created for '{item['title']}'.")
                    st.session_state["borrow_unavailable_list"] = [
                        x for x in st.session_state["borrow_unavailable_list"] if x["isbn"] != item["isbn"]
                    ]
                    st.rerun()

    elif operation == "Extend":
        st.write("**Select Loan(s) to Extend**")
        ecol1, ecol2 = st.columns(2)
        isbn_search = ecol1.text_input("Search by ISBN", key="extend_isbn_search")
        title_search = ecol2.selectbox("Search by Book Title", get_title_options(), key="extend_title_search")

        edited_loans_df = pd.DataFrame(columns=["Select Loan", "loan_id", "isbn", "title", "user_id", "user_name", "due_date", "extension_count"])

        if isbn_search or title_search:
            loans_df = get_all_loans()
            loans_df = loans_df[loans_df["return_date"].isna()]
            if isbn_search:
                loans_df = loans_df[loans_df["isbn"].str.contains(isbn_search, case=False, na=False)]
            if title_search:
                loans_df = loans_df[loans_df["title"] == title_search]

            loans_df = loans_df.copy()
            loans_df.insert(0, "Select Loan", False)

            edited_loans_df = st.data_editor(
                loans_df[["Select Loan", "loan_id", "isbn", "title", "user_id", "user_name", "due_date", "extension_count"]],
                column_config={"Select Loan": st.column_config.CheckboxColumn(required=True)},
                disabled=[col for col in loans_df.columns if col != "Select Loan"],
                hide_index=True,
                use_container_width=True,
                key="extend_loans_editor",
            )

        if st.button("Extend 14 days", key="extend_submit_btn"):
            selected_loan_ids = edited_loans_df[edited_loans_df["Select Loan"]]["loan_id"].tolist()

            if not selected_loan_ids:
                st.warning("Select at least one loan.")
            else:
                extended = []
                capped = []
                for loan_id in selected_loan_ids:
                    loan_row = edited_loans_df[edited_loans_df["loan_id"] == loan_id].iloc[0]
                    rowcount = extend_loan(loan_id)
                    if rowcount == 1:
                        extended.append(f"'{loan_row['title']}' extended by {loan_row['user_name']}")
                    else:
                        capped.append(f"'{loan_row['title']}' ({loan_row['user_name']})")

                st.session_state["extend_result"] = {"extended": extended, "capped": capped}
                st.rerun()

        if "extend_result" in st.session_state:
            result = st.session_state.pop("extend_result")
            if result["extended"]:
                st.success("; ".join(result["extended"]))
            if result["capped"]:
                st.warning(f"Could not extend (already extended twice or not found): {', '.join(result['capped'])}")

    elif operation == "Return":
        st.write("**Select Loan(s) to Return**")
        rcol1, rcol2 = st.columns(2)
        isbn_search = rcol1.text_input("Search by ISBN", key="return_isbn_search")
        title_search = rcol2.selectbox("Search by Book Title", get_title_options(), key="return_title_search")

        edited_returns_df = pd.DataFrame(columns=["Select Loan", "loan_id", "isbn", "title", "user_id", "user_name", "due_date"])

        if isbn_search or title_search:
            loans_df = get_all_loans()
            loans_df = loans_df[loans_df["return_date"].isna()]
            if isbn_search:
                loans_df = loans_df[loans_df["isbn"].str.contains(isbn_search, case=False, na=False)]
            if title_search:
                loans_df = loans_df[loans_df["title"] == title_search]

            loans_df = loans_df.copy()
            loans_df.insert(0, "Select Loan", False)

            edited_returns_df = st.data_editor(
                loans_df[["Select Loan", "loan_id", "isbn", "title", "user_id", "user_name", "due_date"]],
                column_config={"Select Loan": st.column_config.CheckboxColumn(required=True)},
                disabled=[col for col in loans_df.columns if col != "Select Loan"],
                hide_index=True,
                use_container_width=True,
                key="return_loans_editor",
            )

        if st.button("Return Selected", key="return_submit_btn"):
            selected_loan_ids = edited_returns_df[edited_returns_df["Select Loan"]]["loan_id"].tolist()

            if not selected_loan_ids:
                st.warning("Select at least one loan.")
            else:
                returned = []
                failed = []
                for loan_id in selected_loan_ids:
                    loan_row = edited_returns_df[edited_returns_df["loan_id"] == loan_id].iloc[0]
                    isbn = loan_row["isbn"]
                    rowcount = return_loan(loan_id)
                    if rowcount == 1:
                        next_reservation = get_next_waiting_reservation(isbn)
                        if next_reservation:
                            mark_ready(next_reservation["reservation_id"])
                            returned.append(f"{loan_row['title']} (held for reservation, user {next_reservation['user_id']})")
                        else:
                            set_availability(isbn, True)
                            returned.append(f"{loan_row['title']} (now available)")
                    else:
                        failed.append(str(loan_id))

                st.session_state["return_result"] = {"returned": returned, "failed": failed}
                st.rerun()

        if "return_result" in st.session_state:
            result = st.session_state.pop("return_result")
            if result["returned"]:
                st.success("Returned: " + "; ".join(result["returned"]))
            if result["failed"]:
                st.warning(f"Could not process return for loan ID(s): {', '.join(result['failed'])}")


# ---------- RESERVATIONS PAGE ----------

def show_reservations_page():
    st.subheader("Current Reservations")
    st.dataframe(get_all_reservations(), hide_index=True, use_container_width=True)
    st.divider()

    operation = st.radio("Select Operation", ["Reserve", "Fulfill", "Cancel"], horizontal=True, key="reservation_op")

    if operation == "Reserve":
        with st.form("reserve_form"):
            isbn = st.text_input("Book ISBN")
            user_id = st.text_input("User ID")
            submitted = st.form_submit_button("Reserve")

        if submitted:
            book = get_book(isbn)
            user = get_user(user_id)

            if not book:
                st.warning("No book found with that ISBN.")
            elif not user:
                st.warning("No user found with that User ID.")
            else:
                create_reservation(isbn, user_id)
                st.success(f"Reservation created for '{book['title']}' — {user['user_name']} is now in the queue.")
                st.rerun()

    elif operation == "Fulfill":
        ready_df = get_all_reservations()
        ready_df = ready_df[ready_df["status"] == "READY"]

        ready_df = ready_df.copy()
        ready_df.insert(0, "Select", False)

        edited_ready_df = st.data_editor(
            ready_df,
            column_config={"Select": st.column_config.CheckboxColumn(required=True)},
            disabled=[col for col in ready_df.columns if col != "Select"],
            hide_index=True,
            use_container_width=True,
            key="fulfill_reservations_editor",
        )

        if st.button("Fulfill Selected", key="fulfill_submit_btn"):
            selected_ids = edited_ready_df[edited_ready_df["Select"]]["reservation_id"].tolist()
            if not selected_ids:
                st.warning("Select at least one reservation.")
            else:
                fulfilled = []
                failed = []
                for reservation_id in selected_ids:
                    rowcount = fulfill_reservation(reservation_id)
                    if rowcount == 1:
                        fulfilled.append(str(reservation_id))
                    else:
                        failed.append(str(reservation_id))

                st.session_state["fulfill_result"] = {"fulfilled": fulfilled, "failed": failed}
                st.rerun()

        if "fulfill_result" in st.session_state:
            result = st.session_state.pop("fulfill_result")
            if result["fulfilled"]:
                st.success(f"Fulfilled reservation(s): {', '.join(result['fulfilled'])}")
            if result["failed"]:
                st.warning(f"Could not fulfill (not found or not READY): {', '.join(result['failed'])}")

    elif operation == "Cancel":
        reservation_id = st.text_input("Reservation ID")
        if st.button("Cancel Reservation"):
            rowcount = cancel_reservation(reservation_id)
            if rowcount == 1:
                st.success(f"Reservation {reservation_id} cancelled.")
                st.rerun()
            else:
                st.warning("Could not cancel — reservation not found or already closed out.")


# ---------- MAIN APP ----------

def main_app():
    st.sidebar.title("📚 Liana's Library")

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    pages = ["Dashboard", "Users", "Books", "Loans", "Reservations"]
    for p in pages:
        if st.sidebar.button(p, use_container_width=True):
            st.session_state.page = p

    page = st.session_state.page
    st.title("📚 Library Management System")

    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Users":
        show_users_page()
    elif page == "Books":
        show_books_page()
    elif page == "Loans":
        show_loans_page()
    elif page == "Reservations":
        show_reservations_page()


# ---------- GATE ----------

if st.session_state.get("login") == "loggedin":
    main_app()
else:
    login()