import streamlit as st
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_js_eval import streamlit_js_eval as sj

def navigate_to(page):
    st.query_params.from_dict({"page": page})

# Function to connect to the database
def connect_db():
    return sqlite3.connect('users.db')

def retrieve_users(email):
    conn=connect_db()
    c = conn.cursor()
    c.execute('SELECT email,name,age,gender,frequency,fear_of,selected_symptoms,duration,predicted_phobia_type,predicted_phobia_level FROM user_predictions WHERE email=?', (email,))
    result = c.fetchone()    
    conn.close()
    return result

# Function to fetch the latest email from the account creation database
def fetch():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT email FROM user_predictions ORDER BY rowid DESC LIMIT 1')
    email = c.fetchone()
    conn.close()
    return email[0] if email else None

def fetch_name(email):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT name FROM user_predictions WHERE email=?', (email,))
    result = c.fetchone()
    conn.close()
    return result[0]

def insert_users(email, name, age, gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level):
    with connect_db() as conn:
        c = conn.cursor()
        # Check if the email already exists
        c.execute('SELECT email FROM dashboard_users WHERE email=?', (email,))
        existing_email = c.fetchone()

        if existing_email:
            c.execute('SELECT checked_precautions,last_checked_date FROM dashboard_users WHERE email=?',(email,))
            #res=c.fetchone()
            x,y=c.fetchone()
            c.execute('''
                DELETE FROM dashboard_users WHERE email = ?
                ''', (email,))
            c.execute('INSERT INTO dashboard_users (email, name, age, gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level,checked_precautions,last_checked_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                  (email, name, age, gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level,x,y))
            return
            #st.warning("This email is already registered in the database.")

        # If the email does not exist, insert the new user
        c.execute('INSERT INTO dashboard_users (email, name, age, gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level) VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (email, name, age, gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level))
        conn.commit()

import requests

def contact_us():
    st.subheader("Contact Us")
    st.write("Have any questions or feedback? Please fill out the form below to reach us!")

    # User provides their email and message
    user_email = st.text_input("Your Email")
    user_message = st.text_area("Your Message")

    # Send message button
    if st.button("Send Message"):
        if user_email and user_message:
            data = {
                'user_email': user_email,
                'user_message': user_message
            }
            try:
                response = requests.post("http://192.168.31.228/dreadease/send_email.php", data=data)
                if response.status_code == 200:
                    st.success("Your message has been sent successfully! We will get back to you soon.")
                else:
                    st.error("Failed to send the message. Please try again later.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please fill in all fields.")

def fetch_coins(email):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT coins FROM dashboard_users WHERE email=?', (email,))
    coins = c.fetchone()
    conn.close()
    return coins[0] if coins else 0

def update_coins(email, new_coins):
    conn = connect_db()
    c = conn.cursor()
    c.execute('UPDATE dashboard_users SET coins = coins + ? WHERE email = ?', (new_coins, email))
    conn.commit()
    conn.close()

def check_precautions_completed(email):
    # Implement your logic here to check if all precautions have been completed
    # Return True if completed, else False
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT checked_precautions FROM dashboard_users WHERE email=?', (email,))
    completed = c.fetchone()
    conn.close()
    if completed and completed[0]:  # Check if completed is not None
        precautions_list = completed[0].split(',')  # Split by comma
        return len(precautions_list) >= 4  # Return True if all precautions are completed
    return False  # Assuming checked_precautions is a text column

def fire_streak(email):
    if check_precautions_completed(email):
        current_coins = fetch_coins(email)
        new_coins = 5  # Reward for completing all precautions
        if current_coins==None:
            current_coins=0
        x=current_coins+new_coins
        update_coins(email, x)
        y="🔥" * (x // 5)
        if (x//5)>=5:
            y="❤️"*(x//25)
        st.success(y)#Fire Streak Activated! You've earned 5 coins!")
        st.write(f"Total Coins: {x}")
    else:
        st.warning("Complete all precautions to activate Fire Streak!")

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

def fetch_phobia_data(email):    
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT predicted_phobia_type, predicted_phobia_level FROM user_predictions WHERE email=?', (email,))
    result = c.fetchone()
    conn.close()
    return result

def sidebar_menu(email):
    st.sidebar.title(f'Hello, {str(fetch_name(email))}')
    page = st.sidebar.radio("Go to", ("User Account", "Daily Tasks", "Settings"),index=None, key="sidebar_menu")
    #st.stop()
    return page

def dashboardt_page():
    email = fetch()  # Get email from create_account database
    #st.write("HIII")
    email,name,age,gender,frequency,fear_of,selected_symptoms,duration,predicted_phobia_type,predicted_phobia_level=retrieve_users(email)
    insert_users(email,name,age,gender,frequency,fear_of,selected_symptoms,duration,predicted_phobia_type,predicted_phobia_level)
    
    '''if email:
        st.title("Phobia Prediction Dashboard")'''
        
        # Fire Streak Feature
    col1, x,col2 = st.columns([1.5,0.4,0.5])  # Divide the page into two columns
    with col1:
        if email:
            st.title("Phobia Prediction Dashboard")
            #st.success(f"Welcome, {name}!")

            # Display user data or other relevant information
            '''st.write(f"Age: {age}")
            st.write(f"Gender: {gender}")'''
            st.success(f"Predicted Phobia Type: {predicted_phobia_type}")
            st.success(f"Predicted Phobia Level: {predicted_phobia_level}")

        else:
            st.warning("No user found in account creation database.")

    with col2:
        if predicted_phobia_level != 'Major':
        # Fire Streak Feature
            st.write('\n')
            st.write('\n')
            st.write('\n')
            fire_streak(email)  # Check and display fire streak
         
        
    if st.button('User Account'):
        navigate_to('user')
        sj(js_expressions="parent.window.location.reload()")
        '''else:
            st.warning("No prediction has been made yet. Please go back and complete the prediction.")'''
    '''else:
        st.warning("No user found in account creation database.")'''
    selected_page = sidebar_menu(email)
    # Conditional logic for rendering the selected page
    if selected_page == "User Account":
        navigate_to('user')
        sj(js_expressions="parent.window.location.reload()")
    elif selected_page == "Daily Tasks":
        if predicted_phobia_level=='Major':
            navigate_to('major_tasks')
            sj(js_expressions="parent.window.location.reload()")
        else:
            navigate_to('daily_tasks')
            sj(js_expressions="parent.window.location.reload()")
    elif selected_page == "Settings":
        #st.stop()
        navigate_to('settings')
        sj(js_expressions="parent.window.location.reload()")
    contact_us()
    page_footer()
    
