import json
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox


# Load the data from the JSON file
with open('user_data.json', 'r') as f:
    data = json.load(f)

with open(r'D:\Ver_5_updated-main\datas\\url.json', 'r') as f:
    url = json.load(f)
# Create a new SQLite database and establish a connection
new_sql_lite_primary = url['data_path']
new_sql_lite_secondary = url['data_path2']

if os.path.exists(new_sql_lite_primary):
    conn = sqlite3.connect(new_sql_lite_primary)
elif os.path.exists(new_sql_lite_secondary):
    conn = sqlite3.connect(new_sql_lite_secondary)
else:
    QMessageBox.warning(None, 'Error', 'Database file not found')

c = conn.cursor()

try:
    # Create a new table if it doesn't already exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            phone1 TEXT,
            phone2 TEXT,
            phone3 TEXT
        )
    ''')
except sqlite3.DatabaseError as e:
    QMessageBox.warning(None, 'Error', f"An error occurred: {e}")
    
def insert_user(user_id, name, contact1, contact2, contact3):

    
    # Define the primary and alternative database file paths
    primary_db_path = url['data_path']
    alternative_db_path = url['data_path2']

    # Check if the primary database file exists
    if os.path.exists(primary_db_path):
        # If it exists, connect to it
        conn = sqlite3.connect(primary_db_path)
    else:
        # If it doesn't exist, connect to the alternative database file
        conn = sqlite3.connect(alternative_db_path)

    c = conn.cursor()

    # Insert the user's details into the users table
    c.execute('''
        INSERT OR IGNORE INTO users (id, name, phone1, phone2, phone3)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, contact1, contact2, contact3))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def update_user(user_id, name, contact1, contact2, contact3):
    # Define the primary and alternative database file paths
    primary_db_path = url['data_path']
    alternative_db_path = url['data_path2']

    # Check if the primary database file exists
    if os.path.exists(primary_db_path):
        # If it exists, connect to it
        conn = sqlite3.connect(primary_db_path)
    else:
        # If it doesn't exist, connect to the alternative database file
        conn = sqlite3.connect(alternative_db_path)

    c = conn.cursor()

    # Update the user's details in the users table
    c.execute('''
        UPDATE users
        SET name = ?, phone1 = ?, phone2 = ?, phone3 = ?
        WHERE id = ?
    ''', (name, contact1, contact2, contact3, user_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def delete_user(user_id):
    # Define the primary and alternative database file paths
    primary_db_path = url['data_path']
    alternative_db_path = url['data_path2']

    # Check if the primary database file exists
    if os.path.exists(primary_db_path):
        # If it exists, connect to it
        conn = sqlite3.connect(primary_db_path)
    else:
        # If it doesn't exist, connect to the alternative database file
        conn = sqlite3.connect(alternative_db_path)

    c = conn.cursor()

    # Delete the user from the users table
    c.execute('''
        DELETE FROM users
        WHERE id = ?
    ''', (user_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
def print_database():
    # Connect to the database
    new_sql_lite = url['data_path']
    conn = sqlite3.connect(new_sql_lite)
    c = conn.cursor() # Create a cursor object

    # Select all data from the users table
    c.execute("SELECT * FROM users")

    # Fetch all the rows
    rows = c.fetchall()

    for row in rows:
        print(row)

    # Close the connection
    conn.close()

#print_database()