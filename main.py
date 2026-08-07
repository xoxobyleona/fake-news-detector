import streamlit as st
from groq import Groq

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="🔍 Fake News Detector",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Fake News Detector")
st.markdown("*Add meg egy cikk szövegét, és megtudod, mennyire hiteles!*")
st.markdown("---")

ANALYSIS_PROMPT = """
Egy cikk hitelességét vizsgálom. Kérlek, elemezd az alábbi szöveget az alábbi szempontok szerint:

1. Logikai és ténybeli ellentmondások
2. Félrevezető vagy kiragadott információk
3. Túlzó vagy szenzációhajhász cím
4. Érzelmi vagy szélsőséges nyelvezet
5. Elfogultság vagy egyoldalúság

Végeredményben add meg, hogy a cikk mennyire tűnik hitelesnek, és ezt egy 0-100%-os skálán is értékeld!

**A válaszodat magyarul írd!**

Cikk szövege:
"""


user_input = st.text_area(
    "📝 **Cikk szövege:**",
    height=200,
    placeholder="Ide másold a cikk szövegét..."
)

if st.button("🔍 Elemzés indítása", use_container_width=True):
    if not user_input:
        st.warning("⚠️ Kérlek, írd be a cikk szövegét!")
    else:
        with st.spinner("🔎 A cikk elemzése folyamatban... (Ez akár 10-20 másodperc is lehet)"):
            try:
                # --- GROQ API HÍVÁS ---
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "user", "content": ANALYSIS_PROMPT + user_input}
                    ],
                    temperature=0.0,
                    max_tokens=1000
                )
                
                # Eredmény megjelenítése
                st.markdown("---")
                st.subheader("📊 Elemzési Eredmény")
                st.success("✅ A cikk elemzése sikeresen befejeződött!")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"❌ Hiba történt az API hívás közben: {e}")
                st.info("💡 Tipp: Ellenőrizd, hogy az API-kulcsod érvényes-e, és hogy van-e internetkapcsolatod.")


st.markdown("---")
st.caption("Fake News Detector v1.0 | Működteti: Groq AI | Ingyenes oktatási projekt")
