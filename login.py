import streamlit as st
import mysql.connector
import hashlib
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

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Sign up function
def sign_up(username, password, role):
    hashed_password = hash_password(password)
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if role == "Member":
                cursor.execute("INSERT INTO MEMBERS (MEM_ID, PWD) VALUES (%s, %s)", (username, password))
            # elif role == "Trainer":
            #     cursor.execute("INSERT INTO TRAINERS (TRAINER_ID, PWD) VALUES (%s, %s)", (username, hashed_password))
            # elif role == "Owner":
            #     cursor.execute("INSERT INTO OWNERS (OWN_ID, PWD) VALUES (%s, %s)", (username, hashed_password))
            connection.commit()
            st.success("Sign-up successful! You can now log in.")
        except MySQLdb.Error as e:
            st.error(f"Error during sign-up: {e}")
        finally:
            cursor.close()
            connection.close()

# Login function with role-based redirection
def login(username, password, role):
    hashed_password = hash_password(password)
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            if role == "Member":
                cursor.execute("SELECT * FROM MEMBERS WHERE MEM_ID = %s AND PWD = %s", (username, password))
            elif role == "Trainer":
                cursor.execute("SELECT * FROM TRAINERS WHERE TRAIN_ID = %s AND PWD = %s", (username, password))
            elif role == "Owner":
                cursor.execute("SELECT * FROM OWNERS WHERE OWN_ID = %s AND PWD = %s", (username, password))

            user = cursor.fetchone()
            if user:
                # Set session state for redirection
                st.session_state["page"] = "home"
                st.session_state["role"] = role
                st.session_state["id"]=username
                st.success(f"Login successful! Redirecting to {role} dashboard...")
            else:
                st.error("Invalid username or password.")
        except MySQLdb.Error as e:
            st.error(f"Error during login: {e}")
        finally:
            cursor.close()
            connection.close()
