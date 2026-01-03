import streamlit as st
import requests
import PyPDF2
import base64

# 1. הגדרות דף
st.set_page_config(page_title="Master AI Ultra", layout="wide")

# 2. עיצוב RTL
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div { direction: RTL; text-align: right; }
    img { border-radius: 15px; border: 2px solid #444; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה להמרת תמונה לקוד Base64 (כדי שלא תיחסם)
def get_image_base64(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except: return None
    return None

# --- תפריט צד ---
with st.sidebar:
    st.title("🚀 Master AI Ultra")
    ai_model = st.selectbox("בחר מודל חכם:", ["google/gemini-2.0-flash-exp:free", "openai/gpt-4o"])
    mode = st.radio("פעולה:", ["💬 צ'אט", "🎨 יצירת תמונה (DALL-E/Flux)"])
    if st.button("🗑️ נקה הכל"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת הודעות מהעבר
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"], unsafe_allow_html=True)

# קלט משתמש
if prompt := st.chat_input("כתוב כאן..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "🎨 יצירת תמונה (DALL-E/Flux)":
            with st.spinner("יוצר תמונה..."):
                encoded_prompt = requests.utils.quote(prompt)
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
                
                # הפיכת התמונה לקוד כדי לעקוף חסימות
                b64_img = get_image_base64(img_url)
                
                if b64_img:
                    display_html = f'<img src="data:image/png;base64,{b64_img}" width="100%">'
                    st.markdown(display_html, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": display_html})
                else:
                    st.error("לא הצלחתי לטעון את התמונה. נסה שוב בעוד רגע.")
        
        else:
            with st.spinner("חושב..."):
                api_key = st.secrets.get("OPENROUTER_API_KEY")
                try:
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={
                            "model": ai_model,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    ans = res.json()['choices'][0]['message']['content']
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except:
                    st.error("שגיאה בחיבור ל-AI.")




