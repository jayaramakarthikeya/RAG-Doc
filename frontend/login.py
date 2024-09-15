import streamlit as st
from time import sleep
from cryptography.fernet import Fernet
import requests

key = None
with open('filekey.key', 'rb') as filekey:
    key = filekey.read()

fernet = Fernet(key)

from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

 


username = st.text_input("Username")
password = st.text_input("Password", type="password")
password = fernet.encrypt(password.encode())
st.markdown("Not registered yet? [Sign Up](Register)")
if st.button("Log in", type="primary"):
    
    if username and password:
        data = {
            'full_name': username,
            'password': password
        }
        response = requests.post("http://localhost:8000/login/", data=data)
        if response.status_code == 200:
            st.success("Login successful!")
        elif response.status_code == 404:
            st.error("User not found.")
            st.switch_page("pages/2_Register.py")
        elif response.status_code == 401:
            st.error("Incorrect password.")
            st.switch_page("login.py")
        else:
            st.error("An unexpected error occurred.")
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/Home.py")
        
    else:
        st.error("Incorrect username or password")


