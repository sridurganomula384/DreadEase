import pandas as pd
import sqlite3
import streamlit as st
from streamlit_js_eval import streamlit_js_eval as sj

def navigate_to(page):
    st.query_params.from_dict({"page": page}) 

def connect_db():
    return sqlite3.connect('users.db')

def fetch_email():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM dashboard_users ORDER BY rowid DESC LIMIT 1')
    email = cursor.fetchone()
    conn.close()
    return email[0] if email else None


def major_tasks():
    st.title("DreadEase - Consultant Finder")
    excel_file_path = 'https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/Major_Links.xlsx' 
    df = pd.read_excel(excel_file_path)
    email = fetch_email()
    if not email:
        st.error("No user email found.")
        return
    available_states = df['Location'].unique().tolist()
    selected_state = st.selectbox('Select your state:', available_states)
    state_consultants = df[df['Location'] == selected_state]
    if state_consultants.empty:
        st.warning("No consultants found for the selected state.")
        return
    st.write(f"## Consultants in {selected_state}")
    for index, consultant in state_consultants.head(3).iterrows():
        st.write(f"**Consultant**: {consultant['Suffix']} {consultant['Consultant']}")
        st.write(f"**Link**: [Click here]({consultant['Link']})")
        st.write("---")
    if st.button('Back to Home'):
        navigate_to('dashboardl')
        sj(js_expressions="parent.window.location.reload()")
