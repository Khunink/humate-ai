import streamlit as st
import config
from ui_components import apply_custom_css, show_feedback_page
from api_handler import stream_ai_response

# 1. ตั้งค่าหน้าเว็บและโหลด CSS
st.set_page_config(page_title="Hu-Mate Assist", layout="centered")
apply_custom_css()

# 2. จัดการสถานะ (Session State)
if "messages" not in st.session_state: st.session_state.messages = []
if "show_feedback" not in st.session_state: st.session_state.show_feedback = False
if "is_processing" not in st.session_state: st.session_state.is_processing = False

# 3. เลือกหน้าที่จะแสดง (แชท หรือ ประเมิน)
if st.session_state.show_feedback:
    show_feedback_page()
else:
    st.markdown("<h1 style='text-align: center;'>✨ Hu-Mate Assist</h1>", unsafe_allow_html=True)
    
    # แสดงประวัติการแชท
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ปุ่มจบการสนทนา (จะหายไปเมื่อ AI กำลังประมวลผล)
    if len(st.session_state.messages) > 0 and not st.session_state.is_processing:
        st.markdown('<div class="center-btn-container">', unsafe_allow_html=True)
        if st.button("จบการสนทนา"):
            st.session_state.show_feedback = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ช่องรับคำถาม (Requirement 5: disabled=True เมื่อกำลังตอบ)
    if prompt := st.chat_input("พิมพ์ข้อความถามต่อ...", disabled=st.session_state.is_processing):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.is_processing = True
        st.rerun() # รีโหลดเพื่อให้ input กลายเป็นสีเทาทันที

    # ส่วนที่ AI กำลังประมวลผลคำตอบ
    if st.session_state.is_processing:
        with st.chat_message("assistant"):
            with st.spinner("Hu-Mate กำลังคิด..."):
                resp_placeholder = st.empty() # จองพื้นที่สำหรับแสดงคำตอบที่ค่อยๆ โผล่มา
                # เรียกใช้ Backend เพื่อดึงคำตอบ
                answer = stream_ai_response(st.session_state.messages, resp_placeholder)
                st.session_state.messages.append({"role": "assistant", "content": answer})
        
        st.session_state.is_processing = False # ปลดล็อกหน้าจอให้พิมพ์ต่อได้
        st.rerun()