import streamlit as st
import requests
import PyPDF2
import pandas as pd
import io

# הגדרות דף ויישור לימין
st.set_page_config(page_title="Master AI", page_icon="🪄", layout="wide")

# CSS לעברית ותיקון ממשק
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, p, div, h1, h2, h3, input {
        font-family: 'Assistant', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .stChatInputContainer { direction: RTL; }
    /* תיקון מיקום כפתור שליחה במובייל */
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לקריאת קבצים (PDF, Excel, Word)
def process_file(file):
    name = file.name.lower()
    try:
        if name.endswith('.pdf'):
            pdf = PyPDF2.PdfReader(file)
            return " ".join([p.extract_text() for p in pdf.pages])
        elif name.endswith(('.xlsx', '.xls', '.csv')):
            df = pd.read_excel(file) if 'xls' in name else pd.read_csv(file)
            return f"נתוני קובץ:\n{df.to_string()}"
        else:
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"שגיאה בקריאת קובץ: {e}"

# פונקציה מרכזית לפנייה ל-AI
def call_openrouter(prompt, model="google/gemini-2.0-flash-exp:free"):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    except:
        return "שגיאה בתקשורת עם השרת."

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Panel")
    mode = st.radio("בחר פעולה:", ["💬 צ'אט וניתוח קבצים", "🎨 יצירת תמונה אמנותית", "🎬 יצירת וידאו (בקרוב)", "🎵 יצירת מוזיקה (בקרוב)"])
    st.divider()
    uploaded_file = st.file_uploader("צרף קובץ לעבודה", type=["pdf", "docx", "xlsx", "csv", "txt"])
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# --- ניהול צ'אט ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# לוגיקה של שליחה
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה אמנותית":
            with st.spinner("מצייר עבורך..."):
                # אנחנו משתמשים במודל Flux ליצירת תמונות
                image_url_prompt = f"Generate an image based on: {prompt}. high quality, 4k, realistic."
                # הערה: ב-OpenRouter יצירת תמונה מחזירה לעיתים URL או תיאור. 
                # כאן נשתמש בטכניקה שמציגה תמונה דרך Markdown אם המודל תומך בזה.
                response = call_openrouter(prompt, model="black-forest-labs/flux-1-schnell")
                st.markdown(response)
        
        else: # מצב צ'אט וניתוח קבצים
            file_data = process_file(uploaded_file) if uploaded_file else ""
            full_prompt = f"Context: {file_data}\n\nUser Question: {prompt}"
            ans = call_openrouter(full_prompt)
            st.markdown(ans)
        
        st.session_state.messages.append({"role": "assistant", "content": ans})

# כפתור הורדה
if st.session_state.messages:
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    st.sidebar.download_button("💾 שמור היסטוריה למחשב", history, file_name="chat_master_ai.txt")









