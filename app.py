import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64

# הגדרות דף
st.set_page_config(page_title="Master AI", page_icon="🪄", layout="wide")

# CSS לעברית ותצוגה
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .main, p, div, h1, h2, h3, input {
        font-family: 'Assistant', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .stChatInputContainer { direction: RTL; }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה להצגת PDF בתצוגה מקדימה
def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    file.seek(0) # מחזיר את הסמן לתחילת הקובץ לקריאה עתידית

# פונקציה לקריאת תוכן קבצים
def process_file(file):
    name = file.name.lower()
    try:
        if name.endswith('.pdf'):
            pdf = PyPDF2.PdfReader(file)
            return " ".join([p.extract_text() for p in pdf.pages])
        elif name.endswith(('.xlsx', '.xls', '.csv')):
            df = pd.read_excel(file) if 'xls' in name else pd.read_csv(file)
            return f"נתוני קובץ:\n{df.to_string()}"
        else:
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"שגיאה בקריאת קובץ: {e}"

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Panel")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט וניתוח קבצים", "🎨 יצירת תמונה", "🎬 יצירת וידאו", "🎵 יצירת מוזיקה"])
    st.divider()
    uploaded_file = st.file_uploader("צרף קובץ", type=["pdf", "xlsx", "csv", "txt"])
    
    # הצגת תצוגה מקדימה בסידבר אם הועלה קובץ
    if uploaded_file and mode == "🔍 צ'אט וניתוח קבצים":
        st.subheader("תצוגה מקדימה לקובץ:")
        if uploaded_file.name.lower().endswith('.pdf'):
            display_pdf(uploaded_file)
        elif uploaded_file.name.lower().endswith(('.xlsx', '.csv')):
            df = pd.read_excel(uploaded_file) if 'xls' in uploaded_file.name else pd.read_csv(uploaded_file)
            st.dataframe(df.head(10)) # מציג את 10 השורות הראשונות של האקסל
    
    st.divider()
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# --- ניהול צ'אט ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "image_url" in m:
            st.image(m["image_url"])

# לוגיקה של שליחה
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה":
            with st.spinner("מצייר..."):
                encoded_prompt = requests.utils.quote(prompt)
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42"
                st.image(img_url)
                # הורדה תקינה
                img_data = requests.get(img_url).content
                st.download_button("📥 הורד תמונה", img_data, "image.png", "image/png")
                ans = "התמונה מוכנה!"
        
        elif mode == "🔍 צ'אט וניתוח קבצים":
            with st.spinner("מנתח..."):
                file_text = process_file(uploaded_file) if uploaded_file else ""
                api_key = st.secrets["OPENROUTER_API_KEY"]
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": f"Context: {file_text}\n\nQuestion: {prompt}"}]
                }
                res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                ans = res.json()['choices'][0]['message']['content']
                st.markdown(ans)
        else:
            ans = f"מצב {mode} בפיתוח."
            st.markdown(ans)
        
        st.session_state.messages.append({"role": "assistant", "content": ans})








