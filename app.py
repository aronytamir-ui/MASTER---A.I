import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64

# הגדרות דף
st.set_page_config(page_title="Master AI", layout="wide")

# עיצוב RTL ועברית
st.markdown("""
    <style>
    direction: RTL; text-align: right;
    .stChatInputContainer { direction: RTL; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לעיבוד קבצים
def process_file(file):
    if file.name.lower().endswith('.pdf'):
        pdf = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() for p in pdf.pages])
    return "קובץ נטען"

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט", "🎨 יצירת תמונה"])
    uploaded_file = st.file_uploader("העלה קובץ", type=["pdf", "xlsx", "txt"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריה
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "img" in m: st.image(m["img"])

# לוגיקה של שליחה
if prompt := st.chat_input("כתוב כאן..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה":
            with st.spinner("מצייר..."):
                # יצירת כתובת תמונה ישירה על בסיס הטקסט שלך
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1024&height=1024&seed=42"
                st.image(img_url, caption="התמונה נוצרה על ידי AI")
                
                # כפתור הורדה
                img_data = requests.get(img_url).content
                st.download_button("📥 הורד תמונה", img_data, "ai_image.png", "image/png")
                
                st.session_state.messages.append({"role": "assistant", "content": "הנה התמונה:", "img": img_url})
        
        else:
            # צ'אט רגיל דרך OpenRouter
            api_key = st.secrets["OPENROUTER_API_KEY"]
            context = process_file(uploaded_file) if uploaded_file else ""
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": f"{context}\n\n{prompt}"}]
                }
            )
            ans = res.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})








