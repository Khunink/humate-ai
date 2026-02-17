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

def show_feedback_page(session_id):
    st.title("📊 แบบประเมินความพึงพอใจ")
    
    with st.form("feedback_form"):
        q1 = st.select_slider("1. ข้อมูลที่ได้รับมีความถูกต้อง", options=["1", "2", "3" , "4", "5"])
        q2 = st.select_slider("2. ความครบถ้วนของข้อมูล", options=["1", "2", "3" , "4", "5"])
        q3 = st.select_slider("3. ความพึงพอใจต่อ HU-Mate", options=["1", "2", "3" , "4", "5"])
        q4 = st.text_area("4. ข้อเสนอแนะเพิ่มเติม")
        
        if st.form_submit_button("บันทึกข้อมูล"):
            # ส่งข้อมูลไปบันทึกที่ Database
            feedback_data = [str(uuid.uuid4()), session_id, q1, q2, q3, q4, str(datetime.datetime.now())]
            save_feedback(feedback_data)
            st.success("ขอบคุณสำหรับคำแนะนำค่ะ!")
            return True
    return False