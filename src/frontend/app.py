import os
import re
import requests
import pdfplumber
import streamlit as st
from src.utils.scraper import fetch_job_description_from_url

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/analyze")
CHAT_API_URL = "http://127.0.0.1:8000/api/v1/chat"

# Page Config
st.set_page_config(
    page_title="SkillBridge AI — Career Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =================================================================
# PREMIUM VISUAL THEME
# =================================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-0: #0A0C11;
        --bg-1: #10131B;
        --surface: #141822;
        --surface-2: #1A1F2C;
        --border: rgba(148, 163, 184, 0.10);
        --border-strong: rgba(148, 163, 184, 0.22);
        --text-hi: #EEF1F6;
        --text-mid: #93A0B4;
        --text-lo: #5C6679;
        --indigo: #6366F1;
        --teal: #2DD4BF;
        --amber: #F5A524;
        --rose: #F1637A;
        --green: #34D399;
        --radius-sm: 10px;
        --radius-md: 16px;
        --radius-lg: 22px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Space Grotesk', 'Inter', sans-serif;
    }
    .main {
        background:
            radial-gradient(ellipse 900px 500px at 12% -10%, rgba(99,102,241,0.10), transparent 60%),
            radial-gradient(ellipse 700px 500px at 100% 10%, rgba(45,212,191,0.06), transparent 55%),
            var(--bg-0);
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1360px;
    }

    /* ---------- HERO ---------- */
    .hero-container { text-align: center; padding: 3rem 0 1.5rem 0; position: relative; }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 8px; padding: 7px 16px 7px 12px;
        background: var(--surface); border: 1px solid var(--border-strong); color: var(--teal);
        border-radius: 999px; font-size: 0.82rem; font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .hero-badge .dot {
        width: 6px; height: 6px; border-radius: 50%; background: var(--teal);
        box-shadow: 0 0 0 3px rgba(45,212,191,0.18);
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4.2rem; font-weight: 700; color: var(--text-hi);
        text-align: center; margin: 0 0 1.1rem 0; line-height: 1.05; letter-spacing: -0.03em;
    }
    .hero-title .accent {
        background: linear-gradient(120deg, var(--indigo) 10%, var(--teal) 90%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .hero-subtitle {
        font-size: 1.15rem; color: var(--text-mid); text-align: center;
        max-width: 700px; margin: 0 auto; line-height: 1.7; font-weight: 400;
    }

    /* ---------- SECTION HEADINGS ---------- */
    .section-heading {
        display: flex; align-items: baseline; gap: 14px;
        margin: 2.4rem 0 1.4rem 0; padding-bottom: 0.9rem;
        border-bottom: 1px solid var(--border);
    }
    .section-heading-bar {
        width: 4px; height: 22px; border-radius: 4px; flex-shrink: 0;
        background: linear-gradient(180deg, var(--indigo), var(--teal));
        transform: translateY(3px);
    }
    .section-heading-text { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 600; color: var(--text-hi); letter-spacing: -0.01em; }
    .section-heading-caption { font-size: 0.88rem; color: var(--text-lo); margin-top: 3px; }

    /* ---------- CARDS ---------- */
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 1.9rem 1.7rem; height: 100%;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .feature-card:hover {
        border-color: var(--border-strong);
        transform: translateY(-2px);
    }
    .feature-icon {
        width: 46px; height: 46px; border-radius: 12px;
        background: var(--surface-2);
        border: 1px solid var(--border);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.35rem; margin-bottom: 1.1rem;
    }
    .feature-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: var(--text-hi); margin-bottom: 0.5rem; letter-spacing: -0.01em; }
    .feature-desc { font-size: 0.92rem; color: var(--text-mid); line-height: 1.6; }

    /* ---------- METRIC CARDS ---------- */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md); padding: 1.3rem 1.2rem; text-align: left;
        transition: border-color 0.2s ease;
    }
    .metric-card:hover { border-color: var(--border-strong); }
    .metric-label {
        font-size: 0.82rem; color: var(--text-mid); font-weight: 500;
    }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem; font-weight: 700; color: var(--text-hi);
        margin-top: 0.35rem; line-height: 1; letter-spacing: -0.02em;
    }
    .metric-value-gold { color: var(--amber); }
    .metric-value-green { color: var(--green); }
    .metric-value-amber { color: var(--amber); }
    .metric-value-red { color: var(--rose); }

    /* ---------- SCORE HERO ---------- */
    .score-hero {
        background: var(--surface);
        border: 1px solid var(--border-strong);
        border-radius: var(--radius-lg); padding: 2.3rem 2rem; margin: 1.4rem 0;
        position: relative; overflow: hidden; text-align: center;
    }
    .score-hero::before {
        content: ''; position: absolute; inset: 0;
        background: linear-gradient(120deg, rgba(99,102,241,0.10), transparent 55%, rgba(45,212,191,0.08));
        pointer-events: none;
    }
    .score-hero-label {
        font-size: 0.8rem; color: var(--text-mid); font-weight: 600;
        letter-spacing: 0.06em; margin-bottom: 0.7rem; position: relative;
    }
    .score-hero-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4.6rem; font-weight: 700; color: var(--text-hi);
        line-height: 1; letter-spacing: -0.03em; position: relative;
    }
    .score-hero-band {
        font-size: 1.02rem; color: var(--teal);
        margin-top: 0.7rem; font-weight: 500; position: relative;
    }

    /* ---------- BADGES ---------- */
    .badge-matched {
        background: rgba(52,211,153,0.08);
        color: #6EE7B7; border: 1px solid rgba(52,211,153,0.3);
        padding: 6px 13px; border-radius: var(--radius-sm); font-weight: 500;
        font-size: 0.87rem; display: inline-block; margin: 4px 6px 4px 0;
    }
    .badge-partial {
        background: rgba(245,165,36,0.08);
        color: #FBC968; border: 1px solid rgba(245,165,36,0.3);
        padding: 6px 13px; border-radius: var(--radius-sm); font-weight: 500;
        font-size: 0.87rem; display: inline-block; margin: 4px 6px 4px 0;
    }
    .badge-missing {
        background: rgba(241,99,122,0.08);
        color: #F6A0AF; border: 1px solid rgba(241,99,122,0.3);
        padding: 6px 13px; border-radius: var(--radius-sm); font-weight: 500;
        font-size: 0.87rem; display: inline-block; margin: 4px 6px 4px 0;
    }

    /* ---------- RESUME CARD ---------- */
    .resume-card {
        background: var(--surface);
        border-radius: var(--radius-md); padding: 1.3rem 1.6rem; margin-bottom: 1rem;
        border: 1px solid var(--border);
        border-left: 3px solid var(--indigo);
    }
    .resume-category {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem; font-weight: 600; color: var(--text-hi);
        display: flex; align-items: center; gap: 10px;
    }
    .priority-high {
        background: rgba(241,99,122,0.15); color: #F6A0AF; border: 1px solid rgba(241,99,122,0.35);
        padding: 3px 11px; border-radius: 999px;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em;
    }
    .priority-medium {
        background: rgba(245,165,36,0.15); color: #FBC968; border: 1px solid rgba(245,165,36,0.35);
        padding: 3px 11px; border-radius: 999px;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.04em;
    }
    .before-box {
        background: rgba(241, 99, 122, 0.05);
        border: 1px solid rgba(241, 99, 122, 0.2);
        border-radius: var(--radius-sm); padding: 1rem 1.2rem;
        color: #E7A9B3; font-size: 0.92rem; line-height: 1.55;
    }
    .after-box {
        background: rgba(52, 211, 153, 0.05);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: var(--radius-sm); padding: 1rem 1.2rem;
        color: #A7E8CB; font-size: 0.92rem; line-height: 1.55;
    }

    /* ---------- INTERVIEW CARD ---------- */
    .interview-card {
        background: var(--surface);
        border-radius: var(--radius-md); padding: 1.4rem 1.6rem; margin-bottom: 1rem;
        border: 1px solid var(--border);
        border-left: 3px solid var(--indigo);
    }
    .q-type-tech { background: rgba(99,102,241,0.15); color: #A5A8FA; border: 1px solid rgba(99,102,241,0.3); padding: 4px 12px; border-radius: 999px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em; margin-right: 8px; }
    .q-type-behav { background: rgba(52,211,153,0.15); color: #86EFC3; border: 1px solid rgba(52,211,153,0.3); padding: 4px 12px; border-radius: 999px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em; margin-right: 8px; }
    .q-type-design { background: rgba(45,212,191,0.15); color: #7EEAE0; border: 1px solid rgba(45,212,191,0.3); padding: 4px 12px; border-radius: 999px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em; margin-right: 8px; }
    .difficulty-badge {
        background: var(--surface-2); color: var(--amber);
        padding: 4px 11px; border-radius: 999px; font-size: 0.7rem;
        font-weight: 600; border: 1px solid rgba(245,165,36,0.3);
    }
    .question-text { color: var(--text-hi); font-size: 1.08rem; font-weight: 600; margin-top: 0.85rem; line-height: 1.45; }

    /* ---------- RESOURCE CARD ---------- */
    .resource-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm); padding: 0.9rem 1.2rem; margin-bottom: 0.6rem;
        border-left: 3px solid var(--teal); transition: border-color 0.2s ease;
    }
    .resource-card:hover { border-color: var(--border-strong); }
    .resource-link { color: var(--teal); text-decoration: none; font-weight: 600; font-size: 0.96rem; }
    .resource-type { color: var(--text-lo); font-size: 0.82rem; margin-left: 8px; }

    /* ---------- TIP CARD ---------- */
    .tip-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm); padding: 1rem 1.3rem; margin-bottom: 0.8rem;
        border-left: 3px solid var(--indigo); color: #D6DCE8;
        font-size: 0.95rem; line-height: 1.6;
    }

    /* ---------- UTILITY ---------- */
    .glass-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-strong), transparent);
        margin: 1.8rem 0;
    }

    /* Streamlit tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px; background-color: var(--surface);
        padding: 5px; border-radius: 14px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; border-radius: 10px; padding: 0 16px;
        color: var(--text-mid); font-weight: 500; font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        background: var(--surface-2) !important;
        color: var(--text-hi) !important;
        border: 1px solid var(--border-strong);
    }

    /* Streamlit buttons */
    .stButton > button {
        border-radius: var(--radius-sm); font-weight: 600; transition: transform 0.15s ease, filter 0.15s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); }
    .stButton > button[kind="primary"] {
        background: linear-gradient(120deg, var(--indigo), #4F46E5);
        border: none;
    }
    .stButton > button[kind="primary"]:hover { filter: brightness(1.08); }

    /* Streamlit inputs */
    .stTextInput input, .stTextArea textarea {
        border-radius: var(--radius-sm) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =================================================================
# HELPERS
# =================================================================
def get_score_band(score: float) -> tuple:
    if score >= 85:
        return ("Excellent — Job Ready", "excellent")
    elif score >= 70:
        return ("Strong — Minor Gaps", "strong")
    elif score >= 50:
        return ("Developing — Needs Focus", "developing")
    else:
        return ("Early Stage — Build Foundations", "early")


def section_header(icon: str, title: str, caption: str = ""):
    html = f"""
    <div class="section-heading">
        <div class="section-heading-bar"></div>
        <div>
            <div class="section-heading-text">{icon} {title}</div>
            {f'<div class="section-heading-caption">{caption}</div>' if caption else ''}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def extract_unique_skills(raw_input_text: str) -> list:
    """Extract skills: comma-separated splits directly; paragraphs use taxonomy."""
    from src.matching.skill_extractor import extract_skills

    if not raw_input_text or not raw_input_text.strip():
        return []

    text = raw_input_text.strip()

    if "," in text and len(text.split()) < 30 and "\n" not in text:
        return [s.strip() for s in text.split(",") if s.strip()]

    extracted = extract_skills(text)
    if extracted:
        return extracted

    words = re.findall(r"\b[a-zA-Z0-9+#.-]+\b", text)
    return [w for w in words if len(w) > 2][:30]


def generate_markdown_report(target_role: str, score: float, breakdown: dict, advice: dict) -> str:
    report = f"# ⚡ SkillBridge AI — Career Strategy Report\n"
    report += f"**Target Role:** {target_role}\n"
    report += f"**Readiness Score:** {score:.1f}%\n\n---\n\n"

    if "executive_summary" in advice:
        report += f"## 💡 Executive Summary\n{advice['executive_summary']}\n\n"

    report += f"## 📊 Skill Match Breakdown\n"
    report += f"### ✅ Matched Skills ({len(breakdown.get('matched', []))})\n"
    for item in breakdown.get("matched", []):
        report += f"- {item.get('skill', '')}\n"
    report += f"\n### ⚡ Partial Matches ({len(breakdown.get('partial', []))})\n"
    for item in breakdown.get("partial", []):
        report += f"- {item.get('skill', '')} (Match: {item.get('score', 'N/A')})\n"
    report += f"\n### ❌ Missing Requirements ({len(breakdown.get('missing', []))})\n"
    for item in breakdown.get("missing", []):
        report += f"- {item.get('skill', '')}\n"

    report += f"\n---\n\n## 🗺️ Multi-Phase Action Roadmap\n"
    phases = advice.get("roadmap_phases", [])
    if isinstance(phases, list):
        for idx, phase in enumerate(phases, 1):
            if isinstance(phase, dict):
                report += f"### {phase.get('phase_title', f'Phase {idx}')}\n"
                if phase.get("duration"):
                    report += f"**Duration:** {phase['duration']}\n\n"
                report += f"**Focus Skills:** {', '.join(phase.get('focus_skills', []))}\n\n"
                if phase.get("prerequisites"):
                    report += f"**Prerequisites:** {phase['prerequisites']}\n\n"
                report += f"**Objective:** {phase.get('objective', '')}\n\n**Action Steps:**\n"
                for step in phase.get("action_steps", []):
                    report += f"- {step}\n"
                resources = phase.get("learning_resources", [])
                if resources:
                    report += f"\n**Learning Resources:**\n"
                    for res in resources:
                        report += f"- [{res.get('title', '')}]({res.get('url', '')})\n"
                capstone = phase.get("capstone_project", {})
                if isinstance(capstone, dict) and capstone:
                    report += f"\n**Capstone Project:** {capstone.get('title', '')}\n"
                    report += f"- *Description:* {capstone.get('description', '')}\n"
                    if capstone.get("technologies"):
                        report += f"- *Technologies:* {', '.join(capstone.get('technologies', []))}\n"
                    report += f"- *Deliverable:* `{capstone.get('deliverable', '')}`\n"
                report += f"\n"

    report += f"---\n\n## ✍️ Resume Optimization\n"
    opts = advice.get("resume_optimizations", [])
    if isinstance(opts, list):
        for item in opts:
            if isinstance(item, dict):
                report += f"### {item.get('category', 'Resume Bullet')}\n"
                if item.get("priority"):
                    report += f"**Priority:** {item['priority']}\n\n"
                report += f"- **Before:** {item.get('before', '')}\n"
                report += f"- **After:** {item.get('after', '')}\n"
                report += f"- **Why:** {item.get('why', item.get('strategy', ''))}\n\n"
                if item.get("keywords_to_add"):
                    report += f"- **Keywords to add:** {', '.join(item['keywords_to_add'])}\n\n"

    report += f"---\n\n## 💬 Interview Preparation\n"
    preps = advice.get("interview_prep", [])
    if isinstance(preps, list):
        for idx, item in enumerate(preps, 1):
            if isinstance(item, dict):
                report += f"### Q{idx}: {item.get('question', '')}\n"
                if item.get("question_type"):
                    report += f"**Type:** {item['question_type']} | **Difficulty:** {item.get('difficulty', 'N/A')}\n\n"
                report += f"**Intent:** {item.get('intent', '')}\n\n**Key Talking Points:**\n"
                for pt in item.get("key_talking_points", []):
                    report += f"- {pt}\n"
                report += f"\n**Model Answer:**\n{item.get('model_answer', item.get('star_framework_answer', ''))}\n\n"
                if item.get("follow_up_questions"):
                    report += f"**Follow-up Questions:**\n"
                    for fq in item["follow_up_questions"]:
                        report += f"- {fq}\n"
                if item.get("red_flags"):
                    report += f"\n**Red Flags to Avoid:**\n"
                    for rf in item["red_flags"]:
                        report += f"- {rf}\n"
                report += f"\n"

    resources_top = advice.get("learning_resources", [])
    if resources_top:
        report += f"---\n\n## 📚 Learning Resources\n"
        for skill_block in resources_top:
            if isinstance(skill_block, dict):
                report += f"### {skill_block.get('skill', '')}\n"
                for res in skill_block.get("resources", []):
                    report += f"- [{res.get('title', '')}]({res.get('url', '')}) ({res.get('type', '')})\n"
                report += f"\n"

    tips = advice.get("job_search_tips", [])
    if tips:
        report += f"---\n\n## 💼 Job Search Tips\n"
        for tip in tips:
            report += f"- {tip}\n"

    return report


# =================================================================
# SESSION STATE
# =================================================================
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "welcome"
if "roadmap_tracker" not in st.session_state:
    st.session_state["roadmap_tracker"] = {}
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# =================================================================
# SCREEN 1: WELCOME
# =================================================================
if st.session_state["view_mode"] == "welcome":
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-badge"><span class="dot"></span>AI-powered career intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Skill<span class="accent">Bridge</span> AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Analyze your resume against any job. Discover your skill gaps. Get a personalized roadmap. Everything you need to become job-ready — powered by AI.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    _, col_btn2, _ = st.columns([2, 1.2, 2])
    with col_btn2:
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            st.session_state["view_mode"] = "workspace"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Smart Skill Extraction</div>
            <div class="feature-desc">Extracts skills from PDF resumes and job postings using intelligent pattern matching for explainable evaluation scores.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Multi-Phase Roadmaps</div>
            <div class="feature-desc">Step-by-step learning schedules with capstone projects, focus skills, curated resources, and weekly action steps targeting your gaps.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
        <div class="feature-card">
            <div class="feature-icon">💼</div>
            <div class="feature-title">Resume & Interview Prep</div>
            <div class="feature-desc">Transforms bullets into quantifiable STAR achievements and prepares you with scenario-based technical interview frameworks.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


# =================================================================
# SCREEN 2: WORKSPACE
# =================================================================
else:
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.markdown('<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.7rem;font-weight:600;color:#EEF1F6;letter-spacing:-0.02em;">⚡ SkillBridge Workspace</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#5C6679;font-size:0.92rem;margin-top:2px;">Evaluate job readiness and generate your personalized AI career strategy</div>', unsafe_allow_html=True)
    with top_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Home", use_container_width=True):
            st.session_state["view_mode"] = "welcome"
            st.rerun()

    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)

    section_header("📥", "Candidate Inputs", "Upload your resume and paste the target job description")

    input_col1, input_col2 = st.columns(2)

    with input_col1:
        st.markdown('<div style="font-weight:600;color:#93A0B4;margin-bottom:0.5rem;font-size:0.92rem;">📄 Resume</div>', unsafe_allow_html=True)
        upload_option = st.radio("Resume Format:", ["Upload PDF Resume", "Manual Skill List"], horizontal=True, label_visibility="collapsed")

        resume_skills_input = ""
        if upload_option == "Upload PDF Resume":
            uploaded_file = st.file_uploader("Upload Resume (.pdf)", type=["pdf"])
            if uploaded_file is not None:
                try:
                    with pdfplumber.open(uploaded_file) as pdf:
                        extracted_text = " ".join([page.extract_text() or "" for page in pdf.pages if page.extract_text()])
                    st.success("✅ Resume text extracted successfully")
                    resume_skills_input = extracted_text
                except Exception as e:
                    st.error(f"Error parsing PDF: {e}")
        else:
            resume_skills_input = st.text_area(
                "Enter skills separated by commas:",
                value="FastAPI, React, Git, SQL, Python, Docker",
                height=140,
                label_visibility="collapsed",
            )

    with input_col2:
        st.markdown('<div style="font-weight:600;color:#93A0B4;margin-bottom:0.5rem;font-size:0.92rem;">🎯 Target job</div>', unsafe_allow_html=True)
        job_source_option = st.radio("Source:", ["Manual Text Input", "Fetch from URL"], horizontal=True, label_visibility="collapsed")

        job_input = ""
        if job_source_option == "Fetch from URL":
            job_url = st.text_input("Job URL:", placeholder="https://example.com/job-posting")
            if st.button("🌐 Fetch Job Text", use_container_width=True):
                if job_url:
                    with st.spinner("Scraping..."):
                        try:
                            fetched_text = fetch_job_description_from_url(job_url)
                            st.session_state["scraped_job_text"] = fetched_text
                            st.success("✅ Job description fetched")
                        except Exception as err:
                            st.error(f"Scraper error: {err}")
            job_input = st.text_area(
                "Extracted text:",
                value=st.session_state.get("scraped_job_text", ""),
                height=140,
                label_visibility="collapsed",
            )
        else:
            job_input = st.text_area(
                "Job requirements:",
                value="FastAPI, REST API, Docker, AWS, Kubernetes, PostgreSQL",
                height=210,
                label_visibility="collapsed",
            )

    target_role = st.text_input("🎯 Target Role Name:", value="Backend Engineer")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Analyze Readiness & Generate Career Strategy", type="primary", use_container_width=True):
        resume_skills = extract_unique_skills(resume_skills_input)
        job_reqs = extract_unique_skills(job_input)

        if not resume_skills or not job_reqs:
            st.error("Please supply both resume details and job requirements.")
        else:
            with st.spinner("🧠 Analyzing skills and generating AI strategy... (this takes ~30 seconds)"):
                payload = {
                    "resume_skills": resume_skills,
                    "job_requirements": job_reqs,
                    "target_role": target_role,
                }
                try:
                    res = requests.post(API_URL, json=payload, timeout=120)
                    if res.status_code == 200:
                        st.session_state["analysis_result"] = res.json()
                        st.session_state["target_role"] = target_role
                        st.session_state["chat_history"] = []  # reset chat for new analysis
                    else:
                        st.error(f"Backend API error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend API: {str(e)}")

    # ---------------- RESULTS ----------------
    if st.session_state.get("analysis_result"):
        data = st.session_state["analysis_result"]
        active_role = st.session_state.get("target_role", target_role)
        score = data.get("readiness_score", 0.0)
        advice = data.get("career_advice", {})
        breakdown = data.get("breakdown", {})

        st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)

        # ---- SCORE HERO ----
        band_label, band_class = get_score_band(score)
        st.markdown(
            f"""
            <div class="score-hero">
                <div class="score-hero-label">JOB READINESS SCORE</div>
                <div class="score-hero-value">{score:.1f}%</div>
                <div class="score-hero-band">{band_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---- METRIC CARDS ----
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Matched Skills</div><div class="metric-value metric-value-green">{len(breakdown.get("matched", []))}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Partial Matches</div><div class="metric-value metric-value-amber">{len(breakdown.get("partial", []))}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Missing Gaps</div><div class="metric-value metric-value-red">{len(breakdown.get("missing", []))}</div></div>', unsafe_allow_html=True)
        with m4:
            total_req = len(breakdown.get("matched", [])) + len(breakdown.get("partial", [])) + len(breakdown.get("missing", []))
            st.markdown(f'<div class="metric-card"><div class="metric-label">Total Required</div><div class="metric-value metric-value-gold">{total_req}</div></div>', unsafe_allow_html=True)

        # ---- EXECUTIVE SUMMARY ----
        if advice.get("executive_summary"):
            st.markdown(
                f"""
                <div style="background: #141822; border: 1px solid rgba(148,163,184,0.10); border-radius: 16px; padding: 1.4rem 1.6rem; margin: 1.5rem 0; border-left: 3px solid #6366F1;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:0.85rem;font-weight:600;color:#93A0B4;margin-bottom:0.6rem;">💡 Executive summary</div>
                    <div style="color:#D6DCE8;font-size:0.98rem;line-height:1.7;">{advice['executive_summary']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---- DOWNLOAD ----
        report_md = generate_markdown_report(active_role, score, breakdown, advice)
        st.download_button(
            label="📥 Download Complete Strategy Report (.md)",
            data=report_md,
            file_name=f"skillbridge_strategy_{active_role.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- TABS ----
        t_matrix, t_roadmap, t_resume, t_interview, t_resources, t_tips, t_chat = st.tabs([
            "📊 Skill Matrix",
            "🗺️ Roadmap",
            "✍️ Resume Optimization",
            "💬 Interview Prep",
            "📚 Learning Resources",
            "💼 Job Tips",
            "🤖 Career Chat",
        ])

        # ============ TAB 1: SKILL MATRIX ============
        with t_matrix:
            section_header("📊", "Categorized Skill Alignment", "How your skills compare to the job requirements")
            b1, b2, b3 = st.columns(3)
            with b1:
                st.markdown(f'<div style="color:#34D399;font-weight:600;font-size:0.95rem;margin-bottom:0.8rem;">✅ Matched ({len(breakdown.get("matched", []))})</div>', unsafe_allow_html=True)
                for item in breakdown.get("matched", []):
                    st.markdown(f'<span class="badge-matched">✓ {item.get("skill", "")}</span>', unsafe_allow_html=True)
            with b2:
                st.markdown(f'<div style="color:#F5A524;font-weight:600;font-size:0.95rem;margin-bottom:0.8rem;">⚡ Partial ({len(breakdown.get("partial", []))})</div>', unsafe_allow_html=True)
                for item in breakdown.get("partial", []):
                    st.markdown(f'<span class="badge-partial">~ {item.get("skill", "")} · {item.get("score", "N/A")}</span>', unsafe_allow_html=True)
            with b3:
                st.markdown(f'<div style="color:#F1637A;font-weight:600;font-size:0.95rem;margin-bottom:0.8rem;">❌ Missing ({len(breakdown.get("missing", []))})</div>', unsafe_allow_html=True)
                for item in breakdown.get("missing", []):
                    st.markdown(f'<span class="badge-missing">✗ {item.get("skill", "")}</span>', unsafe_allow_html=True)

        # ============ TAB 2: ROADMAP ============
        with t_roadmap:
            section_header("🗺️", "Personalized Learning Roadmap", "Step-by-step path with projects and resources")
            phases = advice.get("roadmap_phases", [])

            total_tasks = 0
            completed_tasks = 0

            if isinstance(phases, list):
                for p_idx, phase in enumerate(phases, 1):
                    if isinstance(phase, dict):
                        for s_idx, _ in enumerate(phase.get("action_steps", []), 1):
                            total_tasks += 1
                            key = f"task_{p_idx}_{s_idx}"
                            if st.session_state["roadmap_tracker"].get(key, False):
                                completed_tasks += 1

                if total_tasks > 0:
                    completion_pct = (completed_tasks / total_tasks) * 100
                    st.markdown(
                        f'<div style="background: #141822; border: 1px solid rgba(148,163,184,0.10); border-radius: 12px; padding: 0.9rem 1.3rem; margin-bottom: 1.2rem; color:#D6DCE8;"><b>📊 Progress:</b> {completed_tasks} of {total_tasks} steps completed ({completion_pct:.0f}%)</div>',
                        unsafe_allow_html=True,
                    )
                    st.progress(completed_tasks / total_tasks)
                    st.markdown("<br>", unsafe_allow_html=True)

                for idx, phase in enumerate(phases, 1):
                    if isinstance(phase, dict):
                        with st.expander(f"📍 {phase.get('phase_title', f'Phase {idx}')}", expanded=(idx == 1)):
                            meta_col1, meta_col2 = st.columns(2)
                            with meta_col1:
                                if phase.get("duration"):
                                    st.markdown(f"⏱️ **Duration:** `{phase['duration']}`")
                            with meta_col2:
                                if phase.get("prerequisites"):
                                    st.markdown(f"📋 **Prerequisites:** {phase['prerequisites']}")

                            st.markdown(f"**🎯 Focus Skills:** `{', '.join(phase.get('focus_skills', []))}`")
                            st.markdown(f"**📝 Objective:** {phase.get('objective', '')}")

                            st.markdown("##### 📌 Action Steps (check off as you complete):")
                            for step_idx, step in enumerate(phase.get("action_steps", []), 1):
                                task_key = f"task_{idx}_{step_idx}"
                                current_val = st.session_state["roadmap_tracker"].get(task_key, False)
                                is_checked = st.checkbox(step, value=current_val, key=task_key)
                                st.session_state["roadmap_tracker"][task_key] = is_checked

                            resources = phase.get("learning_resources", [])
                            if resources:
                                st.markdown("##### 📚 Learning Resources:")
                                for res in resources:
                                    if isinstance(res, dict):
                                        title = res.get("title", "")
                                        url = res.get("url", "")
                                        rtype = res.get("type", "")
                                        emoji = {"docs": "📄", "video": "🎥", "course": "🎓"}.get(rtype, "🔗")
                                        st.markdown(f"{emoji} [{title}]({url})")

                            capstone = phase.get("capstone_project", {})
                            if isinstance(capstone, dict) and capstone:
                                st.markdown("##### 🛠️ Capstone Project:")
                                techs = capstone.get("technologies", [])
                                tech_str = f"\n\n**Technologies:** `{', '.join(techs)}`" if techs else ""
                                st.info(
                                    f"**{capstone.get('title', 'Project')}**\n\n{capstone.get('description', '')}"
                                    f"{tech_str}\n\n**📦 Deliverable:** `{capstone.get('deliverable', '')}`"
                                )

        # ============ TAB 3: RESUME OPTIMIZATION ============
        with t_resume:
            section_header("✍️", "Resume Optimization", "Before/after rewrites to boost ATS ranking")
            opts = advice.get("resume_optimizations", [])
            if isinstance(opts, list):
                for item in opts:
                    if isinstance(item, dict):
                        priority = item.get("priority", "")
                        priority_badge = ""
                        if priority == "High":
                            priority_badge = '<span class="priority-high">HIGH PRIORITY</span>'
                        elif priority == "Medium":
                            priority_badge = '<span class="priority-medium">MEDIUM</span>'

                        st.markdown(
                            f'<div class="resume-card"><div class="resume-category">🏷️ {item.get("category", "Resume Bullet")} {priority_badge}</div></div>',
                            unsafe_allow_html=True,
                        )

                        r1, r2 = st.columns(2)
                        with r1:
                            st.markdown(f'<div class="before-box"><b>❌ BEFORE</b><br><br>{item.get("before", "")}</div>', unsafe_allow_html=True)
                        with r2:
                            st.markdown(f'<div class="after-box"><b>✅ AFTER</b><br><br>{item.get("after", "")}</div>', unsafe_allow_html=True)

                        why = item.get("why", item.get("strategy", ""))
                        if why:
                            st.caption(f"💡 **Why:** {why}")

                        if item.get("keywords_to_add"):
                            kws = " ".join([f"`{k}`" for k in item["keywords_to_add"]])
                            st.markdown(f"**🔑 ATS Keywords to Add:** {kws}")

                        st.markdown("<br>", unsafe_allow_html=True)

        # ============ TAB 4: INTERVIEW PREP ============
        with t_interview:
            section_header("💬", "Interview Preparation", "Technical, behavioral, and system design questions")
            preps = advice.get("interview_prep", [])
            if isinstance(preps, list):
                for idx, item in enumerate(preps, 1):
                    if isinstance(item, dict):
                        q_type = item.get("question_type", "Technical")
                        difficulty = item.get("difficulty", "")

                        if "Tech" in q_type:
                            type_badge = '<span class="q-type-tech">TECHNICAL</span>'
                        elif "Behav" in q_type:
                            type_badge = '<span class="q-type-behav">BEHAVIORAL</span>'
                        elif "Design" in q_type:
                            type_badge = '<span class="q-type-design">SYSTEM DESIGN</span>'
                        else:
                            type_badge = f'<span class="q-type-tech">{q_type.upper()}</span>'

                        diff_badge = f'<span class="difficulty-badge">{difficulty}</span>' if difficulty else ""

                        st.markdown(
                            f'<div class="interview-card">{type_badge} {diff_badge}<div class="question-text">Q{idx}. {item.get("question", "")}</div></div>',
                            unsafe_allow_html=True,
                        )

                        st.caption(f"🎯 **Interviewer Intent:** {item.get('intent', '')}")

                        st.markdown("**🎯 Key Concepts to Emphasize:**")
                        for pt in item.get("key_talking_points", []):
                            st.markdown(f"• `{pt}`")

                        model_ans = item.get("model_answer", item.get("star_framework_answer", ""))
                        with st.expander("👁️ Reveal Strategic Model Answer"):
                            st.write(model_ans)

                        if item.get("follow_up_questions"):
                            with st.expander("🔁 Likely Follow-up Questions"):
                                for fq in item["follow_up_questions"]:
                                    st.markdown(f"• {fq}")

                        if item.get("red_flags"):
                            with st.expander("🚩 Red Flags to Avoid"):
                                for rf in item["red_flags"]:
                                    st.markdown(f"• {rf}")

                        st.markdown("<br>", unsafe_allow_html=True)

        # ============ TAB 5: LEARNING RESOURCES ============
        with t_resources:
            section_header("📚", "Curated Learning Resources", "Hand-picked tutorials, docs, and courses")
            resources_top = advice.get("learning_resources", [])

            if resources_top:
                for skill_block in resources_top:
                    if isinstance(skill_block, dict):
                        st.markdown(f"### 🎯 {skill_block.get('skill', 'Skill')}")
                        for res in skill_block.get("resources", []):
                            if isinstance(res, dict):
                                title = res.get("title", "")
                                url = res.get("url", "")
                                rtype = res.get("type", "")
                                emoji = {"free": "🆓", "paid": "💰"}.get(rtype, "🔗")
                                st.markdown(
                                    f'<div class="resource-card">{emoji} <a href="{url}" target="_blank" class="resource-link">{title}</a> <span class="resource-type">({rtype})</span></div>',
                                    unsafe_allow_html=True,
                                )
                        st.markdown("")
            else:
                st.info("No learning resources generated.")

        # ============ TAB 6: JOB TIPS ============
        with t_tips:
            section_header("💼", "Job Search Strategy", "Practical tips to maximize your applications")
            tips = advice.get("job_search_tips", [])
            if tips:
                for idx, tip in enumerate(tips, 1):
                    st.markdown(f'<div class="tip-card">💡 <b>Tip {idx}:</b> {tip}</div>', unsafe_allow_html=True)
            else:
                st.info("No tips generated.")

        # ============ TAB 7: CAREER CHAT ============
        with t_chat:
            section_header("🤖", "CareerPilot AI Chat", "Ask anything about your career gaps, priorities, or next steps")

            # Suggestion buttons
            st.markdown('<div style="color:#93A0B4;font-size:0.85rem;font-weight:500;margin-bottom:0.6rem;">💡 Suggested questions</div>', unsafe_allow_html=True)
            # Suggestion buttons — directly send the question
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                if st.button("Why am I at this score?", use_container_width=True, key="q1"):
                    st.session_state["pending_question"] = "Why am I only at this readiness score?"
                    st.rerun()
            with sc2:
                if st.button("What should I learn first?", use_container_width=True, key="q2"):
                    st.session_state["pending_question"] = "What should I learn first?"
                    st.rerun()
            with sc3:
                if st.button("Can I apply now?", use_container_width=True, key="q3"):
                    st.session_state["pending_question"] = "Can I apply for this role now?"
                    st.rerun()
            with sc4:
                if st.button("How long will it take?", use_container_width=True, key="q4"):
                    st.session_state["pending_question"] = "How long will it take me to become job-ready?"
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # Display chat history
            for msg in st.session_state["chat_history"]:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div style="background:rgba(99,102,241,0.10); border:1px solid rgba(99,102,241,0.28); border-radius:12px; padding:0.9rem 1.2rem; margin:0.5rem 0 0.5rem 15%; color:#D6DCE8; font-size:0.95rem;">👤 <b>You:</b> {msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="background:#141822; border:1px solid rgba(148,163,184,0.10); border-left:3px solid #2DD4BF; border-radius:12px; padding:0.9rem 1.2rem; margin:0.5rem 15% 0.5rem 0; color:#D6DCE8; font-size:0.95rem; line-height:1.6;">🤖 <b>CareerPilot:</b> {msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Chat input row
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                user_question = st.text_input(
                    "Ask a question...",
                    placeholder="e.g., What should I learn first?",
                    label_visibility="collapsed",
                    key="chat_text_input",
                )
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                send = st.button("Send", use_container_width=True, type="primary", key="chat_send_btn")

            # Handle suggestion click OR Send button click
            pending = st.session_state.pop("pending_question", None)
            final_question = pending if pending else (user_question.strip() if send and user_question else "")

            if final_question:
                # Add user message to history
                st.session_state["chat_history"].append({
                    "role": "user",
                    "content": user_question.strip(),
                })

                # Build user profile
                user_profile = {
                    "score": score,
                    "matched": [m.get("skill", "") for m in breakdown.get("matched", [])],
                    "partial": [p.get("skill", "") for p in breakdown.get("partial", [])],
                    "missing": [k.get("skill", "") for k in breakdown.get("missing", [])],
                    "target_role": active_role,
                }

                # Call backend chat
                with st.spinner("CareerPilot is thinking..."):
                    try:
                        chat_res = requests.post(
                            CHAT_API_URL,
                            json={
                                "question": final_question,
                                "user_profile": user_profile,
                                "history": st.session_state["chat_history"][:-1],
                            },
                            timeout=45,
                        )
                        if chat_res.status_code == 200:
                            answer = chat_res.json().get("answer", "")
                            st.session_state["chat_history"].append({
                                "role": "assistant",
                                "content": answer,
                            })
                        else:
                            st.session_state["chat_history"].append({
                                "role": "assistant",
                                "content": f"⚠️ Error: {chat_res.status_code}",
                            })
                    except Exception as e:
                        st.session_state["chat_history"].append({
                            "role": "assistant",
                            "content": f"⚠️ Could not reach the chatbot: {str(e)[:80]}",
                        })

                st.rerun()

            # Clear chat
            if st.session_state["chat_history"]:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Clear Chat History", use_container_width=False):
                    st.session_state["chat_history"] = []
                    st.rerun()