"""app.py -- PawPal+ Streamlit UI, wired to pawpal_system.py."""

import importlib
import streamlit as st
import pawpal_system
importlib.reload(pawpal_system)
from pawpal_system import (
    VALID_TASK_TYPES, Owner, Pet, Scheduler, Task,
    load_from_json, save_to_json,
)

DATA_FILE = "data.json"

# ---------------------------------------------------------------------------
# Inline SVG icon library
# ---------------------------------------------------------------------------

def _sf(body: str, s: int, color: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" '
            f'viewBox="0 0 24 24" fill="{color}">{body}</svg>')

def _ss(body: str, s: int, color: str, sw: float = 2.0) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" '
            f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')

_B_PAW = (
    '<ellipse cx="12" cy="16" rx="4.5" ry="3.5"/>'
    '<ellipse cx="6" cy="10.5" rx="2" ry="1.8"/>'
    '<ellipse cx="10" cy="7.5" rx="1.8" ry="2.2"/>'
    '<ellipse cx="14" cy="7.5" rx="1.8" ry="2.2"/>'
    '<ellipse cx="18" cy="10.5" rx="2" ry="1.8"/>'
)
_B_CLIP = (
    '<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>'
    '<rect x="9" y="3" width="6" height="4" rx="1"/>'
    '<path d="m9 14 2 2 4-4"/>'
)
_B_CAL = (
    '<rect x="3" y="4" width="18" height="18" rx="2"/>'
    '<line x1="16" y1="2" x2="16" y2="6"/>'
    '<line x1="8" y1="2" x2="8" y2="6"/>'
    '<line x1="3" y1="10" x2="21" y2="10"/>'
    '<circle cx="8" cy="14" r="1" fill="currentColor" stroke="none"/>'
    '<circle cx="12" cy="14" r="1" fill="currentColor" stroke="none"/>'
    '<circle cx="16" cy="14" r="1" fill="currentColor" stroke="none"/>'
    '<circle cx="8" cy="18" r="1" fill="currentColor" stroke="none"/>'
    '<circle cx="12" cy="18" r="1" fill="currentColor" stroke="none"/>'
)
_B_BELL = (
    '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>'
    '<path d="M13.73 21a2 2 0 0 1-3.46 0"/>'
    '<circle cx="18" cy="5" r="3" fill="#F97316" stroke="#F97316" stroke-width="1"/>'
)
_B_WARN = (
    '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3'
    'L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
    '<line x1="12" y1="9" x2="12" y2="13"/>'
    '<line x1="12" y1="17" x2="12.01" y2="17"/>'
)
_B_CLOCK = '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
_B_CHECK = '<polyline points="20 6 9 17 4 12"/>'
_B_LIST  = (
    '<line x1="9" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/>'
    '<line x1="9" y1="18" x2="21" y2="18"/>'
    '<circle cx="4" cy="6"  r="1.5" fill="currentColor" stroke="none"/>'
    '<circle cx="4" cy="12" r="1.5" fill="currentColor" stroke="none"/>'
    '<circle cx="4" cy="18" r="1.5" fill="currentColor" stroke="none"/>'
)
_B_USER = '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>'
_B_SAVE = (
    '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
    '<polyline points="17 21 17 13 7 13 7 21"/>'
    '<polyline points="7 3 7 8 15 8"/>'
)
_B_FOLD = '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
_B_SRCH = '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
_B_GEAR = (
    '<circle cx="12" cy="12" r="3"/>'
    '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06'
    'a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09'
    'A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83'
    'l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09'
    'A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83'
    'l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09'
    'a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83'
    'l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09'
    'a1.65 1.65 0 0 0-1.51 1z"/>'
)
_B_PLUS = '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>'
_B_ARR_L = '<polyline points="15 18 9 12 15 6"/>'
_B_ARR_R = '<polyline points="9 18 15 12 9 6"/>'

