import streamlit as st
import requests
import PyPDF2

# הגדרות דף - חייב להיות בשורה הראשונה
st.set_page_config(page_title="Master AI", layout="wide")

# בדיקת מפתח ב-Secrets
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("שגיאה: המפתח לא נמצא ב-Secrets של Streamlit")
    st.stop()

api_key = st.secrets["OPENROUTER_API_KEY"]

# פונקציה פשוטה לקריאת PDF
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

# ממשק משתמש
st.title("🤖 Master AI")

with st.sidebar:
    st.header("הגדרות")
    uploaded_file = st.file_uploader("העלה קובץ PDF", type="pdf")

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריה
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# כניסת משתמש
if prompt := st.chat_input("שאל אותי משהו..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # שליחה ל-AI
    with st.chat_message("assistant"):
        with st.spinner("מעבד נתונים..."):
            # אם יש קובץ, נשאב ממנו את הטקסט
            file_context = ""
            if uploaded_file:
                file_context = f"תוכן הקובץ המצורף: {read_pdf(uploaded_file)}\n\n"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # בניית הפרומפט המלא
            full_prompt = f"{file_context}שאלה: {prompt}"
            
            data = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [{"role": "user", "content": full_prompt}]
            }
            
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                response.raise_for_status()
                result = response.json()['choices'][0]['message']['content']
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"קרתה שגיאה: {str(e)}")





