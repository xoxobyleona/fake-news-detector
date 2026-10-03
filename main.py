import streamlit as st
from groq import Groq
import json
import re

# 🔑 API KEY
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="🔍 Fake News Detector",
    page_icon="🛡️",
    layout="wide"
)

# --- CUSTOM CSS (WHITE-TEAL) ---
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

# --- TITLE ---
st.title("Fake News Detector")
st.markdown("*Paste an article text to check its credibility!*")
st.markdown("---")

# --- ANALYSIS PROMPT (ENGLISH) ---
ANALYSIS_PROMPT = """
Analyze the following article and provide your response in JSON format with these keys:
- credibility_score: number between 0-100
- analysis: brief summary (1-2 sentences only!)
- issues: list of problems found. If no problems found, return an empty list [].

Check for these issues:
- Logical contradictions
- Misleading information
- Exaggerated or sensationalist headline
- Emotional manipulation
- Bias or one-sidedness

Article: 
"""

# --- MAIN CONTENT ---
user_input = st.text_area(
    "📝 **Article text:**",
    height=150,
    placeholder="Paste the article text here..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

# --- RESULT DISPLAY ---
if analyze_btn and user_input:
    with st.spinner("🔎 Analyzing..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": ANALYSIS_PROMPT + user_input}],
                temperature=0.0,
                max_tokens=800
            )

            raw = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {"credibility_score": 50, "analysis": "Unable to analyze.", "issues": ["Failed to parse response"]}

            score = data.get("credibility_score", 50)
            analysis = data.get("analysis", "No summary available.")
            issues = data.get("issues", [])

            # --- COLOR DETERMINATION (TEAL SHADES) ---
            if score >= 80:
                color = "#0d9488"
                label = "CREDIBLE"
                desc = "The article appears to be from a reliable source."
            elif score >= 60:
                color = "#14b8a6"
                label = "QUESTIONABLE"
                desc = "The article has some concerning points."
            elif score >= 40:
                color = "#f59e0b"
                label = "SUSPICIOUS"
                desc = "The article shows multiple issues."
            else:
                color = "#ef4444"
                label = "LIKELY FALSE"
                desc = "The article appears to be highly misleading."

            st.session_state['last_result'] = {
                'score': score,
                'label': label,
                'desc': desc,
                'analysis': analysis,
                'issues': issues,
                'color': color
            }

        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- RESULT DISPLAY ---
if 'last_result' in st.session_state and st.session_state['last_result'] is not None:
    res = st.session_state['last_result']
    score = res['score']
    label = res['label']
    desc = res['desc']
    analysis = res['analysis']
    issues = res['issues']
    color = res['color']

    st.markdown("---")
    st.markdown(f"""
    <div class="result-card">
        <div class="label">🎯 Credibility Score</div>
        <div class="score" style="color: {color};">{score}%</div>
        <h2 style="color: {color};">{label}</h2>
        <div class="desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Detailed Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 How did I evaluate?", use_container_width=True):
            st.session_state['show_analysis'] = True
        if st.button("📊 Summary", use_container_width=True):
            st.session_state['show_summary'] = True

    with col2:
        if st.button("🔍 Detailed issues", use_container_width=True):
            st.session_state['show_issues'] = True
        if st.button("🔄 New analysis", use_container_width=True):
            del st.session_state['last_result']
            st.rerun()

    if st.session_state.get('show_analysis', False):
        st.markdown("""
        <div class="detail-content">
            <b>📝 How did I evaluate?</b><br><br>
            The article was examined based on <b>5 key criteria</b>:
            <ol style="margin-top: 10px; line-height: 1.8;">
                <li><b>Logical contradictions</b> – Are there contradictions in the text?</li>
                <li><b>Misleading information</b> – Out-of-context or deceptive claims?</li>
                <li><b>Exaggerated headline</b> – Is the headline sensationalist?</li>
                <li><b>Emotional language</b> – Excessive emotional manipulation?</li>
                <li><b>Bias</b> – Is the presentation one-sided?</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_analysis'] = False

    if st.session_state.get('show_summary', False):
        st.markdown(f"""
        <div class="detail-content">
            <b>📊 Summary</b><br><br>
            {analysis}
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_summary'] = False

    if st.session_state.get('show_issues', False):
        if issues and len(issues) > 0:
            issues_html = "".join([f"<li>• {issue}</li>" for issue in issues])
            st.markdown(f"""
            <div class="detail-content">
                <b>🔍 Detailed issues</b><br>
                <ul style="margin-top: 10px; line-height: 1.8; list-style-type: none; padding-left: 0;">
                    {issues_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="detail-content">
                <b>🔍 Detailed issues</b><br><br>
                ✅ No issues found. The article appears to be consistent and well-sourced.
            </div>
            """, unsafe_allow_html=True)
        st.session_state['show_issues'] = False

# --- FOOTER ---
st.markdown("""
<div class="footer">
    Fake News Detector v2.0 | Powered by Groq AI | Free educational project
</div>
""", unsafe_allow_html=True)
