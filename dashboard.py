import streamlit as st

# Owner dashboard with menu navigation
def owner_dashboard():
    st.title("Owner Dashboard")
    menu = st.selectbox("Navigate to", ["Member Management", "Classes Management", "Trainer Management", 
                                        "Equipment Management", "Payment Management"])

    if menu == "Member Management":
        st.subheader("Member Management")
        st.button("Add New Member")
        st.button("Edit Member Details")
        st.button("Remove Member")
    elif menu == "Classes Management":
        st.subheader("Classes Management")
        st.button("Add New Class")
        st.button("Edit Class Schedule")
        st.button("Cancel Class")
    elif menu == "Trainer Management":
        st.subheader("Trainer Management")
        st.button("Add New Trainer")
        st.button("Edit Trainer Details")
        st.button("Remove Trainer")
    elif menu == "Equipment Management":
        st.subheader("Equipment Management")
        st.button("Add New Equipment")
        st.button("Edit Equipment Details")
        st.button("Remove Equipment")
    elif menu == "Payment Management":
        st.subheader("Payment Management")
        st.button("Process New Payment")
        st.button("View Payment History")
        st.button("Manage Outstanding Payments")

# Member dashboard
def member_dashboard():
    st.title("Member Dashboard")
    st.subheader("Membership Information")
    st.write("Membership ID: M12345")
    st.write("Status: Active")
    st.write("Expiration Date: 2025-12-31")
    st.subheader("Workout History")
    st.write("Your recent workouts and performance metrics will appear here.")

# Trainer dashboard
def trainer_dashboard():
    st.title("Trainer Dashboard")
    st.subheader("Training Schedule")
    st.write("Your upcoming training schedule and client details will appear here.")
