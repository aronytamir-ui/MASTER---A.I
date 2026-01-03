import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64
import io

# 1. הגדרות דף חובה בראש הקובץ
st.set_page_config(page_title="Master AI", layout="wide")

# 2. עיצוב RTL (ימין לשמאל) משופר
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div { direction: RTL; text-align: right; }
    .stChatInputContainer { direction: RTL; }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    img { border-radius: 15px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לעיבוד קבצים
def process_file(file):
    try:
        if file.name.lower().endswith('.pdf'):
            pdf = PyPDF2.PdfReader(file)
            return " ".join([p.extract_text() for p in pdf.pages])
        return "קובץ נטען"
    except: return ""

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Panel")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט וניתוח קבצים", "🎨 יצירת תמונה"])
    uploaded_file = st.file_uploader("העלה קובץ", type=["pdf", "xlsx", "txt"])
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# אתחול הודעות
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריה (כולל תמונות שנוצרו)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "img_data" in m:
            st.image(m["img_data"])

# לוגיקת צ'אט
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        final_text = ""
        img_bytes = None
        
        if mode == "🎨 יצירת תמונה":
            with st.spinner("מצייר עבורך..."):
                # יצירת URL לתמונה
                encoded_prompt = requests.utils.quote(prompt)
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42"
                try:
                    # הורדה ישירה של התמונה לזיכרון (פותר את בעיית התמונה השבורה)
                    img_res = requests.get(img_url, timeout=20)
                    if img_res.status_code == 200:
                        img_bytes = img_res.content
                        st.image(img_bytes)
                        st.download_button("📥 הורד תמונה", img_bytes, "ai_art.png", "image/png")
                        final_text = f"הנה התמונה שנוצרה עבור: {prompt}"
                    else:
                        final_text = "שגיאה: שרת התמונות לא זמין כרגע."
                except:
                    final_text = "שגיאה בחיבור לשרת התמונות."
        
        else:
            with st.spinner("חושב..."):
                try:
                    api_key = st.secrets.get("OPENROUTER_API_KEY")
                    context = process_file(uploaded_file) if uploaded_file else ""
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={
                            "model": "google/gemini-2.0-flash-exp:free",
                            "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}\nענה בעברית."}]
                        }
                    )
                    data = res.json()
                    # הגנה מפני KeyError - בודק אם השדות קיימים
                    if "choices" in data and len(data["choices"]) > 0:
                        final_text = data['choices'][0]['message']['content']
                    else:
                        final_text = f"שגיאה מה-AI: {data.get('error', {}).get('message', 'תגובה לא מזוהה')}"
                except Exception as e:
                    final_text = f"חלה שגיאה טכנית: {str(e)}"

        # הצגת הטקסט ושמירה להיסטוריה
        if final_text:
            st.markdown(final_text)
            new_msg = {"role": "assistant", "content": final_text}
            if img_bytes:
                new_msg["img_data"] = img_bytes
            st.session_state.messages.append(new_msg)







