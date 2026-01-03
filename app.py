import streamlit as st
import requests
import PyPDF2

st.set_page_config(page_title="Master AI", layout="wide")

# משיכת מפתח
api_key = st.secrets.get("OPENROUTER_API_KEY")

def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    except Exception as e:
        return f"שגיאה בקריאת הקובץ: {e}"

st.title("🤖 Master AI")

with st.sidebar:
    st.header("הגדרות")
    uploaded_file = st.file_uploader("העלה קובץ PDF לניתוח", type="pdf")
    if st.button("נקה היסטוריה"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("שאל אותי על הקובץ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # כאן אנחנו שואבים את הטקסט מהקובץ אם הוא קיים
        file_text = ""
        if uploaded_file:
            with st.spinner("קורא נתונים מהקובץ..."):
                file_text = read_pdf(uploaded_file)
        
        # בניית ההנחיה ל-AI: תוכן הקובץ + השאלה
        full_prompt = f"תוכן הקובץ המצורף: {file_text}\n\nשאלה: {prompt}" if file_text else prompt

        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [{"role": "user", "content": full_prompt}]
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            ans = response.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error("שגיאה בקבלת תשובה מהשרת.")






