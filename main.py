import streamlit as st
from groq import Groq
import json
import re

# 🔑 API KULCS
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- OLDAL BEÁLLÍTÁSOK ---
st.set_page_config(
    page_title="🔍 Fake News Detector",
    page_icon="🛡️",
    layout="wide"
)

# --- EGYEDI CSS (FEHÉR-TÜRKIZ) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f0fdfa, #e6f9f5) !important;
    }
    .stApp, .stMarkdown, p, div, span, label {
        color: #1a2e35 !important;
    }
    h1 {
        color: #0d9488 !important;
        text-align: center !important;
        font-family: 'Arial Black', sans-serif !important;
        font-size: 3rem !important;
    }
    .stMarkdown p {
        color: #1a2e35 !important;
        text-align: center !important;
        font-size: 1.2rem !important;
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1a2e35 !important;
        border: 2px solid #14b8a6 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        font-size: 16px !important;
    }
    .stTextArea textarea:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.2) !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #14b8a6, #0d9488) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 40px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.3) !important;
    }
    .stButton button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 25px rgba(13, 148, 136, 0.4) !important;
    }
    .result-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid #e6f9f5;
        margin: 20px 0;
    }
    .result-card .label {
        font-size: 1.1rem;
        color: #5a7a82;
        margin-bottom: 5px;
    }
    .result-card .score {
        font-size: 4rem;
        font-weight: bold;
        margin: 5px 0;
    }
    .result-card h2 {
        margin: 0;
        font-size: 2rem;
    }
    .result-card .desc {
        font-size: 1.1rem;
        color: #5a7a82;
        margin-top: 8px;
    }
    .detail-content {
        background: #ffffff;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #14b8a6;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    .detail-content b {
        color: #0d9488;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #94a3b8 !important;
        font-size: 13px;
        border-top: 1px solid #e6f9f5;
        margin-top: 40px;
    }
    .stAlert {
        background-color: #ffffff !important;
        border-radius: 15px !important;
        border-left: 4px solid #14b8a6 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    .stSpinner {
        color: #0d9488 !important;
    }
    .stButton button[kind="secondary"] {
        background: transparent !important;
        color: #0d9488 !important;
        border: 2px solid #14b8a6 !important;
        box-shadow: none !important;
    }
    .stButton button[kind="secondary"]:hover {
        background: #14b8a6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CÍM ---
st.title("Fake News Detector")
st.markdown("*Add meg egy cikk szövegét, és megtudod, mennyire hiteles!*")
st.markdown("---")

# --- ELEMZŐ PROMPT ---
ANALYSIS_PROMPT = """
Elemezd a következő cikket, és a választ JSON formátumban add meg az alábbi kulcsokkal:
- credibility_score: szám 0-100 között
- analysis: rövid indoklás (1-2 mondat)
- issues: lista a problémákról (logikai ellentmondás, félrevezető információ, túlzó cím, érzelmi nyelvezet, elfogultság)

Cikk: 
"""

# --- FŐ TARTALOM ---
user_input = st.text_area(
    "📝 **Cikk szövege:**",
    height=150,
    placeholder="Ide másold a cikk szövegét..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("🔍 Elemzés indítása", use_container_width=True)

# --- KÉP KIVÁLASZTÁSA SZÁZALÉK ALAPJÁN (A FŐ MAPPÁBÓL) ---
def get_image_path(score):
    if score <= 10:
        return "0.png"
    elif score <= 20:
        return "10.png"
    elif score <= 30:
        return "20.png"
    elif score <= 40:
        return "30.png"
    elif score <= 50:
        return "40.png"
    elif score <= 60:
        return "50.png"
    elif score <= 70:
        return "60.png"
    elif score <= 80:
        return "70.png"
    elif score <= 90:
        return "80.png"
    elif score <= 95:
        return "90.png"
    else:
        return "100.png"

# --- ELEMZÉS ---
if analyze_btn and user_input:
    with st.spinner("🔎 Elemzés folyamatban..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": ANALYSIS_PROMPT + user_input}],
                temperature=0.0,
                max_tokens=800
            )

            raw = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {"credibility_score": 50, "analysis": raw[:200], "issues": ["Nem sikerült elemezni"]}

            score = data.get("credibility_score", 50)
            analysis = data.get("analysis", "Nincs elemzés")
            issues = data.get("issues", [])

            # --- SZÍN MEGHATÁROZÁSA (TÜRKIZ ÁRNYLATOK) ---
            if score >= 80:
                color = "#0d9488"
                label = "HITELES"
                desc = "A cikk megbízható forrásból származik."
            elif score >= 60:
                color = "#14b8a6"
                label = "MEGKÉRDŐJELEZHETŐ"
                desc = "A cikk néhány ponton aggályos."
            elif score >= 40:
                color = "#f59e0b"
                label = "GYANÚS"
                desc = "A cikk több problémát is mutat."
            else:
                color = "#ef4444"
                label = "VALÓSZÍNŰLEG HAMIS"
                desc = "A cikk erősen félrevezető."

            image_path = get_image_path(score)

            st.session_state['last_result'] = {
                'score': score,
                'label': label,
                'desc': desc,
                'analysis': analysis,
                'issues': issues,
                'color': color,
                'image_path': image_path
            }

        except Exception as e:
            st.error(f"❌ Hiba: {e}")

