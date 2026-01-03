import streamlit as st
import requests

# הגדרה בסיסית ביותר
st.title("בדיקת יצירת תמונה - Master AI")

# תיבת קלט
user_input = st.text_input("כתוב כאן תיאור לתמונה (באנגלית או עברית):", "cat on mars")

if st.button("צור תמונה עכשיו"):
    if user_input:
        with st.spinner("מייצר..."):
            # יצירת הכתובת
            img_url = f"https://pollinations.ai/p/{requests.utils.quote(user_input)}?width=1024&height=1024&seed=123"
            
            # הצגת הכתובת לביטחון
            st.write(f"מנסה לטעון מהכתובת: {img_url}")
            
            # הצגת התמונה ב-3 שיטות שונות בו זמנית כדי לוודא שאחת תעבוד:
            
            st.subheader("שיטה 1: תצוגה ישירה")
            st.image(img_url)
            
            st.subheader("שיטה 2: הורדה והצגה")
            try:
                res = requests.get(img_url)
                st.image(res.content)
                st.download_button("הורד קובץ", res.content, "image.png")
            except Exception as e:
                st.error(f"שיטה 2 נכשלה: {e}")

            st.subheader("שיטה 3: קישור חיצוני")
            st.markdown(f"[לחץ כאן לצפייה בתמונה בחלון חדש]({img_url})")
    else:
        st.warning("נא לכתוב משהו בתיבה")






