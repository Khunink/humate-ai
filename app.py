import streamlit as st
import uuid
import platform
import datetime
import pytz  # สำหรับจัดการ Timezone
import config
from ui_components import apply_custom_css, show_feedback_page
from api_handler import stream_ai_response
from database_handler import save_log, save_chat

# กำหนด Timezone ไทย
tz = pytz.timezone('Asia/Bangkok')

# จัดการเรื่อง Session ID และ User Log (บันทึกเมื่อเปิดแอปครั้งแรก)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
    # ดึงเวลาปัจจุบันแบบไทย
    timestamp_th = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    # เตรียมข้อมูล Log (ID, วันเวลา, อุปกรณ์)
    user_data = [
        st.session_state.session_id,
        "Guest", 
        timestamp_th,
        f"{platform.system()} {platform.release()}", 
        "Streamlit Web"
    ]
    
    # เรียกใช้ฟังก์ชันบันทึก User Log
    try:
        save_log(user_data)
    except Exception as e:
        print(f"Error saving log: {e}")

# 1. ตั้งค่าหน้าเว็บและโหลด CSS
st.set_page_config(page_title="Hu-Mate Assist", layout="centered")
apply_custom_css()

# 2. จัดการสถานะ (Session State)
if "messages" not in st.session_state: st.session_state.messages = []
if "show_feedback" not in st.session_state: st.session_state.show_feedback = False
if "is_processing" not in st.session_state: st.session_state.is_processing = False

# 3. เลือกหน้าที่จะแสดง (แชท หรือ ประเมิน)
if st.session_state.show_feedback:
    show_feedback_page(st.session_state.session_id)
else:
    st.markdown("<h1 style='text-align: center;'>✨ Hu-Mate Assist</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Easy to Ask, Fast to Flow</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>ช่วยประเมินเพื่อเป็นกำลังใจให้ด้วยนะคะ</p>", unsafe_allow_html=True)

    # แสดงประวัติการแชท
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ปุ่มจบการสนทนา
    if len(st.session_state.messages) > 0 and not st.session_state.is_processing:
        st.markdown('<div class="center-btn-container">', unsafe_allow_html=True)
        if st.button("ประเมินความพึงพอใจ / Feedback", use_container_width=True):
            st.session_state.show_feedback = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ช่องรับคำถาม
    if prompt := st.chat_input("พิมพ์ข้อความถามต่อ... / Type your message here...", disabled=st.session_state.is_processing):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.is_processing = True
        st.rerun()

    # ส่วนที่ AI กำลังประมวลผลคำตอบ
    if st.session_state.is_processing:
        with st.chat_message("assistant"):
            with st.spinner("Hu-Mate Thinking..."):
                resp_placeholder = st.empty()
                # ดึงคำถามล่าสุด
                user_prompt = st.session_state.messages[-1]["content"]
                # เรียกใช้ API
                answer = stream_ai_response(st.session_state.messages, resp_placeholder)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # --- บันทึก Chat History (ใช้เวลาไทย) ---
                try:
                    chat_timestamp = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                    chat_entry = [
                        str(uuid.uuid4()),            # chat_id
                        st.session_state.session_id,  # session_id
                        chat_timestamp,               # timestamp ไทย
                        user_prompt,                  
                        answer                        
                    ]
                    save_chat(chat_entry)
                except Exception as e:
                    print(f"Error saving chat history: {e}")
        
        st.session_state.is_processing = False
        st.rerun()