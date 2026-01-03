import streamlit as st
import requests
import PyPDF2
import base64

# הגדרות דף
st.set_page_config(page_title="Master AI", layout="wide", page_icon="🪄")

# עיצוב RTL ותצוגה נקייה
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div, li { direction: RTL; text-align: right; }
    .stChatInputContainer { direction: RTL; }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    img { border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); margin: 10px 0; }
    .stIFrame { border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# פונקציות עזר לקבצים
def extract_pdf(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() for p in pdf.pages])
    except: return ""

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Panel")
    mode = st.radio("בחר פעולה:", ["🔍 צ'אט וניתוח קבצים", "🎨 יצירת תמונה"])
    st.divider()
    uploaded_file = st.file_uploader("העלה קובץ (PDF/Text)", type=["pdf", "txt"])
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

# אתחול הודעות
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריה
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)
        if "img_url" in m:
            st.markdown(f'<img src="{m["img_url"]}" width="100%">', unsafe_allow_html=True)

# קלט משתמש
if prompt := st.chat_input("איך אני יכול לעזור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה":
            with st.spinner("יוצר אמנות..."):
                encoded_prompt = requests.utils.quote(prompt)
                # שימוש במנוע שעבד לנו בצילום המסך
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
                
                # הצגה בשיטה המנצחת
                st.markdown(f'<img src="{img_url}" width="100%">', unsafe_allow_html=True)
                st.markdown(f"🔗 [קישור ישיר לתמונה]({img_url})")
                
                # שמירה להיסטוריה
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"הנה התמונה שיצרתי עבור: **{prompt}**",
                    "img_url": img_url
                })
        
        else: # מצב צ'אט
            with st.spinner("חושב..."):
                try:
                    api_key = st.secrets.get("OPENROUTER_API_KEY")
                    context = extract_pdf(uploaded_file) if uploaded_file else ""
                    
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={
                            "model": "google/gemini-2.0-flash-exp:free",
                            "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}\nענה בעברית."}]
                        }
                    )
                    data = res.json()
                    if "choices" in data:
                        ans = data['choices'][0]['message']['content']
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    else:
                        st.error("ה-AI לא הגיב כראוי. בדוק את המפתח ב-Secrets.")
                except Exception as e:
                    st.error(f"שגיאה בחיבור: {e}")

# תצוגה מקדימה ל-PDF בסידבר
if uploaded_file and mode == "🔍 צ'אט וניתוח קבצים":
    with st.sidebar:
        st.success("קובץ נטען בהצלחה!")





