import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import calendar
from PIL import Image, ImageDraw,ImageOps
from streamlit_extras.stylable_container import stylable_container
from streamlit_js_eval import streamlit_js_eval as sj
import os
import requests

def navigate_to(page):
    st.query_params.from_dict({"page": page})
# Function to connect to the database
def connect_db():
    return sqlite3.connect('users.db')

def fetch_sec(email):
    conn=connect_db()
    c=conn.cursor()
    c.execute('SELECT secret_key FROM users WHERE email=?',(email,))
    sec=c.fetchone()
    conn.close()
    return sec[0] if sec else None

def fetch():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT email FROM dashboard_users ORDER BY rowid DESC LIMIT 1')
    email= c.fetchone()
    conn.close()
    return email[0] if email else None

# Function to fetch user data from user_predictions
def fetch_user_data(email):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT name, age,gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level FROM user_predictions WHERE email=?', (email,))
    result = c.fetchone()
    conn.close()
    return result

# Function to fetch user activity streak
def fetch_activity_streak(email):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT login_date FROM activity_log WHERE email=? ORDER BY login_date DESC', (email,))
    activity_dates = [row[0] for row in c.fetchall()]
    #st.write(activity_dates)
    conn.close()
    
    streak_days = {}
    #st.write(activity_dates)
    for date in activity_dates:
        streak_days[date] = True  # Mark the date as active

    return streak_days

def display_calendar(year, month, active_days):
    # Get the first day of the month and the number of days in the month
    first_day = datetime(year, month, 1)
    last_day = (first_day + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    days_in_month = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    active_days_set = set(active_days)
    st.write(active_days)

    # Display the calendar
    calendar_html = '<table style="border-collapse: collapse;">'
    calendar_html += '<tr>' + ''.join(['<th style="border: 1px solid black; padding: 5px; ">' + day.strftime('%a') + '</th>' for day in days_in_month[:7]]) + '</tr>'
    
    for week in range(0, len(days_in_month), 7):
        calendar_html += '<tr>'
        for day in days_in_month[week:week + 7]:
            is_active = day.strftime('%Y-%m-%d') in active_days_set            
            cell_style = f"background-color: {'lightgreen' if is_active else 'white'}; color: black;"
            calendar_html += f'<td style="border: 1px solid black; padding: 5px; {cell_style}">{day.day}</td>'
        calendar_html += '</tr>'
    
    calendar_html += '</table>'
    st.markdown(calendar_html, unsafe_allow_html=True)

# Usage in your user profile page
def create_rounded_image(image, size=(300, 300)):
    image = image.resize(size, Image.LANCZOS)
    # Create a mask for the rounded corners
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    # Create a new image with a transparent background
    rounded_image = ImageOps.fit(image, mask.size, Image.LANCZOS)
    rounded_image.putalpha(mask)
    return rounded_image

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

def profile():
    st.title("User Profile")
    with stylable_container(
        key="user_b",
        css_styles="""*{
        font-size:15px;
        /*background-color:#e5a7b3;*/}""",
        
    ):

        email = fetch()
        user_data = fetch_user_data(email)  # Get active days for the logged-in user
        streak_days = fetch_activity_streak(email)
        #st.title("User Profile")
        col1, x,col2 = st.columns([1.2,0.1,1])
        if user_data:
            name, age,gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level = user_data
            with col1:
                st.subheader("User Details")

                if selected_symptoms:
                # Remove extra spaces and split by comma
                    selected_symptoms = selected_symptoms.replace("'", "").strip()
                    selected_symptoms_list = [symptom.strip() for symptom in selected_symptoms.split(',') if symptom.strip()]
                    #st.subheader("User Details")
                    st.write(f"**Name:** {name}")
                    st.write(f"**Age:** {age}")
                    st.write(f"**Gender:** {gender}")
                    st.write(f"**Frequency:** {frequency}")
                    st.write(f"**Fear Of:** {fear_of}")
                    st.write(f"**Selected Symptoms:** {selected_symptoms}")
                    st.write(f"**Duration:** {duration}")
                    st.write(f"**Predicted Phobia Type:** {predicted_phobia_type}")
                    st.write(f"**Predicted Phobia Level:** {predicted_phobia_level}")
        
            with col2:
                st.subheader("Upload Profile Photo")
            
                # Default image based on gender
                default_image_path = ""
                if gender.lower() == "male":
                    default_image_path = "https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/2.png"  # Update with your image path
                elif gender.lower() == "female":
                    default_image_path = "https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/1.png"  # Update with your image path
                else:
                    #st.write("hiii")
                    default_image_path = "https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/3.jpeg"  # Default for others or no gender specified
                      
            # File uploader for user to upload their own picture
                #default_image = st.image(default_image_path, caption="Default Profile Photo", use_column_width=False, width=150)
                response = requests.get(default_image_path, stream=True)
                default_image = Image.open(response.raw)
                rounded_image = create_rounded_image(default_image)
                st.image(rounded_image, caption="Default Profile Photo", use_column_width=False, width=150)
        
            st.subheader("Activity Streak")
        
            current_year = datetime.now().year
            current_month = datetime.now().month

            year = st.selectbox("Select Year", range(2023, current_year + 1), index=current_year-2023)
            month_names = list(calendar.month_name)[1:]  # Exclude the first entry (empty string)
            month_mapping = {name: index for index, name in enumerate(month_names, start=1)}

    # User selects month by name
            month_name = st.selectbox("Select Month", month_names,index=current_month-1)
            month = month_mapping[month_name]
            display_calendar(year,month,streak_days)
            

            st.subheader("Account Details:")
            st.write(f"**Email:** {email}")
            st.write(f"**Secret Key:** {fetch_sec(email)}")

            st.write("\n")
            st.write("\n")
            st.write("\n")

        

    # Now use the standard Streamlit button
            with stylable_container(
                key="user_home",
                css_styles="""            
                div[data-testid="stButton"]{
                display: block;
                margin: 0 auto;
                padding: 0px 2px; /* Reduced padding for height and width */
                text-align: center; 
                text-decoration: none; /* No underline */
                font-size: 25px; /* Smaller font size */
                border-radius: 5px; /* Rounded corners */
                cursor: pointer; /* Pointer on hover */
                width: 100px; 
                border: #45a049;/* Set a fixed width */}

                div[data-testid="stButton"] button:hover{
                background-color: #45a049;
                color: 2px solid #ffffff;}""",
        ):
                if st.button("Go to Home"):
                    navigate_to('dashboardl')
                    sj(js_expressions="parent.window.location.reload()")
            
        else:
            st.warning("No user data found.")
    
    page_footer()
