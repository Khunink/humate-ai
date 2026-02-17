import streamlit as st

def apply_custom_css():
    """ฟังก์ชันสำหรับรวมสไตล์ CSS ทั้งหมด (Requirement 2.1: รองรับ Dark/Light Mode)"""
    st.markdown("""
        <style>
        .stApp { background-color: transparent; } /* ให้ปรับตามธีมของ Browser */
        
        /* จัดตำแหน่งข้อความแชท */
        [data-testid="stChatMessage"] { padding: 1rem 0 !important; }
        
        /* สไตล์ปุ่มจบการสนทนาให้อยู่ตรงกลาง (Requirement 3) */
        .center-btn-container { display: flex; justify-content: center; width: 100%; margin-bottom: 20px; }
        .stButton > button { 
            border-radius: 25px !important; 
            color: #DC3545 !important; 
            border: 1px solid #DEE2E6 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def show_feedback_page():
    """ส่วนการแสดงผลหน้าประเมินความพึงพอใจ"""
    st.title("📊 ประเมินความพึงพอใจ")
    rating = st.feedback("stars")
    comment = st.text_area("ข้อเสนอแนะ:")
    if st.button("บันทึกและเริ่มใหม่"):
        st.session_state.messages = [] # ล้างประวัติแชท
        st.session_state.show_feedback = False # กลับไปหน้าแชท
        st.balloons() # แสดงลูกโป่งฉลอง
        st.rerun()