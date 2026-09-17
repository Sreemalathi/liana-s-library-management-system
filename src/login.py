import base64
import os
import sys

import streamlit as st
from sqlalchemy import create_engine, exc

sys.path.append("..")  # con_lib.py lives in the parent directory of src/
from con_lib import connection_string

APP_USERNAME = "admin"
APP_PASSWORD = "pswd1234"

ILLUSTRATION_PATH = os.path.join(os.path.dirname(__file__), "assets", "login_illustration.png")


def get_illustration_base64():
    try:
        with open(ILLUSTRATION_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


LOGIN_CSS = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #0f2b6b 0%, #1e5799 35%, #2ab6e0 60%, #ffffff 60%, #ffffff 100%);
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: transparent;
}

.login-left {
    height: 560px;
    padding: 2rem 1.5rem 1.5rem 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    text-align: center;
    overflow: visible;
}
.login-left h1 {
    font-size: 3.4rem;
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 1.5rem 0;
    text-shadow: 0 4px 16px rgba(0,0,0,0.25);
    letter-spacing: 0.5px;
}
.login-left img {
    max-width: 85%;
    max-height: 400px;
    width: auto;
    height: auto;
    filter: drop-shadow(0 10px 20px rgba(0,0,0,0.25));
}

/* the one bordered container on this page = the right-hand sign-in box (border only, no fill) */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"] > div,
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
    background: transparent !important;
    background-color: transparent !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    height: 560px;
    border: none !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 0 1.5rem;
}
div[data-testid="stVerticalBlockBorderWrapper"] .stTextInput,
div[data-testid="stVerticalBlockBorderWrapper"] .stFormSubmitButton {
    width: 100%;
}

div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"],
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p,
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] span,
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] label {
    color: #000000 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] input {
    color: #000000 !important;
    background-color: #ffffff !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] .stTextInput input {
    border: 2px solid #2f6690 !important;
    border-radius: 6px !important;
    background-color: #ffffff !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] .stTextInput div[data-baseweb="input"] {
    border: none !important;
    box-shadow: none !important;
    background-color: #ffffff !important;
}

.login-avatar {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: #2f6690;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.6rem;
    color: white;
    margin: 0 auto 0.75rem auto;
}
.login-signin-title {
    text-align: center;
    color: #1e5799;
    letter-spacing: 2px;
    font-weight: 800;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
}

div[data-testid="stFormSubmitButton"] button {
    display: block;
    margin: 0.5rem auto 0 auto;
    background: #ffffff;
    color: #000000;
    border: 1px solid #2f6690;
    border-radius: 6px;
    padding: 0.65rem 3rem;
    font-weight: 700;
    font-size: 1.05rem;
    width: auto;
}
div[data-testid="stFormSubmitButton"] button p {
    font-weight: 700;
    font-size: 1.05rem;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: #f0f0f0;
    color: #000000;
}
</style>
"""


def login():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.write("")
    st.write("")

    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        img_b64 = get_illustration_base64()
        img_tag = f'<img src="data:image/png;base64,{img_b64}" />' if img_b64 else ""
        st.markdown(
            f"""
            <div class="login-left">
                <h1>Liana's Library</h1>
                {img_tag}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        with st.container(border=True):
            st.markdown('<div class="login-avatar">👤</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-signin-title">SIGN IN</div>', unsafe_allow_html=True)

            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in")

    if submitted:
        if username == APP_USERNAME and password == APP_PASSWORD:
            try:
                engine = create_engine(connection_string)
                with engine.connect():
                    pass
                st.session_state["engine"] = engine
                st.session_state["login"] = "loggedin"
                st.rerun()
            except exc.OperationalError:
                st.error("Could not connect to the database. Check con_lib.py / the .env file.")
        else:
            st.warning("Username or password incorrect")
