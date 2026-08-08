import streamlit as st
from groq import Groq

# 🔑 API KULCS
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- OLDAL BEÁLLÍTÁSOK ---
st.set_page_config(
    page_title="🔍 Fake News Detector",
    page_icon="🛡️",
    layout="wide"
)

# --- EGYEDI CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    h1 {
        color: #ff6b6b !important;
        text-align: center !important;
        font-family: 'Arial Black', sans-serif !important;
        font-size: 3rem !important;
    }
    .stMarkdown p {
        color: #d1d5db !important;
        text-align: center !important;
        font-size: 1.2rem !important;
    }
    .stTextArea textarea {
        background-color: #1e1e2e !important;
        color: #ffffff !important;
        border: 2px solid #ff6b6b !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 40px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        transform: scale(1.05) !important;
    }
    /* Eredmény kártya */
    .result-card {
        background: rgba(30, 30, 46, 0.9);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 20px 0;
    }
    .result-card h2 {
        margin: 0;
        font-size: 2.5rem;
    }
    .result-card .score {
        font-size: 4rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .result-card .label {
        font-size: 1.2rem;
        opacity: 0.8;
    }
    /* Részletes info gombok */
    .detail-btn {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        width: 100% !important;
        text-align: left !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    .detail-btn:hover {
        background: rgba(255, 107, 107, 0.1) !important;
        border-color: #ff6b6b !important;
    }
    .detail-content {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 3px solid #ff6b6b;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 14px;
        border-top: 1px solid #333;
        margin-top: 40px;
    }
    .green { color: #2ecc71; }
    .yellow { color: #f1c40f; }
    .orange { color: #e67e22; }
    .red { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)

# --- CÍM ---
st.title("🛡️ Fake News Detector")
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

# --- EREDMÉNY MEGJELENÍTÉS ---
if analyze_btn and user_input:
    with st.spinner("🔎 Elemzés folyamatban..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": ANALYSIS_PROMPT + user_input}],
                temperature=0.0,
                max_tokens=800
            )

            # Válasz feldolgozása
            import json
            import re

            raw = response.choices[0].message.content
            # JSON kinyerése a szövegből
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {"credibility_score": 50, "analysis": raw[:200], "issues": ["Nem sikerült elemezni"]}

            score = data.get("credibility_score", 50)
            analysis = data.get("analysis", "Nincs elemzés")
            issues = data.get("issues", [])

            # --- SZÍN ÉS IKON MEGHATÁROZÁSA ---
            if score >= 80:
                color = "#2ecc71"
                emoji = "🟢"
                label = "HITELES"
                desc = "A cikk megbízható forrásból származik."
            elif score >= 60:
                color = "#f1c40f"
                emoji = "🟡"
                label = "MEGKÉRDŐJELEZHETŐ"
                desc = "A cikk néhány ponton aggályos."
            elif score >= 40:
                color = "#e67e22"
                emoji = "🟠"
                label = "GYANÚS"
                desc = "A cikk több problémát is mutat."
            else:
                color = "#e74c3c"
                emoji = "🔴"
                label = "VALÓSZÍNŰLEG HAMIS"
                desc = "A cikk erősen félrevezető."

            # --- ELEMZÉS TÁROLÁSA SESSION-BE ---
            st.session_state['last_result'] = {
                'score': score,
                'label': label,
                'desc': desc,
                'analysis': analysis,
                'issues': issues,
                'raw': raw
            }

        except Exception as e:
            st.error(f"❌ Hiba: {e}")

# --- EREDMÉNY MEGJELENÍTÉSE (HA VAN) ---
if 'last_result' in st.session_state:
    res = st.session_state['last_result']
    score = res['score']
    label = res['label']
    desc = res['desc']
    analysis = res['analysis']
    issues = res['issues']

    # --- KÁRTYA ---
    st.markdown("---")
    st.markdown(f"""
    <div class="result-card">
        <div class="label">Hitelességi szint</div>
        <div class="score" style="color: {color};">{score}%</div>
        <h2 style="color: {color};">{label}</h2>
        <div class="label">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- RÉSZLETES GOMBOK ---
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

    # --- TARTALOMAK ---
    if st.session_state.get('show_analysis', False):
        st.markdown("""
        <div class="detail-content">
            <b>📝 Mi alapján értékeltem?</b><br>
            A cikket az alábbi 5 szempont alapján vizsgáltam:
            <ol>
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
            <b>📊 Összegzés</b><br>
            {analysis}
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_summary'] = False

    if st.session_state.get('show_issues', False):
        issues_html = "".join([f"<li>{issue}</li>" for issue in issues]) if issues else "<li>Nincs konkrét probléma</li>"
        st.markdown(f"""
        <div class="detail-content">
            <b>🔍 Részletes problémák</b><br>
            <ul>{issues_html}</ul>
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_issues'] = False

# --- LÁBLÉC ---
st.markdown("""
<div class="footer">
    Fake News Detector v2.0 | Működteti: Groq AI | Ingyenes oktatási projekt
</div>
""", unsafe_allow_html=True)
