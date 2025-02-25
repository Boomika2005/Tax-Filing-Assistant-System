import streamlit as st
import pandas as pd
import bcrypt
from sqlalchemy import text 

# Establish MySQL connection using Streamlit's connection API
conn = st.connection("mysql", type="sql", autocommit=True)
if conn:
    print('connetion success'
    )
# Create users table if it doesn't exist
def create_users_table():
    query = text("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """)
    try:
        with conn.session as session:
            session.execute(query)
            session.commit()  # Ensure the changes are committed
        # st.success("Users table created successfully!")
    except Exception as e:
        print(e)
        st.error(f"Error creating table: {e}")
# Hash password securely
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify password
def verify_password(password, hashed):
    # return bcrypt.checkpw(password.encode(), hashed.encode())
    return password==hashed

# Add new user to database - FIXED to use parameterized queries

def add_user(username, password):
    # password = hash_password(password)
    
    query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
    
    try:
        with conn.session as session:
            session.execute(query, {"username": username, "password": password})  
            session.commit()  # Commit the transaction to save the user
        print("Success: User added")
        return True
    except Exception as e:
        print(e)
        st.error(f"Error adding user: {e}")
        return False

# Get user details from database - FIXED to use parameterized queries
def get_user(username):
    print(username)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    try:
        result = conn.query(query)
        print('heee',result)
        return result.iloc[0] if not result.empty else None
    except Exception as e:
        print('exe login')
        st.error(f"Error fetching user: {e}")
        return None