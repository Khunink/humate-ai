import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# 1. ตั้งค่า Scopes (ต้องมีทั้ง Sheets และ Drive)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 2. เชื่อมต่อกับ Google Sheets
# ใช้ st.cache_resource เพื่อให้เชื่อมต่อแค่ครั้งเดียว ช่วยให้แอปไม่อืด
@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scopes
    )
    return gspread.authorize(creds)

# ดึง Client และเปิด Spreadsheet
client = get_gspread_client()
sheet = client.open("HU-Mate_Database")

# --- ฟังก์ชันสำหรับบันทึกข้อมูล ---

def save_log(session_data):
    """บันทึกข้อมูลการเข้าใช้งาน (Log)"""
    try:
        wks = sheet.worksheet("user_logs")
        wks.append_row(session_data)
    except Exception as e:
        st.error(f"Error saving log: {e}")

def save_chat(chat_data):
    """บันทึกประวัติคำถาม-คำตอบ"""
    try:
        wks = sheet.worksheet("chat_history")
        wks.append_row(chat_data)
    except Exception as e:
        st.error(f"Error saving chat: {e}")

def save_feedback(feedback_data):
    """บันทึกแบบประเมินความพึงพอใจ"""
    try:
        wks = sheet.worksheet("feedback")
        wks.append_row(feedback_data)
    except Exception as e:
        st.error(f"Error saving feedback: {e}")