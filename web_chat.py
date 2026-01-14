import streamlit as st
import google.generativeai as genai
import requests
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="Family Pharmacy AI", page_icon="💊", layout="wide")

# 2. SECURE API SETUP
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ API Key not found! Please add 'GEMINI_API_KEY' to your Streamlit Cloud Secrets.")
    st.stop()

# 3. ROBUST MODEL INITIALIZATION (Fixes 404 Errors)
def get_working_model():
    # Priority list of model names to try
    model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    for name in model_names:
        try:
            m = genai.GenerativeModel(
                model_name=name,
                system_instruction="You are a professional pharmacy assistant in Qatar. Be concise. Advise doctor visits for serious symptoms."
            )
            # Test call to verify model availability
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except Exception:
            continue
    return genai.GenerativeModel('gemini-1.5-flash') # Default fallback

model = get_working_model()

# 4. DATA ENGINE
API_URL = "https://robustremedy.com/superadmin/api/api/preetchatbotapi.php"

@st.cache_data(ttl=600)
def load_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json().get("data", [])
    except:
        return []

inventory = load_data()

# 5. SEARCH LOGIC
def advanced_search(query, items):
    q = query.lower().strip()
    scored_matches = []
    for item in items:
        name = str(item.get('item_name', '')).lower()
        blob = " ".join([str(v) for v in item.values()]).lower()
        score = 20 if q in name else (5 if any(w in blob for w in q.split()) else 0)
        if score > 0: scored_matches.append((score, item))
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in scored_matches[:6]]

# 6. SIDEBAR & UI
with st.sidebar:
    st.image("https://onlinefamilypharmacy.com/images/logo.png", width=250)
    language = st.selectbox("Language / اللغة", ["English", "Arabic"])
    st.divider()
    whatsapp_number = "+91 8879905105" 
    label = "🟢 Consult Pharmacist" if language == "English" else "🟢 استشارة صيدلي"
    st.markdown(f'''<a href="https://wa.me/{whatsapp_number}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">{label}</div></a>''', unsafe_allow_html=True)

st.title("Family Pharmacy AI" if language == "English" else "صيدلية العائلة")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. CHAT LOGIC WITH MEMORY
prompt = st.chat_input("Ask about medicine..." if language == "English" else "اسأل عن الدواء...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    results = advanced_search(prompt, inventory)
    context = "Products: " + ", ".join([i['item_name'] for i in results])

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Convert history to Gemini format (user/model roles)
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ]
        
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(f"Context: {context}\n\nUser: {prompt}\nRespond in {language}.", stream=True)
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"AI Error: {str(e)}")
            full_response = "Connection error. Please try again."

        if results:
            st.divider()
            cols = st.columns(3)
            for idx, item in enumerate(results):
                with cols[idx % 3]:
                    st.container(border=True).image(item['image'], use_container_width=True)
                    st.write(f"**{item['item_name']}**")
                    st.link_button("🛒 Buy Now", item['productlink'], type="primary", use_container_width=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
