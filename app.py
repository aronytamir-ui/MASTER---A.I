import streamlit as st
import requests
import json
from PyPDF2 import PdfReader

# --- 1. הגדרות SEO ומראה דף ---
st.set_page_config(
    page_title="Master AI - בינה מלאכותית מאוחדת וסיכום מסמכים",
    page_icon="💠",
    layout="centered"
)

# --- 2. ניהול מצב (State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# --- 3. עיצוב CSS מותאם אישית (כולל תמיכה בעברית) ---
bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#000000"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-size: {st.session_state.font_size}px;
        direction: rtl;
        text-align: right;
    }}
    [data-testid="stSidebar"] {{
        direction: rtl;
        background-color: {"#1a1c24" if st.session_state.dark_mode else "#f0f2f6"};
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. תפריט צד (Sidebar) ---
with st.sidebar:
    st.title("💠 Master AI")
    st.caption("השליטה ב-AI בידיים שלך")
    
    # הגדרות נגישות
    with st.expander("♿ נגישות ומראה"):
        if st.button("🌓 החלף מצב כהה/בהיר"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        st.session_state.font_size = st.slider("גודל גופן", 12, 24, st.session_state.font_size)

    st.divider()

    # ניהול מנוי (מודל Freemium)
    is_premium = st.toggle("🌟 מצב Premium (פתוח למפתחים)")
    if not is_premium:
        st.warning("גרסה חינמית - מודל Gemini Flash")
        if st.button("💳 שדרג ל-Premium"):
            st.markdown("[לחץ כאן למעבר לתשלום מאובטח](https://buy.stripe.com/your_link_here)")
    else:
        st.success("חשבון Premium פעיל - Claude 3.5")

    st.divider()
    
    # העלאת קבצים (זמין ב-Premium או כפי שתבחר)
    uploaded_file = st.file_uploader("📂 ניתוח וסיכום PDF", type="pdf")
    
    st.divider()
    
    # מדיניות פרטיות
    if st.button("📜 מדיניות פרטיות"):
        st.info("""
        **מדיניות פרטיות Master AI**
        - המידע שלך מעובד לצורך מתן תשובה בלבד.
        - קבצים נמחקים מהזיכרון עם סגירת הלשונית.
        - התשלומים מאובטחים ע"י Stripe.
        """)

# --- 5. לוגיקת תוכן וצ'אט ---
st.title("Master AI - הכל במקום אחד")

# חילוץ טקסט מ-PDF
pdf_context = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_context = "\n".join([page.extract_text() for page in reader.pages])
    st.info("המסמך נטען בהצלחה! תוכל לבקש סיכום שלו בצ'אט.")

# כפתורי פעולה מהירה
col1, col2 = st.columns(2)
preset = ""
with col1:
    if st.button("📝 סכם לי את ה-PDF"):
        if pdf_context: preset = f"סכם לי את המסמך הבא בנקודות ברורות:\n{pdf_context}"
        else: st.error("נא להעלות קובץ תחילה")
with col2:
    if is_premium:
        use_search = st.checkbox("🔍 חיפוש חי ברשת (Web Search)")
    else:
        st.checkbox("🔍 חיפוש חי (Premium Only)", disabled=True)
        use_search = False

# תצוגת צ'אט
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# קלט משתמש
if user_input := st.chat_input("איך אוכל לעזור לך היום?"):
    final_query = preset + user_input if preset else user_input
    
    st.session_state.messages.append({"role": "user", "content": final_query})
    with st.chat_message("user"):
        st.markdown(user_input if not preset else "🚀 מפעיל סיכום מסמך...")

    # שליחה ל-OpenRouter
    with st.chat_message("assistant"):
        with st.spinner("Master AI חושב..."):
            # כאן תחליף ל-st.secrets["OPENROUTER_API_KEY"] אחרי שתגדיר ב-Streamlit
            api_key = st.secrets["OPENROUTER_API_KEY"]
            model = "anthropic/claude-3.5-sonnet" if is_premium else "google/gemini-flash-1.5"
            
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "perplexity/llama-3-sonar-large-32k-online" if use_search else model,
                "messages": st.session_state.messages
            }
            
            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except:
                st.error("חיבור ה-API נכשל. וודא שהמפתח תקין.")
