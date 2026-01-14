import streamlit as st
import google.generativeai as genai
import requests
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="Family Pharmacy AI", page_icon="💊", layout="centered")

# 2. SETUP GEMINI
# We use st.secrets so your API key stays hidden on GitHub
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key! Please add it to Streamlit Secrets.")

model = genai.GenerativeModel('gemini-1.5-flash')

# 3. DATA ENGINE
API_URL = "https://robustremedy.com/superadmin/api/api/preetchatbotapi.php"

@st.cache_data(ttl=600)
def load_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json().get("data", [])
    except: return []

inventory = load_data()

# 4. SEARCH LOGIC
def advanced_search(query, items):
    q = query.lower().strip()
    scored_matches = []
    for item in items:
        name = str(item.get('item_name', '')).lower()
        full_blob = " ".join([str(v) for v in item.values()]).lower()
        score = 0
        if q in name: score += 20
        elif q in full_blob: score += 5
        if score > 0: scored_matches.append((score, item))
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in scored_matches[:6]]

# 5. SIDEBAR
with st.sidebar:
    st.image("https://onlinefamilypharmacy.com/images/logo.png", width=250)
    language = st.selectbox("Select Language / اختر اللغة", ["English", "Arabic"])
    st.divider()
    
    # WhatsApp Integration
    whatsapp_number = "+91 8879905105" 
    if st.button("🟢 Consult Pharmacist" if language == "English" else "🟢 استشارة صيدلي", use_container_width=True):
        st.markdown(f'<a href="https://wa.me/{whatsapp_number}" target="_blank">Open WhatsApp</a>', unsafe_allow_html=True)

# 6. CHAT INTERFACE
st.title("Family Pharmacy AI" if language == "English" else "صيدلية العائلة")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. INPUT LOGIC
prompt = st.chat_input("Ask about medicine...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    results = advanced_search(prompt, inventory)
    context = "Available Products: " + ", ".join([i['item_name'] for i in results])

    with st.chat_message("assistant"):
        placeholder = st.empty()
        # Gemini API Call replacing Ollama
        response = model.generate_content(f"Pharmacy AI: {prompt}. Context: {context}", stream=True)
        
        full_response = ""
        for chunk in response:
            full_response += chunk.text
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

        if results:
            st.divider()
            cols = st.columns(3)
            for idx, item in enumerate(results):
                with cols[idx % 3]:
                    st.image(item['image'], use_container_width=True)
                    st.write(f"**{item['item_name']}**")
                    st.link_button("🛒 Buy Now", item['productlink'], type="primary", use_container_width=True)
