# ============================================================
# FILE: ui/app.py  —  CLAIMA v2 UI
# Clean editorial design — warm off-white + deep ink + amber
# ============================================================

import streamlit as st
import sys, os, tempfile, json
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from main    import process_submission
from chatbot import chat

st.set_page_config(
    page_title="CLAIMA",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&family=Nunito+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
    background-color: #f5f2ed;
    color: #1c1c1e;
}

#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f2ed; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #1c1c1e;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #e8e2d9 !important; }

/* ── TOPBAR ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 0 24px 0;
    border-bottom: 2px solid #1c1c1e;
    margin-bottom: 36px;
}
.brand {
    display: flex;
    align-items: baseline;
    gap: 14px;
}
.brand-name {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #1c1c1e;
    letter-spacing: -1px;
    line-height: 1;
}
.brand-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8a7d6b;
    letter-spacing: 2px;
    text-transform: uppercase;
    border: 1px solid #c8bfb0;
    padding: 3px 8px;
    border-radius: 3px;
}
.topbar-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8a7d6b;
    letter-spacing: 1px;
    text-align: right;
}

/* ── STAT STRIP ── */
.stat-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #c8bfb0;
    border: 1px solid #c8bfb0;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 40px;
}
.stat-cell {
    background: #f5f2ed;
    padding: 20px 24px;
    text-align: center;
}
.stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1c1c1e;
    line-height: 1;
}
.stat-lbl {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8a7d6b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 5px;
}

