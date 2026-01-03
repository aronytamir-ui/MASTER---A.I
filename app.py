import streamlit as st
import requests
import PyPDF2
import pandas as pd
from io import BytesIO

# 1. הגדרות דף ויישור לימין (RTL)
st.set_page_config(page_title="Master AI", layout="wide")

# הזרקת CSS לעברית ותיקון ממשק
st.markdown("""
    <style>
    .main, .stChatMessage, .stTextInput, p, h1, h2, h3 {
        direction: RTL;
        text-align: right;
    }
    div[data-testid="stSidebarNav"] {direction: RTL;}
    .stChatInputContainer {direction: RTL;}
    </style>
    """, unsafe_allow_html=True)

# פונקציות קריאת קבצים
def extract_text(file):
    filename = file.name.lower()
    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in pdf_reader.pages])
    elif filename.endswith('.docx'):
        # דורש python-docx, בינתיים נחזיר הודעה או נקרא כטקסט
        return "קובץ Word זוהה (נדרשת ספרייה נוספת לעיבוד מלא)"
    elif filename.endswith('.csv') or filename.endswith(('.xls', '.xlsx')):
        df = pd.read_csv(file) if filename.endswith('.csv') else pd.read_excel(file)
        return df.to_string()
    else:
        return file.read().decode("utf-8", errors="ignore")

# בדיקת מפתח
api_key = st.secrets.get("OPENROUTER_API_KEY")

# --- תפריט צד ---
with st.sidebar:
    st.title("🛠️ תפריט Master AI")
    
    # 2. העלאת קבצים מגוונים
    uploaded_file = st.file_uploader("העלה קובץ (PDF, Excel, Word, Text)", type=["pdf", "docx", "csv", "xlsx", "txt"])
    
    st.divider()
    
    # 3. תפריט מהיר ליצירה
    st.subheader("🎨 יצירת תוכן מהירה")
    mode = st.radio("בחר פעולה:", ["צ'אט רגיל", "צור תמונה", "צור וידאו", "צור מוזיקה"])
    
    if mode != "צ'אט רגיל":
        st.info(f"מצב {mode} פעיל. תאר בצאט מה תרצה ליצור.")

    st.divider()
    if st.button("נקה היסטוריה"):
        st.session_state.messages = []
        st.rerun()

# --- גוף האפליקציה ---
st.title("🤖 Master AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# כפתור הורדה (4) - מופיע אם יש היסטוריה
if st.session_state.messages:
    chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    st.download_button("📥 הורד את השיחה למחשב", chat_text, file_name="chat_history.txt")

# לוגיקה של שליחה
if prompt := st.chat_input("איך אני יכול לעזור היום?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # הכנת הקשר מהקובץ
    context = ""
    if uploaded_file:
        context = f"תוכן הקובץ: {extract_text(uploaded_file)}\n\n"

    with st.chat_message("assistant"):
        with st.spinner("מעבד..."):
            try:
                # התאמת הפרומפט לפי המצב (תמונה/וידאו/טקסט)
                final_prompt = f"מצב עבודה: {mode}. {context} שאלה: {prompt}"
                
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": final_prompt}]
                }
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                ans = response.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except:
                st.error("שגיאה בחיבור.")







