import streamlit as st
import uuid
import datetime
import time
import pytz  # เพิ่มการจัดการ Timezone
from database_handler import save_feedback

def apply_custom_css():
    """ฟังก์ชันแต่งสวย: รองรับทั้งโหมดมืดและสว่างอัตโนมัติ"""
    st.markdown("""
        <style>
        /* ปรับพื้นหลังตาม Theme ของระบบ */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .center-btn-container {
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        
        /* ตกแต่งปุ่มให้เด่นชัด */
        div.stButton > button {
            background-color: #ff4b4b;
            color: white !important;
            border-radius: 20px;
            padding: 10px 25px;
            border: none;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def show_feedback_page(session_id):
    """หน้าประเมินผล 5 ดาว และระบบ Reset กลับหน้าหลัก"""
    st.markdown("<h1 style='text-align: center;'>📊 ประเมินความพึงพอใจ</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>คะแนนของคุณช่วยให้ Hu-Mate พัฒนาได้ดียิ่งขึ้นค่ะ</p>", unsafe_allow_html=True)

    st.write("---")
    
    # ส่วนการให้คะแนน (จัดวางให้อ่านง่ายขึ้น)
    st.write("**1. ความแม่นยำของคำแนะนำ**")
    q1 = st.feedback("stars", key="q1")
    
    st.write("**2. ความรวดเร็วในการตอบ**")
    q2 = st.feedback("stars", key="q2")

    st.write("**3. ความสุภาพและเป็นมิตร**")
    q3 = st.feedback("stars", key="q3")

    st.write("**4. ความง่ายในการใช้งานระบบ**")
    q4 = st.feedback("stars", key="q4")

    st.write("---")
    comment = st.text_area("ข้อเสนอแนะเพิ่มเติม", placeholder="บอกความรู้สึกของคุณ...")

    if st.button("บันทึกการประเมิน", use_container_width=True):
        if q1 is not None and q2 is not None and q3 is not None and q4 is not None:
            
            # --- แก้ไขเรื่อง Timezone ให้เป็นเวลาไทย ---
            tz = pytz.timezone('Asia/Bangkok')
            timestamp_th = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            
            # เตรียมข้อมูล (บวก 1 เพื่อให้เป็นคะแนน 1-5)
            feedback_data = [
                str(uuid.uuid4()), 
                session_id, 
                q1 + 1, q2 + 1, q3 + 1, q4 + 1, 
                comment,
                timestamp_th  # ใช้เวลาไทยที่จัด Format แล้ว
            ]
            
            try:
                save_feedback(feedback_data)
                st.success("บันทึกข้อมูลสำเร็จ! ระบบจะพากลับไปหน้าหลัก...")
                
                # ล้าง Session เพื่อให้เริ่มคุยใหม่ได้ทันที
                st.session_state.show_feedback = False
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                
                time.sleep(1.5)
                st.rerun() 
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
        else:
            st.warning("กรุณาให้ดาวให้ครบทุกหัวข้อก่อนกดบันทึกนะคะ")