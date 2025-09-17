import streamlit as st
import sqlite3
import time
from PIL import Image, ImageOps, ImageDraw
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container
from streamlit_js_eval import streamlit_js_eval as sj
import os
import requests

def navigate_to(page):
    st.query_params.from_dict({"page": page}) 

# Database connection
def connect_db():
    return sqlite3.connect('users.db')

# Function to verify if the secret key matches
def verify_secret_key(email, secret_key):
    conn=connect_db()
    c=conn.cursor()
    c.execute("SELECT secret_key FROM users WHERE email = ?", (email,))
    data = c.fetchone()
    if data:
        return data[0] == secret_key
    return False

# Logout functionality
def logout_user(email):
    if st.button("Logout"):
        conn=connect_db()
        c=conn.cursor()
        logout_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current time
        c.execute("UPDATE activity_log SET logout_time = ? WHERE email = ?", (logout_time, email))
        conn.commit()
        conn.close()
        with st.expander("Notification", expanded=True):
            st.success("Logged out successfully!")
            time.sleep(3)
            navigate_to('splash')
            sj(js_expressions="parent.window.location.reload()")

# Delete account functionality
def delete_account(email):
    conn=connect_db()
    c=conn.cursor()
    if st.button("Delete Account"):
        c.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        c.execute("DELETE FROM user_predictions WHERE email=?",(email,))
        conn.commit()
        c.execute("DELETE FROM activity_log WHERE email=?",(email,))
        conn.commit()
        c.execute("DELETE FROM dashboard_users WHERE email=?",(email,))
        conn.commit()

        with st.expander("Notification", expanded=True):
            st.success("Deleted Account successfully!")
            time.sleep(3)
            navigate_to('splash')
            sj(js_expressions="parent.window.location.reload()")

# Change password functionality using secret key
def change_password(email):
    secret_key_input = st.text_input("Enter your secret key", type='password')
    new_password = st.text_input("Enter new password", type='password')
    confirm_password = st.text_input("Confirm new password", type='password')
    if st.button("Change Password"):
        if new_password != confirm_password:
            st.error("Passwords do not match.")
        elif not verify_secret_key(email, secret_key_input):
            st.error("Secret key is incorrect.")
        else:
            st.expander(f"Your New Password: {new_password}")
            conn=connect_db()
            c=conn.cursor()
            c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            st.success("Password changed successfully!")
            sj(js_expressions="parent.window.location.reload()")

def create_rounded_image(image, size=(400, 400)):
    image = image.resize(size, Image.LANCZOS)
    # Create a mask for the rounded corners
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    # Create a new image with a transparent background
    rounded_image = ImageOps.fit(image, mask.size, Image.LANCZOS)
    rounded_image.putalpha(mask)
    return rounded_image

def fetch_email():
    conn=connect_db()
    c=conn.cursor()
    c.execute('SELECT email FROM dashboard_users ORDER BY rowid DESC LIMIT 1')
    email = c.fetchone()
    conn.close()
    return email[0] if email else None

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
    <a href="/contact">Contact Us</a></p>
    </div>

        """, 
        unsafe_allow_html=True
    )

# Settings page implementation
def settings():
    st.title("Settings")

    email = fetch_email()
    if email:
        # Create two columns
        col1, col2 = st.columns([1, 1])  # Adjust the column width if needed

        # Column 1: Logout and Delete Account buttons
        with col1:
            st.subheader("Logout")
            logout_user(email)

            st.subheader("Delete Account")
            delete_account(email)

        # Column 2: Logo display
        with col2:
            # Load and display the logo
            logo_url = "https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/dreadease_logo.png"
            response = requests.get(logo_url, stream=True)
            logo = Image.open(response.raw)  # Replace with the actual path to your logo
            rounded_image = create_rounded_image(logo)
            st.image(rounded_image, use_column_width=False, width=250)

        # Below both columns: Change Password option
        st.subheader("Change Password")
        change_password(email) 
    else:
        st.error("You need to be logged in to access settings.")
    if st.button('Back to Home'):
        navigate_to('dashboardl')
        sj(js_expressions="parent.window.location.reload()")
    page_footer()
