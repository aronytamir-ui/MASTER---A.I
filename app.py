import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64

# הגדרות דף - חובה בשורה הראשונה
st.set_page_config(page_title="Master AI", layout="wide")

# עיצוב ממשק RTL (ימין לשמאל)
st.markdown("""
    <style>
    .main, .stChatMessage, .stChatInputContainer, p, h1, h2, div {
        direction: RTL;
        text-align: right;
    }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    </style>
    """, unsafe_allow_html=True)

# פונקציות עזר
def get_pdf_text(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([p.extract_text() for p in pdf.pages])

# --- תפריט צד ---
with st.sidebar:
    st.title("🛠️ תפריט Master AI")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט וניתוח", "🎨 צור תמונה"])
    uploaded_file = st.file_uploader("העלה קובץ", type=["pdf", "xlsx", "txt"])
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# אתחול הודעות
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת הצ'אט
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "img_url" in m:
            st.image(m["img_url"])

# כתיבת הודעה חדשה
if prompt := st.chat_input("איך אפשר לעזור?"):
    # הוספת הודעת משתמש
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # תגובת המערכת
    with st.chat_message("assistant"):
        if mode == "🎨 צור תמונה":
            with st.spinner("מצייר..."):
                # יצירת תמונה ישירות דרך קישור (עוקף בעיות API)
                clean_prompt = requests.utils.quote(prompt)
                image_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed=123"
                
                # הצגה מיידית
                st.image(image_url, caption=f"התוצאה עבור: {prompt}")
                
                # הורדה
                img_data = requests.get(image_url).content
                st.download_button("📥 הורד תמונה", img_data, "image.png", "image/png")
                
                # שמירה להיסטוריה
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "הנה התמונה שיצרתי:", 
                    "img_url": image_url
                })
        
        else:
            with st.spinner("חושב..."):
                # צ'אט טקסטואלי רגיל
                api_key = st.secrets.get("OPENROUTER_API_KEY")
                context = get_pdf_text(uploaded_file) if uploaded_file else ""
                
                try:
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
                except:
                    st.error("שגיאה בחיבור ל-AI. וודא שהמפתח ב-Secrets תקין.")
                    







