import streamlit as st
import requests
import PyPDF2
import pandas as pd
import io

# הגדרות דף ויישור לימין
st.set_page_config(page_title="Master AI", layout="wide")

# CSS מתקדם לעברית מלאה ועיצוב כפתורים
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, p, div, h1, h2, h3, input {
        font-family: 'Assistant', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .stChatInputContainer { direction: RTL; }
    .stChatMessage { direction: RTL; border-radius: 15px; }
    /* תיקון מיקום כפתור שליחה */
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לקריאת כל סוגי הקבצים
def process_file(file):
    name = file.name.lower()
    try:
        if name.endswith('.pdf'):
            pdf = PyPDF2.PdfReader(file)
            return " ".join([p.extract_text() for p in pdf.pages])
        elif name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
            return f"תוכן טבלת אקסל:\n{df.to_string()}"
        elif name.endswith('.csv'):
            df = pd.read_csv(file)
            return f"תוכן קובץ CSV:\n{df.to_string()}"
        elif name.endswith(('.docx', '.doc')):
            return "קובץ Word זוהה. (לעיבוד מלא נדרש docx2txt ב-requirements)"
        else:
            return file.read().decode("utf-8")
    except Exception as e:
        return f"שגיאה בקריאת הקובץ: {e}"

# שליחה ל-OpenRouter
def ask_ai(prompt, system_msg=""):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# --- תפריט צד ---
with st.sidebar:
    st.title("🤖 Master AI")
    mode = st.radio("בחר מצב עבודה:", ["🔍 ניתוח קבצים וצ'אט", "🎨 יצירת תמונה", "🎬 יצירת וידאו", "🎵 יצירת מוזיקה"])
    st.divider()
    uploaded_file = st.file_uploader("העלה קובץ (PDF, Excel, Word, Text)", type=["pdf", "docx", "csv", "xlsx", "txt"])
    st.divider()
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# --- צ'אט ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("כתוב כאן..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        file_context = process_file(uploaded_file) if uploaded_file else ""
        
        # התאמת המערכת לפי המצב הנבחר
        if mode == "🎨 יצירת תמונה":
            st.info("מייצר תמונה עבורך...")
            # כאן בגרסה הבאה נחבר API של יצירת תמונות. כרגע ה-AI יחזיר תיאור טכני.
            ans = ask_ai(f"צור תיאור מפורט עבור DALL-E לתמונה: {prompt}")
        elif mode == "🔍 ניתוח קבצים וצ'אט":
            ans = ask_ai(f"הקשר מהקובץ: {file_context}\n\nשאלה: {prompt}")
        else:
            ans = f"מצב {mode} נמצא כרגע בפיתוח ויתחבר למודלים ייעודיים בקרוב."
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})

# כפתור הורדה
if st.session_state.messages:
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    st.download_button("💾 שמור שיחה", history, file_name="master_ai_chat.txt")








