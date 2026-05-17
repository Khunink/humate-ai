import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# 1. ตั้งค่า Scopes สำหรับการเข้าถึง Google API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# 2. ฟังก์ชันเชื่อมต่อ Google Sheets แบบใช้ Cache
# FIX: ย้ายการเรียก get_spreadsheet() ออกจาก module level
# ก่อนหน้านี้ `sheet = get_spreadsheet()` ถูกเรียกตอน import ซึ่งทำให้
# แอปพัง (EnvironmentError) ถ้า st.secrets ยังไม่พร้อม
# ตอนนี้ทุกฟังก์ชันเรียก _get_sheet() เองซึ่งใช้ cache ดังนั้นยังเร็วเท่าเดิม
@st.cache_resource
def get_spreadsheet():
    """สร้าง connection ไปยัง Google Sheets และ cache ไว้ตลอด session"""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client.open("HU-Mate_Database")


def _get_sheet():
    """Helper: ดึง spreadsheet object จาก cache (lazy init)"""
    return get_spreadsheet()


# ── ฟังก์ชันสำหรับบันทึกข้อมูล (Backend) ─────────────────────────────────

def save_log(session_data: list) -> None:
    """บันทึกข้อมูลการเข้าใช้งานลงใน Tab 'user_logs'"""
    try:
        wks = _get_sheet().worksheet("user_logs")
        wks.append_row(session_data)
    except Exception as e:
        st.error(f"Error saving log: {e}")


def save_chat(chat_data: list) -> None:
    """บันทึกประวัติการแชทลงใน Tab 'chat_history'"""
    try:
        wks = _get_sheet().worksheet("chat_history")
        wks.append_row(chat_data)
    except Exception as e:
        st.error(f"Error saving chat: {e}")


def save_feedback(feedback_data: list) -> None:
    """บันทึกข้อมูลการประเมินลงใน Tab 'feedback'"""
    try:
        wks = _get_sheet().worksheet("feedback")
        wks.append_row(feedback_data)
    except Exception as e:
        st.error(f"Error saving feedback: {e}")
