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
    """หน้าประเมินผล และระบบ Reset กลับหน้าหลัก (Bilingual Version)"""
    # หัวข้อใหญ่ (Main Title)
    st.markdown("<h1 style='text-align: center;'>📊 ประเมินความพึงพอใจ<br><span style='font-size: 24px; color: gray;'>Customer Satisfaction Survey</span></h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>คะแนนของคุณช่วยให้ Hu-Mate พัฒนาได้ดียิ่งขึ้นค่ะ<br>Your feedback helps Hu-Mate improve.</p>", unsafe_allow_html=True)

    st.write("---")
    
    # ข้อ 1: สถานะผู้ใช้บริการ / User Status
    st.write("**1. สถานะผู้ใช้บริการ / User Status**")
    q1 = st.radio(
        label="โปรดเลือกสถานะของคุณ / Please select your status",
        options=[
            "นักศึกษา (Student)", 
            "เจ้าหน้าที่ (Staff)", 
            "อาจารย์ (Faculty/Teacher)", 
            "ผู้ปกครอง (Parent)"
        ],
        index=None,  # เริ่มต้นแบบยังไม่มีการเลือก เพื่อป้องกันผู้ใช้ข้าม
        label_visibility="collapsed"
    )
    
    st.write("---")
    
    # ข้อ 2: ความสะดวก/ รวดเร็วในการเข้าถึง / Convenience and Speed of Access
    st.write("**2. ความสะดวก/ รวดเร็วในการเข้าถึง / Convenience and Speed of Access**")
    st.caption("(ใช้งานง่ายและสอบถามได้ตลอด 24 ชั่วโมง ไม่ต้องรอเวลาราชการ และไม่ต้องรอคำตอบนาน / Easy to use, available 24/7, no need to wait for official hours or long responses)")
    q2 = st.feedback("stars", key="q2")
    
    st.write("---")

    # ข้อ 3: ความถูกต้องของข้อมูล / Accuracy of Information
    st.write("**3. ความถูกต้องของข้อมูล / Accuracy of Information**")
    st.caption("(ข้อมูลที่ได้รับถูกต้อง ครบถ้วน และตรงกับคำถาม / The information received is accurate, complete, and directly answers the question)")
    q3 = st.feedback("stars", key="q3")

    st.write("---")

    # ข้อ 4: ระบบช่วยแก้ปัญหา / ตอบข้อสงสัยได้จริง / Problem-Solving and Inquiry Resolution
    st.write("**4. ระบบช่วยแก้ปัญหา / ตอบข้อสงสัยได้จริง / Problem-Solving & Inquiry Resolution**")
    st.caption("(คำอธิบายเข้าใจง่าย สามารถแก้ปัญหาหรือรับคำแนะนำได้โดยไม่ต้องติดต่อเจ้าหน้าที่ / Explanations are easy to understand, allowing you to solve problems or get advice without contacting staff)")
    q4 = st.feedback("stars", key="q4")

    st.write("---")
    
    # ข้อ 5: ข้อเสนอแนะเพื่อการปรับปรุงและพัฒนาระบบ / Suggestions for Improvement
    comment = st.text_area(
        "**5. ข้อเสนอแนะเพื่อการปรับปรุงและพัฒนาระบบ / Suggestions for Improvement and Development**", 
        placeholder="บอกความรู้สึกหรือข้อเสนอแนะของคุณ... / Share your thoughts or suggestions..."
    )

    # ปุ่มบันทึกการประเมิน
    if st.button("บันทึกการประเมิน / Submit Feedback", use_container_width=True):
        # ตรวจสอบว่าเลือกสถานะ (q1) และให้ดาวข้อ 2,3,4 (q2,q3,q4) ครบถ้วนหรือไม่
        if q1 is not None and q2 is not None and q3 is not None and q4 is not None:
            
            # --- แก้ไขเรื่อง Timezone ให้เป็นเวลาไทย ---
            tz = pytz.timezone('Asia/Bangkok')
            timestamp_th = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            
            # เตรียมข้อมูล 
            feedback_data = [
                str(uuid.uuid4()), 
                session_id, 
                q1,          # จะบันทึกค่าเป็นภาษาไทยพร้อมอังกฤษในวงเล็บ เช่น "นักศึกษา (Student)"
                q2 + 1,      
                q3 + 1,      
                q4 + 1,      
                comment,
                timestamp_th  
            ]
            
            try:
                save_feedback(feedback_data)
                st.success("บันทึกข้อมูลสำเร็จ! ระบบจะพากลับไปหน้าหลัก... / Submitted successfully! Returning to main page...")
                
                # ล้าง Session เพื่อให้เริ่มคุยใหม่ได้ทันที
                st.session_state.show_feedback = False
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                
                time.sleep(1.5)
                st.rerun() 
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด / Error: {e}")
        else:
            st.warning("กรุณาเลือกสถานะและให้ดาวให้ครบทุกหัวข้อก่อนกดบันทึกนะคะ / Please complete all fields and star ratings before submitting.")