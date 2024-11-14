import streamlit as st
import pandas as pd
import MySQLdb

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

# Fetch data from a table
def fetch_data(query, params=None):
    connection = connect_to_db()
    if connection:
        df = pd.read_sql(query, connection, params=params)
        connection.close()
        return df
    else:
        return None

def member_management():
    st.subheader("Member Management")

    # View all members
    view_mem=st.button("View All Legacy Members", key="view_all_members")
    if view_mem:
        df = fetch_data("SELECT MEM_ID, GENDER, EMAIL, FIRST_NAME, LAST_NAME,  BRANCH_ID, STATUS FROM MEMBERS")
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.error("No members found.")

    # Section for updating member details by entering MEM_ID
    st.header("Update Member")
    update_member_id = st.text_input("Enter Member ID to Update")
    if update_member_id:
        # Fetch the member's current data based on `update_member_id`
        df = fetch_data("SELECT MEM_ID, GENDER, EMAIL, FIRST_NAME, LAST_NAME, BRANCH_ID, STATUS FROM MEMBERS WHERE MEM_ID = %s", (update_member_id,))
        
        if not df.empty:
            row = df.iloc[0]
            
            # Collect updated values for each field
            update_data = {
                "FIRST_NAME": st.text_input("Edit First Name", value=row['FIRST_NAME'] if row['FIRST_NAME'] is not None else ""),
                "LAST_NAME": st.text_input("Edit Last Name", value=row['LAST_NAME'] if row['LAST_NAME'] is not None else ""),
                "GENDER": st.selectbox("Edit Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(row['GENDER']) if row['GENDER'] in ["Male", "Female", "Other"] else 0),
                "EMAIL": st.text_input("Edit Email", value=row['EMAIL'] if row['EMAIL'] is not None else ""),
                "BRANCH_ID": st.text_input("Edit Branch ID", value=row['BRANCH_ID'] if row['BRANCH_ID'] is not None else ""),
                "STATUS": st.selectbox("Edit Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(row['STATUS']))
            }
            
            update_columns = list(update_data.keys())

            if st.button("Update Record"):
                set_clause = ", ".join([f"{col} = %s" for col in update_columns])
                connection = connect_to_db()
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        f"UPDATE MEMBERS SET {set_clause} WHERE MEM_ID = %s",
                        (*update_data.values(), update_member_id)
                    )
                    connection.commit()
                    st.success(f"Member {update_data['FIRST_NAME']} {update_data['LAST_NAME']} updated successfully!")
                except Exception as e:
                    st.error(f"Error updating member: {e}")
                finally:
                    cursor.close()
                    connection.close()
        else:
            st.error("No member found with the provided Member ID.")

    # Section for deleting a member by entering MEM_ID
    st.header("Delete Member")
    delete_member_id = st.text_input("Enter Member ID to Delete")
    if delete_member_id and st.button("Delete Record"):
        connection = connect_to_db()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM MEMBERS WHERE MEM_ID = %s", (delete_member_id,))
            connection.commit()
            st.warning(f"Member with ID {delete_member_id} deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting member: {e}")
        finally:
            cursor.close()
            connection.close()

    # Section for adding a new member
    st.header("Add New Member")
    with st.expander("Add New Member"):
        new_member_id = st.text_input("Member ID")
        new_member_first_name = st.text_input("First Name")
        new_member_last_name = st.text_input("Last Name")
        new_member_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        new_member_email = st.text_input("Email")
        #new_member_plan_id = st.text_input("Plan ID")
        new_member_branch_id = st.text_input("Branch ID")
       # new_member_status = st.selectbox("Status", ["Active", "Inactive"])

        if st.button("Submit New Member"):
            if new_member_id and new_member_first_name and new_member_last_name and new_member_email:
                connection = connect_to_db()
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        """
                        INSERT INTO MEMBERS (MEM_ID, FIRST_NAME, LAST_NAME, GENDER, EMAIL,   BRANCH_ID) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (new_member_id, new_member_first_name, new_member_last_name, new_member_gender, new_member_email,
                          new_member_branch_id)
                    )
                    connection.commit()
                    st.success("New member added successfully!")
                except Exception as e:
                    st.error(f"Error adding new member: {e}")
                finally:
                    cursor.close()
                    connection.close()

def classes_management():
    st.subheader("Classes Management")
    
    # 1. View Classes Table with Branch Names
    if st.button("View All Classes"):
        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            # Join CLASSES, TRAINERS, and BRANCHES to get branch names
            cursor.execute("""
                SELECT C.CLASS_ID, C.CLASS_NAME, C.DAY, T.TRAIN_ID, B.BRANCH_NAME
                FROM CLASSES C
                JOIN TRAINERS T ON C.TRAINER_ID = T.TRAIN_ID
                JOIN BRANCHES B ON T.BRANCH_ID = B.BRANCH_ID
            """)
            classes_data = cursor.fetchall()
            cursor.close()
            connection.close()

            # Display classes in a DataFrame format
            if classes_data:
                df = pd.DataFrame(classes_data, columns=["CLASS_ID", "CLASS_NAME", "DAY", "TRAINER_ID", "BRANCH_NAME"])
                st.dataframe(df)
            else:
                st.warning("No classes found in the database.")
        except Exception as e:
            st.error(f"Error: {e}")

    # 2. Add New Class
    with st.expander("Add New Class"):
        class_id = st.text_input("Class_ID")
        class_name = st.text_input("Class Name")
        day = st.selectbox("Day", ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
        trainer_id = st.text_input("Trainer ID")

        if st.button("Add Class"):
            try:
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO CLASSES (CLASS_ID, CLASS_NAME, DAY, TRAINER_ID) 
                    VALUES (%s, %s, %s, %s)
                """, (class_id, class_name, day, trainer_id))
                connection.commit()
                st.success("Class added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()

    # 3. Edit Class Details
    with st.expander("Edit Class Details"):
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT CLASS_ID, CLASS_NAME FROM CLASSES")
        classes = cursor.fetchall()
        cursor.close()
        connection.close()

        class_id = st.selectbox("Select Class to Edit", [c[0] for c in classes])

        if class_id:
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute("SELECT CLASS_NAME, DAY, TRAINER_ID FROM CLASSES WHERE CLASS_ID = %s", (class_id,))
            class_details = cursor.fetchone()

            class_name = st.text_input("Class Name", value=class_details[0])
            day = st.selectbox("Day of class", ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], index=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"].index(class_details[1]))
            trainer_id = st.text_input("Trainer ID", value=class_details[2])

            if st.button("Update Class"):
                try:
                    cursor.execute("""
                        UPDATE CLASSES 
                        SET CLASS_NAME = %s, DAY = %s, TRAINER_ID = %s 
                        WHERE CLASS_ID = %s
                    """, (class_name, day, trainer_id, class_id))
                    connection.commit()
                    st.success("Class updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    cursor.close()
                    connection.close()

    # 4. Manage Class Enrollments
    with st.expander("Manage Class Enrollments"):
        connection = connect_to_db()
        cursor = connection.cursor()
        
        cursor.execute("SELECT CLASS_ID, CLASS_NAME FROM CLASSES")
        classes = cursor.fetchall()
        cursor.execute("SELECT MEM_ID, FIRST_NAME, LAST_NAME FROM MEMBERS")
        members = cursor.fetchall()
        cursor.close()
        connection.close()

        class_id = st.selectbox("Select Class to Manage Enrollments", [c[0] for c in classes])

        if class_id:
            st.write(f"Enrolled members for Class ID: {class_id}")

            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT M.MEM_ID, M.FIRST_NAME, M.LAST_NAME 
                FROM CLASSES_OPTED CO
                JOIN MEMBERS M ON CO.MEM_ID = M.MEM_ID
                WHERE CO.CLASS_ID = %s
            """, (class_id,))
            enrolled_members = cursor.fetchall()
            cursor.close()
            connection.close()

            for mem in enrolled_members:
                st.write(f"{mem[1]} {mem[2]} (ID: {mem[0]})")
                if st.button(f"Remove {mem[1]} {mem[2]} from Class", key=f"Remove_{mem[0]}"):
                    connection = connect_to_db()
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM CLASSES_OPTED WHERE MEM_ID = %s AND CLASS_ID = %s", (mem[0], class_id))
                    connection.commit()
                    st.success(f"{mem[1]} {mem[2]} removed from class.")
                    cursor.close()
                    connection.close()

            mem_id = st.selectbox("Select Member to Add", [m[0] for m in members])

            if st.button("Add Member to Class"):
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO CLASSES_OPTED (MEM_ID, CLASS_ID) VALUES (%s, %s)", (mem_id, class_id))
                connection.commit()
                st.success("Member added to class!")
                cursor.close()
                connection.close()

def branches_management():
    st.subheader("Branch Management")

    # View all branches
    if st.button("View Branches"):
        df = fetch_data("SELECT BRANCH_ID, BRANCH_NAME,  MEMBER_COUNT, TRAINER_COUNT FROM BRANCHES")
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.error("No branches found.")

    # Update branch name by entering BRANCH_ID
    st.header("Update Branch Name")
    update_branch_id = st.text_input("Enter Branch ID to Update")
    if update_branch_id:
        # Fetch the branch's current name
        df = fetch_data("SELECT BRANCH_NAME FROM BRANCHES WHERE BRANCH_ID = %s", (update_branch_id,))
        
        if not df.empty:
            current_name = df.iloc[0]['BRANCH_NAME']
            
            # Input for the new branch name
            new_name = st.text_input("Enter New Branch Name", value=current_name)

            if st.button("Update Branch Name"):
                connection = connect_to_db()
                if connection:
                    try:
                        cursor = connection.cursor()
                        cursor.execute(
                            "UPDATE BRANCHES SET BRANCH_NAME = %s WHERE BRANCH_ID = %s",
                            (new_name, update_branch_id)
                        )
                        connection.commit()
                        st.success(f"Branch name updated successfully for Branch ID {update_branch_id}.")
                    except MySQLdb.MySQLError as e:
                        st.error(f"Error updating branch name: {e}")
                    finally:
                        connection.close()
        else:
            st.error(f"No branch found with ID {update_branch_id}.")

    # Add new branch with check for existing BRANCH_ID
    st.header("Add New Branch")
    new_branch_id = st.text_input("Enter New Branch ID")
    new_branch_name = st.text_input("Enter New Branch Name")

    if st.button("Add New Branch"):
        if new_branch_id and new_branch_name:
            # Check if the branch ID already exists
            check_df = fetch_data("SELECT BRANCH_ID FROM BRANCHES WHERE BRANCH_ID = %s", (new_branch_id,))
            
            if not check_df.empty:
                st.warning(f"A branch with ID {new_branch_id} already exists. Please use a unique ID.")
            else:
                # Proceed to add the new branch if the ID is unique
                connection = connect_to_db()
                if connection:
                    try:
                        cursor = connection.cursor()
                        cursor.execute(
                            "INSERT INTO BRANCHES (BRANCH_ID, BRANCH_NAME) VALUES (%s, %s)",
                            (new_branch_id, new_branch_name)
                        )
                        connection.commit()
                        st.success(f"New branch '{new_branch_name}' added with ID {new_branch_id}.")
                    except MySQLdb.MySQLError as e:
                        st.error(f"Error adding new branch: {e}")
                    finally:
                        connection.close()
        else:
            st.warning("Please enter both Branch ID and Branch Name.")

def trainer_management():

    st.subheader("Trainer Management")

    # View all trainers with their phone numbers
    if st.button("View Trainers"):
        df = fetch_data("""
            SELECT T.TRAIN_ID, T.FIRST_NAME, T.LAST_NAME, T.GENDER, T.EMAIL, T.BRANCH_ID, GROUP_CONCAT(P.PHONE_NUMBER) AS PHONE_NUMBERS
            FROM TRAINERS T
            LEFT JOIN TRAIN_PH P ON T.TRAIN_ID = P.TRAIN_ID
            GROUP BY T.TRAIN_ID
        """)
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.error("No trainers found.")

    # Update trainer details by entering TRAIN_ID
    st.header("Update Trainer")
    update_trainer_id = st.text_input("Enter Trainer ID to Update")
    if update_trainer_id:
        df = fetch_data("SELECT TRAIN_ID, FIRST_NAME, LAST_NAME, GENDER, EMAIL, BRANCH_ID FROM TRAINERS WHERE TRAIN_ID = %s", (update_trainer_id,))
        
        if not df.empty:
            row = df.iloc[0]

            update_data = {
                "FIRST_NAME": st.text_input("Edit First Name", value=row['FIRST_NAME']),
                "LAST_NAME": st.text_input("Edit Last Name", value=row['LAST_NAME']),
                "GENDER": st.selectbox("Edit Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(row['GENDER'])),
                "EMAIL": st.text_input("Edit Email", value=row['EMAIL']),
                "BRANCH_ID": st.text_input("Edit Branch ID", value=row['BRANCH_ID'])
            }

            # Fetch phone numbers
            phone_df = fetch_data("SELECT PHONE_NUMBER FROM TRAIN_PH WHERE TRAIN_ID = %s", (update_trainer_id,))
            phone_numbers = ", ".join(phone_df["PHONE_NUMBER"]) if not phone_df.empty else ""
            updated_phone_numbers = st.text_area("Edit Phone Numbers (comma-separated)", value=phone_numbers)

            update_columns = list(update_data.keys())
            if st.button("Update Trainer Record"):
                set_clause = ", ".join([f"{col} = %s" for col in update_columns])
                connection = connect_to_db()
                cursor = connection.cursor()
                try:
                    # Update trainer info
                    cursor.execute(
                        f"UPDATE TRAINERS SET {set_clause} WHERE TRAIN_ID = %s",
                        (*update_data.values(), update_trainer_id)
                    )
                    
                    # Update phone numbers
                    cursor.execute("DELETE FROM TRAIN_PH WHERE TRAIN_ID = %s", (update_trainer_id,))
                    for phone in updated_phone_numbers.split(","):
                        phone = phone.strip()
                        if phone:
                            cursor.execute(
                                "INSERT INTO TRAIN_PH (TRAIN_ID, PHONE_NUMBER) VALUES (%s, %s)",
                                (update_trainer_id, phone)
                            )
                    
                    connection.commit()
                    st.success(f"Trainer {update_data['FIRST_NAME']} {update_data['LAST_NAME']} updated successfully!")
                except Exception as e:
                    st.error(f"Error updating trainer: {e}")
                finally:
                    cursor.close()
                    connection.close()
        else:
            st.error("No trainer found with the provided Trainer ID.")

    # Delete trainer by entering TRAIN_ID
    st.header("Delete Trainer")
    delete_trainer_id = st.text_input("Enter Trainer ID to Delete")
    if delete_trainer_id and st.button("Delete Trainer"):
        connection = connect_to_db()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM TRAINERS WHERE TRAIN_ID = %s", (delete_trainer_id,))
            cursor.execute("DELETE FROM TRAIN_PH WHERE TRAIN_ID = %s", (delete_trainer_id,))
            connection.commit()
            st.warning(f"Trainer with ID {delete_trainer_id} deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting trainer: {e}")
        finally:
            cursor.close()
            connection.close()

    # Add new trainer
    st.header("Add New Trainer")
    with st.expander("Add New Trainer"):
        new_trainer_id = st.text_input("Trainer's ID")
        new_trainer_first_name = st.text_input("Trainer's First Name")
        new_trainer_last_name = st.text_input("Trainer's Last Name")
        new_trainer_gender = st.selectbox("Trainer's Gender", ["Male", "Female", "Other"])
        new_trainer_email = st.text_input("Trainer's Email")
        new_trainer_branch_id = st.text_input("Trainer's Branch ID")
        
        # Collect multiple phone numbers
        st.subheader("Phone Numbers")
        phone_numbers = st.text_area("Enter phone numbers (comma-separated)")

        if st.button("Submit New Trainer"):
            if new_trainer_id and new_trainer_first_name and new_trainer_last_name and new_trainer_email:
                connection = connect_to_db()
                cursor = connection.cursor()
                try:
                    # Insert into TRAINERS table
                    cursor.execute(
                        """
                        INSERT INTO TRAINERS (TRAIN_ID, FIRST_NAME, LAST_NAME, GENDER, EMAIL, BRANCH_ID) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (new_trainer_id, new_trainer_first_name, new_trainer_last_name, new_trainer_gender, new_trainer_email, new_trainer_branch_id)
                    )
                    # Insert into TRAIN_PH table
                    for phone in phone_numbers.split(","):
                        phone = phone.strip()
                        if phone:
                            cursor.execute(
                                "INSERT INTO TRAIN_PH (TRAIN_ID, PHONE_NUMBER) VALUES (%s, %s)",
                                (new_trainer_id, phone)
                            )
                    connection.commit()
                    st.success("New trainer added successfully!")
                except Exception as e:
                    st.error(f"Error adding new trainer: {e}")
                finally:
                    cursor.close()
                    connection.close()

def equipment_management():
    st.title("Equipment Management")

    # Step 1: Show all branches
    st.subheader("Select Branch")
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute("SELECT BRANCH_ID, BRANCH_NAME FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.close()
    connection.close()

    # Dropdown to select a branch
    branch_id = st.selectbox("Choose a branch", [branch[1] for branch in branches])
    
    if branch_id:
        # Get branch_id from selected branch name
        branch_id_selected = [branch[0] for branch in branches if branch[1] == branch_id][0]
        
        # Step 2: View the equipment for the selected branch
        st.subheader(f"Equipment for {branch_id}")
        
        # Fetch equipment for the selected branch
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT EQUIP_ID, EQUIP_NAME, LAST_MAINTENANCE_DAY, NEXT_MAINTENANCE_DAY FROM EQUIPMENTS WHERE BRANCH_ID = %s", (branch_id_selected,))
        equipment = cursor.fetchall()
        cursor.close()
        connection.close()

        if equipment:
            st.write("Existing Equipment:")
            equipment_df = pd.DataFrame(equipment, columns=["Equipment ID", "Equipment Name", "Last Maintenance", "Next Maintenance"])
            st.dataframe(equipment_df)
        else:
            st.write("No equipment found for this branch.")

        # Step 3: Add New Equipment
        st.subheader("Add New Equipment")
        with st.form("Add Equipment Form"):
            equip_id = st.text_input("Equipment ID")  # You can provide your own method for generating or assigning EQUIP_ID
            equip_name = st.text_input("Equipment Name")
            last_maintenance = st.date_input("Last Maintenance Date")
            next_maintenance = st.date_input("Next Maintenance Date")

            # Form submission button
            submit_button = st.form_submit_button("Add Equipment")
            if submit_button:
                if equip_name and equip_id:  # Ensure Equipment ID and Name are provided
                    try:
                        connection = connect_to_db()
                        cursor = connection.cursor()
                        cursor.execute("""
                            INSERT INTO EQUIPMENTS (EQUIP_ID, BRANCH_ID, EQUIP_NAME, LAST_MAINTENANCE_DAY, NEXT_MAINTENANCE_DAY)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (equip_id, branch_id_selected, equip_name, last_maintenance, next_maintenance))
                        connection.commit()
                        cursor.close()
                        st.success(f"Equipment '{equip_name}' added successfully!")
                    except MySQLdb.Error as e:
                        st.error(f"Error adding equipment: {e}")
                    finally:
                        connection.close()
                else:
                    st.error("Both Equipment ID and Equipment name are required.")

        # Step 4: Update Equipment
        st.subheader("Update Equipment")
        equipment_ids = [equip[0] for equip in equipment]  # Get equipment IDs for selection
        if equipment_ids:
            selected_equipment_id = st.selectbox("Select Equipment to Update", equipment_ids)
            if selected_equipment_id:
                # Fetch details of the selected equipment
                connection = connect_to_db()
                cursor = connection.cursor()
                cursor.execute("SELECT EQUIP_NAME, LAST_MAINTENANCE_DAY, NEXT_MAINTENANCE_DAY FROM EQUIPMENTS WHERE EQUIP_ID = %s AND BRANCH_ID = %s", 
                               (selected_equipment_id, branch_id_selected))
                equip_details = cursor.fetchone()
                cursor.close()
                connection.close()

                if equip_details:
                    updated_equip_name = st.text_input("Equipment Name", value=equip_details[0])
                    updated_last_maintenance = st.date_input("Last Maintenance Date", value=equip_details[1])
                    updated_next_maintenance = st.date_input("Next Maintenance Date", value=equip_details[2])

                    if st.button("Update Equipment"):
                        try:
                            connection = connect_to_db()
                            cursor = connection.cursor()
                            cursor.execute("""
                                UPDATE EQUIPMENTS
                                SET EQUIP_NAME = %s, LAST_MAINTENANCE_DAY = %s, NEXT_MAINTENANCE_DAY = %s
                                WHERE EQUIP_ID = %s AND BRANCH_ID = %s
                            """, (updated_equip_name, updated_last_maintenance, updated_next_maintenance, selected_equipment_id, branch_id_selected))
                            connection.commit()
                            cursor.close()
                            st.success(f"Equipment '{updated_equip_name}' updated successfully!")
                        except MySQLdb.Error as e:
                            st.error(f"Error updating equipment: {e}")
                        finally:
                            connection.close()

        # Step 5: Delete Equipment
        st.subheader("Delete Equipment")
        if equipment_ids:
            selected_equipment_id_to_delete = st.selectbox("Select Equipment to Delete", equipment_ids)
            if selected_equipment_id_to_delete:
                if st.button("Delete Equipment"):
                    try:
                        connection = connect_to_db()
                        cursor = connection.cursor()
                        cursor.execute("DELETE FROM EQUIPMENTS WHERE EQUIP_ID = %s AND BRANCH_ID = %s", 
                                       (selected_equipment_id_to_delete, branch_id_selected))
                        connection.commit()
                        cursor.close()
                        st.warning("Equipment deleted successfully!")
                    except MySQLdb.Error as e:
                        st.error(f"Error deleting equipment: {e}")
                    finally:
                        connection.close()

def add_transaction(transaction_type, trans_id, sender_id, receiver_id, amount):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
           # timestamp = datetime.now()
            cursor.execute(
                "INSERT INTO PAYMENTS (TRANSACTION_TYPE, TRANS_ID, SENDER_ID, RECEIVER_ID, AMOUNT) VALUES (%s, %s, %s, %s, %s)",
                (transaction_type, trans_id, sender_id, receiver_id, amount )
            )
            connection.commit()
            st.success("Transaction added successfully.")
        except MySQLdb.Error as e:
            st.error(f"Error adding transaction: {e}")
        finally:
            cursor.close()
            connection.close()

# Delete a transaction
def delete_transaction(trans_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM PAYMENTS WHERE TRANS_ID = %s", (trans_id,))
            connection.commit()
            st.success("Transaction deleted successfully.")
        except MySQLdb.Error as e:
            st.error(f"Error deleting transaction: {e}")
        finally:
            cursor.close()
            connection.close()

# Payment Management Function for Owner
def payment_management():
    st.title("Owner Payment Management")

    # Tabs for viewing all transactions, filtering, adding, and deleting transactions
    tab1, tab2, tab3, tab4 = st.tabs(["All Transactions", "Filter by Type", "Add Transaction", "Delete Transaction"])

    # All Transactions Tab
    with tab1:
        st.header("All Transactions")
        query = "SELECT TRANSACTION_TYPE, TRANS_ID, SENDER_ID, RECEIVER_ID, AMOUNT, TIMESTAMP FROM PAYMENTS"
        all_transactions = fetch_data(query)
        if all_transactions is not None and not all_transactions.empty:
            st.dataframe(all_transactions)
        else:
            st.write("No transactions found.")

    # Filter by Type Tab
    with tab2:
        st.header("Filter Transactions by Type")
        transaction_type = st.selectbox("Select Transaction Type", ["SALARY", "MEMBERSHIP"])
        query = "SELECT TRANSACTION_TYPE, TRANS_ID, SENDER_ID, RECEIVER_ID, AMOUNT, TIMESTAMP FROM PAYMENTS WHERE TRANSACTION_TYPE = %s"
        filtered_transactions = fetch_data(query, (transaction_type,))
        if filtered_transactions is not None and not filtered_transactions.empty:
            st.dataframe(filtered_transactions)
        else:
            st.write(f"No {transaction_type} transactions found.")

    # Add Transaction Tab
    with tab3:
        st.header("Add New Transaction")
        transaction_type = st.selectbox("Transaction Type", ["SALARY", "MEMBERSHIP"])
        trans_id = st.text_input("Transaction ID", key="trans_id")
        sender_id = st.text_input("Sender ID",  key="send_id")
        receiver_id = st.text_input("Receiver ID", key="receive_id")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        
        if st.button("Add Transaction", key="add_trans"):
            if trans_id and sender_id and receiver_id and amount > 0:
                add_transaction(transaction_type, trans_id, sender_id, receiver_id, amount)
            else:
                st.warning("Please fill all the fields with valid data.")

    # Delete Transaction Tab
    with tab4:
        st.header("Delete Transaction")
        trans_id_to_delete = st.text_input("Enter Transaction ID to Delete")
        
        if st.button("Delete Transaction", key="delete_trans"):
            if trans_id_to_delete:
                delete_transaction(trans_id_to_delete)
            else:
                st.warning("Please enter a Transaction ID.")


# Function to get all plans
def get_all_plans():
    query = "SELECT PLAN_ID, PRICING, DURATION, DESCRIPTION FROM PLANS"
    plans = fetch_data(query)
    return plans

# Function to get subscribers for a specific plan
def get_subscribers_for_plan(plan_id):
    query = """
    SELECT MEMBERS.FIRST_NAME, MEMBERS.LAST_NAME, SUBSCRIPTION.START_DATE 
    FROM SUBSCRIPTION 
    INNER JOIN MEMBERS ON SUBSCRIPTION.MEM_ID = MEMBERS.MEM_ID 
    WHERE SUBSCRIPTION.PLAN_ID = %s
    """
    subscribers = fetch_data(query, (plan_id,))
    return subscribers

# Function to update an existing plan
def update_plan(plan_id, pricing, duration, description):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            UPDATE PLANS 
            SET PRICING = %s, DURATION = %s, DESCRIPTION = %s 
            WHERE PLAN_ID = %s
            """, (pricing, duration, description, plan_id))
            connection.commit()
            st.success("Plan updated successfully.")
        except MySQLdb.Error as e:
            st.error(f"Error updating plan: {e}")
        finally:
            cursor.close()
            connection.close()

# Function to add a new plan
def add_plan(plan_id, pricing, duration, description):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            INSERT INTO PLANS (PLAN_ID, PRICING, DURATION, DESCRIPTION) 
            VALUES (%s, %s, %s, %s)
            """, (plan_id, pricing, duration, description))
            connection.commit()
            st.success("New plan added successfully.")
        except MySQLdb.Error as e:
            st.error(f"Error adding new plan: {e}")
        finally:
            cursor.close()
            connection.close()

# Function to get all available members
def get_all_members():
    query = "SELECT MEM_ID, FIRST_NAME, LAST_NAME FROM MEMBERS"
    members = fetch_data(query)
    return members

# Function to add a new member to a subscription
def add_member_to_subscription(mem_id, plan_id, start_date, transaction_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            INSERT INTO SUBSCRIPTION (MEM_ID, PLAN_ID, START_DATE, TRANSACTION_ID)
            VALUES (%s, %s, %s, %s)
            """, (mem_id, plan_id, start_date, transaction_id))
            connection.commit()
            st.success("Member added to subscription successfully.")
        except MySQLdb.Error as e:
            st.error(f"Error adding member to subscription: {e}")
        finally:
            cursor.close()
            connection.close()
# Function to delete a subscription
def delete_subscription(mem_id, plan_id):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            DELETE FROM SUBSCRIPTION 
            WHERE MEM_ID = %s AND PLAN_ID = %s
            """, (mem_id, plan_id))
            connection.commit()
            st.success("Subscription deleted successfully.")
        except MySQLdb.Error as e:
            st.error(f"Error deleting subscription: {e}")
        finally:
            cursor.close()
            connection.close()

# Subscription Management Function for Owner
def subscription_management():
    st.title("Owner Subscription Management")

    # Tabs for viewing all plans, adding, editing plans, adding member to subscription, deleting subscription
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["All Plans", "Add New Plan", "Edit Plan", "Add Member to Subscription", "Delete Subscription"])

    # All Plans Tab
    with tab1:
        st.header("All Available Plans")
        plans = get_all_plans()
        if plans is not None and not plans.empty:
            st.dataframe(plans)
            for plan in plans.itertuples():
                plan_id = plan.PLAN_ID
                st.subheader(f"Subscribers for Plan: {plan_id}")
                subscribers = get_subscribers_for_plan(plan_id)
                if subscribers is not None and not subscribers.empty:
                    st.write("Subscribers:")
                    st.dataframe(subscribers)
                else:
                    st.write("No subscribers found for this plan.")
        else:
            st.write("No plans available.")

    # Add New Plan Tab
    with tab2:
        st.header("Add New Plan")
        plan_id = st.text_input("Plan ID")
        pricing = st.number_input("Pricing", min_value=0.0, format="%.2f")
        duration = st.number_input("Duration (in months)", min_value=1, step=1)
        description = st.text_input("Description")
        
        if st.button("Add Plan"):
            if plan_id and pricing and duration and description:
                add_plan(plan_id, pricing, duration, description)
            else:
                st.warning("Please fill all the fields with valid data.")

    # Edit Plan Tab
    with tab3:
        st.header("Edit Existing Plan")
        plan_id_to_edit = st.text_input("Enter Plan ID to Edit")
        
        if plan_id_to_edit:
            plans = get_all_plans()
            plan = plans[plans['PLAN_ID'] == plan_id_to_edit]
            if not plan.empty:
                current_pricing = plan['PRICING'].values[0]
                current_duration = plan['DURATION'].values[0]
                current_description = plan['DESCRIPTION'].values[0]
                
                new_pricing = st.number_input("New Pricing", min_value=0.0, value=current_pricing, format="%.2f")
                new_duration = st.number_input("New Duration (in months)", min_value=1, value=current_duration, step=1)
                new_description = st.text_input("New Description", value=current_description)

                if st.button("Update Plan"):
                    update_plan(plan_id_to_edit, new_pricing, new_duration, new_description)
            else:
                st.warning("Plan ID not found.")
    
    # Add Member to Subscription Tab
    with tab4:
        st.header("Add Member to Subscription")
        # Get available plans and members
        plans = get_all_plans()
        members = get_all_members()

        if plans is not None and not plans.empty and members is not None and not members.empty:
            # Select member and plan
            member_id = st.selectbox("Select Member", members['MEM_ID'])
            plan_id = st.selectbox("Select Plan", plans['PLAN_ID'])
            start_date = st.date_input("Start Date")
            transaction_id = st.text_input("Transaction ID")

            if st.button("Add Member to Subscription"):
                if member_id and plan_id and start_date and transaction_id:
                    add_member_to_subscription(member_id, plan_id, start_date, transaction_id)
                else:
                    st.warning("Please fill all fields with valid data.")
        else:
            st.error("No plans or members available.")

    # Delete Subscription Tab
    with tab5:
        st.header("Delete Subscription")
        
        # Get available members and plans for deletion
        plans = get_all_plans()
        members = get_all_members()

        if plans is not None and not plans.empty and members is not None and not members.empty:
            # Select member and plan to delete subscription
            member_id = st.selectbox("Select Member to Remove Subscription", members['MEM_ID'])
            plan_id = st.selectbox("Select Plan to Remove", plans['PLAN_ID'])

            if st.button("Delete Subscription"):
                if member_id and plan_id:
                    delete_subscription(member_id, plan_id)
                else:
                    st.warning("Please select a valid member and plan to delete the subscription.")
        else:
            st.error("No plans or members available.")

def owner_dashboard():
    st.title("Owner Dashboard")
    
    # Create tabs for each section
    tabs = st.tabs(["Member Management", "Classes Management", "Trainer Management", "Branches",
                    "Equipment Management", "Subscription Plans", "Payment Management"]) #

    with tabs[0]:
        member_management()

        # --- Classes Management Tab ---
    with tabs[1]:
        classes_management()

    # --- Trainer Management Tab ---
    with tabs[2]:
        trainer_management()
    # --- branches Management Tab ---
    with tabs[3]:
        branches_management()

    with tabs[4]:
        equipment_management()

    with tabs[5]:
        subscription_management()

    with tabs[6]:
        payment_management()

# To display the dashboard in your main app
owner_dashboard()
