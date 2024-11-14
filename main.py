import streamlit as st
from login import sign_up, login
from member import member_dashboard
from owner import owner_dashboard
from trainer import trainer_dashboard
# Main layout with Login, Signup, and Home Page redirection
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "role" not in st.session_state:
    st.session_state["role"] = None  # No default role

if st.session_state["page"] == "home":
    role = st.session_state["role"]
    if role == "Owner":
        owner_dashboard()
    elif role == "Member":
        member_dashboard()
    elif role == "Trainer":
        trainer_dashboard()
    else:
        st.write("Access Denied: Invalid role.")

    # Logout button
    if st.button("Logout"):
        st.session_state["page"] = "login"
        st.session_state["role"] = None  # Reset role
        st.success("Logged out successfully! Redirecting to login page...")
else:
    st.title("Gym Management System")

    option = st.selectbox("Choose an option", ["Sign Up", "Login"])

    if option == "Sign Up":
        st.subheader("Sign Up")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        # new_role = st.selectbox("Role", ["Member", "Trainer", "Owner"])
        new_role = st.selectbox("Role", ["Member"])
        if st.button("Sign Up"):
            if new_username and new_password and new_role:
                sign_up(new_username, new_password, new_role)
            else:
                st.error("Please fill all fields.")

    elif option == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Member", "Trainer", "Owner"])
        if st.button("Login"):
            if username and password and role:
                login(username, password, role)
            else:
                st.error("Please fill all fields.")
