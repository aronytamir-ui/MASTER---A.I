import streamlit as st
import requests
import PyPDF2
import pandas as pd
import base64

# הגדרות דף ועיצוב RTL
st.set_page_config(page_title="Master AI", page_icon="🪄", layout="wide")

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
    .stImage > img { border-radius: 15px; border: 2px solid #4A90E2; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה להצגת PDF
def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    file.seek(0)

# פונקציה לעיבוד קבצים
def process_file(file):
    name = file.name.lower()
    try:
        if name.endswith('.pdf'):
            pdf = PyPDF2.PdfReader(file)
            return " ".join([p.extract_text() for p in pdf.pages])
        elif name.endswith(('.xlsx', '.csv')):
            df = pd.read_excel(file) if 'xls' in name else pd.read_csv(file)
            return f"תוכן טבלה:\n{df.to_string()}"
        return file.read().decode("utf-8", errors="ignore")
    except: return ""

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט וניתוח קבצים", "🎨 צור תמונה"])
    uploaded_file = st.file_uploader("העלה קובץ", type=["pdf", "xlsx", "csv", "txt"])
    
    if uploaded_file and mode == "🔍 צ'אט וניתוח קבצים":
        if uploaded_file.name.lower().endswith('.pdf'): display_pdf(uploaded_file)
    
    if st.button("🗑️ נקה היסטוריה"):
        st.session_state.messages = []
        st.rerun()

# --- ניהול הודעות ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "img" in m: st.image(m["img"])

# --- לוגיקת צ'אט ---
if prompt := st.chat_input("כתוב כאן..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 צור תמונה":
            with st.spinner("מצייר..."):
                # יצירת קישור תמונה ישיר
                encoded_prompt = requests.utils.quote(prompt)
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024"
                
                # הצגה במסך
                st.image(img_url, caption=f"תוצאה עבור: {prompt}")
                
                # הוספת כפתור הורדה
                img_data = requests.get(img_url).content
                st.download_button("📥 הורד תמונה", img_data, "ai_image.png", "image/png")
                
                msg = {"role": "assistant", "content": "הנה התמונה שיצרתי עבורך:", "img": img_url}
        
        else:
            with st.spinner("חושב..."):
                context = process_file(uploaded_file) if uploaded_file else ""
                api_key = st.secrets["OPENROUTER_API_KEY"]
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}]
                }
                res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                ans = res.json()['choices'][0]['message']['content']
                st.markdown(ans)
                msg = {"role": "assistant", "content": ans}
        
        st.session_state.messages.append(msg)








