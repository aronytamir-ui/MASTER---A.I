import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64
import io

# הגדרות דף - חובה בראש הקובץ
st.set_page_config(page_title="Master AI", layout="wide")

# עיצוב RTL ועברית
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div { direction: RTL; text-align: right; }
    .stChatInputContainer { direction: RTL; }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    img { border-radius: 12px; border: 1px solid #333; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# פונקציות עיבוד קבצים
def get_pdf_text(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() for p in pdf.pages])
    except: return ""

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Panel")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט וניתוח קבצים", "🎨 יצירת תמונה"])
    uploaded_file = st.file_uploader("העלה קובץ (PDF/Excel)", type=["pdf", "xlsx", "txt"])
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# אתחול היסטוריה
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריית צ'אט
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "img_data" in m:
            st.image(m["img_data"])

# תיבת קלט
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        final_ans = ""
        img_to_save = None

        if mode == "🎨 יצירת תמונה":
            with st.spinner("מצייר עבורך..."):
                # יצירת כתובת תמונה נקייה
                clean_prompt = requests.utils.quote(prompt)
                img_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed=99"
                try:
                    # הורדת התמונה לשרת כדי לעקוף חסימות תצוגה
                    response = requests.get(img_url, timeout=20)
                    if response.status_code == 200:
                        img_to_save = response.content
                        st.image(img_to_save)
                        st.download_button("📥 הורד תמונה למחשב", img_to_save, "master_ai_art.png", "image/png")
                        final_ans = f"הנה התמונה שביקשת: {prompt}"
                    else:
                        final_ans = "שגיאה: שרת התמונות לא הגיב בזמן."
                except:
                    final_ans = "שגיאה בחיבור לשרת התמונות."
        
        else:
            with st.spinner("מנתח נתונים..."):
                api_key = st.secrets.get("OPENROUTER_API_KEY")
                context = get_pdf_text(uploaded_file) if uploaded_file else ""
                
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "google/gemini-2.0-flash-exp:free",
                        "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}\nענה בעברית."}]
                    }
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                    data = res.json()
                    
                    if "choices" in data:
                        final_ans = data['choices'][0]['message']['content']
                    else:
                        final_ans = f"שגיאה מה-API: {data.get('error', {}).get('message', 'לא ידוע')}"
                except Exception as e:
                    final_ans = f"שגיאה טכנית: {str(e)}"
        
        # הצגת התשובה ושמירה להיסטוריה
        if final_ans:
            st.markdown(final_ans)
            history_entry = {"role": "assistant", "content": final_ans}
            if img_to_save:
                history_entry["img_data"] = img_to_save
            st.session_state.messages.append(history_entry)







