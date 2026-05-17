# ============================================================
# FILE: ui/app.py
# PURPOSE: Full Streamlit UI for CLAIMA
#          — Upload documents, process them, view results,
#            check queue, and chat with the CLAIMA assistant
# LIBRARY USED:
#   - streamlit       → builds the entire web UI using Python
#   - sys, os         → helps Python find our agents folder
#   - tempfile        → saves uploaded file temporarily to disk
# ============================================================

import streamlit as st
import sys
import os
import tempfile
import json
from datetime import datetime

# ----------------------------------------------------------
# PATH FIX
# Since app.py is inside the 'ui/' folder, we need to tell
# Python where to find our agents and other files.
# os.path.dirname gets the parent folder (CLAIMA root)
# sys.path.insert adds it to Python's search path
# ----------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from main    import process_submission
from chatbot import chat

# ----------------------------------------------------------
# PAGE CONFIGURATION — Must be the FIRST streamlit command
# ----------------------------------------------------------
st.set_page_config(
    page_title="CLAIMA — Insurance AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# CUSTOM CSS — Unique dark professional design
# Deep navy + electric teal + clean typography
# ----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ---- GLOBAL ---- */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #080f1e;
    color: #e8edf5;
}

/* ---- HIDE DEFAULT STREAMLIT ELEMENTS ---- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---- MAIN BACKGROUND ---- */
.stApp {
    background: linear-gradient(135deg, #080f1e 0%, #0d1a2e 50%, #091622 100%);
    min-height: 100vh;
}

/* ---- SIDEBAR ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #061020 100%);
    border-right: 1px solid #1a3a5c;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #00d4aa;
    font-family: 'Syne', sans-serif;
}

/* ---- HEADER BANNER ---- */
.claima-header {
    background: linear-gradient(90deg, #001f3f 0%, #003366 50%, #001f3f 100%);
    border: 1px solid #00d4aa33;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.claima-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 70% 50%, #00d4aa11 0%, transparent 60%);
    pointer-events: none;
}
.claima-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #00d4aa, #4db8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}
.claima-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: #7a9bb5;
    margin-top: 8px;
    letter-spacing: 0.5px;
}
.claima-badge {
    display: inline-block;
    background: #00d4aa22;
    border: 1px solid #00d4aa55;
    color: #00d4aa;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
}

/* ---- METRIC CARDS ---- */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.metric-card {
    background: linear-gradient(135deg, #0d1f35 0%, #0a1628 100%);
    border: 1px solid #1a3a5c;
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease;
}
.metric-card:hover { border-color: #00d4aa55; }
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: #00d4aa;
    border-radius: 3px 0 0 3px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00d4aa;
    line-height: 1;
}
.metric-label {
    font-size: 0.8rem;
    color: #7a9bb5;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 6px;
}

/* ---- SECTION HEADERS ---- */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8edf5;
    border-left: 3px solid #00d4aa;
    padding-left: 14px;
    margin: 28px 0 18px 0;
    letter-spacing: -0.3px;
}

/* ---- UPLOAD ZONE ---- */
.upload-zone {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f35 100%);
    border: 2px dashed #1a3a5c;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    transition: border-color 0.3s;
    margin-bottom: 20px;
}
.upload-zone:hover { border-color: #00d4aa55; }

/* ---- RESULT CARDS ---- */
.result-card {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f35 100%);
    border: 1px solid #1a3a5c;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
}
.result-card.success { border-left: 4px solid #00d4aa; }
.result-card.warning { border-left: 4px solid #f59e0b; }
.result-card.error   { border-left: 4px solid #ef4444; }

/* ---- STATUS PILLS ---- */
.pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.pill-green  { background: #00d4aa22; color: #00d4aa; border: 1px solid #00d4aa44; }
.pill-yellow { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
.pill-red    { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
.pill-blue   { background: #4db8ff22; color: #4db8ff; border: 1px solid #4db8ff44; }

/* ---- DATA TABLE ---- */
.data-table { width: 100%; border-collapse: collapse; }
.data-table tr { border-bottom: 1px solid #1a3a5c; }
.data-table tr:last-child { border-bottom: none; }
.data-table td {
    padding: 10px 14px;
    font-size: 0.88rem;
    color: #c8d8e8;
    vertical-align: top;
}
.data-table td:first-child {
    color: #7a9bb5;
    font-weight: 500;
    width: 40%;
    white-space: nowrap;
}
.data-table td:last-child { color: #e8edf5; }

/* ---- CHAT BUBBLE ---- */
.chat-user {
    background: linear-gradient(135deg, #003366 0%, #004080 100%);
    border: 1px solid #1a5276;
    border-radius: 14px 14px 4px 14px;
    padding: 12px 18px;
    margin: 8px 0 8px 60px;
    font-size: 0.9rem;
    color: #e8edf5;
}
.chat-bot {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f35 100%);
    border: 1px solid #1a3a5c;
    border-left: 3px solid #00d4aa;
    border-radius: 14px 14px 14px 4px;
    padding: 12px 18px;
    margin: 8px 60px 8px 0;
    font-size: 0.9rem;
    color: #c8d8e8;
    line-height: 1.6;
}
.chat-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.chat-label.user { color: #4db8ff; text-align: right; }
.chat-label.bot  { color: #00d4aa; }

/* ---- STREAMLIT BUTTONS ---- */
.stButton > button {
    background: linear-gradient(90deg, #00d4aa 0%, #00b894 100%);
    color: #080f1e;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.5px;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* ---- FILE UPLOADER ---- */
[data-testid="stFileUploader"] {
    background: #0a1628;
    border: 1px solid #1a3a5c;
    border-radius: 12px;
    padding: 12px;
}

/* ---- TEXT INPUT ---- */
.stTextInput > div > div > input {
    background: #0a1628 !important;
    border: 1px solid #1a3a5c !important;
    border-radius: 8px !important;
    color: #e8edf5 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00d4aa !important;
    box-shadow: 0 0 0 2px #00d4aa22 !important;
}

/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
    border-bottom: 1px solid #1a3a5c;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7a9bb5;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #0a1628 !important;
    color: #00d4aa !important;
    border-bottom: 2px solid #00d4aa !important;
}

/* ---- SPINNER ---- */
.stSpinner > div { border-top-color: #00d4aa !important; }

/* ---- SUCCESS / ERROR MESSAGES ---- */
.stSuccess {
    background: #00d4aa11 !important;
    border: 1px solid #00d4aa33 !important;
    color: #00d4aa !important;
    border-radius: 8px !important;
}
.stError {
    background: #ef444411 !important;
    border: 1px solid #ef444433 !important;
    border-radius: 8px !important;
}
.stWarning {
    background: #f59e0b11 !important;
    border: 1px solid #f59e0b33 !important;
    border-radius: 8px !important;
}

/* ---- QUEUE CARD ---- */
.queue-card {
    background: #0a1628;
    border: 1px solid #1a3a5c;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.queue-icon { font-size: 1.4rem; }
.queue-info { flex: 1; }
.queue-title { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.95rem; }
.queue-count { font-size: 0.8rem; color: #7a9bb5; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------

def load_submissions():
    """Load all submissions from data/submissions.json"""
    path = os.path.join(ROOT_DIR, "data", "submissions.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
    except Exception:
        pass
    return []


def load_queues():
    """Load queue data from data/queues.json"""
    path = os.path.join(ROOT_DIR, "data", "queues.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
    except Exception:
        pass
    return {}


def get_priority_pill(priority):
    """Return colored HTML pill for priority level"""
    colors = {"High": "pill-red", "Medium": "pill-yellow", "Low": "pill-green"}
    return f'<span class="pill {colors.get(priority, "pill-blue")}">{priority}</span>'


def get_validation_pill(status):
    """Return colored HTML pill for validation status"""
    if status == "passed":
        return '<span class="pill pill-green">✓ Complete</span>'
    return '<span class="pill pill-yellow">⚠ Incomplete</span>'


# ----------------------------------------------------------
# INITIALIZE SESSION STATE
# Session state in Streamlit stores data between reruns
# Without this, variables reset every time user clicks anything
# ----------------------------------------------------------
if "chat_history"      not in st.session_state:
    st.session_state.chat_history = []
if "last_result"       not in st.session_state:
    st.session_state.last_result = None
if "processing"        not in st.session_state:
    st.session_state.processing = False


# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 10px 0;">
        <div style="font-family: 'Syne', sans-serif; font-size: 1.5rem;
                    font-weight: 800; color: #00d4aa; letter-spacing:-0.5px;">
            🛡️ CLAIMA
        </div>
        <div style="font-size: 0.75rem; color: #7a9bb5; margin-top: 4px;
                    text-transform: uppercase; letter-spacing: 1.5px;">
            AI Insurance Platform
        </div>
    </div>
    <hr style="border-color: #1a3a5c; margin: 12px 0;">
    """, unsafe_allow_html=True)

    # Live Stats in sidebar
    submissions = load_submissions()
    queues      = load_queues()

    total    = len(submissions)
    complete = sum(1 for s in submissions if s.get("is_complete"))
    high_pri = sum(1 for s in submissions if s.get("priority") == "High")

    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="font-size: 0.7rem; color: #7a9bb5; text-transform: uppercase;
                    letter-spacing: 1px; margin-bottom: 12px;">Live Statistics</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 0.85rem; color: #c8d8e8;">Total Processed</span>
            <span style="font-family: 'Syne', sans-serif; font-weight: 700;
                         color: #00d4aa; font-size: 1rem;">{total}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-size: 0.85rem; color: #c8d8e8;">Complete</span>
            <span style="font-family: 'Syne', sans-serif; font-weight: 700;
                         color: #4db8ff; font-size: 1rem;">{complete}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="font-size: 0.85rem; color: #c8d8e8;">High Priority</span>
            <span style="font-family: 'Syne', sans-serif; font-weight: 700;
                         color: #ef4444; font-size: 1rem;">{high_pri}</span>
        </div>
    </div>
    <hr style="border-color: #1a3a5c; margin: 12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 0.7rem; color: #7a9bb5; text-transform: uppercase;
                letter-spacing: 1px; margin-bottom: 12px;">Supported Lines</div>
    """, unsafe_allow_html=True)

    for line, icon in [("Commercial Auto", "🚛"), ("Property", "🏢"), ("General Liability", "⚖️")]:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0;
                    border-bottom: 1px solid #1a3a5c11; font-size: 0.85rem; color: #c8d8e8;">
            <span>{icon}</span><span>{line}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="border-color: #1a3a5c; margin: 16px 0;">
    <div style="font-size: 0.72rem; color: #3a5a7c; text-align: center;">
        Built with Python · Gemini AI · Streamlit<br>
        <span style="color: #00d4aa;">CLAIMA v1.0</span>
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.markdown("""
<div class="claima-header">
    <div class="claima-badge">AI-Powered · Multi-Agent · Real-Time</div>
    <div class="claima-title">CLAIMA</div>
    <div class="claima-subtitle">
        Cognitive Line Agent for Insurance Management & Automation
    </div>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# METRICS ROW
# ----------------------------------------------------------
submissions = load_submissions()
total    = len(submissions)
complete = sum(1 for s in submissions if s.get("is_complete"))
auto_c   = sum(1 for s in submissions if s.get("line_of_business") == "Commercial Auto")
prop_c   = sum(1 for s in submissions if s.get("line_of_business") == "Property")
liab_c   = sum(1 for s in submissions if s.get("line_of_business") == "General Liability")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total}</div>
        <div class="metric-label">Total Submissions</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #4db8ff;">
        <div class="metric-value" style="color:#4db8ff;">{complete}</div>
        <div class="metric-label">Complete</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #a78bfa;">
        <div class="metric-value" style="color:#a78bfa;">{auto_c}</div>
        <div class="metric-label">Auto Submissions</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 3px solid #f59e0b;">
        <div class="metric-value" style="color:#f59e0b;">{prop_c + liab_c}</div>
        <div class="metric-label">Property + Liability</div>
    </div>""", unsafe_allow_html=True)


# ----------------------------------------------------------
# MAIN TABS
# ----------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📤  Upload & Process",
    "📋  All Submissions",
    "🔀  Queues",
    "💬  CLAIMA Assistant"
])


# ══════════════════════════════════════════════════════════
# TAB 1 — UPLOAD & PROCESS
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">Upload Insurance Document</div>',
                unsafe_allow_html=True)

    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("""
        <div style="font-size:0.85rem; color:#7a9bb5; margin-bottom:16px; line-height:1.6;">
        Upload a PDF insurance document. CLAIMA will automatically extract all fields,
        validate completeness, classify the line of business, and route it to the
        correct underwriting queue.
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your PDF here",
            type=["pdf"],
            help="Supported: Commercial Auto, Property, General Liability"
        )

        if uploaded_file:
            st.markdown(f"""
            <div style="background:#0a1628; border:1px solid #1a3a5c; border-radius:8px;
                        padding:12px 16px; margin: 12px 0; font-size:0.85rem;">
                <div style="color:#7a9bb5; font-size:0.72rem; text-transform:uppercase;
                             letter-spacing:1px; margin-bottom:4px;">Selected File</div>
                <div style="color:#e8edf5; font-weight:500;">📄 {uploaded_file.name}</div>
                <div style="color:#7a9bb5; margin-top:4px;">
                    Size: {uploaded_file.size / 1024:.1f} KB
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Process with CLAIMA"):
                # Save uploaded file to a temporary location on disk
                # We do this because our agents need a file path, not bytes
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                with st.spinner("Running AI agents... This may take 10–20 seconds"):
                    result = process_submission(tmp_path)

                # Clean up temp file
                os.unlink(tmp_path)

                # Store result in session state so we can display it
                st.session_state.last_result = result

                if result["status"] == "success":
                    st.success(f"✅ Submission processed! ID: **{result['submission_id']}**")
                else:
                    st.error(f"❌ Processing failed at stage: {result.get('stage', 'unknown')}")

    with col_result:
        if st.session_state.last_result:
            result = st.session_state.last_result

            if result["status"] == "success":
                val = result["validation"]
                data = result["extracted_data"]

                # Submission ID and priority
                st.markdown(f"**{result['submission_id']}** — Priority: `{result['priority']}`")
                st.caption("Processed just now")
                st.divider()

                # Core summary fields using Streamlit columns
                r1c1, r1c2 = st.columns(2)
                with r1c1:
                    st.markdown("**Applicant Name**")
                    st.write(data.get("applicant_name", "N/A"))
                with r1c2:
                    st.markdown("**Business Name**")
                    st.write(data.get("business_name", "N/A"))

                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    st.markdown("**Line of Business**")
                    st.write(result["line_of_business"])
                with r2c2:
                    st.markdown("**Policy Type**")
                    st.write(data.get("policy_type", "N/A"))

                r3c1, r3c2 = st.columns(2)
                with r3c1:
                    st.markdown("**Coverage Amount**")
                    st.write(data.get("coverage_amount", "N/A"))
                with r3c2:
                    st.markdown("**Assigned Team**")
                    st.write(result["routed_to"])

                r4c1, r4c2 = st.columns(2)
                with r4c1:
                    st.markdown("**Effective Date**")
                    st.write(data.get("effective_date", "N/A"))
                with r4c2:
                    st.markdown("**Expiration Date**")
                    st.write(data.get("expiration_date", "N/A"))

                r5c1, r5c2 = st.columns(2)
                with r5c1:
                    st.markdown("**Contact Email**")
                    st.write(data.get("contact_email", "N/A"))
                with r5c2:
                    st.markdown("**Contact Phone**")
                    st.write(data.get("contact_phone", "N/A"))

                r6c1, r6c2 = st.columns(2)
                with r6c1:
                    st.markdown("**Agent Name**")
                    st.write(data.get("agent_name", "N/A"))
                with r6c2:
                    st.markdown("**Validation Status**")
                    if val["is_complete"]:
                        st.success("✅ Complete")
                    else:
                        st.warning("⚠ Incomplete")

                st.divider()

                # Missing fields warning
                if val.get("missing_fields"):
                    st.warning(f"⚠ Missing Fields: {', '.join(val['missing_fields'])}")

                # All extracted fields (expandable)
                with st.expander("View All Extracted Fields"):
                    for key, value in data.items():
                        if value and value != "null":
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.markdown(f"**{key.replace('_', ' ').title()}**")
                            with c2:
                                st.write(str(value))
                            st.divider()
        else:
            st.markdown("""
            <div style="background:#0a1628; border:1px dashed #1a3a5c; border-radius:12px;
                        padding:60px 40px; text-align:center; margin-top:10px;">
                <div style="font-size:2.5rem; margin-bottom:12px;">📄</div>
                <div style="font-family:'Syne',sans-serif; color:#3a5a7c; font-size:1rem;">
                    Upload a document to see results here
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 2 — ALL SUBMISSIONS
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">All Processed Submissions</div>',
                unsafe_allow_html=True)

    submissions = load_submissions()

    if not submissions:
        st.markdown("""
        <div style="text-align:center; padding:60px; color:#3a5a7c;">
            <div style="font-size:2rem;">📭</div>
            <div style="margin-top:10px;">No submissions processed yet.</div>
            <div style="font-size:0.85rem; margin-top:6px;">
                Upload a document in the first tab to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Filter controls
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_lob = st.selectbox(
                "Filter by Line",
                ["All", "Commercial Auto", "Property", "General Liability"]
            )
        with col_f2:
            filter_pri = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
        with col_f3:
            filter_val = st.selectbox("Filter by Status", ["All", "passed", "failed"])

        # Apply filters
        filtered = submissions
        if filter_lob != "All":
            filtered = [s for s in filtered if s.get("line_of_business") == filter_lob]
        if filter_pri != "All":
            filtered = [s for s in filtered if s.get("priority") == filter_pri]
        if filter_val != "All":
            filtered = [s for s in filtered if s.get("validation_status") == filter_val]

        st.markdown(f"""
        <div style="font-size:0.8rem; color:#7a9bb5; margin-bottom:16px;">
            Showing {len(filtered)} of {len(submissions)} submissions
        </div>
        """, unsafe_allow_html=True)

        # Display each submission
        for sub in reversed(filtered):   # reversed = newest first
            data = sub.get("extracted_data", {})
            is_complete = sub.get("is_complete", False)

            with st.expander(
                f"🗂  {sub.get('submission_id')}  —  "
                f"{data.get('applicant_name', 'Unknown')}  |  "
                f"{sub.get('line_of_business')}  |  "
                f"Priority: {sub.get('priority')}"
            ):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown(f"""
                    <table class="data-table">
                        <tr><td>Submission ID</td>
                            <td>{sub.get('submission_id')}</td></tr>
                        <tr><td>Applicant</td>
                            <td>{data.get('applicant_name', 'N/A')}</td></tr>
                        <tr><td>Business</td>
                            <td>{data.get('business_name', 'N/A')}</td></tr>
                        <tr><td>Email</td>
                            <td>{data.get('contact_email', 'N/A')}</td></tr>
                        <tr><td>Phone</td>
                            <td>{data.get('contact_phone', 'N/A')}</td></tr>
                        <tr><td>Agent</td>
                            <td>{data.get('agent_name', 'N/A')}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)

                with col_b:
                    st.markdown(f"""
                    <table class="data-table">
                        <tr><td>Policy Type</td>
                            <td>{data.get('policy_type', 'N/A')}</td></tr>
                        <tr><td>Coverage</td>
                            <td>{data.get('coverage_amount', 'N/A')}</td></tr>
                        <tr><td>Effective</td>
                            <td>{data.get('effective_date', 'N/A')}</td></tr>
                        <tr><td>Expiry</td>
                            <td>{data.get('expiration_date', 'N/A')}</td></tr>
                        <tr><td>Assigned Team</td>
                            <td>{sub.get('assigned_team', 'N/A')}</td></tr>
                        <tr><td>Processed On</td>
                            <td>{sub.get('timestamp', 'N/A')}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)

                # Status row
                st.markdown(f"""
                <div style="margin-top:12px; display:flex; gap:10px; align-items:center;">
                    {get_validation_pill(sub.get('validation_status', 'unknown'))}
                    {get_priority_pill(sub.get('priority', 'Medium'))}
                    <span class="pill pill-blue">{sub.get('line_of_business')}</span>
                </div>
                """, unsafe_allow_html=True)

                # Show missing fields if any
                if sub.get("missing_fields"):
                    st.markdown(f"""
                    <div style="margin-top:10px; font-size:0.82rem; color:#f59e0b;">
                        ⚠ Missing: {', '.join(sub['missing_fields'])}
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 3 — QUEUES
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Underwriting Queues</div>',
                unsafe_allow_html=True)

    queues      = load_queues()
    submissions = load_submissions()

    # Build submission lookup by ID for quick access
    sub_lookup = {s["submission_id"]: s for s in submissions}

    queue_display = [
        ("auto_underwriting_queue",      "🚛", "Commercial Auto Team",     "#a78bfa"),
        ("property_underwriting_queue",  "🏢", "Property Team",            "#4db8ff"),
        ("liability_underwriting_queue", "⚖️", "General Liability Team",   "#00d4aa"),
        ("manual_review_queue",          "👁️", "Manual Review Team",       "#f59e0b"),
    ]

    for q_key, icon, label, color in queue_display:
        ids   = queues.get(q_key, [])
        count = len(ids)

        st.markdown(f"""
        <div style="background:#0a1628; border:1px solid #1a3a5c; border-left:3px solid {color};
                    border-radius:10px; padding:16px 20px; margin-bottom:12px;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:1.4rem;">{icon}</span>
                    <div>
                        <div style="font-family:'Syne',sans-serif; font-weight:700;
                                    font-size:0.95rem; color:#e8edf5;">{label}</div>
                        <div style="font-size:0.78rem; color:#7a9bb5; margin-top:2px;">
                            {q_key}
                        </div>
                    </div>
                </div>
                <div style="font-family:'Syne',sans-serif; font-size:1.8rem;
                            font-weight:800; color:{color};">{count}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show individual submissions in this queue
        if ids:
            with st.expander(f"View {count} submission(s) in this queue"):
                for sid in reversed(ids):
                    sub = sub_lookup.get(sid, {})
                    data = sub.get("extracted_data", {})
                    st.markdown(f"""
                    <div style="background:#061020; border:1px solid #1a3a5c; border-radius:8px;
                                padding:12px 16px; margin-bottom:8px; font-size:0.85rem;">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:center;">
                            <div>
                                <span style="font-family:'Syne',sans-serif; font-weight:700;
                                             color:{color};">{sid}</span>
                                <span style="color:#7a9bb5; margin-left:10px;">
                                    {data.get('applicant_name', 'Unknown')}
                                </span>
                            </div>
                            {get_priority_pill(sub.get('priority', 'Medium'))}
                        </div>
                        <div style="color:#7a9bb5; margin-top:6px; font-size:0.78rem;">
                            Coverage: {data.get('coverage_amount', 'N/A')} ·
                            Processed: {sub.get('timestamp', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">CLAIMA Assistant</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.85rem; color:#7a9bb5; margin-bottom:20px; line-height:1.6;">
    Ask me anything about your submissions. Try:<br>
    <span style="color:#00d4aa">
    "What is the status of CLAIMA-20241215-143022?"<br>
    "Show me all high priority submissions"<br>
    "Is the submission for Rajesh Kumar complete?"
    </span>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center; padding:40px; color:#3a5a7c;">
                <div style="font-size:2rem;">💬</div>
                <div style="margin-top:8px; font-size:0.9rem;">
                    Start a conversation with CLAIMA Assistant
                </div>
            </div>
            """, unsafe_allow_html=True)

        for turn in st.session_state.chat_history:
            if turn["role"] == "user":
                st.markdown(f"""
                <div class="chat-label user">You</div>
                <div class="chat-user">{turn['content']}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-label bot">🛡️ CLAIMA Assistant</div>
                <div class="chat-bot">{turn['content']}</div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Chat input
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        user_input = st.text_input(
            "Message",
            placeholder="Ask about a submission status, applicant, or queue...",
            label_visibility="collapsed",
            key="chat_input"
        )
    with col_btn:
        send = st.button("Send →")

    if send and user_input.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip()
        })

        # Get response from chatbot
        with st.spinner("CLAIMA is thinking..."):
            response = chat(
                user_input.strip(),
                st.session_state.chat_history[:-1]  # History without current message
            )

        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        # Rerun to refresh the display
        st.rerun()

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()