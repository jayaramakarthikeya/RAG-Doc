import streamlit as st
import requests
from time import sleep
from cryptography.fernet import Fernet

key = None
with open('filekey.key', 'rb') as filekey:
    key = filekey.read()

fernet = Fernet(key)

# Set up the page title and description
st.title("Registration Form")
st.write("Please fill in the details below and upload your Medical History file.")

# Create the form
with st.form("registration_form"):
    # Full Name input
    full_name = st.text_input("Full Name")

    # Email input
    email = st.text_input("Email")

    # Age input
    age = st.number_input("Age", min_value=0, max_value=120, step=1)

    # Blood Group input
    blood_group = st.selectbox("Blood Group", 
                                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    # Password input
    password = st.text_input("Password", type="password")
    password = fernet.encrypt(password.encode())

    # File uploader
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    # Submit button
    submitted = st.form_submit_button("Submit")

    st.markdown("Already registered? [Sign In](login)")

    # Handle form submission
    if submitted:
        if uploaded_file is not None:
            # Process the uploaded file if needed
            file_details = {
                "Filename": uploaded_file.name,
                "FileType": uploaded_file.type,
                "FileSize": uploaded_file.size
            }
            st.write(file_details)
            st.success(f"Form submitted successfully for {full_name}!")
            data = {
            'password': password,
            'full_name': full_name,
            'email': email,
            'age': age,
            'blood_group': blood_group
            
            }
            response = requests.post("http://127.0.0.1:8000/register/", data=data, files={"file": uploaded_file})
        
            if response.status_code == 200:
                st.success("User registered successfully!")
            else:
                st.error("Error occurred during registration.")
        else:
            st.error("Please upload a PDF file.")

        sleep(0.5)
        st.switch_page("pages/Home.py")