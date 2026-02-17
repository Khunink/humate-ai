import requests
import json
import config # ดึงค่าจากไฟล์ config.py มาใช้

def stream_ai_response(messages, placeholder):
    """ฟังก์ชันสำหรับส่งข้อความไปหา AI และดึงคำตอบแบบ Streaming (พิมพ์ทีละตัว)"""
    full_response = ""
    try:
        headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json"
        }
        # Payload คือข้อมูลที่เราจะส่งไปหา API
        payload = {
            "model": config.MODEL_NAME,
            "messages": messages, # ส่งประวัติการแชททั้งหมดเพื่อให้บอทตอบได้ต่อเนื่อง (Requirement 4)
            "stream": True       # เปิดโหมดส่งข้อมูลแบบต่อเนื่อง
        }
        
        # ส่ง Request แบบ stream=True
        response = requests.post(config.API_URL, json=payload, headers=headers, stream=True, timeout=120)
        
        # วนลูปอ่านข้อมูลที่ AI ค่อยๆ ส่งกลับมา
        for line in response.iter_lines():
            if line:
                txt = line.decode('utf-8')
                if txt.startswith('data: '):
                    js_str = txt[6:] # ตัดคำว่า 'data: ' ออกเพื่อให้เหลือแค่ JSON
                    if js_str.strip() == "[DONE]": break # ถ้า AI ตอบจบแล้วให้หยุด
                    try:
                        # ดึงเนื้อหาคำพูด (content) ออกมาแสดงผล
                        content = json.loads(js_str)['choices'][0].get('delta', {}).get('content', '')
                        full_response += content
                        placeholder.markdown(full_response + "▌") # แสดง Cursor กระพริบขณะพิมพ์
                    except: continue
        return full_response
    except Exception as e:
        return f"Error: {str(e)}"