def paw(s=20, c="#F97316"):        return _sf(_B_PAW,  s, c)
def ico_clip(s=20, c="#7C2D12"):   return _ss(_B_CLIP, s, c)
def ico_cal(s=20, c="#7C2D12"):    return _ss(_B_CAL,  s, c)
def ico_bell(s=20, c="#7C2D12"):   return _ss(_B_BELL, s, c)
def ico_warn(s=20, c="#92400E"):   return _ss(_B_WARN, s, c)
def ico_clock(s=20, c="#7C2D12"): return _ss(_B_CLOCK, s, c)
def ico_check(s=20, c="#065F46"): return _ss(_B_CHECK, s, c)
def ico_list(s=20, c="#7C2D12"):  return _ss(_B_LIST,  s, c)
def ico_user(s=20, c="#7C2D12"):  return _ss(_B_USER,  s, c)
def ico_save(s=20, c="#7C2D12"):  return _ss(_B_SAVE,  s, c)
def ico_fold(s=20, c="#7C2D12"):  return _ss(_B_FOLD,  s, c)
def ico_srch(s=20, c="#7C2D12"):  return _ss(_B_SRCH,  s, c)
def ico_gear(s=20, c="#7C2D12"):  return _ss(_B_GEAR,  s, c)
def ico_plus(s=20, c="#7C2D12"):  return _ss(_B_PLUS,  s, c)
def ico_arrl(s=16, c="#7C2D12"): return _ss(_B_ARR_L,  s, c)
def ico_arrr(s=16, c="#7C2D12"): return _ss(_B_ARR_R,  s, c)


