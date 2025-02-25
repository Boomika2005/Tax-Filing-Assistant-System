import streamlit as st
from db import add_user, get_user,create_users_table

def show_signup():
    create_users_table()
    st.title("Sign Up")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password == confirm_password:
            if get_user(username):
                st.error("Username already exists. Choose another one.")
            else:
                add_user(username, password)
                st.success("Account created successfully! Please log in.")
                st.switch_page("pages/login.py")
        else:
            st.error("Passwords do not match!")

    if st.button("Go to Login"):
        st.switch_page("pages/login.py")

if __name__ == "__main__":
    if "authenticated" in st.session_state and st.session_state.authenticated:
        st.switch_page("pages/home.py")
    show_signup()
