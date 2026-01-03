import streamlit as st
import requests
import PyPDF2

# הגדרות דף
st.set_page_config(page_title="Master AI", page_icon="🤖", layout="wide")

# עיצוב CSS - תיקון unsafe_allow_html
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# בדיקת מפתח API
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("חסר מפתח API ב-Secrets")
    st.stop()

api_key = st.secrets["OPENROUTER_API_KEY"]

# פונקציה לקריאת טקסט מ-PDF
def get_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# תפריט צד
with st.sidebar:
    st.title("🛠️ הגדרות")
    uploaded_file = st.file_uploader("לניתוח PDF העלה קובץ", type="pdf")
    if st.button("נקה היסטוריית צ'אט"):
        st.session_state.messages = []
        st.rerun()

# ניהול היסטוריית הודעות
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Master AI")
st.caption("העוזר האישי החכם שלך לסיכום קבצים ומענה על שאלות")

# הצגת הודעות קודמות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# לוגיקה של שליחת הודעה
if prompt := st.chat_input("איך אני יכול לעזור היום?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # הכנת ההקשר (Context) מה-PDF
    pdf_content = ""
    if uploaded_file:
        pdf_content = f"\n\nמידע מהקובץ שהועלה:\n{get_pdf_text(uploaded_file)}\n\n"

    with st.chat_message("assistant"):
        with st.spinner("מנתח נתונים..."):
            try:
                headers = {"Authorization": f"Bearer {api_key}"}
                # כאן הקסם: אנחנו מחברים את תוכן ה-PDF לשאלה של המשתמש
                full_query = f"{pdf_content} המשתמש שואל: {prompt}"
                
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": full_query}]
                }
                
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                ans = response.json()['choices'][0]['message']['content']
                
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error("שגיאה בחיבור לבינה המלאכותית. בדוק את ה-API Key.")




