import streamlit as st
import google.generativeai as genai
import json
import os
import base64
import uuid
import numpy as np
from PIL import Image
import io
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION & SETUP
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FamilyMed AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = "medical_data"
RECORDS_FILE = f"{DATA_DIR}/records.json"
PROFILES_DIR = f"{DATA_DIR}/profiles"
REPORTS_DIR  = f"{DATA_DIR}/reports"

for d in [DATA_DIR, PROFILES_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

PALETTE = [
    "#FF6B6B", "#4FC3F7", "#66BB6A", "#FFB74D",
    "#BA68C8", "#26C6DA", "#EF5350", "#42A5F5",
    "#EC407A", "#26A69A"
]

# ══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS  —  deep-space clinical aesthetic
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap');

/* ── Reset & root ─────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif;
    background: #040b17 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Scrollbar ─────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060d1c; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 10px; }

/* ── Topbar ────────────────────────────────────────── */
.topbar {
    background: linear-gradient(90deg, #061020 0%, #091828 100%);
    border-bottom: 1px solid rgba(0,200,255,0.1);
    padding: 13px 32px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: sticky; top: 0; z-index: 999;
}
.topbar-logo { font-size: 26px; }
.topbar-name {
    font-family: 'Sora', sans-serif;
    font-size: 19px; font-weight: 800;
    background: linear-gradient(100deg, #00E5CC 0%, #2196F3 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.3px;
}
.topbar-pill {
    margin-left: auto;
    font-size: 10px; font-weight: 600;
    color: rgba(0,200,255,0.6);
    border: 1px solid rgba(0,200,255,0.2);
    background: rgba(0,200,255,0.05);
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.5px; text-transform: uppercase;
}

/* ── Page wrapper ──────────────────────────────────── */
.pw {
    max-width: 860px;
    margin: 0 auto;
    padding: 36px 20px 80px;
}

/* ── HOME HERO ─────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 56px 20px 48px;
}
.hero-badge {
    display: inline-block;
    font-size: 11px; font-weight: 600; letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #00E5CC;
    background: rgba(0,229,204,0.08);
    border: 1px solid rgba(0,229,204,0.2);
    padding: 5px 16px; border-radius: 30px;
    margin-bottom: 22px;
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: clamp(28px, 5vw, 48px);
    font-weight: 800; color: #fff;
    line-height: 1.15; margin-bottom: 16px;
}
.hero-title .g {
    background: linear-gradient(110deg, #00E5CC 10%, #2196F3 90%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 15px; color: rgba(255,255,255,0.42);
    max-width: 500px; margin: 0 auto 52px;
    line-height: 1.75;
}

/* ── Choice cards ──────────────────────────────────── */
.choice-row {
    display: flex; gap: 18px;
    justify-content: center;
    flex-wrap: wrap;
}
.choice-card {
    flex: 1; min-width: 240px; max-width: 320px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 22px; padding: 30px 22px 22px;
    text-align: center;
    transition: all 0.3s cubic-bezier(.2,.8,.3,1);
}
.choice-card:hover {
    border-color: rgba(0,229,204,0.4);
    background: rgba(0,229,204,0.04);
    transform: translateY(-5px);
    box-shadow: 0 24px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,229,204,0.1);
}
.cc-icon { font-size: 38px; margin-bottom: 14px; display: block; }
.cc-title {
    font-family: 'Sora', sans-serif;
    font-size: 17px; font-weight: 700; color: #fff;
    margin-bottom: 8px;
}
.cc-desc { font-size: 13px; color: rgba(255,255,255,0.38); line-height: 1.6; margin-bottom: 18px; }

/* ── Glass card ────────────────────────────────────── */
.gc {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 18px;
}
.gc-title {
    font-family: 'Sora', sans-serif;
    font-size: 13px; font-weight: 600;
    color: rgba(255,255,255,0.55);
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
}

/* ── Profile capture highlight box ────────────────── */
.profile-box {
    border: 2px dashed rgba(0,229,204,0.45);
    border-radius: 18px;
    padding: 20px 22px;
    background: rgba(0,229,204,0.03);
    margin-bottom: 18px;
}
.profile-box-label {
    font-family: 'Sora', sans-serif;
    font-size: 16px; font-weight: 700;
    color: #00E5CC;
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 4px;
}
.profile-box-hint {
    font-size: 12px; color: rgba(255,255,255,0.32);
    margin-bottom: 14px;
}

/* ── Camera section ────────────────────────────────── */
.cam-box {
    border: 1.5px solid rgba(33,150,243,0.35);
    border-radius: 20px; padding: 24px;
    background: rgba(33,150,243,0.03);
    text-align: center;
}
.cam-title {
    font-family: 'Sora', sans-serif;
    font-size: 15px; font-weight: 700; color: #2196F3;
    margin-bottom: 4px;
}
.cam-hint { font-size: 12px; color: rgba(255,255,255,0.3); margin-bottom: 16px; }

/* ── Captured photos strip ─────────────────────────── */
.photo-strip { display: flex; gap: 9px; flex-wrap: wrap; margin-top: 14px; }
.photo-chip {
    width: 72px; height: 90px;
    border-radius: 10px; overflow: hidden;
    border: 2px solid rgba(0,229,204,0.3);
    position: relative;
}
.photo-chip img { width: 100%; height: 100%; object-fit: cover; }
.photo-badge {
    display: inline-block;
    background: rgba(0,229,204,0.1);
    border: 1px solid rgba(0,229,204,0.25);
    border-radius: 10px; padding: 8px 16px;
    font-size: 13px; font-weight: 500; color: #00E5CC;
    margin-top: 12px;
}

/* ── Disease box (explore) ──────────────────────────── */
.dbox {
    border-radius: 22px;
    overflow: hidden;
    margin-bottom: 16px;
    transition: transform 0.28s cubic-bezier(.2,.8,.3,1), box-shadow 0.28s ease;
    cursor: pointer;
}
.dbox:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.55);
}
.dbox-head {
    padding: 18px 22px;
    display: flex; align-items: center; gap: 15px;
}
.dav {
    width: 50px; height: 50px; border-radius: 50%;
    object-fit: cover;
    border: 2.5px solid rgba(255,255,255,0.22);
    flex-shrink: 0;
}
.dav-init {
    width: 50px; height: 50px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Sora', sans-serif;
    font-size: 20px; font-weight: 800; color: #fff;
    border: 2.5px solid rgba(255,255,255,0.22);
    flex-shrink: 0;
}
.dbox-info { flex: 1; min-width: 0; }
.dbox-disease {
    font-family: 'Sora', sans-serif;
    font-size: 16px; font-weight: 700; color: #fff;
    margin-bottom: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.dbox-person { font-size: 13px; color: rgba(255,255,255,0.55); }
.dbox-count {
    background: rgba(0,0,0,0.25);
    color: rgba(255,255,255,0.8);
    padding: 4px 13px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    white-space: nowrap;
}

/* ── Messages ───────────────────────────────────────── */
.msg-ok {
    background: rgba(0,200,120,0.08); border: 1px solid rgba(0,200,120,0.25);
    border-radius: 12px; padding: 13px 18px;
    color: #00E676; font-size: 14px; font-weight: 500;
    margin: 10px 0;
}
.msg-err {
    background: rgba(255,80,80,0.08); border: 1px solid rgba(255,80,80,0.25);
    border-radius: 12px; padding: 13px 18px;
    color: #FF6B6B; font-size: 14px; font-weight: 500;
    margin: 10px 0;
}
.msg-warn {
    background: rgba(255,193,7,0.08); border: 1px solid rgba(255,193,7,0.25);
    border-radius: 12px; padding: 13px 18px;
    color: #FFD600; font-size: 14px; font-weight: 500;
    margin: 10px 0;
}

/* ── Empty state ────────────────────────────────────── */
.empty-wrap {
    text-align: center; padding: 70px 20px;
}
.empty-icon { font-size: 58px; display: block; margin-bottom: 18px; }
.empty-title {
    font-family: 'Sora', sans-serif;
    font-size: 21px; font-weight: 700;
    color: rgba(255,255,255,0.38); margin-bottom: 8px;
}
.empty-sub { font-size: 13px; color: rgba(255,255,255,0.22); margin-bottom: 24px; }

/* ── Page title ─────────────────────────────────────── */
.pg-title {
    font-family: 'Sora', sans-serif;
    font-size: 26px; font-weight: 800; color: #fff;
    margin-bottom: 4px;
}
.pg-sub { font-size: 13px; color: rgba(255,255,255,0.35); margin-bottom: 28px; }

/* ── Streamlit overrides ────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(10,18,40,0.9) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 11px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 11px 15px !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00E5CC !important;
    box-shadow: 0 0 0 2px rgba(0,229,204,0.15) !important;
    outline: none !important;
}
.stTextInput label {
    color: rgba(255,255,255,0.55) !important;
    font-size: 12px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
}
.stButton > button {
    background: linear-gradient(110deg, #00E5CC 0%, #2196F3 100%) !important;
    color: #04080f !important; border: none !important;
    border-radius: 13px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    letter-spacing: 0.2px !important;
    padding: 13px 22px !important;
    transition: all 0.25s ease !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(0,229,204,0.3) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

div[data-testid="stCameraInput"] label {
    color: rgba(255,255,255,0.5) !important;
    font-size: 12px !important;
}
div[data-testid="stCameraInput"] video { border-radius: 14px !important; }
div[data-testid="stCameraInput"] img  { border-radius: 14px !important; }

div[data-testid="stToggle"] label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 13px !important;
}
div[data-testid="stToggle"] .st-bw { background: rgba(0,229,204,0.2) !important; }

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.018) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.65) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
div[data-testid="stExpander"] > div > div > div {
    background: transparent !important;
}

div[data-testid="stSidebar"] {
    background: #050d1e !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
div[data-testid="stSidebar"] * { color: rgba(255,255,255,0.7) !important; }
div[data-testid="stSidebar"] h3 { color: #fff !important; }
div[data-testid="stSidebar"] .stTextInput > div > div > input { color: #fff !important; }

.stSpinner > div { color: #00E5CC !important; }
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Image caption in explore */
div[data-testid="stImage"] { border-radius: 12px; overflow: hidden; }
div[data-testid="stImage"] img { border-radius: 12px; }

.stInfo {
    background: rgba(33,150,243,0.07) !important;
    border: 1px solid rgba(33,150,243,0.2) !important;
    border-radius: 12px !important; color: rgba(255,255,255,0.7) !important;
}

/* filter count tag */
.count-tag {
    font-size: 12px; color: rgba(255,255,255,0.3);
    margin-bottom: 20px;
}

/* profile preview circle */
.prof-preview-wrap { text-align: center; }
.prof-preview-img {
    width: 78px; height: 78px; border-radius: 50%;
    object-fit: cover;
    border: 3px solid #00E5CC;
    display: block; margin: 0 auto 6px;
}
.prof-preview-label { font-size: 11px; color: rgba(0,229,204,0.6); }
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════
def load_data():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'r') as f:
            return json.load(f)
    return {"members": {}}

