import streamlit as st
import requests

# 1. הגדרות בסיסיות ללא עיצובים כבדים
st.set_page_config(page_title="Master AI Test")

st.title("🤖 Master AI - בדיקת יצירת תמונה")

# 2. בחירת מצב פשוטה מאוד
mode = st.sidebar.selectbox("בחר מצב:", ["צ'אט", "יצירת תמונה"])

# 3. אתחול היסטוריה
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. הצגת הודעות מהעבר
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if "img" in m:
            st.image(m["img"])

# 5. תיבת קלט
if prompt := st.chat_input("כתוב כאן מה ליצור..."):
    # הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # יצירת תגובה
    with st.chat_message("assistant"):
        if mode == "יצירת תמונה":
            # יצירת הכתובת של התמונה
            img_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed=1"
            
            # הצגת התמונה מיד!
            st.image(img_url, caption="הנה התמונה שלך")
            
            # כפתור הורדה
            img_raw = requests.get(img_url).content
            st.download_button("📥 לחץ כאן להורדת התמונה", img_raw, "ai_image.png", "image/png")
            
            # שמירה להיסטוריה
            st.session_state.messages.append({"role": "assistant", "content": "בוצע!", "img": img_url})
        
        else:
            # צ'אט רגיל (מוודא שהמפתח קיים)
            api_key = st.secrets.get("OPENROUTER_API_KEY")
            if not api_key:
                st.error("חסר מפתח API ב-Secrets!")
            else:
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "google/gemini-2.0-flash-exp:free",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                ans = res.json()['choices'][0]['message']['content']
                st.write(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})








