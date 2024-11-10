import streamlit as st
import mysql.connector
import hashlib
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

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to get equipment IDs and details for the trainer's branch
def get_equipment_details(branch_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT EQUIP_ID, EQUIP_NAME, LAST_MAINTENANCE_DAY, NEXT_MAINTENANCE_DAY FROM EQUIPMENTS WHERE BRANCH_ID = %s", (branch_id,))
            equipment_details = cursor.fetchall()
            return equipment_details
        except MySQLdb.Error as e:
            st.error(f"Error fetching equipment details: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

# Function to get trainer information
def get_trainer_info(trainer_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM TRAINERS WHERE TRAIN_ID = %s", (trainer_id,))
            trainer_info = cursor.fetchone()
            return trainer_info
        except MySQLdb.Error as e:
            st.error(f"Error fetching trainer information: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def fetch_payments_for_trainer(trainer_id):
    connection = connect_to_db()
    
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(" SELECT TRANSACTION_TYPE, TRANS_ID, SENDER_ID, RECEIVER_ID, AMOUNT, TIMESTAMP FROM PAYMENTS WHERE RECEIVER_ID = %s", (trainer_id,))
            payment_deets = cursor.fetchall()
            return payment_deets
        except MySQLdb.Error as e:
            st.error(f"Error fetching payment details: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

# Function to get classes the trainer is taking
def get_trainer_classes(trainer_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT CLASS_NAME, DAY FROM CLASSES WHERE TRAINER_ID = %s", (trainer_id,))
            classes = cursor.fetchall()
            return classes
        except MySQLdb.Error as e:
            st.error(f"Error fetching classes: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []

# Function to manage equipment
def manage_equipment(branch_id, action, equip_id, equip_name=None, last_maintenance=None, next_maintenance=None):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if action == "add":
                cursor.execute(
                    "INSERT INTO EQUIPMENTS (EQUIP_ID, EQUIP_NAME, LAST_MAINTENANCE_DAY, NEXT_MAINTENANCE_DAY, BRANCH_ID) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (equip_id, equip_name, last_maintenance, next_maintenance, branch_id)
                )
                st.success("Equipment added successfully.")
            elif action == "delete":
                cursor.execute("DELETE FROM EQUIPMENTS WHERE EQUIP_ID = %s AND BRANCH_ID = %s", (equip_id, branch_id))
                st.success("Equipment deleted successfully.")
            elif action == "update":
                cursor.execute(
                    "UPDATE EQUIPMENTS SET EQUIP_NAME = %s, LAST_MAINTENANCE_DAY = %s, NEXT_MAINTENANCE_DAY = %s "
                    "WHERE EQUIP_ID = %s AND BRANCH_ID = %s",
                    (equip_name, last_maintenance, next_maintenance, equip_id, branch_id)
                )
                st.success("Equipment updated successfully.")
            connection.commit()
        except MySQLdb.Error as e:
            st.error(f"Error managing equipment: {e}")
        finally:
            cursor.close()
            connection.close()

        
def trainer_dashboard():
    trainer_id = st.session_state.get("id")
    st.title("Trainer Dashboard")

    # Get trainer information including gender, email, and password
    trainer_info = get_trainer_info(trainer_id)
    if trainer_info:
        branch_id = trainer_info[5]  # Assuming branch_id is in the 6th position in TRAINERS table

        # Get phone numbers for the trainer from TRAIN_PH table
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT PHONE_NUMBER FROM TRAIN_PH WHERE TRAIN_ID = %s", (trainer_id,))
        phone_numbers = cursor.fetchall()
        cursor.close()
        connection.close()

        # Set up tabs for each section
        tab1, tab2, tab3, tab4 = st.tabs(["Personal Information", "My Classes", "Manage Equipment", "Payments Received"])

        # Personal Information Section
        with tab1:
            st.header("Personal Information")
            
            # Correctly assign variables from trainer_info
            first_name = trainer_info[1]  # First Name is assumed to be in the 2nd column
            last_name = trainer_info[2]  # Last Name is assumed to be in the 3rd column
            gender = trainer_info[3]  # Gender is in the 4th column
            email = trainer_info[4]  # Email in the 5th column

            # Display the information
            st.write(f"**First Name**: {first_name}")
            st.write(f"**Last Name**: {last_name}")
            st.write(f"**Gender**: {gender}")
            st.write(f"**Email**: {email}")
            
            # Display phone numbers
            st.write("**Phone Numbers**:")
            if phone_numbers:
                for number in phone_numbers:
                    st.write(f"- {number[0]}")  # Displaying each phone number in the list
            else:
                st.write("No phone numbers found for this trainer.")
            
            # Option to update trainer's details
            st.subheader("Update Personal Information")
            
            # Fields for updating First Name, Last Name, Email, Gender
            updated_first_name = st.text_input("Your First Name", value=first_name)
            updated_last_name = st.text_input("Your Last Name", value=last_name)
            updated_email = st.text_input("Email", value=email)
            updated_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender))
            
            # Phone Number Management (for adding or editing existing phone numbers)
            phone_numbers_to_edit = st.text_area("Edit Phone Numbers (comma separated)", value=", ".join([number[0] for number in phone_numbers]))

            # Button to update the information in the database
            if st.button("Update Information"):
                try:
                    connection = connect_to_db()
                    cursor = connection.cursor()

                    # Update the trainer's personal information
                    cursor.execute(""" 
                        UPDATE TRAINERS
                        SET FIRST_NAME = %s, LAST_NAME = %s, EMAIL = %s, GENDER = %s
                        WHERE TRAIN_ID = %s
                    """, (updated_first_name, updated_last_name, updated_email, updated_gender, trainer_id))
                    
                    # Update phone numbers
                    # Delete old phone numbers and insert new ones
                    cursor.execute("DELETE FROM TRAIN_PH WHERE TRAIN_ID = %s", (trainer_id,))
                    if phone_numbers_to_edit:
                        phone_numbers_list = phone_numbers_to_edit.split(",")  # Split by commas
                        for number in phone_numbers_list:
                            number = number.strip()  # Remove any extra spaces
                            if number:  # Ensure the number is not empty
                                cursor.execute(""" 
                                    INSERT INTO TRAIN_PH (TRAIN_ID, PHONE_NUMBER)
                                    VALUES (%s, %s)
                                """, (trainer_id, number))
                    
                    connection.commit()
                    st.success("Personal information and phone numbers updated successfully!")
                except MySQLdb.Error as e:
                    st.error(f"Error updating personal information: {e}")
                finally:
                    cursor.close()
                    connection.close()

        # My Classes Section (fetching classes from the CLASSES table)
        with tab2:
            st.header("My Classes")
            trainer_classes = get_trainer_classes(trainer_id)
            if trainer_classes:
                for cls in trainer_classes:
                    st.write(f"Class: {cls[0]}, Day: {cls[1]}")  # Display class name and day
            else:
                st.write("No classes found for this trainer.")

        # Manage Equipment Section
        with tab3:
            st.header("Manage Equipment")
            action = st.selectbox("Choose Action", ["Add", "Delete", "Update"], key="equip_action")
            
            # Display equipment details for the trainer's branch
            st.subheader("Equipment List")
            equipment_details = get_equipment_details(branch_id)
            if equipment_details:
                for equip in equipment_details:
                    st.write(f"ID: {equip[0]}, Name: {equip[1]}, Last Maintenance: {equip[2]}, Next Maintenance: {equip[3]}")
            else:
                st.write("No equipment found for this branch.")

            # Equipment Management
            if action == "Delete" or action == "Update":
                equip_id = st.selectbox("Select Equipment ID", [equip[0] for equip in equipment_details], key="equip_id")
            else:
                equip_id = st.text_input("New Equipment ID", key="equip_id")

            # Additional fields for adding or updating equipment
            if action == "Add" or action == "Update":
                equip_name = st.text_input("Equipment Name", key="equip_name")
                last_maintenance = st.date_input("Last Maintenance Date", key="last_maintenance")
                next_maintenance = st.date_input("Next Maintenance Date", key="next_maintenance")

            if st.button(f"{action} Equipment", key="manage_equipment"):
                manage_equipment(branch_id, action.lower(), equip_id, equip_name, last_maintenance, next_maintenance)

        # Payments Received Section
        with tab4:
            st.header("Payments Received")

            # Fetch payment details for the logged-in trainer
            payment_data = fetch_payments_for_trainer(trainer_id)

            if payment_data:
                st.write("Your payment records:")
                st.dataframe(payment_data)  # Display the payment details in a table format
            else:
                st.write("No payment records found for you.")
        
# Ma        in function to handle login and display dashboard
trainer_dashboard()
