import streamlit as st
import google.generativeai as genai

# 1. SECURE SETUP
# Use st.secrets to hide your key from GitHub
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key! Please add it to Streamlit Secrets.")
    st.stop()

# Initialize the model once
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("Family Pharmacy AI 💊")

# 2. INITIALIZE SESSION STATE
# We need to store 'messages' to show them on the screen
if "messages" not in st.session_state:
    st.session_state.messages = []

# We store the 'chat_session' to keep the AI's "memory"
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 3. DISPLAY CHAT HISTORY
# This ensures old messages stay on the screen when the user types something new
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. USER INPUT
if prompt := st.chat_input("How can I help you today?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to our local history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. GENERATE RESPONSE
    try:
        # Send message to Gemini's internal memory session
        response = st.session_state.chat_session.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Add assistant response to our local history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