# --- EREDMÉNY MEGJELENÍTÉSE ---
if 'last_result' in st.session_state:
    res = st.session_state['last_result']
    score = res['score']
    label = res['label']
    desc = res['desc']
    analysis = res['analysis']
    issues = res['issues']
    color = res['color']
    image_path = res['image_path']

    st.markdown("---")
    st.markdown(f"""
    <div class="result-card">
        <div class="label">🎯 Hitelességi szint</div>
        <div class="score" style="color: {color};">{score}%</div>
        <h2 style="color: {color};">{label}</h2>
        <div class="desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- KÉP MEGJELENÍTÉSE ---
    try:
        st.image(image_path, width=200)
    except Exception as e:
        st.info(f"🖼️ Kép betöltése nem sikerült: {e}")

    st.markdown("### 📋 Részletes elemzés")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Mi alapján értékeltem?", use_container_width=True):
            st.session_state['show_analysis'] = True
        if st.button("📊 Összegzés", use_container_width=True):
            st.session_state['show_summary'] = True

    with col2:
        if st.button("🔍 Részletes problémák", use_container_width=True):
            st.session_state['show_issues'] = True
        if st.button("🔄 Új elemzés", use_container_width=True):
            st.session_state['last_result'] = None
            st.rerun()

    if st.session_state.get('show_analysis', False):
        st.markdown("""
        <div class="detail-content">
            <b>📝 Mi alapján értékeltem?</b><br><br>
            A cikket az alábbi <b>5 szempont</b> alapján vizsgáltam:
            <ol style="margin-top: 10px; line-height: 1.8;">
                <li><b>Logikai és ténybeli ellentmondások</b> – Van-e ellentmondás a szövegben?</li>
                <li><b>Félrevezető információk</b> – Kiragadott vagy félrevezető állítások?</li>
                <li><b>Túlzó cím</b> – A cím szenzációhajhász?</li>
                <li><b>Érzelmi nyelvezet</b> – Túlzott érzelmi töltet?</li>
                <li><b>Elfogultság</b> – Egyoldalú a bemutatás?</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_analysis'] = False

    if st.session_state.get('show_summary', False):
        st.markdown(f"""
        <div class="detail-content">
            <b>📊 Összegzés</b><br><br>
            {analysis}
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_summary'] = False

    if st.session_state.get('show_issues', False):
        issues_html = "".join([f"<li>{issue}</li>" for issue in issues]) if issues else "<li>✅ Nincs konkrét probléma</li>"
        st.markdown(f"""
        <div class="detail-content">
            <b>🔍 Részletes problémák</b><br>
            <ul style="margin-top: 10px; line-height: 1.8;">{issues_html}</ul>
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_issues'] = False

# --- LÁBLÉC ---
st.markdown("""
<div class="footer">
    Fake News Detector v2.0 | Működteti: Groq AI | Ingyenes oktatási projekt
</div>
""", unsafe_allow_html=True)
