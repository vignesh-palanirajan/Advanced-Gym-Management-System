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
    if st.button("View Members"):
        df = fetch_data("SELECT MEM_ID, GENDER, EMAIL, FIRST_NAME, LAST_NAME, PLAN_ID, BRANCH_ID, STATUS FROM MEMBERS")
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.error("No members found.")

    # Section for updating member details by entering MEM_ID
    st.header("Update Member")
    update_member_id = st.text_input("Enter Member ID to Update")
    if update_member_id:
        # Fetch the member's current data based on `update_member_id`
        df = fetch_data("SELECT MEM_ID, GENDER, EMAIL, FIRST_NAME, LAST_NAME, PLAN_ID, BRANCH_ID, STATUS FROM MEMBERS WHERE MEM_ID = %s", (update_member_id,))
        
        if not df.empty:
            row = df.iloc[0]
            
            # Collect updated values for each field
            update_data = {
                "FIRST_NAME": st.text_input("Edit First Name", value=row['FIRST_NAME']),
                "LAST_NAME": st.text_input("Edit Last Name", value=row['LAST_NAME']),
                "GENDER": st.selectbox("Edit Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(row['GENDER'])),
                "EMAIL": st.text_input("Edit Email", value=row['EMAIL']),
                "PLAN_ID": st.text_input("Edit Plan ID", value=row['PLAN_ID']),
    
                "BRANCH_ID": st.text_input("Edit Branch ID", value=row['BRANCH_ID']),
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
        new_member_plan_id = st.text_input("Plan ID")
        new_member_branch_id = st.text_input("Branch ID")
        new_member_status = st.selectbox("Status", ["Active", "Inactive"])

        if st.button("Submit New Member"):
            if new_member_id and new_member_first_name and new_member_last_name and new_member_email:
                connection = connect_to_db()
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        """
                        INSERT INTO MEMBERS (MEM_ID, FIRST_NAME, LAST_NAME, GENDER, EMAIL, PLAN_ID,  BRANCH_ID, STATUS) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (new_member_id, new_member_first_name, new_member_last_name, new_member_gender, new_member_email,
                         new_member_plan_id, new_member_branch_id, new_member_status)
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

    # --- Payment Management Tab ---
    with tabs[4]:
        st.subheader("Payment Management")
        
        # Process a new payment
        with st.expander("Process New Payment"):
           # member_id = st.text_input("Member ID")
            payment_amount = st.number_input("Payment Amount", min_value=0.0)
            payment_date = st.date_input("Payment Date")
            if st.button("Submit Payment"):
                connection = connect_to_db()
                cursor = connection.cursor()
                #cursor.execute("INSERT INTO PAYMENTS (MemberID, Amount, Date) VALUES (%s, %s, %s)",
                            #   (member_id, payment_amount, payment_date))
                connection.commit()
                st.success("Payment processed successfully!")
                cursor.close()
                connection.close()
        
        # View payment history
        if st.button("View Payment History"):
            df = fetch_data("SELECT * FROM PAYMENTS")
            if df is not None:
                st.dataframe(df)

# To display the dashboard in your main app
owner_dashboard()
