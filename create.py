import streamlit as st
import sqlite3
import uuid
import datetime
import time
from streamlit_js_eval import streamlit_js_eval as sj

# Function to connect to the database
def connect_db():
    return sqlite3.connect('users.db')

# Function to create a new user
def create_user(email, password, secret_key):
    conn = connect_db()
    c = conn.cursor()
    try:
        # Insert the user into the database
        c.execute('INSERT INTO users (email, password, secret_key) VALUES (?, ?, ?)', (email, password, secret_key))
        login_date = datetime.datetime.now().date()
        c.execute('INSERT INTO activity_log (email, login_date) VALUES (?, ?)', (email, login_date))
        conn.commit()
        st.success("Account created successfully!")
        return True
    except sqlite3.IntegrityError:
        # Handle the case where the email already exists
        st.error("An account with this email already exists.")
        return False
    finally:
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

# Create Account page layout function
def create_account_page(navigate_to):
    st.title("Create Account")

    # Input for new email and password
    new_email = st.text_input("New Email", placeholder="Enter a new email")
    new_password = st.text_input("New Password", placeholder="Enter a new password", type="password")

    if st.button("Submit"):
        if not new_email:
            st.error("Email field is empty.")
        elif not new_password:
            st.error("Password field is empty.")
        else:
            # Generate a unique secret key for the user
            st.write("The Secret Key is crucial to keep safe for future reference, as it is necessary for actions like password recovery and account verification.")
            secret_key = str(uuid.uuid4())
            
            # Create the user and log them in if successful
            if create_user(new_email, new_password, secret_key):
                # Display the secret key for future password resets
               
                with st.expander("Your Secret Key"):
                    st.write(f"Secret Key: {secret_key}")
                with st.spinner("Processing..."):
                    time.sleep(5)

                # Redirect to the dashboard (or any other page)
                navigate_to('test')  # Assuming 'dashboard' is the page to navigate after login
                sj(js_expressions="parent.window.location.reload()")

    # Button to go back to the login page
    if st.button("Back to Login"):
        navigate_to('login')
        sj(js_expressions="parent.window.location.reload()")
    page_footer()
