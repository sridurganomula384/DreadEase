import streamlit as st
import sqlite3
from streamlit_js_eval import streamlit_js_eval as sj

# Function to connect to the database
def connect_db():
    return sqlite3.connect('users.db')

# Function to validate the secret key and email
def validate_secret_key(email, secret_key):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=? AND secret_key=?', (email, secret_key))
    result = c.fetchone()
    conn.close()
    return result

# Function to reset the password
def reset_password(email, new_password):
    conn = connect_db()
    c = conn.cursor()
    c.execute('UPDATE users SET password=? WHERE email=?', (new_password, email))
    conn.commit()
    conn.close()

# Reset Password page layout
def reset_password_page(navigate_to):
    st.title("Reset Password")

    email = st.text_input("Email", placeholder="Enter your email")
    secret_key = st.text_input("Secret Key", placeholder="Enter your secret key")
    new_password = st.text_input("New Password", placeholder="Enter your new password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reset Password"):
            if not email:
                st.error("Email field is empty.")
            elif not secret_key:
                st.error("Secret Key field is empty.")
            elif not new_password:
                st.error("New Password field is empty.")
            else:
                if validate_secret_key(email, secret_key):
                    reset_password(email, new_password)
                    st.success("Password has been reset!")
                    navigate_to('login')  # Navigate to the login page after reset
                    sj(js_expressions="parent.window.location.reload()")
                else:
                    st.error("Invalid email or secret key.")

    with col2:
        if st.button("Back to Login"):
            navigate_to('login')  # Navigate back to the login page
            sj(js_expressions="parent.window.location.reload()")