/* ── TAB BAR ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 2px solid #c8bfb0;
    gap: 0;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8a7d6b;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 12px 24px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #1c1c1e !important;
    border-bottom: 2px solid #1c1c1e !important;
    background: transparent !important;
}

/* ── UPLOAD PANEL ── */
.upload-panel {
    background: #ffffff;
    border: 1px solid #d8d0c4;
    border-radius: 10px;
    padding: 32px;
}
.panel-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #1c1c1e;
    margin-bottom: 6px;
}
.panel-sub {
    font-size: 0.82rem;
    color: #8a7d6b;
    margin-bottom: 24px;
    line-height: 1.6;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #faf8f5;
    border: 2px dashed #c8bfb0;
    border-radius: 8px;
    padding: 8px;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: #8a7d6b; }

/* ── PROCESS BUTTON ── */
.stButton > button {
    background: #1c1c1e;
    color: #f5f2ed;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    border: none;
    border-radius: 6px;
    padding: 12px 32px;
    width: 100%;
    transition: background 0.2s;
}
.stButton > button:hover { background: #3a3a3c; }

/* ── RESULT PANEL ── */
.result-panel {
    background: #ffffff;
    border: 1px solid #d8d0c4;
    border-radius: 10px;
    padding: 28px;
}
.result-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e8e2d9;
}
.result-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #8a7d6b;
    margin-bottom: 4px;
}
.result-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: #1c1c1e;
}
.badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
}
.badge-high   { background: #fde8e8; color: #c0392b; border: 1px solid #f5c6c6; }
.badge-medium { background: #fef3cd; color: #7d5a00; border: 1px solid #f0d78c; }
.badge-low    { background: #e8f5e9; color: #2e7d32; border: 1px solid #b8ddb9; }
.badge-ok     { background: #e8f5e9; color: #2e7d32; border: 1px solid #b8ddb9; }
.badge-warn   { background: #fef3cd; color: #7d5a00; border: 1px solid #f0d78c; }

/* ── FIELD TABLE ── */
.field-row {
    display: flex;
    padding: 9px 0;
    border-bottom: 1px solid #f0ece6;
    font-size: 0.85rem;
    gap: 16px;
}
.field-row:last-child { border-bottom: none; }
.field-key {
    color: #8a7d6b;
    font-weight: 600;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    min-width: 140px;
    padding-top: 1px;
}
.field-val { color: #1c1c1e; flex: 1; line-height: 1.5; }

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 60px 40px;
    background: #faf8f5;
    border: 2px dashed #c8bfb0;
    border-radius: 10px;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
.empty-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #8a7d6b;
    margin-bottom: 6px;
}
.empty-sub { font-size: 0.8rem; color: #b0a898; }

/* ── SUBMISSION CARD ── */
.sub-card {
    background: #ffffff;
    border: 1px solid #d8d0c4;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.sub-card:hover { border-color: #8a7d6b; }
.sub-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.sub-card-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #8a7d6b;
}
.sub-card-name {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #1c1c1e;
    margin-bottom: 4px;
}
.sub-card-meta { font-size: 0.78rem; color: #8a7d6b; }

/* ── QUEUE BLOCK ── */
.queue-block {
    background: #ffffff;
    border: 1px solid #d8d0c4;
    border-left: 4px solid #1c1c1e;
    border-radius: 0 8px 8px 0;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.queue-name {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #1c1c1e;
    margin-bottom: 3px;
}
.queue-count {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8a7d6b;
    letter-spacing: 1px;
}

/* ── CHAT ── */
.chat-wrap { max-width: 700px; margin: 0 auto; }
.msg-user {
    background: #1c1c1e;
    color: #f5f2ed;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 10px 0 10px 80px;
    font-size: 0.88rem;
    line-height: 1.6;
}
.msg-bot {
    background: #ffffff;
    border: 1px solid #d8d0c4;
    color: #1c1c1e;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 10px 80px 10px 0;
    font-size: 0.88rem;
    line-height: 1.6;
}
.msg-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 3px;
    color: #8a7d6b;
}
.msg-label.right { text-align: right; }

/* ── TEXT INPUT ── */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid #d8d0c4 !important;
    border-radius: 6px !important;
    color: #1c1c1e !important;
    font-family: 'Nunito Sans', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1c1c1e !important;
    box-shadow: none !important;
}

/* ── SELECT BOX ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid #d8d0c4 !important;
    border-radius: 6px !important;
    color: #1c1c1e !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border: 1px solid #d8d0c4 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #1c1c1e !important;
    letter-spacing: 0.5px !important;
    font-weight: 600 !important;
}
.streamlit-expanderHeader:hover {
    background: #f5f2ed !important;
    border-color: #8a7d6b !important;
}
.streamlit-expanderContent {
    background: #faf8f5 !important;
    border: 1px solid #d8d0c4 !important;
    border-top: none !important;
}
/* Force all expander header text to be dark */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] > div:first-child,
[data-testid="stExpander"] > div:first-child p {
    color: #1c1c1e !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] > div:first-child svg {
    fill: #1c1c1e !important;
    color: #1c1c1e !important;
}

/* ── ALERTS ── */
.stSuccess { background: #e8f5e9 !important; border-left: 3px solid #2e7d32 !important; }
.stError   { background: #fde8e8 !important; border-left: 3px solid #c0392b !important; }
.stWarning { background: #fef3cd !important; border-left: 3px solid #f39c12 !important; }
.stSpinner > div { border-top-color: #1c1c1e !important; }

/* ── MISSING FIELDS BOX ── */
.missing-box {
    background: #fef9ee;
    border: 1px solid #f0d78c;
    border-left: 3px solid #f39c12;
    border-radius: 6px;
    padding: 14px 18px;
    margin-top: 14px;
}
.missing-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #7d5a00;
    margin-bottom: 8px;
}
.missing-item { font-size: 0.82rem; color: #5a4000; padding: 2px 0; }

/* ── ROUTING BOX ── */
.routing-box {
    background: #f0f4ff;
    border: 1px solid #c5d0f0;
    border-left: 3px solid #3a5bd9;
    border-radius: 6px;
    padding: 14px 18px;
    margin-top: 14px;
}
.routing-team {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 600;
    color: #1c2e6e;
    margin-bottom: 2px;
}
.routing-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #5a6ea0;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────
def load_submissions():
    try:
        sys.path.insert(0, ROOT_DIR)
        from database import get_all_submissions
        return get_all_submissions()
    except Exception as e:
        print(f"UI load_submissions error: {e}")
        return []

def load_queues():
    try:
        sys.path.insert(0, ROOT_DIR)
        from database import get_queues
        return get_queues()
    except Exception as e:
        print(f"UI load_queues error: {e}")
        return {}

def priority_badge(p):
    cls = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}.get(p,"badge-medium")
    return f'<span class="badge {cls}">{p} Priority</span>'

def validation_badge(ok):
    if ok: return '<span class="badge badge-ok">✓ Complete</span>'
    return '<span class="badge badge-warn">⚠ Incomplete</span>'

# ── SESSION STATE ─────────────────────────────────────────────
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "last_result"  not in st.session_state: st.session_state.last_result  = None

# ── TOP BAR ──────────────────────────────────────────────────
submissions = load_submissions()
total    = len(submissions)
complete = sum(1 for s in submissions if s.get("is_complete"))
high_pri = sum(1 for s in submissions if s.get("priority") == "High")
queues   = load_queues()
pending  = sum(len(v) for v in queues.values())

st.markdown(f"""
<div class="topbar">
  <div class="brand">
    <div class="brand-name">CLAIMA</div>
    <div class="brand-tag">Insurance AI</div>
  </div>
  <div class="topbar-meta">
    Cognitive Line Agent for Insurance<br>
    Management &amp; Automation
  </div>
</div>
""", unsafe_allow_html=True)

# ── STAT STRIP ────────────────────────────────────────────────
st.markdown(f"""
<div class="stat-strip">
  <div class="stat-cell">
    <div class="stat-num">{total}</div>
    <div class="stat-lbl">Total Processed</div>
  </div>
  <div class="stat-cell">
    <div class="stat-num">{complete}</div>
    <div class="stat-lbl">Complete</div>
  </div>
  <div class="stat-cell">
    <div class="stat-num">{high_pri}</div>
    <div class="stat-lbl">High Priority</div>
  </div>
  <div class="stat-cell">
    <div class="stat-num">{pending}</div>
    <div class="stat-lbl">In Queues</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "01  Upload & Process",
    "02  All Submissions",
    "03  Queues",
    "04  Assistant"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — UPLOAD
# ══════════════════════════════════════════════════════════════
with tab1:
    col_L, col_R = st.columns([1, 1], gap="large")

    with col_L:
        st.markdown("""
        <div class="upload-panel">
          <div class="panel-title">Process a Submission</div>
          <div class="panel-sub">
            Upload any PDF insurance document — application form, fleet schedule,
            property details, or liability summary. CLAIMA will extract, validate,
            classify, and route it automatically.
          </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid #d8d0c4;border-radius:6px;
                        padding:14px 18px;margin:12px 0;font-size:0.82rem;">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                          color:#8a7d6b;text-transform:uppercase;letter-spacing:1.5px;
                          margin-bottom:4px;">Selected Document</div>
              <div style="font-weight:700;color:#1c1c1e;">📄 {uploaded.name}</div>
              <div style="color:#8a7d6b;margin-top:3px;">{uploaded.size/1024:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("→  Run CLAIMA Pipeline"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name

                with st.spinner("Processing through 5 agents..."):
                    result = process_submission(tmp_path)
                os.unlink(tmp_path)
                st.session_state.last_result = result

                if result["status"] == "success":
                    st.success(f"Done — {result['submission_id']}")
                else:
                    st.error(f"Failed at: {result.get('stage','unknown')}")
        else:
            st.markdown("""
            <div class="empty-state" style="margin-top:12px;">
              <div class="empty-icon">📂</div>
              <div class="empty-title">No document selected</div>
              <div class="empty-sub">Drop a PDF above to begin processing</div>
            </div>
            """, unsafe_allow_html=True)

    with col_R:
        if st.session_state.last_result and st.session_state.last_result["status"] == "success":
            r   = st.session_state.last_result
            val = r["validation"]
            d   = r["extracted_data"]

            st.markdown(f"""
            <div class="result-panel">
              <div class="result-header">
                <div>
                  <div class="result-id">{r['submission_id']}</div>
                  <div class="result-name">{d.get('applicant_name','Unknown Applicant')}</div>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;">
                  {priority_badge(r['priority'])}
                  {validation_badge(val['is_complete'])}
                </div>
              </div>

              <div class="field-row">
                <div class="field-key">Business</div>
                <div class="field-val">{d.get('business_name','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Policy Type</div>
                <div class="field-val">{d.get('policy_type','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Line of Business</div>
                <div class="field-val">{r['line_of_business']}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Coverage</div>
                <div class="field-val">{d.get('coverage_amount','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Effective Date</div>
                <div class="field-val">{d.get('effective_date','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Expiry Date</div>
                <div class="field-val">{d.get('expiration_date','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Agent</div>
                <div class="field-val">{d.get('agent_name','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Email</div>
                <div class="field-val">{d.get('contact_email','—')}</div>
              </div>
              <div class="field-row">
                <div class="field-key">Phone</div>
                <div class="field-val">{d.get('contact_phone','—')}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Routing box
            st.markdown(f"""
            <div class="routing-box">
              <div class="routing-team">→ {r['routed_to']}</div>
              <div class="routing-meta">Assigned queue · Priority: {r['priority']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Missing fields
            if val.get("missing_fields"):
                items = "".join(f'<div class="missing-item">· {f}</div>' for f in val["missing_fields"])
                st.markdown(f"""
                <div class="missing-box">
                  <div class="missing-title">Missing Fields</div>
                  {items}
                </div>
                """, unsafe_allow_html=True)

            # All fields expander
            with st.expander("VIEW ALL EXTRACTED FIELDS"):
                for k, v in d.items():
                    if v and str(v) not in ("null", "None", ""):
                        st.markdown(f"""
                        <div class="field-row">
                          <div class="field-key">{k.replace('_',' ').title()}</div>
                          <div class="field-val">{v}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">📋</div>
              <div class="empty-title">Results will appear here</div>
              <div class="empty-sub">Upload and process a document on the left</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — ALL SUBMISSIONS
# ══════════════════════════════════════════════════════════════
with tab2:
    submissions = load_submissions()

    if not submissions:
        st.markdown("""
        <div class="empty-state" style="margin-top:24px;">
          <div class="empty-icon">📭</div>
          <div class="empty-title">No submissions yet</div>
          <div class="empty-sub">Process a document in the first tab to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_lob = st.selectbox("Line of Business", ["All","Commercial Auto","Property","General Liability"])
        with fc2:
            f_pri = st.selectbox("Priority", ["All","High","Medium","Low"])
        with fc3:
            f_val = st.selectbox("Validation", ["All","passed","failed"])

        filtered = submissions
        if f_lob != "All": filtered = [s for s in filtered if s.get("line_of_business") == f_lob]
        if f_pri != "All": filtered = [s for s in filtered if s.get("priority") == f_pri]
        if f_val != "All": filtered = [s for s in filtered if s.get("validation_status") == f_val]

        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
                    color:#8a7d6b;margin:20px 0 12px;letter-spacing:1px;">
            SHOWING {len(filtered)} OF {len(submissions)} SUBMISSIONS
        </div>
        """, unsafe_allow_html=True)

        for sub in reversed(filtered):
            data = sub.get("extracted_data", {})
            name = data.get("applicant_name", "Unknown")
            lob  = sub.get("line_of_business","—")
            pri  = sub.get("priority","—")
            ts   = sub.get("timestamp","—")
            sid  = sub.get("submission_id","—")
            ok   = sub.get("is_complete", False)

            with st.expander(f"{sid}  —  {name}  ·  {lob}"):
                c1, c2 = st.columns(2)
                left_fields = [
                    ("Applicant",    data.get("applicant_name","—")),
                    ("Business",     data.get("business_name","—")),
                    ("Email",        data.get("contact_email","—")),
                    ("Phone",        data.get("contact_phone","—")),
                    ("Agent",        data.get("agent_name","—")),
                ]
                right_fields = [
                    ("Policy Type",  data.get("policy_type","—")),
                    ("Coverage",     data.get("coverage_amount","—")),
                    ("Effective",    data.get("effective_date","—")),
                    ("Expiry",       data.get("expiration_date","—")),
                    ("Processed",    ts),
                ]
                with c1:
                    for k,v in left_fields:
                        st.markdown(f'<div class="field-row"><div class="field-key">{k}</div><div class="field-val">{v}</div></div>', unsafe_allow_html=True)
                with c2:
                    for k,v in right_fields:
                        st.markdown(f'<div class="field-row"><div class="field-key">{k}</div><div class="field-val">{v}</div></div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;">
                  {priority_badge(pri)}
                  {validation_badge(ok)}
                  <span class="badge" style="background:#f0f4ff;color:#1c2e6e;border:1px solid #c5d0f0;">{lob}</span>
                </div>
                """, unsafe_allow_html=True)

                if sub.get("missing_fields"):
                    st.markdown(f"""
                    <div class="missing-box" style="margin-top:12px;">
                      <div class="missing-title">Missing Fields</div>
                      {"".join(f'<div class="missing-item">· {f}</div>' for f in sub["missing_fields"])}
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 3 — QUEUES
# ══════════════════════════════════════════════════════════════
with tab3:
    queues      = load_queues()
    submissions = load_submissions()
    sub_lookup  = {s["submission_id"]: s for s in submissions}

    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                font-weight:600;color:#1c1c1e;margin:8px 0 24px;">
        Underwriting Queues
    </div>
    """, unsafe_allow_html=True)

    queue_info = [
        ("auto_underwriting_queue",      "Commercial Auto Underwriting",  "#3a5bd9"),
        ("property_underwriting_queue",  "Property Underwriting",         "#2e7d32"),
        ("liability_underwriting_queue", "General Liability Underwriting","#7b3fa0"),
        ("manual_review_queue",          "Manual Review",                  "#c0392b"),
    ]

    for qkey, qname, qcolor in queue_info:
        ids   = queues.get(qkey, [])
        count = len(ids)

        st.markdown(f"""
        <div class="queue-block" style="border-left-color:{qcolor};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div class="queue-name">{qname}</div>
              <div class="queue-count">{count} SUBMISSION{'S' if count!=1 else ''} IN QUEUE</div>
            </div>
            <div style="font-family:'Playfair Display',serif;font-size:2rem;
                        font-weight:700;color:{qcolor};">{count}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if ids:
            with st.expander(f"VIEW {count} SUBMISSION(S)"):
                for sid in reversed(ids):
                    sub  = sub_lookup.get(sid, {})
                    data = sub.get("extracted_data", {})
                    name = data.get("applicant_name","Unknown")
                    cov  = data.get("coverage_amount","—")
                    ts   = sub.get("timestamp","—")
                    pri  = sub.get("priority","—")
                    st.markdown(f"""
                    <div class="sub-card">
                      <div class="sub-card-top">
                        <div class="sub-card-id">{sid}</div>
                        {priority_badge(pri)}
                      </div>
                      <div class="sub-card-name">{name}</div>
                      <div class="sub-card-meta">Coverage: {cov} · Processed: {ts}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                font-weight:600;color:#1c1c1e;margin:8px 0 6px;">
        CLAIMA Assistant
    </div>
    <div style="font-size:0.82rem;color:#8a7d6b;margin-bottom:28px;line-height:1.7;">
        Ask about submission status, missing fields, queue assignments, or anything
        about your processed documents.<br>
        <span style="font-family:'IBM Plex Mono',monospace;color:#3a5bd9;">
        Try: "What is the status of CLAIMA-XXXXXXXX-XXXXXX?"
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-title">Start a conversation</div>
          <div class="empty-sub">Type a question below to talk to CLAIMA Assistant</div>
        </div>
        """, unsafe_allow_html=True)

    for turn in st.session_state.chat_history:
        if turn["role"] == "user":
            st.markdown(f"""
            <div class="msg-label right">You</div>
            <div class="msg-user">{turn['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-label">CLAIMA Assistant</div>
            <div class="msg-bot">{turn['content']}</div>
            """, unsafe_allow_html=True)

    # Input row
    ci, cb = st.columns([5, 1])
    with ci:
        user_input = st.text_input("Message", placeholder="Ask about a submission, queue, or status...",
                                   label_visibility="collapsed", key="chat_input")
    with cb:
        send = st.button("Send")

    if send and user_input.strip():
        st.session_state.chat_history.append({"role":"user","content":user_input.strip()})
        with st.spinner("Thinking..."):
            reply = chat(user_input.strip(), st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()