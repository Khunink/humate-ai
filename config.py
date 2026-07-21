import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env (สำหรับรันในเครื่อง)
load_dotenv()

# ดึงค่า Config มาเก็บในตัวแปร เพื่อให้เรียกใช้ง่ายและปลอดภัย
API_URL = os.getenv("OPENWEBUI_API_URL")
API_KEY = os.getenv("OPENWEBUI_API_KEY")
MODEL_NAME = os.getenv("hu-mate") # ถ้าไม่มีการตั้งค่าจะใช้ชื่อ hu-mate เป็นค่าเริ่มต้น