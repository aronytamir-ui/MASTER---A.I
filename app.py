import streamlit as st
import requests
import base64

# הגדרות דף
st.set_page_config(page_title="Master AI", layout="wide")

# עיצוב RTL
st.markdown("""
    <style>
    .main, .stChatMessage, p, h1, h2, div { direction: RTL; text-align: right; }
    img { border-radius: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

st.title("🪄 Master AI - יצירת אמנות")

# בחירת מודל (הוספתי מנוע נוסף למקרה של חסימה)
engine = st.sidebar.selectbox("בחר מנוע יצירה:", ["מנוע 1 (Pollinations)", "מנוע 2 (Stable Diffusion)"])

prompt = st.text_input("תאר את התמונה שברצונך ליצור (עדיף באנגלית):", "A beautiful sunset over the ocean")

if st.button("✨ צור תמונה עכשיו"):
    if prompt:
        with st.spinner("ה-AI בתהליך יצירה..."):
            encoded_prompt = requests.utils.quote(prompt)
            
            # בחירת כתובת ה-URL לפי המנוע
            if "1" in engine:
                img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
            else:
                img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

            # הצגת הקישור לבדיקה
            st.write(f"🔗 [קישור ישיר לתמונה למקרה שלא נטען]({img_url})")

            # ניסיון הצגה בטוח ב-HTML (שיטה שעוקפת הרבה חסימות דפדפן)
            html_code = f"""
            <div style="display: flex; justify-content: center;">
                <img src="{img_url}" width="700" style="border-radius: 15px;">
            </div>
            """
            st.markdown(html_code, unsafe_allow_html=True)
            
            # כפתור הורדה משופר
            try:
                # שימוש ב-User-Agent כדי להתחזות לדפדפן רגיל ולמנוע חסימה
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(img_url, headers=headers, timeout=20)
                if res.status_code == 200:
                    st.download_button("📥 הורד תמונה למחשב", res.content, "master_ai.png", "image/png")
                else:
                    st.error("השרת חסם את הגישה להורדה, נסה להשתמש בקישור הישיר.")
            except:
                st.info("ניתן לשמור את התמונה באמצעות לחיצה ימנית עליה ושמירה.")
    else:
        st.warning("נא להזין תיאור לתמונה.")

st.divider()
st.info("טיפ: אם התמונה לא מופיעה, נסה להחליף מנוע בתפריט הצד או ללחוץ על הקישור הישיר.")






