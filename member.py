import streamlit as st
import mysql.connector
import MySQLdb
import pandas as pd

# Database connection function
def connect_to_db():
    try:
        connection = MySQLdb.connect(
            host="localhost",
            user="root",
            password="#Vignesh2010",
            db="legacy_gym"
        )
        return connection
    except MySQLdb.MySQLError as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Function to get member information
def get_member_info(member_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM MEMBERS WHERE MEM_ID = %s", (member_id,))
            member_info = cursor.fetchone()
            return member_info
        except MySQLdb.Error as e:
            st.error(f"Error fetching member information: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

# Function to get payments made by the member
def fetch_payments_by_member(member_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT TRANSACTION_TYPE, TRANS_ID, SENDER_ID, RECEIVER_ID, AMOUNT, TIMESTAMP FROM PAYMENTS WHERE SENDER_ID = %s", (member_id,))
            payment_records = cursor.fetchall()
            return payment_records
        except MySQLdb.Error as e:
            st.error(f"Error fetching payment records: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

# Function to get classes opted by the member
def get_member_classes(member_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT CLASS_NAME, DAY FROM CLASSES INNER JOIN CLASSES_OPTED ON CLASSES.CLASS_ID = CLASSES_OPTED.CLASS_ID WHERE MEM_ID = %s", (member_id,))
            classes = cursor.fetchall()
            return classes
        except MySQLdb.Error as e:
            st.error(f"Error fetching classes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

def member_dashboard():
    member_id = st.session_state.get("id")
    st.title("Member Dashboard")
   
    # Fetch and display member information
    member_info = get_member_info(member_id)

    if member_info:
        branch_id = member_info[6]  # Assuming branch_id is in the 7th position in MEMBERS table

        # Set up tabs for each section
        tab1, tab2, tab3 = st.tabs(["Personal Information", "My Classes", "Payments Made"])

        # Personal Information Section
        with tab1:
            st.header("Personal Information")
            first_name = member_info[4]
            last_name = member_info[5]
            gender = member_info[2]
            email = member_info[3]
            status = member_info[7]  # Assuming status is in the 8th column

            # Display the information
            st.write(f"**First Name**: {first_name}")
            st.write(f"**Last Name**: {last_name}")
            st.write(f"**Gender**: {gender}")
            st.write(f"**Email**: {email}")
            st.write(f"**Membership Status**: {status}")

        # My Classes Section
        with tab2:
            st.header("My Classes")
            member_classes = get_member_classes(member_id)
            if member_classes:
                for cls in member_classes:
                    st.write(f"Class: {cls[0]}, Day: {cls[1]}")
            else:
                st.write("No classes found for this member.")

        # Payments Made Section
        with tab3:
            st.header("Payments Made")
            payment_data = fetch_payments_by_member(member_id)
            if payment_data:
                # Convert payment data to DataFrame with column labels
                payment_df = pd.DataFrame(payment_data, columns=["Transaction Type", "Transaction ID", "Sender ID", "Receiver ID", "Amount", "Timestamp"])
                
                st.write("Your payment records:")
                st.dataframe(payment_df)
            else:
                st.write("No payment records found for you.")

# Main function to display the dashboard
member_dashboard()
