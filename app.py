import streamlit as st
import requests
import PyPDF2
import pandas as pd
import io

# הגדרות דף
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
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    .stImage > img { border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לקריאת קבצים
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

# פונקציה לקריאה ל-AI (OpenRouter)
def call_openrouter(prompt):
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"שגיאה בחיבור לשרת. וודא שהמפתח ב-Secrets תקין."

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Panel")
    mode = st.radio("בחר פעולה:", [
        "🔍 צ'אט וניתוח קבצים", 
        "🎨 יצירת תמונה", 
        "🎬 יצירת וידאו (בקרוב)", 
        "🎵 יצירת מוזיקה (בקרוב)"
    ])
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
        if "image_url" in m:
            st.image(m["image_url"])

# לוגיקה של שליחה
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        ans = ""
        image_url = None
        
        if mode == "🎨 יצירת תמונה":
            with st.spinner("מצייר עבורך..."):
                encoded_prompt = requests.utils.quote(prompt)
                image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42"
                ans = f"הנה התמונה שיצרתי עבור: '{prompt}'"
                st.markdown(ans)
                st.image(image_url)
                
                # כפתור הורדה ישירה לתמונה
                img_data = requests.get(image_url).content
                st.download_button(label="📥 הורד תמונה למחשב", data=img_data, file_name="generated_image.png", mime="image/png")
        
        elif mode == "🔍 צ'אט וניתוח קבצים":
            with st.spinner("מנתח..."):
                file_data = process_file(uploaded_file) if uploaded_file else ""
                full_prompt = f"Context: {file_data}\n\nUser Question: {prompt}\nענה בעברית."
                ans = call_openrouter(full_prompt)
                st.markdown(ans)
        else:
            ans = f"מצב {mode} יהיה זמין בקרוב עם חיבור למודלי וידאו ומוזיקה מתקדמים."
            st.markdown(ans)
        
        # שמירת ההודעה
        new_msg = {"role": "assistant", "content": ans}
        if image_url:
            new_msg["image_url"] = image_url
        st.session_state.messages.append(new_msg)

# כפתור הורדה להיסטוריית הצ'אט
if st.session_state.messages:
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    st.sidebar.download_button("💾 שמור היסטוריית צ'אט", history, file_name="chat_log.txt")








