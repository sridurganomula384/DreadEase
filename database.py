import sqlite3

def create_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create table for users
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        secret_key TEXT
    )
    ''')
    
    # Create table for sessions
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            login_date TEXT NOT NULL,
            logout_time TEXT
        )
    ''')
    #c.execute('''ALTER TABLE activity_log ADD COLUMN logout_time TEXT''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            name TEXT,
            age INTEGER,
            gender TEXT,
            frequency TEXT,
            fear_of TEXT,
            selected_symptoms TEXT,
            duration TEXT,
            predicted_phobia_type TEXT,
            predicted_phobia_level TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES users (email)
        )
    ''')
    c.execute('''
            CREATE TABLE IF NOT EXISTS dashboard_users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            age INTEGER,
            gender TEXT,
            frequency TEXT,
            fear_of TEXT,
            selected_symptoms TEXT,
            duration TEXT,
            predicted_phobia_type TEXT,
            predicted_phobia_level TEXT,
            checked_precautions TEXT, 
            last_checked_date DATE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            coins INTEGER ,
            FOREIGN KEY (email) REFERENCES users (email))''')
    #c.execute('''ALTER TABLE dashboard_users ADD COLUMN coins INTEGER''')
    


