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
    """หน้าประเมินผล และระบบ Reset กลับหน้าหลัก"""
    st.markdown("<h1 style='text-align: center;'>📊 ประเมินความพึงพอใจ</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>คะแนนของคุณช่วยให้ Hu-Mate พัฒนาได้ดียิ่งขึ้นค่ะ</p>", unsafe_allow_html=True)

    st.write("---")
    
    # ข้อ 1: สถานะผู้ใช้บริการ (เปลี่ยนเป็น Radio ตามช้อยส์)
    st.write("**1. สถานะผู้ใช้บริการ**")
    q1 = st.radio(
        label="โปรดเลือกสถานะของคุณ",
        options=["นักศึกษา", "เจ้าหน้าที่", "อาจารย์", "ผู้ปกครอง"],
        index=None,  # เริ่มต้นแบบยังไม่มีการเลือก เพื่อป้องกันผู้ใช้ข้าม
        label_visibility="collapsed"
    )
    
    st.write("---")
    
    # ข้อ 2: ความสะดวก/ รวดเร็วในการเข้าถึง
    st.write("**2. ความสะดวก/ รวดเร็วในการเข้าถึง**")
    st.caption("(ใช้งานง่ายและสอบถามได้ตลอด 24 ชั่วโมง ไม่ต้องรอเวลาราชการ และไม่ต้องรอคำตอบนาน)")
    q2 = st.feedback("stars", key="q2")
    
    st.write("---")

    # ข้อ 3: ความถูกต้องของข้อมูล
    st.write("**3. ความถูกต้องของข้อมูล**")
    st.caption("(ข้อมูลที่ได้รับถูกต้อง ครบถ้วน และตรงกับคำถาม)")
    q3 = st.feedback("stars", key="q3")

    st.write("---")

    # ข้อ 4: ระบบช่วยแก้ปัญหา / ตอบข้อสงสัยได้จริง
    st.write("**4. ระบบช่วยแก้ปัญหา / ตอบข้อสงสัยได้จริง**")
    st.caption("(คำอธิบายเข้าใจง่าย สามารถแก้ปัญหาหรือรับคำแนะนำได้โดยไม่ต้องติดต่อเจ้าหน้าที่)")
    q4 = st.feedback("stars", key="q4")

    st.write("---")
    
    # ข้อ 5: ข้อเสนอแนะเพื่อการปรับปรุงและพัฒนาระบบ
    comment = st.text_area("**5. ข้อเสนอแนะเพื่อการปรับปรุงและพัฒนาระบบ**", placeholder="บอกความรู้สึกหรือข้อเสนอแนะของคุณ...")

    if st.button("บันทึกการประเมิน", use_container_width=True):
        # ตรวจสอบว่าเลือกสถานะ (q1) และให้ดาวข้อ 2,3,4 (q2,q3,q4) ครบถ้วนหรือไม่
        if q1 is not None and q2 is not None and q3 is not None and q4 is not None:
            
            # --- แก้ไขเรื่อง Timezone ให้เป็นเวลาไทย ---
            tz = pytz.timezone('Asia/Bangkok')
            timestamp_th = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            
            # เตรียมข้อมูล 
            # q1 เก็บเป็นข้อความตัวเลือก (เช่น "นักศึกษา")
            # q2, q3, q4 บวก 1 เพื่อให้เป็นคะแนนดาว 1-5
            feedback_data = [
                str(uuid.uuid4()), 
                session_id, 
                q1,          # ข้อ 1 เป็น Text จาก Radio
                q2 + 1,      # ข้อ 2 เป็น คะแนนดาว 1-5
                q3 + 1,      # ข้อ 3 เป็น คะแนนดาว 1-5
                q4 + 1,      # ข้อ 4 เป็น คะแนนดาว 1-5
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
            st.warning("กรุณาเลือกสถานะและให้ดาวให้ครบทุกหัวข้อก่อนกดบันทึกนะคะ")