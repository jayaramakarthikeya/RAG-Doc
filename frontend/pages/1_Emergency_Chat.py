import streamlit as st
import replicate
import os
import requests
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time


API_URL = "http://127.0.0.1:8000/query/"
# App title
st.set_page_config(page_title="Symptoms Prediction")
    
st.sidebar.header("Symptoms Prediction")
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Please tell me what are you facing problems? PS. We respect your privacy so we are not using any public \
                                available LLM APIs to chat with you today."}]



# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Please tell me what are facing problems? \n How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = ""
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    
    try:
            response = requests.post(API_URL, params={"question": prompt_input})
            response.raise_for_status()
            bot_response = response.json().get("result", "Sorry, I didn't understand that.")
    except requests.exceptions.RequestException as e:
            bot_response = f"Error: {e}"
    return bot_response

# User-provided prompt
if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)