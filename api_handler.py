import requests
import json
import config 

def stream_ai_response(messages, placeholder):
    """ส่งข้อความไปหา Agent ใน Open WebUI และดึงคำตอบแบบ Streaming"""
    full_response = ""
    try:
        # 1. ตั้งค่า Header เพื่อยืนยันตัวตนกับ Open WebUI
        headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 2. เตรียมข้อมูล (Payload)
        # ไม่ต้องใส่ System Prompt เองที่นี่ เพราะ Agent ใน Open WebUI จัดการให้แล้ว
        payload = {
            "model": config.MODEL_NAME, # จะวิ่งไปเรียก Agent ที่มี RAG ทันที
            "messages": messages,
            "stream": True 
        }
        
        # 3. ยิง Request ไปที่ Open WebUI API
        response = requests.post(config.API_URL, json=payload, headers=headers, stream=True, timeout=120)
        
        # ตรวจสอบว่าเชื่อมต่อสำเร็จหรือไม่
        if response.status_code != 200:
            return f"❌ เชื่อมต่อ Open WebUI ไม่สำเร็จ (Status: {response.status_code}): {response.text}"
        
        # 4. วนลูปอ่านข้อมูล Streaming ที่ส่งกลับมา
        for line in response.iter_lines():
            if line:
                txt = line.decode('utf-8')
                if txt.startswith('data: '):
                    js_str = txt[6:] 
                    if js_str.strip() == "[DONE]": break 
                    try:
                        content = json.loads(js_str)['choices'][0].get('delta', {}).get('content', '')
                        full_response += content
                        placeholder.markdown(full_response + "▌") 
                    except: continue
        
        placeholder.markdown(full_response)
        return full_response
        
    except requests.exceptions.ConnectionError:
        return "❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ Open WebUI ได้ โปรดตรวจสอบ API_URL"
    except Exception as e:
        return f"❌ Error: {str(e)}"