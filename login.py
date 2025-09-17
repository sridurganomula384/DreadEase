import streamlit as st
import sqlite3
import datetime
from streamlit_js_eval import streamlit_js_eval as sj

# Function to connect to the database
def connect_db():
    return sqlite3.connect('users.db')

# Function to check login credentials
def login_user(email, password):
    conn = connect_db()
    c = conn.cursor()
    
    # Check the users table for valid credentials
    c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
    user_result = c.fetchone()
    
    # If login is successful, check for account in user_predictions table
    if user_result:
        c.execute('SELECT * FROM user_predictions WHERE email=?', (email,))
        account_check = c.fetchone()
        conn.close()
        return True, account_check is not None  # Return login success and account existence
    conn.close()
    return False, False 

# Function to save the login session and log the login date
def save_login_session(email):
    conn = connect_db()
    c = conn.cursor()
    # Log the login date
    login_date = datetime.datetime.now().date()
    logout_time=None
    c.execute('INSERT INTO activity_log (email, login_date,logout_time) VALUES (?,?,?)', (email, login_date,logout_time))
    
    conn.commit()
    conn.close()

def page_footer():
    # Add custom CSS for styling the footer
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            color: #333;
            border-top: 1px solid #eaeaea;
        }
        .footer a {
            color: #0366d6;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # Add footer content
    st.markdown(
        """<div class="footer">
    <p>© 2024 DreadEase. All rights reserved.</p>
    <p>Powered by Streamlit | <a href="mailto:dreadease.18@gmail.com" target="_blank">Mail Id</a> | 
    <a href="https://github.com/Reethz30" target="_blank">GitHub</a> | 
    <a href="https://www.linkedin.com/in/buddi-reethika-chovudary-3382a0255/" target="_blank">LinkedIn</a> |
    <a href="#contact_us">Contact Us</a></p>
    </div>

        """, 
        unsafe_allow_html=True
    )

# Login page layout function
def login_page(navigate_to):
    st.title("Login Page")
    # Email and Password Input
    email = st.text_input("Email", placeholder="Enter your email", key="email_input")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    
    if st.button("Login"):
        if not email:
            st.error("Email field is empty.")
        elif not password:
            st.error("Password field is empty.")
        else:
            login_success, account_exists = login_user(email, password)
            if login_success:
                if account_exists:
                    st.success("Login successful!")
                    save_login_session(email)  # Save session with expiration
                    navigate_to('dashboardl')  # Navigate to the dashboard page
                    sj(js_expressions="parent.window.location.reload()")
                else:
                    st.error("You have no account associated with this email.")
            else:
                st.error("Invalid email or password")


    # Line to separate the options
    st.markdown("---")
    
    # Forgot Password and Create Account buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Forgot Password"):
            navigate_to('password')  # Navigate to the reset password page
            sj(js_expressions="parent.window.location.reload()")

    with col2:
        if st.button("Create Account"):
            navigate_to('create')  # Navigate to the create account page
            sj(js_expressions="parent.window.location.reload()")
    page_footer()
