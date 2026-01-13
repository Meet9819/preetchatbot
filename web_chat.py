import streamlit as st
import ollama
import requests
import urllib.parse

# 1. PAGE CONFIG
st.set_page_config(page_title="Family Pharmacy AI", page_icon="💊", layout="centered")

# 2. DATA ENGINE
API_URL = "https://robustremedy.com/superadmin/api/api/preetchatbotapi.php"

@st.cache_data(ttl=600)
def load_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json().get("data", [])
    except: return []

inventory = load_data()

# 3. ADVANCED SEARCH LOGIC
def advanced_search(query, items):
    q = query.lower().strip()
    search_terms = q.split()
    symptom_map = {
        "fever": ["panadol", "paracetamol", "relief", "syrup"],
        "cough": ["syrup", "expectorant", "chest", "mucus"],
        "dental": ["colgate", "toothpaste", "oral", "brush"],
    }
    for symptom, keywords in symptom_map.items():
        if symptom in q: search_terms.extend(keywords)
    
    scored_matches = []
    for item in items:
        name = str(item.get('item_name', '')).lower()
        full_blob = " ".join([str(v) for v in item.values()]).lower()
        score = 0
        for term in search_terms:
            if term in name: score += 15 # Brand boost
            elif term in full_blob: score += 2
        if score > 0: scored_matches.append((score, item))
    
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in scored_matches[:6]]

# 4. SIDEBAR SETTINGS (Branding, Categories & Locator)
with st.sidebar:
    st.image("https://onlinefamilypharmacy.com/images/logo.png", width=300)
    st.title("Family Pharmacy")
    
    language = st.selectbox("Select Language / اختر اللغة", ["English", "Arabic"])
    st.divider()

    # Top Categories
    st.write("### 🛍️ Quick Browse" if language == "English" else "### 🛍️ تصفح الفئات")
    cat_cols = st.columns(2)
    # Using small dummy searches to simulate category filtering
    if cat_cols[0].button("💊 Meds" if language == "English" else "💊 أدوية"):
        st.session_state.cat_trigger = "medicine"
    if cat_cols[1].button("👶 Baby" if language == "English" else "👶 أطفال"):
        st.session_state.cat_trigger = "baby"
    if cat_cols[0].button("🍎 Vit" if language == "English" else "🍎 فيتامين"):
        st.session_state.cat_trigger = "vitamin"
    if cat_cols[1].button("🦷 Dental" if language == "English" else "🦷 أسنان"):
        st.session_state.cat_trigger = "dental"
    
    st.divider()
    
    # WhatsApp & Store Locator
    whatsapp_number = "97400000000" 
    if st.button("🟢 Consult Pharmacist" if language == "English" else "🟢 استشارة صيدلي"):
        last_msg = st.session_state.messages[-1]['content'] if st.session_state.messages else ""
        msg_encoded = urllib.parse.quote(f"Hi Family Pharmacy, I need help with: {last_msg}")
        st.markdown(f'<a href="https://wa.me/{whatsapp_number}?text={msg_encoded}" target="_blank">Open WhatsApp</a>', unsafe_allow_html=True)

    if st.button("📍 Store Locator" if language == "English" else "📍 موقعنا"):
         st.markdown(f'<a href="https://google.com/maps" target="_blank">View Maps</a>', unsafe_allow_html=True)

# 5. CHAT INTERFACE
st.title("Family Pharmacy AI" if language == "English" else "صيدلية العائلة - الذكاء الاصطناعي")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "products" in msg:
            cols = st.columns(3)
            for idx, item in enumerate(msg["products"]):
                with cols[idx % 3]:
                    st.image(item['image'], use_container_width=True)
                    st.caption(f"**{item['item_name']}**")

# 6. INPUT LOGIC
# Check if a category button was clicked
prompt = st.chat_input("How can I help you today?" if language == "English" else "كيف يمكنني مساعدتك اليوم؟")
if "cat_trigger" in st.session_state:
    prompt = st.session_state.pop("cat_trigger")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    results = advanced_search(prompt, inventory)
    context = "Available Products at Family Pharmacy:\n" + "\n".join([f"- {i['item_name']} ({i['RS Price']} QAR)" for i in results])

    sys_prompt = f"You are the official AI Pharmacist for Family Pharmacy in Qatar. Respond ONLY in {language}."
    if any(s in prompt.lower() for s in ["fever", "cough", "pain"]):
        safety_note = "If advising on symptoms, you MUST ask for the patient's age." if language == "English" else "عند تقديم المشورة بشأن الأعراض، يجب عليك السؤال عن عمر المريض."
        sys_prompt += f" {safety_note}"

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        stream = ollama.chat(
            model='llama3.2',
            messages=[{"role": "system", "content": f"{sys_prompt}\n\n{context}"}, {"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            full_response += chunk['message']['content']
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

        if results:
            st.markdown("---")
            p_cols = st.columns(3)
            for idx, item in enumerate(results):
                with p_cols[idx % 3]:
                    st.image(item['image'], use_container_width=True)
                    st.markdown(f"[{item['item_name']}]({item['productlink']})")
                    st.write(f"**{item['RS Price']} QAR**")

    st.session_state.messages.append({"role": "assistant", "content": full_response, "products": results})
    st.rerun()