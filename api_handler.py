import requests
import json
import config # ดึงค่าจากไฟล์ config.py มาใช้

# ==========================================
# 🛠️ ฟังก์ชันสำหรับค้นหาข้อมูล (คุณต้องไปเขียนเพิ่มตรงนี้)
# ==========================================
def search_knowledge_base(user_query):
    """
    ฟังก์ชันนี้มีหน้าที่ค้นหาข้อมูลที่เกี่ยวข้องจากคลังความรู้ (PDF, Word, ฯลฯ)
    *** สำคัญ: ตอนนี้เป็นเพียงข้อมูลจำลอง คุณต้องเขียนระบบเชื่อมต่อกับ Vector DB 
    (เช่น ChromaDB, FAISS, LangChain หรือ API ภายนอก) เพื่อดึงข้อมูลจริงๆ มาใส่ตรงนี้ ***
    """
    
    # TODO: ใส่โค้ดค้นหาข้อมูลของคุณที่นี่
    # context = my_vector_db.similarity_search(user_query)
    
    # ตอนนี้เป็นแค่ตัวอย่างจำลอง
    mock_context = "ข้อมูลจากคลังความรู้: ระเบียบการลาพักการศึกษา คณะมนุษยศาสตร์ ให้นักศึกษาติดต่อที่ห้องบริการการศึกษา HB7 พร้อมใบคำร้อง..." 
    
    return mock_context

# ==========================================
# 🚀 ฟังก์ชันหลักสำหรับส่งข้อมูลหา AI
# ==========================================
def stream_ai_response(messages, placeholder):
    """ฟังก์ชันสำหรับส่งข้อความไปหา AI และดึงคำตอบแบบ Streaming (พิมพ์ทีละตัว)"""
    full_response = ""
    try:
        headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 1. ดึงคำถามล่าสุดของผู้ใช้ เพื่อเอาไปค้นหาในคลังข้อมูล
        user_query = messages[-1]["content"] if messages else ""
        
        # 2. ทำการค้นหาข้อมูลจากคลังความรู้ (เรียกฟังก์ชันด้านบน)
        context_data = search_knowledge_base(user_query)
        
        # 3. รวบรวม System Prompt และ Context ที่ค้นหาได้
        system_message_content = f"""You are "Humate AI", an intelligent assistant for the Faculty of Humanities, Chiang Mai University (CMU). You have over 10 years of experience in educational services. Your primary responsibility is to provide information regarding the rules, regulations, procedures, and guidelines of the Faculty to students, parents, professors, and staff.

Your Persona:
Friendly, approachable, highly helpful, and you answer questions with utmost professionalism and reliability.

Strict Constraints (Rules of Operation):
1. Language Matching: Automatically detect the language of the user's input. You must respond in the exact same language used by the user.
2. Mandatory Retrieval & Strict Knowledge Base Reliance (RAG Only): You must answer questions based strictly on the provided Context/Knowledge Base below. You are strictly prohibited from searching the internet, using external websites, or referencing any outside sources. Do not invent information, do not guess, and absolutely do not use your own pre-trained knowledge outside of the provided context.
3. Fallback Behavior (Out of Context): If the answer to the user's question is not found in the knowledge base, or if the information is insufficient, do not attempt to guess or search the web. You must reply strictly with the following message (accurately translated into the language the user is using):
"I apologize, Humate AI does not currently have this information. For further details, please contact the Educational Services Section, Faculty of Humanities, 1st Floor, HB7 Building, or call 053-943274."
4. Absolute Accuracy for Regulations: If the context references any university or faculty laws, rules, regulations, or official announcements, you must cite the full and 100% correct title of that regulation exactly as it appears in the text. Do not abbreviate, modify, paraphrase, or summarize the names of any regulations under any circumstances.

Output Format:
- Summarize the content so that it is concise and easy to understand, while ensuring all relevant and essential details remain complete.
- Always use Bullet Points (- or 1. 2. 3.) when explaining procedures or detailing information with multiple aspects to ensure it is highly readable and scannable.
- Format the response to be visually appealing and easy to read. Use **bold text** to emphasize key terms, important notes, or headings.

--- Knowledge Base (Context) ---
{context_data}
--------------------------------
"""

        # 4. ประกอบร่าง Array ข้อมูล (เอา System Prompt ไว้เป็นกล่องแรกสุด แล้วตามด้วยประวัติการแชท)
        api_messages = [{"role": "system", "content": system_message_content}]
        api_messages.extend(messages)
        
        # 5. Payload คือข้อมูลที่เราจะส่งไปหา API (ใช้ api_messages ที่ประกอบใหม่)
        payload = {
            "model": config.MODEL_NAME,
            "messages": api_messages, 
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
        
        # เมื่อพิมพ์จบ ให้แสดงข้อความปกติแบบไม่มี Cursor
        placeholder.markdown(full_response)
        return full_response
        
    except Exception as e:
        return f"Error: {str(e)}"