def save_data(data):
    with open(RECORDS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_or_create_member(data, name):
    name_key = name.strip().lower()
    for mid, m in data["members"].items():
        if m["name"].strip().lower() == name_key:
            return mid, m
    mid = str(uuid.uuid4())[:10]
    data["members"][mid] = {
        "id": mid,
        "name": name.strip(),
        "profile_pic": None,
        "diseases": {},
        "color_idx": len(data["members"]) % len(PALETTE)
    }
    return mid, data["members"][mid]

def b64(img_bytes: bytes) -> str:
    return base64.b64encode(img_bytes).decode()

def compress_image(img_bytes: bytes, max_px=1800, quality=88) -> bytes:
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality)
    return buf.getvalue()

def check_blur(img_bytes: bytes, threshold=180) -> tuple[bool, float]:
    """Return (is_sharp, score). Uses Laplacian variance approximation."""
    img = Image.open(io.BytesIO(img_bytes)).convert('L').resize((480, 480))
    arr = np.array(img, dtype=np.float32)
    dx = np.diff(arr, 2, axis=1)
    dy = np.diff(arr, 2, axis=0)
    score = float(np.var(dx) + np.var(dy))
    return score >= threshold, round(score, 1)

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def analyze_with_gemini(img_bytes_list: list, disease_hint: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    hint_clause = (
        f"The user indicated the condition is: '{disease_hint}'. Confirm or refine this."
        if disease_hint else
        "No disease name was provided — infer it entirely from medicines and findings."
    )

    prompt = f"""You are a medical document AI analyzer.
Analyze the uploaded medical prescription/report image(s) carefully.
{hint_clause}

Reply with ONLY a valid JSON object — no markdown, no backticks, no extra text:
{{
  "disease_name": "Primary condition (e.g. 'Type 2 Diabetes', 'Hypertension', 'Viral Fever'). Use hint if given. If unknown, write 'General'.",
  "medicines": ["list of medicine / drug names exactly as written"],
  "doctor": "Doctor name if visible, else null",
  "date": "Date on document if visible, else null",
  "document_type": "one of: prescription | lab_report | discharge_summary | imaging_report | other",
  "key_findings": "2-3 concise sentences describing the main medical findings or prescribed treatment",
  "confidence": "high | medium | low — your confidence in disease identification"
}}"""

    parts = [prompt]
    for b in img_bytes_list:
        parts.append({"mime_type": "image/jpeg", "data": b64(b)})

    response = model.generate_content(parts)
    raw = response.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    return json.loads(raw)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_state():
    defs = {
        "page":              "home",
        "captured_reports":  [],      # list of (bytes, b64_str)
        "profile_bytes":     None,
        "profile_b64":       None,
        "cam_counter":       0,       # incremented to reset camera key
        "last_status":       None,    # {"type": ok/err, "msg": str}
        "api_key":           os.environ.get("GEMINI_API_KEY", ""),
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_topbar():
    st.markdown("""
    <div class="topbar">
        <span class="topbar-logo">🩺</span>
        <span class="topbar-name">FamilyMed AI</span>
        <span class="topbar-pill">Gemini 2.5 Flash</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">AI-Powered Health Records</div>
        <div class="hero-title">
            Your Family's Health,<br>
            <span class="g">Organized Intelligently</span>
        </div>
        <p class="hero-sub">
            Snap prescriptions and reports with your camera.
            Gemini AI reads the documents, identifies conditions,
            and files everything in smart, searchable disease vaults — for every family member.
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, mid_col, _ = st.columns([1, 6, 1])
    with mid_col:
        st.markdown('<div class="choice-row">', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="medium")

        with c1:
            st.markdown("""
            <div class="choice-card">
                <span class="cc-icon">📋</span>
                <div class="cc-title">Store Data</div>
                <div class="cc-desc">Capture prescriptions & reports. AI auto-classifies and stores them in the right health vault.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📋  Store Data", key="home_store", use_container_width=True):
                st.session_state.page = "store"
                st.session_state.captured_reports = []
                st.session_state.profile_bytes = None
                st.session_state.profile_b64 = None
                st.rerun()

        with c2:
            st.markdown("""
            <div class="choice-card">
                <span class="cc-icon">🔍</span>
                <div class="cc-title">Explore Data</div>
                <div class="cc-desc">Browse all saved records organized by person and disease in beautifully structured boxes.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔍  Explore Data", key="home_explore", use_container_width=True):
                st.session_state.page = "explore"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  STORE DATA PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_store():
    # ── Sidebar: API Key & instructions ──────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        api_key_input = st.text_input(
            "Gemini API Key",
            value=st.session_state.api_key,
            type="password",
            help="Get your key at aistudio.google.com"
        )
        st.session_state.api_key = api_key_input
        st.markdown("---")
        st.markdown("**📌 How to use**")
        st.markdown("""
1. Set your profile photo *(optional)*
2. Enter your name
3. Enter disease name *(optional — AI will detect)*
4. Capture prescription / report photos
5. Hit **Analyze & Save**
        """)
        st.markdown("---")
        st.caption("Photos are stored locally on this device.")

    st.markdown('<div class="pw">', unsafe_allow_html=True)

    if st.button("← Home", key="back_store"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("""
    <div class="pg-title">📋 Store Medical Data</div>
    <div class="pg-sub">Fill in the form, capture documents, and let AI do the rest</div>
    """, unsafe_allow_html=True)

    # ── 1. Profile Picture ────────────────────────────────────────────────────
    st.markdown("""
    <div class="profile-box">
        <div class="profile-box-label">📷 Set Your Profile Picture</div>
        <div class="profile-box-hint">Optional — your photo will appear on your health vaults so everyone can tell them apart at a glance</div>
    </div>
    """, unsafe_allow_html=True)

    show_prof_cam = st.toggle("Open camera for profile picture", key="toggle_prof")
    if show_prof_cam:
        prof_img = st.camera_input("Take a clear selfie", key="prof_cam")
        if prof_img:
            raw = prof_img.getvalue()
            compressed = compress_image(raw, max_px=320, quality=82)
            st.session_state.profile_bytes = compressed
            st.session_state.profile_b64 = b64(compressed)
            st.markdown('<div class="msg-ok">✅ Profile picture captured!</div>', unsafe_allow_html=True)

    if st.session_state.profile_b64:
        st.markdown(f"""
        <div class="prof-preview-wrap">
            <img class="prof-preview-img"
                 src="data:image/jpeg;base64,{st.session_state.profile_b64}" />
            <div class="prof-preview-label">Profile set ✓</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── 2. Name & Disease ─────────────────────────────────────────────────────
    st.markdown('<div class="gc">', unsafe_allow_html=True)
    st.markdown('<div class="gc-title">👤 Member Information</div>', unsafe_allow_html=True)

    col_name, col_disease = st.columns(2, gap="medium")
    with col_name:
        member_name = st.text_input(
            "Full Name *",
            placeholder="e.g. Sarah Ahmed",
            key="inp_name"
        )
    with col_disease:
        disease_hint = st.text_input(
            "Disease / Condition (Optional)",
            placeholder="e.g. Hypertension, Diabetes…",
            key="inp_disease"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Medical Document Camera ───────────────────────────────────────────
    st.markdown("""
    <div class="cam-box">
        <div class="cam-title">📄 Capture Medical Documents</div>
        <div class="cam-hint">Hold the document steady and in good light — blurry photos are automatically rejected</div>
    </div>
    """, unsafe_allow_html=True)

    cam_key = f"report_cam_{st.session_state.cam_counter}"
    report_img = st.camera_input(
        "📷 Point at prescription or report",
        key=cam_key
    )

    if report_img is not None:
        raw_bytes = report_img.getvalue()
        is_sharp, blur_score = check_blur(raw_bytes)

        if is_sharp:
            compressed = compress_image(raw_bytes)
            img_b64 = b64(compressed)
            # Preview
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;margin:10px 0;">
                <img src="data:image/jpeg;base64,{img_b64}"
                     style="width:90px;height:112px;border-radius:10px;object-fit:cover;
                            border:2px solid rgba(0,229,204,0.45);" />
                <div>
                    <div style="font-size:13px;color:#00E5CC;font-weight:600;margin-bottom:4px;">
                        ✅ Sharp image ready
                    </div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.35);">
                        Clarity score: {blur_score:.0f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("➕  Add photo to collection", key="add_photo"):
                st.session_state.captured_reports.append((compressed, img_b64))
                st.session_state.cam_counter += 1  # reset camera
                st.rerun()
        else:
            st.markdown(
                f'<div class="msg-warn">⚠️ Photo too blurry (score: {blur_score:.0f}). '
                f'Please hold still and retake.</div>',
                unsafe_allow_html=True
            )

    # Show captured strip
    n = len(st.session_state.captured_reports)
    if n:
        st.markdown(f'<div class="photo-badge">📁 {n} photo{"s" if n>1 else ""} collected</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="photo-strip">', unsafe_allow_html=True)
        thumbs_html = ""
        for _, img_b64 in st.session_state.captured_reports[:8]:
            thumbs_html += f"""
            <div class="photo-chip">
                <img src="data:image/jpeg;base64,{img_b64}" />
            </div>"""
        if n > 8:
            thumbs_html += f"""
            <div class="photo-chip" style="display:flex;align-items:center;justify-content:center;
                 background:rgba(255,255,255,0.05);font-size:14px;color:rgba(255,255,255,0.4);">
                +{n-8}
            </div>"""
        st.markdown(thumbs_html + '</div>', unsafe_allow_html=True)

        colcl, _ = st.columns([1, 3])
        with colcl:
            if st.button("🗑️  Clear all", key="clear_photos"):
                st.session_state.captured_reports = []
                st.session_state.cam_counter += 1
                st.rerun()

    st.markdown("---")

    # ── 4. Submit ─────────────────────────────────────────────────────────────
    if not st.session_state.api_key.strip():
        st.markdown(
            '<div class="msg-warn">⚠️ Add your Gemini API key in the sidebar to enable AI analysis.</div>',
            unsafe_allow_html=True
        )

    can_submit = bool(
        member_name.strip() and
        st.session_state.captured_reports and
        st.session_state.api_key.strip()
    )

    if st.button("🔬  Analyze & Save Records", key="submit_btn", disabled=not can_submit):
        _process_and_save(member_name.strip(), disease_hint.strip())

    # Show last status
    if st.session_state.last_status:
        s = st.session_state.last_status
        cls = "msg-ok" if s["type"] == "ok" else "msg-err"
        st.markdown(f'<div class="{cls}">{s["msg"]}</div>', unsafe_allow_html=True)
        st.session_state.last_status = None

    st.markdown("</div>", unsafe_allow_html=True)


def _process_and_save(name: str, disease_hint: str):
    """Run Gemini analysis and persist data."""
    data = load_data()
    mid, member = get_or_create_member(data, name)

    with st.spinner("🤖 Gemini AI is reading your documents…"):
        try:
            img_bytes_list = [byt for byt, _ in st.session_state.captured_reports]
            analysis = analyze_with_gemini(img_bytes_list, disease_hint, st.session_state.api_key)
        except Exception as e:
            st.session_state.last_status = {"type": "err", "msg": f"Analysis failed: {e}"}
            st.rerun()
            return

    # Determine final disease name
    disease_name = (
        disease_hint or
        analysis.get("disease_name") or
        "General"
    )
    dkey = disease_name.lower().replace(" ", "_").replace("/", "_")[:40]

    # Save profile picture (first time only)
    if st.session_state.profile_bytes and not member.get("profile_pic"):
        prof_path = os.path.join(PROFILES_DIR, f"{mid}.jpg")
        with open(prof_path, "wb") as f:
            f.write(st.session_state.profile_bytes)
        member["profile_pic"] = prof_path

    # Create disease slot if new
    if dkey not in member["diseases"]:
        color_idx = len(member["diseases"]) % len(PALETTE)
        member["diseases"][dkey] = {
            "name": disease_name,
            "color": PALETTE[color_idx],
            "reports": []
        }

    # Save each image file
    saved_ids = []
    for img_bytes, _ in st.session_state.captured_reports:
        rid = str(uuid.uuid4())[:14]
        rpath = os.path.join(REPORTS_DIR, f"{rid}.jpg")
        with open(rpath, "wb") as f:
            f.write(img_bytes)
        saved_ids.append({"id": rid, "path": rpath})

    # Append record entry
    member["diseases"][dkey]["reports"].append({
        "images": saved_ids,
        "analysis": analysis,
        "added_date": datetime.now().isoformat(),
        "image_count": len(saved_ids)
    })

    save_data(data)

    st.session_state.last_status = {
        "type": "ok",
        "msg": (
            f'✅ Saved {len(saved_ids)} document(s) for <b>{name}</b> '
            f'under "<b>{disease_name}</b>"'
        )
    }
    st.session_state.captured_reports = []
    st.session_state.profile_bytes = None
    st.session_state.profile_b64 = None
    st.session_state.cam_counter += 1
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  EXPLORE DATA PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_explore():
    st.markdown('<div class="pw">', unsafe_allow_html=True)

    if st.button("← Home", key="back_explore"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("""
    <div class="pg-title">🔍 Explore Medical Records</div>
    <div class="pg-sub">All family health vaults organized by person and condition</div>
    """, unsafe_allow_html=True)

    data = load_data()
    members = data.get("members", {})

    # Collect all disease boxes
    boxes = []
    for mid, member in members.items():
        for dkey, disease in member["diseases"].items():
            if disease.get("reports"):
                boxes.append({"mid": mid, "member": member,
                               "dkey": dkey, "disease": disease})

    if not boxes:
        st.markdown("""
        <div class="empty-wrap">
            <span class="empty-icon">📭</span>
            <div class="empty-title">No records saved yet</div>
            <div class="empty-sub">Start by storing your family's prescriptions and reports</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📋  Save your first record", key="goto_store_from_explore"):
            st.session_state.page = "store"
            st.session_state.captured_reports = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Search bar
    q = st.text_input("🔎 Search by name or condition…",
                       placeholder="e.g. Ahmed, Diabetes, Hypertension",
                       key="explore_search").strip().lower()

    if q:
        boxes = [b for b in boxes
                 if q in b["member"]["name"].lower()
                 or q in b["disease"]["name"].lower()]

    total = len(boxes)
    st.markdown(f'<div class="count-tag">{total} health vault{"s" if total!=1 else ""} found</div>',
                unsafe_allow_html=True)

    if not boxes:
        st.markdown('<div class="msg-warn">⚠️ No matching records found.</div>',
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Render each disease box ───────────────────────────────────────────────
    for box in boxes:
        member  = box["member"]
        disease = box["disease"]
        mid     = box["mid"]
        color   = disease.get("color", PALETTE[0])
        n_recs  = len(disease["reports"])
        last_dt = disease["reports"][-1]["added_date"][:10]

        # Profile avatar HTML
        prof_html = ""
        if member.get("profile_pic") and os.path.exists(member["profile_pic"]):
            with open(member["profile_pic"], "rb") as pf:
                pb64 = base64.b64encode(pf.read()).decode()
            prof_html = f'<img class="dav" src="data:image/jpeg;base64,{pb64}" />'
        else:
            init = member["name"][0].upper()
            prof_html = (
                f'<div class="dav-init" style="background:{color}55;">{init}</div>'
            )

        st.markdown(f"""
        <div class="dbox"
             style="background:linear-gradient(135deg,{color}20 0%,{color}08 100%);
                    border:1px solid {color}45;">
            <div class="dbox-head">
                {prof_html}
                <div class="dbox-info">
                    <div class="dbox-disease">{disease['name']}</div>
                    <div class="dbox-person">👤 {member['name']}</div>
                </div>
                <div style="text-align:right;">
                    <div class="dbox-count">{n_recs} record{"s" if n_recs>1 else ""}</div>
                    <div style="font-size:10px;color:rgba(255,255,255,0.28);margin-top:5px;">
                        Last: {last_dt}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📂  Open {disease['name']} vault — {member['name']}"):
            for i, record in enumerate(disease["reports"]):
                analysis   = record.get("analysis", {})
                added_date = record.get("added_date", "")[:10]
                img_entries = record.get("images", [])

                st.markdown(f"""
                <div style="font-family:'Sora',sans-serif;font-size:14px;
                             font-weight:700;color:rgba(255,255,255,0.75);
                             margin-bottom:10px;">
                    Record {i+1} &nbsp;·&nbsp;
                    <span style="font-weight:400;color:rgba(255,255,255,0.35);">
                        {added_date}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                if analysis:
                    col_a, col_b = st.columns(2, gap="medium")
                    with col_a:
                        doc_type = analysis.get("document_type","").replace("_"," ").title()
                        st.markdown(f"🏷️ **Type:** {doc_type or 'N/A'}")
                        meds = analysis.get("medicines", [])
                        if meds:
                            st.markdown(f"💊 **Medicines:** {', '.join(meds[:6])}"
                                        + (f" +{len(meds)-6} more" if len(meds) > 6 else ""))
                    with col_b:
                        if analysis.get("doctor"):
                            st.markdown(f"👨‍⚕️ **Doctor:** {analysis['doctor']}")
                        if analysis.get("date"):
                            st.markdown(f"📅 **Date on doc:** {analysis['date']}")

                    if analysis.get("key_findings"):
                        st.info(f"📋 {analysis['key_findings']}")

                    conf = analysis.get("confidence", "medium")
                    conf_icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(conf, "🟡")
                    st.caption(f"{conf_icon} AI confidence: **{conf}**")

                # Show thumbnails
                if img_entries:
                    img_cols = st.columns(min(len(img_entries), 4))
                    for j, entry in enumerate(img_entries[:4]):
                        rpath = entry.get("path", "")
                        if os.path.exists(rpath):
                            with img_cols[j]:
                                st.image(rpath, use_container_width=True)

                if i < len(disease["reports"]) - 1:
                    st.divider()

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()
    render_topbar()

    page = st.session_state.page
    if   page == "home":    page_home()
    elif page == "store":   page_store()
    elif page == "explore": page_explore()

if __name__ == "__main__":
    main()
