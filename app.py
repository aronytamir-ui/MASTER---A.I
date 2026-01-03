import streamlit as st
import requests
import PyPDF2
import base64

# 1. הגדרות דף חובה
st.set_page_config(page_title="Master AI Ultra", layout="wide", page_icon="🚀")

# 2. עיצוב ממשק RTL ועיצוב כפתורי מודלים
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div, li { direction: RTL; text-align: right; }
    .stChatInputContainer { direction: RTL; }
    button[data-testid="stChatInputSubmit"] { left: 10px; right: auto; }
    img { border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); margin: 10px 0; }
    .model-tag { background-color: #4A90E2; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לעיבוד קבצים
def extract_pdf(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        return " ".join([p.extract_text() for p in pdf.pages])
    except: return ""

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Ultra")
    
    # בחירת מודל בינה מלאכותית
    ai_model = st.selectbox("בחר מודל חכם:", [
        "google/gemini-2.0-flash-exp:free",
        "openai/gpt-4o",
        "anthropic/claude-3-sonnet",
        "meta-llama/llama-3-70b-instruct"
    ])
    
    # בחירת סוג פעולה
    mode = st.radio("מה תרצה לעשות?", ["💬 צ'אט וניתוח קבצים", "🎨 יצירת תמונה (DALL-E/Flux)", "🎬 וידאו ומוזיקה"])
    
    st.divider()
    uploaded_file = st.file_uploader("צרף קובץ לניתוח", type=["pdf", "txt", "docx"])
    
    if st.button("🗑️ נקה היסטוריה"):
        st.session_state.messages = []
        st.rerun()

# אתחול הודעות
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת הצ'אט
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)
        if "img_url" in m:
            st.markdown(f'<img src="{m["img_url"]}" width="100%">', unsafe_allow_html=True)

# לוגיקת קלט
if prompt := st.chat_input("כתוב כאן הודעה..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה (DALL-E/Flux)":
            with st.spinner("ה-AI מצייר ברגעים אלו..."):
                encoded_prompt = requests.utils.quote(prompt)
                # מנוע משולב המדמה איכות של DALL-E/Flux
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
                
                st.markdown(f'<img src="{img_url}" width="100%">', unsafe_allow_html=True)
                st.markdown(f"🔗 [הורד תמונה בקישור ישיר]({img_url})")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"יצרתי עבורך תמונה באמצעות מודל ויזואלי מתקדם.",
                    "img_url": img_url
                })

        elif mode == "🎬 וידאו ומוזיקה":
            st.warning("יכולת הוידאו והמוזיקה נמצאת בחיבור לשרת חיצוני. נסה לתאר מה תרצה ליצור.")
            st.info("בקרוב: אינטגרציה מלאה עם Runway ו-Suno!")

        else: # מצב צ'אט חכם
            with st.spinner(f"חושב באמצעות {ai_model.split('/')[1]}..."):
                api_key = st.secrets.get("OPENROUTER_API_KEY")
                if not api_key:
                    st.error("חסר מפתח API ב-Secrets!")
                else:
                    context = extract_pdf(uploaded_file) if uploaded_file else ""
                    try:
                        res = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {api_key}"},
                            json={
                                "model": ai_model,
                                "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}\nענה בעברית."}]
                            }
                        )
                        data = res.json()
                        ans = data['choices'][0]['message']['content']
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    except:
                        st.error("חלה שגיאה בחיבור למודל. נסה מודל אחר מהרשימה.")





