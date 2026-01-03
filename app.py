import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64

# הגדרות דף
st.set_page_config(page_title="Master AI", layout="wide")

# עיצוב RTL ותיקון תצוגה
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div { direction: RTL; text-align: right; }
    .stChatInputContainer { direction: RTL; }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    /* עיצוב התמונה כדי שתיראה טוב */
    img { border-radius: 10px; max-width: 100%; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לקריאת PDF
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

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריה
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "img_data" in m:
            st.image(m["img_data"])

# קלט מהמשתמש
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה":
            with st.spinner("מייצר תמונה..."):
                # יצירת התמונה דרך Pollinations
                img_url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1024&height=1024&seed=42&nologo=true"
                try:
                    # אנחנו מורידים את הנתונים ומציגים אותם כ-Bytes כדי לעקוף חסימות תצוגה
                    img_res = requests.get(img_url, timeout=15)
                    if img_res.status_code == 200:
                        st.image(img_res.content)
                        st.download_button("📥 הורד תמונה", img_res.content, "ai_image.png", "image/png")
                        st.session_state.messages.append({"role": "assistant", "content": "הנה התמונה שיצרתי:", "img_data": img_res.content})
                    else:
                        st.error("שרת התמונות עמוס, נסה שוב בעוד רגע.")
                except:
                    st.error("שגיאה בתקשורת עם שרת התמונות.")
        
        else:
            with st.spinner("חושב..."):
                api_key = st.secrets.get("OPENROUTER_API_KEY")
                context = get_pdf_text(uploaded_file) if uploaded_file else ""
                
                try:
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={
                            "model": "google/gemini-2.0-flash-exp:free",
                            "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}\nענה בעברית."}]
                        }
                    )
                    data = res.json()
                    # הגנה מפני KeyError: בודק אם התשובה תקינה
                    if "choices" in data:
                        ans = data['choices'][0]['message']['content']
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    else:
                        st.error(f"שגיאה מה-API: {data.get('error', {}).get('message', 'לא ידוע')}")
                except Exception as e:
                    st.error(f"חלה שגיאה: {str(e)}")








