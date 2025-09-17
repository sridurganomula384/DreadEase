import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval as sj

def navigate_to(page):
    st.query_params.from_dict({"page": page}) 

# Function to connect to the database
def connect_db():
    return sqlite3.connect('users.db')

def fetch():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT email FROM dashboard_users ORDER BY rowid DESC LIMIT 1')
    email = c.fetchone()
    conn.close()
    return email[0] if email else None

def fetch_phobia_data(email):    
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT predicted_phobia_type, predicted_phobia_level FROM user_predictions WHERE email=?', (email,))
    result = c.fetchone()
    conn.close()
    return result

def load_precautions():
    # Load the Excel file
    excel_file_path = 'https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/symptoms.xlsx'
    df = pd.read_excel(excel_file_path)
    return df

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

def fetch_checked_precautions(email):
    conn = connect_db()
    c = conn.cursor()
    '''c.execute('SELECT age,fear_of,last_checked_date FROM dashboard_users WHERE email=? ',(email,))
    res=c.fetchone()
    st.write(res)'''
    c.execute('''SELECT name,checked_precautions, last_checked_date FROM dashboard_users WHERE email=?''', (email,))
    result = c.fetchone()
    #st.write(f"Fetched data for {email}: {result}")
    conn.close()
    
    # Return (None, None) if no results, or if either checked_precautions or last_checked_date is missing
    if result:# and result[0] and result[1]:
        return result
    return (None, None)

def update_checked_precautions(email, checked_precautions):
    conn = connect_db()
    c = conn.cursor()
    checked_precautions=','.join(checked_precautions)
    st.write(checked_precautions)
    c.execute('UPDATE dashboard_users SET checked_precautions=?, last_checked_date=? WHERE email=?', 
              (checked_precautions, datetime.now().date(), email))
    conn.commit()
    conn.close()

def daily_tasks():
    email = fetch()  # Fetch the user's email
    if email:
        phobia_data = fetch_phobia_data(email)
        
        if phobia_data:
            phobia_type, phobia_level = phobia_data
            st.title("Daily Tasks to Overcome Phobia")

            # Load the precautions from the Excel sheet
            precaution_df = load_precautions()
            if precaution_df.empty:
                st.warning("No precautions data loaded from Excel.")
                return

            phobia_type = str(phobia_type.strip().lower())
            phobia_level = phobia_level.lower()
            precaution_df['phobia'] = precaution_df['phobia'].str.strip()
            precaution_df['phobia'] = precaution_df['phobia'].str.lower()
            precaution_df['level'] = precaution_df['level'].str.lower()
            #st.write(precaution_df,precaution_df['phobia'],precaution_df['level'])
            
            #test_filter = precaution_df[precaution_df['phobia'] == 'nomophobia']
            #st.write("Test Filter Results:", test_filter, phobia_type)
            precautions_df=precaution_df
            filtered_precautions = precautions_df[
                (precautions_df['level'] == phobia_level)]
            #st.write("Filtered Precautions:", filtered_precautions)
            filtered_precautions = filtered_precautions[(precautions_df['phobia']==phobia_type)]
            #st.write("Filtered Precautions:", filtered_precautions)

            # Fetch previously checked precautions and the last checked date
            x,checked_precautions, last_checked_date = fetch_checked_precautions(email)
            #st.write(x,checked_precautions)

            # Reset checked precautions if the day has changed
            if last_checked_date and str(last_checked_date) != str(datetime.now().date()):
                #st.write(str(datetime.now().date()))
                checked_precautions = []  # Clear checked precautions for the new day
                update_checked_precautions(email, checked_precautions)

            # Display the precautions as checkboxes
            if not filtered_precautions.empty:
                # Convert checked_precautions from a comma-separated string to a list
                checked_precautions = checked_precautions.split(',') if checked_precautions else []
                #st.write(checked_precautions)
                current_checked = []

                for index, row in filtered_precautions.iterrows():
                    for i in range(1, 5):  # Loop through precaution1 to precaution4
                        precaution = row.get(f'precaution{i}')
                        if pd.notna(precaution):  # Ensure the precaution exists (not NaN)
                            # If the precaution was previously checked, lock it
                            if precaution in checked_precautions:
                                st.checkbox(
                                    precaution, 
                                    key=f'checkbox_{index}_{i}', 
                                    value=True,
                                    disabled=True  # Lock the checkbox if it was previously checked
                                )
                            else:
                                # If not previously checked, allow it to be checked
                                checkbox_state = st.checkbox(
                                    precaution, 
                                    key=f'checkbox_{index}_{i}', 
                                    value=False
                                )
                                
                                # Store current checked state in a list
                                if checkbox_state:
                                    current_checked.append(precaution)

                # Save button
                if st.button("Save Checked Precautions"):
                    # Update the database with the newly and previously checked precautions
                    #st.write(checked_precautions)
                    update_checked_precautions(email, current_checked + checked_precautions)
                    sj(js_expressions="parent.window.location.reload()")
                    #st.success("Your checked precautions have been saved!")

                # Check if all precautions are checked
                if len(current_checked) + len(checked_precautions) >= 4:
                    st.success("Great job! You've completed all your tasks! Keep it up!")
                    st.balloons()
                else:
                    st.warning("Keep going! Every small step you take brings you closer to overcoming your phobia.")
            else:
                st.warning("No precautions available for your phobia.")
        else:
            st.warning("No phobia data found.")
    else:
        st.warning("No user found in the database.")
    if st.button("Back to Home"):
        navigate_to('dashboardl')
        sj(js_expressions="parent.window.location.reload()")
    page_footer()
