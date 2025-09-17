import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
import numpy as np
import sqlite3
from streamlit_js_eval import streamlit_js_eval as sj


def navigate_to(page):
    st.query_params.from_dict({"page": page})

def get_email():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users ORDER BY rowid DESC LIMIT 1')
    email = c.fetchone()
    conn.close()
    return email[0] if email else None

# Function to load and prepare the training dataset
def load_training_data():
    df = pd.read_csv('https://raw.githubusercontent.com/Reethz30/DreadEase/main/Code/Mini-Project.csv')

    # Combine symptom columns into a single list for each row
    df['All_Symptoms'] = df[['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4', 'Symptom_5', 'Symptom_6']].apply(lambda row: ', '.join([str(symptom) for symptom in row if pd.notna(symptom)]), axis=1)
    
    return df

# Load or train the model
def load_or_train_model():
    try:
        model = joblib.load('phobia_model.pkl')
        le_symptoms = joblib.load('le_symptoms.pkl')
        le_phobia = joblib.load('le_phobia.pkl')
        le_duration = joblib.load('le_duration.pkl')
        le_frequency = joblib.load('le_frequency.pkl')
    except FileNotFoundError:
        df = load_training_data()
        X = df[['All_Symptoms', 'Duration', 'Frequency', 'Age']]
        y = df['Phobia']
        
        # Initialize LabelEncoders
        le_symptoms = LabelEncoder()
        le_duration = LabelEncoder()
        le_frequency = LabelEncoder()
        le_phobia = LabelEncoder()

        # Fit LabelEncoders and transform data
        X['All_Symptoms'] = le_symptoms.fit_transform(X['All_Symptoms'])
        X['Duration'] = le_duration.fit_transform(X['Duration'])
        X['Frequency'] = le_frequency.fit_transform(X['Frequency'])
        X['Age'] = X['Age'].astype(float)  # Ensure Age is numeric
        y = le_phobia.fit_transform(y)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier()
        model.fit(X_train, y_train)
        
        # Save models and encoders
        joblib.dump(model, 'phobia_model.pkl')
        joblib.dump(le_symptoms, 'le_symptoms.pkl')
        joblib.dump(le_phobia, 'le_phobia.pkl')
        joblib.dump(le_duration, 'le_duration.pkl')
        joblib.dump(le_frequency, 'le_frequency.pkl')
    
    return model, le_symptoms, le_phobia, le_duration, le_frequency
def handle_unseen_labels(symptoms, le):
    known_labels = set(le.classes_)
    processed = []
    for symptom in symptoms.split(', '):
        if symptom in known_labels:
            processed.append(symptom)
        else:
            processed.append('unknown')  # Or handle it in some other way
    return ', '.join(processed)

