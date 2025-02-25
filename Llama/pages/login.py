import streamlit as st
from db import get_user

def show_login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(username)  # Fetch user details from DB
        
        if user is not None:  # Ensure user exists
            stored_password = user["password"]  # Retrieve the stored password

            if password == stored_password:  
                print("Authenticated")
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.switch_page("pages/home.py")
            else:
                st.error("Invalid username or password.")
        else:
            st.error("User not found.")

    if st.button("Go to Signup"):
        st.switch_page("pages/signup.py")

if __name__ == "__main__":
    if "authenticated" in st.session_state and st.session_state.authenticated:
        st.switch_page("pages/home.py")
    show_login()