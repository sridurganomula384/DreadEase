import streamlit as st
import login
import create
import dashboardt
import dashboardl
import test
import database
import user
import daily_tasks
import settings
import password
import splash
import major_tasks

st.set_page_config(
    page_title="DreadEase", 
    layout="wide",  # Use the entire screen width
    #initial_sidebar_state="collapsed"
)
# Call the function to create the database and tables
database.create_db()
# Get the current page from query parameters
query_params = st.query_params.to_dict()
current_page = query_params.get('page', 'splash')

# Function to handle navigation using query parameters
def navigate_to(page):
    st.query_params.from_dict({"page": page})

# Display the appropriate page based on the query parameter
if current_page == 'splash':
    splash.splash_page()
if current_page == 'login':
    login.login_page(navigate_to)
elif current_page == 'password':
    password.reset_password_page(navigate_to)
elif current_page == 'create':
    create.create_account_page(navigate_to)
elif current_page == 'dashboardt':
    dashboardt.dashboardt_page()
elif current_page == 'test':
    test.prediction_page()
elif current_page == 'dashboardl':
    dashboardl.dashboardl_page()
elif current_page == 'user':
    user.profile()
elif current_page == 'daily_tasks':
    daily_tasks.daily_tasks()
elif current_page == 'settings':
    settings.settings()
elif current_page == 'major_tasks':
    major_tasks.major_tasks()
