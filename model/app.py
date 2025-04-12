import streamlit as st
import pickle
import json
import numpy as np
from PIL import Image, ImageOps
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('user_credentials.db')
cursor = conn.cursor()

# Create a table to store user credentials if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (email TEXT PRIMARY KEY, password TEXT)''')

# Placeholder database for storing user credentials
user_database = {}

# Function to predict price
def predict_price(location, total_sqft, bath, bhk):
    # Load trained model
    with open("house_price_prediction.pickle", "rb") as f:
        model = pickle.load(f)
    
    # Load column names
    with open("columns.json", "r") as f:
        columns = json.load(f)
        feature_columns = columns["data_columns"]

    # Create input array for prediction
    input_data = np.zeros(len(feature_columns))
    input_data[0] = total_sqft
    input_data[1] = bath
    input_data[2] = bhk
    try:
        loc_index = feature_columns.index(location.lower())
        input_data[loc_index] = 1
    except ValueError:
        pass  # Location not found in columns
    # Predict the price
    predicted_price = model.predict([input_data])[0]
    return predicted_price

# Registration functionality
def registration():
    st.title("Registration")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            st.warning("User already exists! Please login.")
        else:
            # Save user details
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            st.success("Registration successful! Please login.")
            st.button("Login", on_click=set_state, args=("login_page",))

# Authentication function
def authenticate(email, password):
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    if cursor.fetchone():
        return True
    return False.L

# Login functionality
def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Verify the credentials
        if authenticate(email, password):
            st.session_state.authenticated = True
            st.session_state.email = email
            set_state("prediction_page")
        else:
            st.error("Invalid email or password")
    if st.button("Register"):
        set_state("registration_page")

# Streamlit UI for main prediction page
def prediction_page():
    st.title("Welcome to House Price Prediction App")
# Load Image
    image = Image.open(r'D:\study\Final yeat project\demo_Final_year_project\images\house.jpg')

    st.image(image, width=700)
    st.title("House Price Prediction Form")

    # Load column names
    with open("columns.json", "r") as f:
        columns = json.load(f)
        feature_columns = columns["data_columns"]

    # Input components
    location = st.selectbox("Location", feature_columns[3:])  # Skip first 3 columns
    total_sqft = st.number_input("Total Square Feet Area")
    bath = st.number_input("Number of Bathrooms", min_value=1, step=1)
    bhk = st.number_input("Number of Bedrooms", min_value=1, step=1)

    # Predict button
    if st.button("Predict"):
        predicted_price = predict_price(location, total_sqft, bath, bhk)
        st.success(f"Predicted Price: {predicted_price:.2f} LAC ")

# State management
def set_state(state):
    st.session_state.current_page = state

# Main function to control app flow
def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login_page"

    if st.session_state.current_page == "login_page":
        login()
    elif st.session_state.current_page == "registration_page":
        registration()
    elif st.session_state.current_page == "prediction_page":
        prediction_page()

if __name__ == "__main__":
    main()  # or st.cache(main) if you want to cache the main function
