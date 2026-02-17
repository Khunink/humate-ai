import gspread
from google.oauth2.service_account import Credentials
import uuid
import datetime

# ตั้งค่าสิทธิ์การเข้าถึง Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
# ไฟล์ JSON นี้จะได้จากการสร้าง Service Account ใน Google Cloud
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("HU-Mate_Database")

def save_log(session_data):
    # บันทึกข้อมูลการเข้าใช้งาน (Log)
    wks = sheet.worksheet("user_logs")
    wks.append_row(session_data)

def save_chat(chat_data):
    # บันทึกประวัติคำถาม-คำตอบ
    wks = sheet.worksheet("chat_history")
    wks.append_row(chat_data)

def save_feedback(feedback_data):
    # บันทึกแบบประเมิน
    wks = sheet.worksheet("feedback")
    wks.append_row(feedback_data)