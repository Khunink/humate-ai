import requests
import json
import config 

def stream_ai_response(messages, placeholder):
    """ส่งข้อความไปหา Agent ใน Open WebUI และดึงคำตอบแบบ Streaming"""
    full_response = ""
    try:
        headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json"
        }
        
        # ส่งแค่ model และ messages ก็พอครับ เพราะ Open WebUI 
        # จะจัดการเรื่อง RAG/Knowledge ให้เองเมื่อเห็นชื่อรุ่น "hu-mate"
        payload = {
            "model": config.MODEL_NAME, 
            "messages": messages,
            "stream": True 
        }
        
        response = requests.post(config.API_URL, json=payload, headers=headers, stream=True, timeout=120)
        
        if response.status_code != 200:
            return f"❌ เชื่อมต่อ Open WebUI ไม่สำเร็จ (Status: {response.status_code}): {response.text}"
        
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