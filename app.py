import streamlit as st
import requests

# הגדרות דף בסיסיות
st.set_page_config(page_title="Master AI", layout="wide")

# משיכת המפתח מה-Secrets
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except:
    st.error("המפתח (API Key) לא הוגדר ב-Secrets של Streamlit")
    st.stop()

# כותרת
st.title("🤖 Master AI - פעיל")

# יצירת היסטוריית צ'אט אם לא קיימת
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת הודעות קודמות
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# תיבת הצ'אט - חשוב שתהיה מחוץ לכל 'with'
if prompt := st.chat_input("איך אני יכול לעזור היום?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = "החיבור הצליח! אני כאן. בקרוב אוסיף את יכולות ה-PDF."
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

