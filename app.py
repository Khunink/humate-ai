import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
import datetime

# --- 1. การตั้งค่าระบบ ---
load_dotenv()
API_URL = os.getenv("OPENWEBUI_API_URL")
API_KEY = os.getenv("OPENWEBUI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "hu-mate")

st.set_page_config(page_title="Hu-Mate Assist", layout="centered")

# --- 2. CSS: Gemini UI Style ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stChatMessage"] { padding: 1rem 0 !important; background-color: transparent !important; }
    
    /* USER: Right Side */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
    [data-testid="stChatMessage"]:has(img[alt="user avatar"]) { flex-direction: row-reverse !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background-color: #F0F4F9 !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 12px 20px !important;
        margin-right: 12px !important;
        margin-left: 15% !important;
    }

    /* CENTER BUTTON */
    .center-btn-container { display: flex; justify-content: center; width: 100%; margin-bottom: 20px; }
    .stButton > button { border-radius: 25px !important; border: 1px solid #DEE2E6 !important; color: #DC3545 !important; background-color: white !important; padding: 5px 25px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. การจัดการสถานะ ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# --- 4. Logic หน้าประเมิน ---
if st.session_state.show_feedback:
    st.title("📊 ประเมินความพึงพอใจ")
    rating = st.feedback("stars")
    comment = st.text_area("ข้อเสนอแนะ:")
    if st.button("บันทึกและเริ่มใหม่"):
        st.session_state.messages = []
        st.session_state.show_feedback = False
        st.balloons()
        st.rerun()
else:
    st.markdown("<h1 style='text-align: center;'>✨ Hu-Mate Assist</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.messages) == 0:
        st.markdown("<p style='text-align: center; color: #5F6368;'>Easy to Ask, Fast to Flow</p>", unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if len(st.session_state.messages) > 0 and not st.session_state.is_processing:
        st.markdown('<div class="center-btn-container">', unsafe_allow_html=True)
        if st.button("จบการสนทนา"):
            st.session_state.show_feedback = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("พิมพ์ข้อความถามต่อ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.is_processing = True
        st.rerun()

    if st.session_state.is_processing:
        with st.chat_message("assistant"):
            with st.spinner("Hu-Mate กำลังคิด..."):
                response_placeholder = st.empty()
                full_response = ""
                try:
                    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                    payload = {"model": MODEL_NAME, "messages": st.session_state.messages, "stream": True}
                    response = requests.post(API_URL, json=payload, headers=headers, stream=True, timeout=120)
                    
                    for line in response.iter_lines():
                        if line:
                            txt = line.decode('utf-8')
                            if txt.startswith('data: '):
                                js_str = txt[6:]
                                if js_str.strip() == "[DONE]": break
                                try:
                                    content = json.loads(js_str)['choices'][0].get('delta', {}).get('content', '')
                                    full_response += content
                                    response_placeholder.markdown(full_response + "▌")
                                except: continue
                    
                    response_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Error: {e}")
            
            st.session_state.is_processing = False
            st.rerun()