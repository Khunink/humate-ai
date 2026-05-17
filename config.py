import os
import sys
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env (สำหรับรันในเครื่อง / local dev)
load_dotenv()

# ── Required variables ──────────────────────────────────────────────────────
API_URL   = os.getenv("OPENWEBUI_API_URL")
API_KEY   = os.getenv("OPENWEBUI_API_KEY")

# ── Optional variable (มีค่า default ถ้าไม่ได้ตั้งไว้) ──────────────────────
MODEL_NAME = os.getenv("MODEL_NAME", "hu-mate")

# ── Startup validation ───────────────────────────────────────────────────────
# ตรวจสอบตัวแปรที่จำเป็นตั้งแต่เริ่มต้น เพื่อให้ error message ชัดเจน
# แทนที่จะ crash ด้วย AttributeError ภายหลัง
_missing = [name for name, val in [("OPENWEBUI_API_URL", API_URL),
                                    ("OPENWEBUI_API_KEY", API_KEY)]
            if not val]

if _missing:
    # ถ้ารันบน Streamlit Cloud จะใช้ st.secrets แทน — ไม่ต้อง raise ตรงนี้
    # แต่ถ้ารันแบบ standalone ให้แจ้งเตือนให้ชัดเจน
    _in_streamlit = "streamlit" in sys.modules
    if not _in_streamlit:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(_missing)}\n"
            "Please set them in your .env file or server environment."
        )
