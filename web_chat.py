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

# Initialize Model with System Instructions
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="You are the official Family Pharmacy AI assistant in Qatar. Be helpful, professional, and concise. Always advise users to consult a human doctor for serious symptoms. If products are available in the context, mention them."
)

# 3. DATA ENGINE
API_URL = "https://robustremedy.com/superadmin/api/api/preetchatbotapi.php"

@st.cache_data(ttl=600)
def load_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json().get("data", [])
    except Exception:
        return []

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
        elif any(word in full_blob for word in q.split()): score += 5
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
    st.write("💬 Need human help?")
    label = "🟢 Consult Pharmacist" if language == "English" else "🟢 استشارة صيدلي"
    encoded_msg = urllib.parse.quote("Hello Family Pharmacy, I have a question about my medication.")
    st.markdown(f'''
        <a href="https://wa.me/{whatsapp_number}?text={encoded_msg}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">
                {label}
            </div>
        </a>
    ''', unsafe_allow_html=True)

# 6. CHAT INTERFACE
st.title("Family Pharmacy AI" if language == "English" else "صيدلية العائلة")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. INPUT LOGIC
prompt = st.chat_input("How can I help you today?" if language == "English" else "كيف يمكنني مساعدتك اليوم؟")

if prompt:
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Search Inventory
    results = advanced_search(prompt, inventory)
    context_text = "Available Products in our pharmacy: " + ", ".join([i['item_name'] for i in results])

    # Assistant Response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Build conversation history for the AI
        chat = model.start_chat(history=[
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ])
        
        try:
            # Combine Context and Prompt
            enriched_prompt = f"Context: {context_text}\n\nUser Question: {prompt}\nRespond in {language}."
            response = chat.send_message(enriched_prompt, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"AI Error: {str(e)}")
            full_response = "I apologize, I am having trouble connecting. Please try again."

        # Display Recommended Products
        if results:
            st.divider()
            st.subheader("Recommended for You" if language == "English" else "مقترح لك")
            cols = st.columns(3)
            for idx, item in enumerate(results):
                with cols[idx % 3]:
                    st.container(border=True).image(item['image'], use_container_width=True)
                    st.write(f"**{item['item_name']}**")
                    st.link_button("🛒 Buy Now", item['productlink'], type="primary", use_container_width=True)

    # Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