def species_svg(species: str, size: int = 40) -> str:
    colors = {"dog": "#EA580C", "cat": "#9A3412", "other": "#F97316"}
    return paw(size, colors.get(species, "#F97316"))


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", layout="wide")

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap');

    html, body,
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    .stMarkdown, p, label, .stRadio, .stSelectbox, .stTextInput,
    .stNumberInput, .stMultiSelect, .stCaption, .stAlert, .stMetric,
    input, textarea {
        font-family: 'Nunito', sans-serif;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Fredoka', sans-serif !important;
        color: #7C2D12;
        letter-spacing: .3px;
    }

    /* Preserve Streamlit Material icon fonts */
    [class*="material-symbols"], [class*="material-icons"],
    [data-testid="stIconMaterial"], [data-testid="stExpanderToggleIcon"],
    span[translate="no"], .material-symbols-rounded, .material-symbols-outlined {
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }

    .stApp { background: #FFF7ED; }

    [data-testid="stSidebar"] {
        background: #FFEDD5 !important;
        border-right: 2px solid #FED7AA;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #9A3412 !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #FED7AA; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Fredoka', sans-serif !important;
        font-size: 1.05rem; color: #9A3412;
        border-radius: 12px 12px 0 0;
        padding: 8px 22px; border: none; background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #F97316 !important; color: #FFFFFF !important;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'Fredoka', sans-serif !important;
        border-radius: 14px; border: 2px solid #FDBA74;
        background: #FFFFFF; color: #9A3412;
        font-weight: 600; font-size: .97rem;
        padding: 8px 20px; transition: all 180ms ease; cursor: pointer;
    }
    .stButton > button:hover { background: #FB923C; color: #FFF; border-color: #F97316; }
    .stButton > button[kind="primary"] { background: #F97316; color: #FFF; border-color: #EA580C; }
    .stButton > button[kind="primary"]:hover { background: #7C2D12; border-color: #7C2D12; }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 10px !important;
        border: 1.5px solid #FED7AA !important;
        background: #FFFBF7 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #F97316 !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,.15) !important;
    }

    hr { border-color: #FED7AA !important; }
    [data-testid="stDataFrame"] { border: 1.5px solid #FED7AA; border-radius: 12px; overflow: hidden; }
    [data-testid="stAlert"] { border-radius: 14px !important; }
    [data-testid="stMetricValue"] { color: #9A3412 !important; font-family: 'Fredoka', sans-serif !important; }
    [data-testid="stMetricLabel"] { color: #92400E !important; }
    .block-container { padding-top: 2.2rem; }

    /* Sidebar logo */
    .sidebar-logo {
        display: flex; align-items: center; gap: 10px;
        padding: 4px 0 8px 0;
    }
    .logo-name {
        font-family: 'Fredoka', sans-serif; font-size: 1.45rem;
        color: #7C2D12; font-weight: 700; line-height: 1;
    }
    .logo-sub { font-size: .8rem; color: #92400E; margin-top: 2px; }

    /* Hero */
    .pawpal-hero {
        background: linear-gradient(135deg, #EA580C 0%, #F97316 55%, #FB923C 100%);
        border-radius: 24px; padding: 28px 32px; color: #FFF;
        margin-bottom: 24px;
        box-shadow: 0 12px 32px rgba(234,88,12,.25);
        display: flex; align-items: center; gap: 18px;
        position: relative; overflow: hidden;
    }
    .pawpal-hero h1 { color: #FFF !important; margin: 0; font-size: 2.3rem; line-height: 1.2; }
    .pawpal-hero p  { margin: 6px 0 0 0; opacity: .93; font-size: 1.05rem; }
    .pawpal-hero .hero-text { position: relative; z-index: 1; }
    .pawpal-hero::after {
        content: ""; position: absolute; right: -24px; bottom: -24px;
        width: 160px; height: 160px; border-radius: 50%;
        background: rgba(255,255,255,.08);
    }
    .pawpal-hero::before {
        content: ""; position: absolute; right: 140px; top: -36px;
        width: 90px; height: 90px; border-radius: 50%;
        background: rgba(255,255,255,.06);
    }

    /* Section header */
    .section-header { display: flex; align-items: center; gap: 12px; margin: 8px 0 20px 0; }
    .section-header .accent-bar { width: 5px; height: 32px; background: #F97316; border-radius: 3px; flex-shrink: 0; }
    .section-header h2 { margin: 0; font-size: 1.55rem; }

    /* Feature cards */
    .feature-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(210px,1fr));
        gap: 16px; margin: 8px 0 4px 0;
    }
    .feature-card {
        background: #FFF; border: 1.5px solid #FED7AA; border-radius: 20px;
        padding: 22px 20px; box-shadow: 0 4px 16px rgba(124,45,18,.06);
        transition: transform 180ms ease, box-shadow 180ms ease;
    }
    .feature-card:hover { transform: translateY(-4px); box-shadow: 0 10px 26px rgba(124,45,18,.12); }
    .feature-card .fc-icon {
        width: 52px; height: 52px; display: flex; align-items: center;
        justify-content: center; border-radius: 14px;
        background: linear-gradient(135deg, #FFEDD5, #FED7AA); margin-bottom: 14px;
    }
    .feature-card .fc-title { font-family: 'Fredoka', sans-serif; font-size: 1.1rem; color: #7C2D12; font-weight: 600; margin: 0 0 5px 0; }
    .feature-card .fc-desc  { color: #92400E; font-size: .9rem; line-height: 1.45; margin: 0; }

    /* How-it-works steps */
    .steps-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 14px; }
    .step-card {
        background: #FFF; border: 1.5px solid #FED7AA;
        border-radius: 16px; padding: 16px 18px;
    }
    .step-card .step-num {
        width: 30px; height: 30px; border-radius: 50%; background: #F97316;
        color: #FFF; font-family: 'Fredoka', sans-serif; font-weight: 700;
        display: flex; align-items: center; justify-content: center; margin-bottom: 8px;
    }
    .step-card .step-title { font-weight: 800; color: #7C2D12; font-size: .98rem; }
    .step-card .step-desc  { color: #92400E; font-size: .85rem; margin-top: 2px; }

    /* Stat cards */
    .stat-card {
        background: #FFF; border: 1.5px solid #FED7AA; border-radius: 18px;
        padding: 16px 18px; display: flex; align-items: center; gap: 14px;
        box-shadow: 0 3px 12px rgba(124,45,18,.05);
    }
    .stat-card .stat-ico {
        width: 48px; height: 48px; border-radius: 14px;
        background: #FFF7ED; border: 1px solid #FDBA74;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .stat-card .stat-num   { font-family: 'Fredoka', sans-serif; font-size: 1.5rem; color: #EA580C; font-weight: 600; line-height: 1; }
    .stat-card .stat-label { color: #92400E; font-size: .82rem; margin-top: 2px; }

    /* Pet card */
    .pet-card {
        background: #FFF; border: 1.5px solid #FED7AA; border-radius: 20px;
        padding: 20px; text-align: center;
        box-shadow: 0 4px 16px rgba(124,45,18,.07);
        transition: transform 180ms ease, box-shadow 180ms ease; height: 100%;
    }
    .pet-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(124,45,18,.13); }
    .pet-card .pet-icon   { display: flex; justify-content: center; margin-bottom: 10px; }
    .pet-card .pet-name   { font-family: 'Fredoka', sans-serif; font-size: 1.35rem; color: #7C2D12; font-weight: 600; margin: 0; }
    .pet-card .pet-meta   { color: #92400E; font-size: .9rem; margin-top: 4px; }
    .pet-card .pet-badge  {
        display: inline-block; margin-top: 10px;
        background: #FFF7ED; border: 1px solid #FDBA74;
        border-radius: 999px; padding: 3px 12px;
        font-size: .82rem; color: #9A3412; font-weight: 700;
    }

    /* Task card */
    .task-card {
        background: #FFF; border: 1.5px solid #FED7AA; border-radius: 16px;
        padding: 12px 14px; margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(124,45,18,.06);
    }
    .task-card .task-title { font-weight: 700; color: #7C2D12; font-size: .97rem; display: flex; align-items: center; gap: 6px; }
    .task-card .task-meta  { color: #92400E; font-size: .82rem; margin-top: 4px; }

    /* Pills */
    .pill { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .78rem; font-weight: 700; margin-right: 4px; vertical-align: middle; }
    .pill-high        { background: #FEE2E2; color: #991B1B; }
    .pill-medium      { background: #FEF3C7; color: #92400E; }
    .pill-low         { background: #DCFCE7; color: #166534; }
    .pill-todo        { background: #F3F4F6; color: #374151; }
    .pill-in_progress { background: #DBEAFE; color: #1E40AF; }
    .pill-done        { background: #D1FAE5; color: #065F46; }

    /* Kanban */
    .kanban-col {
        background: #FFECE0; border: 2px dashed #FDBA74;
        border-radius: 18px; padding: 14px; min-height: 200px;
    }
    .kanban-col-head {
        font-family: 'Fredoka', sans-serif; font-size: 1.1rem; font-weight: 600;
        color: #9A3412; text-align: center;
        padding-bottom: 10px; border-bottom: 1.5px solid #FED7AA; margin-bottom: 12px;
        display: flex; align-items: center; justify-content: center; gap: 8px;
    }

    /* Schedule slot row */
    .slot-row {
        display: flex; align-items: center; gap: 14px;
        background: #FFF; border: 1px solid #FED7AA; border-radius: 14px;
        padding: 11px 16px; margin-bottom: 8px;
    }
    .slot-time  { font-family: 'Fredoka', sans-serif; font-size: 1.1rem; color: #EA580C; font-weight: 600; min-width: 52px; }
    .slot-title { font-weight: 700; color: #7C2D12; }
    .slot-meta  { font-size: .82rem; color: #92400E; margin-top: 2px; }

    /* Conflict item */
    .conflict-item {
        background: #FEF3C7; border: 1.5px solid #FDE68A;
        border-left: 5px solid #F59E0B; border-radius: 12px;
        padding: 10px 14px; margin-bottom: 8px;
        font-size: .9rem; color: #78350F;
        display: flex; align-items: flex-start; gap: 8px;
    }

    /* Slot finder */
    .slot-finder-card {
        background: #FFF; border: 1.5px solid #FED7AA;
        border-radius: 18px; padding: 18px 20px;
    }

    /* Owner card (sidebar) */
    .owner-card {
        background: #FFF; border: 1.5px solid #FDBA74;
        border-radius: 16px; padding: 14px 16px; margin-top: 12px;
    }
    .owner-card .owner-name { font-family: 'Fredoka', sans-serif; font-size: 1.1rem; color: #7C2D12; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .owner-card .owner-meta { font-size: .87rem; color: #92400E; margin-top: 6px; display: flex; flex-direction: column; gap: 4px; }
    .owner-meta-row { display: flex; align-items: center; gap: 6px; }

    /* Inline icon alignment helper */
    .ico { display: inline-flex; align-items: center; vertical-align: middle; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pill(text: str, css_class: str) -> str:
    return f'<span class="pill {css_class}">{text}</span>'


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state["owner"] = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        f'<div class="sidebar-logo">'
        f'{paw(32, "#F97316")}'
        f'<div><div class="logo-name">PawPal+</div>'
        f'<div class="logo-sub">Your pet care planner</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    # Owner settings — regular inputs (no st.form) so browser never shows
    # the "Press Enter to submit form" tooltip.
    with st.expander(
        "Owner settings",
        expanded=st.session_state["owner"] is None,
    ):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'{ico_gear(16)}<span style="font-size:.85rem;color:#92400E;">Configure your profile</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        _default_name  = st.session_state["owner"].name      if st.session_state["owner"] else "Jordan"
        _default_start = st.session_state["owner"].day_start  if st.session_state["owner"] else "07:00"
        _default_end   = st.session_state["owner"].day_end    if st.session_state["owner"] else "19:00"
        _default_email = st.session_state["owner"].email      if st.session_state["owner"] else ""

        owner_name  = st.text_input("Your name",       value=_default_name,  key="inp_owner_name")
        col_s, col_e = st.columns(2)
        with col_s:
            day_start = st.text_input("Day start", value=_default_start, key="inp_day_start")
        with col_e:
            day_end   = st.text_input("Day end",   value=_default_end,   key="inp_day_end")
        owner_email = st.text_input("Email (optional)", value=_default_email, key="inp_email")

        if st.button("Save owner", type="primary", use_container_width=True):
            st.session_state["owner"] = Owner(
                name=owner_name.strip(),
                email=owner_email.strip(),
                day_start=day_start.strip(),
                day_end=day_end.strip(),
            )
            st.success(f"Saved {owner_name.strip()}!")

    st.divider()

    # Persistence
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;font-weight:700;color:#7C2D12;margin-bottom:4px;">'
        f'{ico_save(16)} Save / Load data</div>'
        f'<div style="font-size:.8rem;color:#92400E;margin-bottom:8px;">File: <code>{DATA_FILE}</code></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save", use_container_width=True):
            if st.session_state["owner"]:
                save_to_json(st.session_state["owner"], DATA_FILE)
                st.success("Saved!")
            else:
                st.error("No owner yet.")
    with c2:
        if st.button("Load", use_container_width=True):
            loaded = load_from_json(DATA_FILE)
            if loaded:
                st.session_state["owner"] = loaded
                st.success(f"Loaded {loaded.name}!")
            else:
                st.warning(f"No {DATA_FILE} found.")

    if st.session_state["owner"]:
        o = st.session_state["owner"]
        st.markdown(
            f'<div class="owner-card">'
            f'<div class="owner-name">{ico_user(16)} {o.name}</div>'
            f'<div class="owner-meta">'
            f'<div class="owner-meta-row">{ico_clock(14)} {o.day_start} to {o.day_end} &middot; {o.available_minutes()} min/day</div>'
            f'<div class="owner-meta-row">{paw(14, "#F97316")} {len(o.get_pets())} pet(s) registered</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown(
    f'<div class="pawpal-hero">'
    f'<div style="flex-shrink:0;z-index:1;">{paw(56, "rgba(255,255,255,0.9)")}</div>'
    f'<div class="hero-text">'
    f'<h1>Welcome to PawPal+</h1>'
    f'<p>Take care of your pets: walks, meals, meds, and more. All planned, all on time.</p>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Guard -- rich welcome screen when no owner is set
# ---------------------------------------------------------------------------

if not st.session_state["owner"]:
    st.markdown(
        f'<div class="feature-grid">'

        f'<div class="feature-card">'
        f'<div class="fc-icon">{paw(28, "#F97316")}</div>'
        f'<p class="fc-title">Track every pet</p>'
        f'<p class="fc-desc">Register all your dogs, cats, and companions with breed, age, and weight.</p>'
        f'</div>'

        f'<div class="feature-card">'
        f'<div class="fc-icon">{ico_clip(28, "#7C2D12")}</div>'
        f'<p class="fc-title">Plan care tasks</p>'
        f'<p class="fc-desc">Walks, feedings, meds, grooming, and play, with priority and recurrence.</p>'
        f'</div>'

        f'<div class="feature-card">'
        f'<div class="fc-icon">{ico_cal(28, "#7C2D12")}</div>'
        f'<p class="fc-title">Smart daily schedule</p>'
        f'<p class="fc-desc">Auto-sorts by priority or time of day and fits everything in your window.</p>'
        f'</div>'

        f'<div class="feature-card">'
        f'<div class="fc-icon">{ico_bell(28, "#7C2D12")}</div>'
        f'<p class="fc-title">Conflict alerts</p>'
        f'<p class="fc-desc">Warns you when two pets need you at the same moment.</p>'
        f'</div>'

        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-header" style="margin-top:26px;">'
        '<div class="accent-bar"></div><h2>Get started in 3 steps</h2></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="steps-row">'

        '<div class="step-card">'
        '<div class="step-num">1</div>'
        '<div class="step-title">Set up your day</div>'
        '<div class="step-desc">Open <b>Owner settings</b> in the sidebar, add your name and daily window, then click <b>Save owner</b>.</div>'
        '</div>'

        '<div class="step-card">'
        '<div class="step-num">2</div>'
        '<div class="step-title">Add pets and tasks</div>'
        '<div class="step-desc">Register your pets, then give each one care tasks with durations and priorities.</div>'
        '</div>'

        '<div class="step-card">'
        '<div class="step-num">3</div>'
        '<div class="step-title">Generate a plan</div>'
        '<div class="step-desc">Build a daily schedule, track tasks on the Kanban board, and save your data.</div>'
        '</div>'

        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "Open **Owner settings** in the sidebar and click **Save owner** to begin, "
        "or click **Load** to restore a saved session."
    )
    st.stop()

owner: Owner = st.session_state["owner"]

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_pets, tab_tasks, tab_kanban, tab_schedule = st.tabs(
    ["Pets", "Tasks", "Kanban", "Schedule"]
)

# ===========================================================================
# TAB 1 -- Pets
# ===========================================================================

with tab_pets:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Your Pets</h2></div>',
        unsafe_allow_html=True,
    )

    _pets       = owner.get_pets()
    _total      = sum(len(p.get_tasks()) for p in _pets)
    _pending    = sum(len(p.filter_tasks(completed=False)) for p in _pets)
    _done_cnt   = sum(len(p.filter_tasks(completed=True))  for p in _pets)

    s1, s2, s3, s4 = st.columns(4)
    for col, icon_html, num, label in [
        (s1, paw(22, "#F97316"),     len(_pets),  "Pets"),
        (s2, ico_list(22),           _total,      "Total tasks"),
        (s3, ico_clock(22),          _pending,    "Pending"),
        (s4, ico_check(22, "#F97316"), _done_cnt, "Completed"),
    ]:
        with col:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-ico">{icon_html}</div>'
                f'<div><div class="stat-num">{num}</div><div class="stat-label">{label}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Add a new pet", expanded=len(owner.get_pets()) == 0):
        with st.form("add_pet_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                pet_name = st.text_input("Pet name", placeholder="e.g. Biscuit")
            with c2:
                species  = st.selectbox("Species", ["dog", "cat", "other"],
                                        format_func=lambda s: s.capitalize())
            with c3:
                breed = st.text_input("Breed", placeholder="optional")
            c4, c5 = st.columns(2)
            with c4:
                age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, step=0.5, value=1.0)
            with c5:
                weight = st.number_input("Weight (kg)", min_value=0.0, max_value=150.0, step=0.5, value=0.0)
            add_pet_btn = st.form_submit_button("Add pet", type="primary", use_container_width=True)

        if add_pet_btn:
            if not pet_name.strip():
                st.error("Pet needs a name.")
            else:
                owner.add_pet(Pet(
                    name=pet_name.strip(), species=species,
                    breed=breed.strip(), age_years=float(age), weight_kg=float(weight),
                ))
                st.success(f"Added {pet_name.strip()} the {species}!")

    pets = owner.get_pets()
    if pets:
        st.markdown(f"**{len(pets)} pet(s) registered**")
        cols_per_row = 3
        for row_start in range(0, len(pets), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, pet in zip(cols, pets[row_start:row_start + cols_per_row]):
                incomplete = len(pet.filter_tasks(completed=False))
                done_n     = len(pet.filter_tasks(completed=True))
                with col:
                    st.markdown(
                        f'<div class="pet-card">'
                        f'<div class="pet-icon">{species_svg(pet.species, 44)}</div>'
                        f'<p class="pet-name">{pet.name}</p>'
                        f'<p class="pet-meta">'
                        f'{pet.species.capitalize()}{", " + pet.breed if pet.breed else ""}<br>'
                        f'{pet.age_years} yr'
                        f'{" &middot; " + str(pet.weight_kg) + " kg" if pet.weight_kg else ""}'
                        f'</p>'
                        f'<div class="pet-badge">{incomplete} pending &middot; {done_n} done</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.info("No pets yet. Add one above to get started.")

# ===========================================================================
# TAB 2 -- Tasks
# ===========================================================================

with tab_tasks:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Pet Tasks</h2></div>',
        unsafe_allow_html=True,
    )

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet in the Pets tab first.")
    else:
        selected_name = st.selectbox(
            "Viewing tasks for:", [p.name for p in pets], key="task_pet_select",
        )
        selected_pet: Pet = next(p for p in pets if p.name == selected_name)

        left_col, right_col = st.columns([5, 3], gap="large")

        with right_col:
            st.markdown("#### Add task")
            with st.form("add_task_form"):
                task_title = st.text_input("Title", placeholder="e.g. Morning walk")
                task_type  = st.selectbox(
                    "Type", sorted(VALID_TASK_TYPES),
                    format_func=lambda t: t.replace("_", " ").title(),
                )
                c1, c2 = st.columns(2)
                with c1:
                    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
                    priority = st.selectbox("Priority", ["high", "medium", "low"],
                                            format_func=lambda p: p.capitalize())
                with c2:
                    preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "any"])
                    recurrence     = st.selectbox("Recurrence", ["daily", "weekly", "none"])
                rec_days = st.multiselect(
                    "Days (weekly only)",
                    ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"],
                )
                add_task_btn = st.form_submit_button("Add task", type="primary", use_container_width=True)

            if add_task_btn:
                if not task_title.strip():
                    st.error("Task needs a title.")
                else:
                    selected_pet.add_task(Task(
                        title=task_title.strip(), task_type=task_type,
                        duration_minutes=int(duration), priority=priority,
                        preferred_time=preferred_time, recurrence=recurrence,
                        recurrence_days=rec_days if recurrence == "weekly" else [],
                    ))
                    st.success(f"Added {task_title.strip()}!")

            incomplete = selected_pet.filter_tasks(completed=False)
            if incomplete:
                st.markdown("#### Mark complete")
                with st.form("mark_complete_form"):
                    choice = st.selectbox(
                        "Task", [t.title for t in incomplete],
                        format_func=lambda ti: ti,
                    )
                    mark_btn = st.form_submit_button("Mark and reschedule", use_container_width=True)
                if mark_btn:
                    target = next(t for t in incomplete if t.title == choice)
                    target.mark_complete()
                    next_t = target.next_occurrence()
                    if next_t:
                        selected_pet.add_task(next_t)
                        st.success(f"Done. Next {target.title} due {next_t.due_date}.")
                    else:
                        st.success(f"{target.title} marked complete.")

        with left_col:
            st.markdown("#### Task list")
            filter_opt = st.radio(
                "Show:", ["All", "Pending", "Completed"],
                horizontal=True, key="task_filter",
            )
            completed_map = {"All": None, "Pending": False, "Completed": True}
            filtered = selected_pet.filter_tasks(completed=completed_map[filter_opt])

            if not filtered:
                st.info(f"No {filter_opt.lower()} tasks for {selected_pet.name}.")
            else:
                for t in filtered:
                    check_ico = ico_check(14, "#065F46") if t.completed else ico_clock(14, "#92400E")
                    st.markdown(
                        f'<div class="task-card">'
                        f'<div class="task-title">{check_ico} {t.title}</div>'
                        f'<div class="task-meta">'
                        f'{pill(t.priority, f"pill-{t.priority}")} &nbsp;'
                        f'{t.duration_minutes} min &nbsp;&middot;&nbsp;'
                        f'{t.preferred_time} &nbsp;&middot;&nbsp;'
                        f'{t.recurrence}'
                        f'{"&nbsp;&middot;&nbsp; due " + t.due_date if t.due_date else ""}'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )

# ===========================================================================
# TAB 3 -- Kanban
# ===========================================================================

with tab_kanban:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Kanban Board</h2></div>',
        unsafe_allow_html=True,
    )

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet and some tasks first.")
    else:
        kb_name = st.selectbox("Pet:", [p.name for p in pets], key="kanban_pet_select")
        kb_pet: Pet = next(p for p in pets if p.name == kb_name)
        tasks_all = kb_pet.get_tasks()

        if not tasks_all:
            st.info(f"{kb_pet.name} has no tasks yet. Add some in the Tasks tab.")
        else:
            st.caption("Use the arrow buttons to move tasks between columns.")
            col_todo, col_inprog, col_done = st.columns(3, gap="medium")

            STATUS_LABELS = {
                "todo":        ("To Do",       ico_clock(16, "#374151")),
                "in_progress": ("In Progress", ico_clip(16,  "#1E40AF")),
                "done":        ("Done",        ico_check(16, "#065F46")),
            }
            ORDER = ["todo", "in_progress", "done"]
            COLS  = [col_todo, col_inprog, col_done]

            for col_widget, status_key in zip(COLS, ORDER):
                label_text, label_ico = STATUS_LABELS[status_key]
                col_tasks = kb_pet.tasks_by_status(status_key)
                with col_widget:
                    st.markdown(
                        f'<div class="kanban-col-head">{label_ico} {label_text} ({len(col_tasks)})</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown('<div class="kanban-col">', unsafe_allow_html=True)
                    if not col_tasks:
                        st.caption("Nothing here yet.")
                    for t in col_tasks:
                        cur_idx = ORDER.index(status_key)
                        st.markdown(
                            f'<div class="task-card" style="margin-bottom:4px;">'
                            f'<div class="task-title">{t.title}</div>'
                            f'<div class="task-meta">'
                            f'{pill(t.priority, f"pill-{t.priority}")}'
                            f'&nbsp;{t.duration_minutes} min'
                            f'</div></div>',
                            unsafe_allow_html=True,
                        )
                        b1, b2 = st.columns(2)
                        with b1:
                            if cur_idx > 0 and st.button(
                                "Back", key=f"kb_back_{t.task_id}", use_container_width=True
                            ):
                                t.set_status(ORDER[cur_idx - 1])
                                st.rerun()
                        with b2:
                            if cur_idx < 2 and st.button(
                                "Next", key=f"kb_next_{t.task_id}", use_container_width=True
                            ):
                                t.set_status(ORDER[cur_idx + 1])
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

# ===========================================================================
# TAB 4 -- Schedule
# ===========================================================================

with tab_schedule:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Daily Schedule</h2></div>',
        unsafe_allow_html=True,
    )

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet in the Pets tab first.")
    else:
        ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 3])
        with ctrl1:
            sched_name = st.selectbox("Pet:", [p.name for p in pets], key="sched_pet_select")
        with ctrl2:
            day = st.selectbox("Day:", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"])
        with ctrl3:
            sort_mode_label = st.radio(
                "Sort by:",
                ["Priority (high to low)", "Time of day (morning to evening)"],
                horizontal=True, key="sort_mode",
            )
        sort_key = "time" if "Time" in sort_mode_label else "priority"

        sched_pet: Pet = next(p for p in pets if p.name == sched_name)

        gen_col, _ = st.columns([2, 5])
        with gen_col:
            gen_btn = st.button("Generate schedule", type="primary", use_container_width=True)

        if gen_btn:
            if not sched_pet.get_tasks():
                st.warning(f"{sched_pet.name} has no tasks yet. Add some in the Tasks tab.")
            else:
                scheduler = Scheduler(owner=owner, pet=sched_pet, day_of_week=day)
                schedule  = scheduler.generate_schedule(sort_mode=sort_key)
                st.session_state["last_scheduler"] = scheduler

                if not schedule:
                    st.warning("No tasks qualify for this day. Check recurrence settings in Tasks.")
                else:
                    total_used = sum(s["task"].duration_minutes for s in schedule)
                    budget     = owner.available_minutes()
                    skipped    = len(sched_pet.get_tasks()) - len(schedule)

                    st.success(
                        f"{sched_pet.name} on {day.title()} -- "
                        f"{len(schedule)} tasks, {total_used}/{budget} min"
                    )

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Tasks scheduled", len(schedule))
                    m2.metric("Time used",        f"{total_used} min")
                    m3.metric("Available",         f"{budget} min")
                    m4.metric("Skipped",           skipped)

                    st.divider()

                    sched_col, explain_col = st.columns([3, 2], gap="large")

                    with sched_col:
                        st.markdown("#### Schedule")
                        for slot in schedule:
                            t = slot["task"]
                            st.markdown(
                                f'<div class="slot-row">'
                                f'<div class="slot-time">{slot["start_time"]}</div>'
                                f'<div>'
                                f'<div class="slot-title">{t.title}</div>'
                                f'<div class="slot-meta">'
                                f'{t.duration_minutes} min &nbsp;&middot;&nbsp;'
                                f'{pill(t.priority, f"pill-{t.priority}")}'
                                f'&nbsp;{pill(t.status, f"pill-{t.status}")}'
                                f'</div></div></div>',
                                unsafe_allow_html=True,
                            )

                    with explain_col:
                        st.markdown("#### Plan explanation")
                        st.code(scheduler.explain_plan(), language=None)

                    other_pets = [p for p in owner.get_pets() if p.name != sched_pet.name]
                    if other_pets:
                        st.divider()
                        other_scheds = []
                        for op in other_pets:
                            os_ = Scheduler(owner=owner, pet=op, day_of_week=day)
                            os_.generate_schedule(sort_mode=sort_key)
                            other_scheds.append(os_)
                        conflicts = scheduler.detect_conflicts(other_schedules=other_scheds)
                        if conflicts:
                            st.markdown(f"#### {len(conflicts)} scheduling conflict(s) on {day.title()}")
                            st.caption(f"{owner.name} cannot attend two pets simultaneously.")
                            for c in conflicts:
                                msg = c.replace("CONFLICT: ", "")
                                st.markdown(
                                    f'<div class="conflict-item">'
                                    f'{ico_warn(16)} {msg}</div>',
                                    unsafe_allow_html=True,
                                )
                            st.info("Tip: Set one pet's tasks to a later preferred time to reduce overlap.")
                        else:
                            st.success(
                                f"No schedule conflicts between {sched_pet.name} "
                                f"and other pets on {day.title()}."
                            )

        st.divider()
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'{ico_srch(18)} <strong>Find next available slot</strong></div>',
            unsafe_allow_html=True,
        )
        with st.container():
            st.markdown('<div class="slot-finder-card">', unsafe_allow_html=True)
            sf1, sf2, sf3 = st.columns([2, 2, 2])
            with sf1:
                slot_dur = st.number_input("Task length (min)", min_value=1, max_value=240, value=30, key="slot_dur")
            with sf2:
                after_t  = st.text_input("After time (HH:MM, optional)", value="", key="after_t")
            with sf3:
                st.markdown("<br>", unsafe_allow_html=True)
                find_btn = st.button("Find earliest slot", use_container_width=True)
            if find_btn:
                sched_obj = st.session_state.get("last_scheduler")
                if not sched_obj:
                    st.warning("Generate a schedule above first.")
                else:
                    slot_result = sched_obj.find_next_available_slot(
                        int(slot_dur), after_time=after_t.strip() or None
                    )
                    if slot_result:
                        st.success(f"Earliest {int(slot_dur)}-min opening: {slot_result}")
                    else:
                        st.error("No opening fits before the day ends.")
            st.markdown("</div>", unsafe_allow_html=True)