def save_prediction_to_db(email,name, age, gender,frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    #st.write(email, name, age, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level)
    c.execute('''
        INSERT INTO user_predictions (email,name, age,gender, frequency, fear_of, selected_symptoms, duration, predicted_phobia_type, predicted_phobia_level)
        VALUES (?, ?, ?, ?, ?,?, ?,?, ?, ?)
    ''', (email,name, age,gender, frequency, fear_of, ', '.join(selected_symptoms), duration, predicted_phobia_type, predicted_phobia_level))
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

def sym(df, fear, fre):
    a = df[df['Frequency'] == fre]
    a = a[a['Fear_Of_1'] == fear]
    x = ', '.join(a['All_Symptoms'])
    xx = list(set(x.split(', ')))
    xx = sorted(xx)  # Sort the symptoms list
    return xx

# Prediction page layout
def prediction_page():

    email = get_email()  # Get email from the URL
    #st.write(f"Fetched email: {email}, type: {type(email)}")

    if not email:
        st.error("Email not provided. Please log in or create an account.")
        return

    st.title("Phobia Prediction")
    #st.write(f"Logged in as: {email}")
    df = load_training_data()
    fears = df['Fear_Of_1'].unique()
        

    # Initialize session state if not already
    if 'step' not in st.session_state:
        st.session_state.email=email,
        st.session_state.gender='',
        st.session_state.step = 1
        st.session_state.name = ''
        st.session_state.age = None
        st.session_state.frequency = None
        st.session_state.fear_of = ''
        st.session_state.selected_symptoms = []
        st.session_state.duration = ''
        st.session_state.phobia_level = ''
        st.session_state.phobia_type=''

    if st.session_state.step == 1:
        st.header("Step 1: Enter Name")
        name = st.text_input("Name", key="name_input")
        gender = st.selectbox("Gender", options=["Female", "Male", "Prefer not to say"], index=0, key="gender_input")
        if st.button("Enter"):
            if name:
                st.session_state.name = name
                st.session_state.gender=gender
                st.session_state.step = 2
            else:
                st.error("Please enter your name.")

    elif st.session_state.step == 2:
        st.header(f"Hello, {st.session_state.name}!\n Step 2: Enter Age")
        age = st.number_input("Age", key="age_input")
        if st.button("Enter"):
            if age:
                st.session_state.age = age
                st.session_state.step = 3
            else:
                st.error("Please enter your age.")

    elif st.session_state.step == 3:
        st.header("Step 3: Phobia")

        # Use a dropdown (selectbox) for selecting the fear
        st.subheader("Select Your Fear")
        fear_of = st.selectbox("Select your fear from the list:", fears, index=fears.tolist().index(st.session_state.fear_of) if st.session_state.fear_of else 0, key="fear_select")

        if st.button("Next"):
            st.session_state.fear_of = fear_of
            st.session_state.step = 4

    elif st.session_state.step == 4:
        st.header("Step 4: Frequency of Symptoms")
        frequency_list = ['Occasional', 'Regular', 'Persistent']
        frequency = st.radio("Frequency of symptoms:", frequency_list, index=frequency_list.index(st.session_state.frequency) if st.session_state.frequency else 0, key="frequency_input")
        if st.button("Enter"):
            st.session_state.frequency = frequency
            st.session_state.step = 5

    
    elif st.session_state.step == 5:
        st.header("Step 5: Symptoms")
        fear_of = st.session_state.fear_of
        frequency = st.session_state.frequency

        # Get symptoms related to the user's fear
        symptoms_list = sym(df, fear_of, frequency)
        symptoms_str1 = ', '.join(sorted(symptoms_list))

        if not symptoms_list:
            st.warning("No symptoms found for the selected fear.")
            return

        # Display symptom options as buttons
        selected_symptoms = st.multiselect("Select the symptoms you are experiencing:", symptoms_list, default=st.session_state.selected_symptoms, key="symptoms_input")
        st.session_state.selected_symptoms = selected_symptoms

        st.subheader("Select Duration:")
        duration_list = ['Less than 1 hour', '1-3 hours', 'More than 3 hours']
        duration = st.radio("Select the duration of symptoms:", duration_list, index=duration_list.index(st.session_state.duration) if st.session_state.duration else 0, key="duration_input")
        st.session_state.duration = duration

        if st.button("Predict"):
            if not selected_symptoms or not duration:
                st.error("Please select symptoms and duration.")
            else:
                # Load the model and encoders
                model, le_symptoms, le_phobia, le_duration, le_frequency = load_or_train_model()

                # Prepare input data
                symptoms_str = ', '.join(sorted(selected_symptoms))

                # Determine phobia level based on frequency
                if st.session_state.frequency == 'Occasional':
                    st.session_state.phobia_level = 'Mild'
                elif st.session_state.frequency == 'Regular':
                    st.session_state.phobia_level = 'Moderate'
                elif st.session_state.frequency == 'Persistent':
                    st.session_state.phobia_level = 'Major'

                # Add phobia_level to the symptoms_str for prediction
                data = pd.DataFrame([[symptoms_str1, duration, st.session_state.frequency, st.session_state.age]], columns=['All_Symptoms', 'Duration', 'Frequency', 'Age'])
                phobia_type = df[df['Fear_Of_1'].str.lower() == st.session_state.fear_of.lower()]['Type'].unique()
                
                st.session_state.phobia_type=phobia_type[0]

                # Handle unseen labels in All_Symptoms
                #data['All_Symptoms'] = data['All_Symptoms'].apply(lambda x: handle_unseen_labels(x, le_symptoms))
                data['All_Symptoms'] = le_symptoms.fit_transform(data['All_Symptoms'])
                data['Duration'] = le_duration.fit_transform(data['Duration'])
                data['Frequency'] = le_frequency.fit_transform(data['Frequency'])
                data['Age'] = data['Age'].astype(float)  # Ensure Age is numeric

                # Make prediction
                prediction = model.predict(data)
                phobia_typ = le_phobia.inverse_transform(prediction)

                # Display results
                st.success(f"Predicted Phobia Type: {st.session_state.phobia_type}")
                st.success(f"Predicted Phobia Level: {st.session_state.phobia_level}")
                #st.session_state.selected_symptoms=symptoms_str

                # Save user inputs and predictions to the database
                '''st.write("User Prediction Details:")
                st.write(f"Email: {st.session_state.email}")
                st.write(f"Name: {st.session_state.name}")
                st.write(f"Age: {st.session_state.age}")
                st.write(f"Frequency: {st.session_state.frequency}")
                st.write(f"Fear Of: {st.session_state.fear_of}")
                st.write(f"Selected Symptoms: {','.join(st.session_state.selected_symptoms)}")
                st.write(f"Duration: {st.session_state.duration}")
                st.write(f"Predicted Phobia Type: {st.session_state.phobia_type}")
                st.write(f"Predicted Phobia Level: {st.session_state.phobia_level}")'''

                                
                save_prediction_to_db(
                    email,
                    st.session_state.name,
                    st.session_state.age,
                    st.session_state.gender,
                    st.session_state.frequency,
                    st.session_state.fear_of,
                    st.session_state.selected_symptoms,
                    st.session_state.duration,
                    st.session_state.phobia_type,
                    st.session_state.phobia_level
                )

                st.session_state.control_source = 'test'
                navigate_to('dashboardt')
                sj(js_expressions="parent.window.location.reload()")
    page_footer()
