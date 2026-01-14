import streamlit as st
import google.generativeai as genai

# 1. SETUP: Gemini requires an API Key instead of a local server
# In Streamlit Cloud, add this to "Advanced Settings > Secrets"
genai.configure(api_key=st.secrets["AIzaSyA88af8HzXTHe959_ek92Es6b8FDKS5aXU"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("Family Pharmacy AI (Gemini)")

# 2. MEMORY: Use Streamlit's session_state to persist history across browser refreshes
if "chat_session" not in st.session_state:
    # Initializing Gemini's built-in chat manager
    st.session_state.chat_session = model.start_chat(history=[])

# 3. DISPLAY: Show past messages from the chat session history
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 4. INPUT: Handle new user queries
if prompt := st.chat_input("How can I help you today?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    # 5. RESPONSE: Send message to the session (it remembers the previous turns)
    response = st.session_state.chat_session.send_message(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
