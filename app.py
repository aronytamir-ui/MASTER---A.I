import streamlit as st
import requests
import PyPDF2

# 1. הגדרות דף - חייב להופיע רק פעם אחת בראש הקוד!
st.set_page_config(page_title="Master AI", page_icon="🤖", layout="wide")

# 2. עיצוב CSS מותאם אישית
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 3. בדיקת מפתח ה-API מה-Secrets
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("חובה להוסיף את המפתח ב-Secrets תחת השם: OPENROUTER_API_KEY")
    st.stop()

api_key = st.secrets["OPENROUTER_API_KEY"]

# 4. תפריט צד (Sidebar)
with st.sidebar:
    st.title("🛠️ הגדרות")
    uploaded_file = st.file_uploader("העלה קובץ PDF לניתוח", type="pdf")
    if st.button("נקה היסטוריית צ'אט"):
        st.session_state.messages = []
        st.rerun()

# 5. ניהול הודעות הצ'אט
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Master AI")
st.caption("העוזר האישי החכם שלך לסיכום קבצים ומענה על שאלות")

# הצגת הודעות מההיסטוריה
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. לוגיקה של הצ'אט
if prompt := st.chat_input("איך אני יכול לעזור היום?"):
    # הוספת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # פנייה ל-OpenRouter (ה-AI)
    with st.chat_message("assistant"):
        with st.spinner("חושב..."):
            try:
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": st.session_state.messages
                }
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                full_response = response.json()['choices'][0]['message']['content']
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"שגיאה בהתחברות לבינה המלאכותית. וודא שהמפתח תקין.")



