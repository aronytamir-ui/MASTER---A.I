import streamlit as st
import requests

# הגדרות דף
st.set_page_config(page_title="Master AI", layout="wide")

# עיצוב בסיסי (הורדתי את ה-RTL המורכב כדי לשלול חסימת תצוגה)
st.markdown("<style>direction: RTL; text-align: right;</style>", unsafe_allow_html=True)

st.title("🪄 Master AI - יוצר תמונות חכם")

# תפריט צד
with st.sidebar:
    mode = st.radio("בחר פעולה:", ["צ'אט", "יצירת תמונה"])
    st.info("אם התמונה לא מופיעה, נסה ללחוץ על 'צור' פעם נוספת.")

# אתחול היסטוריה
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת צ'אט (טקסט בלבד)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# קלט משתמש
if prompt := st.chat_input("מה תרצה ליצור?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    if mode == "יצירת תמונה":
        with st.chat_message("assistant"):
            with st.spinner("מצייר..."):
                # יצירת ה-URL
                encoded = requests.utils.quote(prompt)
                # שימוש בכתובת חלופית ויציבה יותר
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
                
                # תצוגה מחוץ לבועת הצ'אט כדי למנוע חסימות CSS
                st.image(url, caption=f"התוצאה עבור: {prompt}", use_container_width=True)
                
                # הוספת קישור גיבוי למקרה חירום
                st.markdown(f"🔗 [לחץ כאן אם התמונה לא נטענה]({url})")
                
                st.session_state.messages.append({"role": "assistant", "content": f"יצרתי תמונה עבור: {prompt}"})
    else:
        # לוגיקת צ'אט רגילה
        with st.chat_message("assistant"):
            st.write("מצב צ'אט פעיל. איך אוכל לעזור?")
            st.session_state.messages.append({"role": "assistant", "content": "מצב צ'אט פעיל."})




