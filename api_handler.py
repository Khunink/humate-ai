import json
import requests
import config  # ดึงค่าจากไฟล์ config.py


def stream_ai_response(messages: list, placeholder) -> str:
    """
    ส่งข้อความไปหา AI และดึงคำตอบแบบ Streaming (พิมพ์ทีละตัว)

    Args:
        messages:    ประวัติการแชททั้งหมด (list of {"role": ..., "content": ...})
        placeholder: Streamlit placeholder สำหรับแสดงผลแบบ real-time

    Returns:
        full_response (str) — คำตอบทั้งหมดที่ได้รับ
        หรือ error string ที่ขึ้นต้นด้วย "Error:" ถ้าเกิดปัญหา
    """
    full_response = ""

    try:
        headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json",
        }

        # Payload คือข้อมูลที่ส่งไปหา API
        payload = {
            "model": config.MODEL_NAME,
            "messages": messages,  # ส่งประวัติทั้งหมดเพื่อให้บอทตอบต่อเนื่อง
            "stream": True,
        }

        # ส่ง Request แบบ stream=True
        response = requests.post(
            config.API_URL,
            json=payload,
            headers=headers,
            stream=True,
            timeout=120,
        )
        # FIX: raise ทันทีถ้า API คืน HTTP error (4xx / 5xx)
        # ก่อนหน้านี้ข้าม raise_for_status ทำให้ error ถูกกลืนไว้เงียบๆ
        response.raise_for_status()

        # วนลูปอ่านข้อมูลที่ AI ค่อยๆ ส่งกลับมา
        for line in response.iter_lines():
            if not line:
                continue

            txt = line.decode("utf-8")
            if not txt.startswith("data: "):
                continue

            js_str = txt[6:]  # ตัดคำว่า 'data: ' ออก
            if js_str.strip() == "[DONE]":
                break  # AI ตอบจบแล้ว

            # FIX: ระบุ exception ที่จับให้ชัดเจน แทน bare `except: continue`
            # ก่อนหน้านี้ใช้ `except: continue` ซึ่งกลืน error ทุกประเภทรวมถึง
            # KeyboardInterrupt และ SystemExit
            try:
                data = json.loads(js_str)
                content = (
                    data["choices"][0]
                    .get("delta", {})
                    .get("content", "")
                )
                full_response += content
                placeholder.markdown(full_response + "▌")  # Cursor กระพริบ
            except (json.JSONDecodeError, KeyError, IndexError):
                # ข้าม chunk ที่ parse ไม่ได้ — เป็นพฤติกรรมปกติของ SSE
                continue

    except requests.exceptions.Timeout:
        return "Error: Request timed out — AI ใช้เวลานานเกินไป กรุณาลองใหม่"
    except requests.exceptions.HTTPError as http_err:
        return f"Error: API ตอบกลับด้วย HTTP {http_err.response.status_code}: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Error: ไม่สามารถเชื่อมต่อ API ได้ — {req_err}"

    return full_response
