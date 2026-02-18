import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# 1. ตั้งค่า Scopes สำหรับการเข้าถึง Google API
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 2. ฟังก์ชันเชื่อมต่อ Google Sheets แบบใช้ Cache
# ช่วยให้ไม่ต้องต่อเน็ตไปหา Google ใหม่ทุกครั้งที่บันทึกข้อมูล (แอปจะเร็วขึ้นมาก)
@st.cache_resource
def get_spreadsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scopes
    )
    client = gspread.authorize(creds)
    # คืนค่าไฟล์ Spreadsheet กลับไป
    return client.open("HU-Mate_Database")

# เรียกใช้งาน Spreadsheet ผ่าน Cache
sheet = get_spreadsheet()

# --- ฟังก์ชันสำหรับบันทึกข้อมูล (Backend) ---

def save_log(session_data):
    """บันทึกข้อมูลการเข้าใช้งานลงใน Tab 'user_logs'"""
    try:
        wks = sheet.worksheet("user_logs")
        wks.append_row(session_data)
    except Exception as e:
        st.error(f"Error saving log: {e}")

def save_chat(chat_data):
    """บันทึกประวัติการแชทลงใน Tab 'chat_history'"""
    try:
        wks = sheet.worksheet("chat_history")
        wks.append_row(chat_data)
    except Exception as e:
        st.error(f"Error saving chat: {e}")

def save_feedback(feedback_data):
    """บันทึกข้อมูลการประเมินลงใน Tab 'feedback'"""
    try:
        wks = sheet.worksheet("feedback")
        wks.append_row(feedback_data)
    except Exception as e:
        st.error(f"Error saving feedback: {e}")