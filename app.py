"""app.py — PawPal+ Streamlit UI, wired to pawpal_system.py.

Design: warm orange/brown palette, Fredoka + Nunito typography.
Web-first layout: card grids, sidebar owner panel, tabbed sections.
"""

import importlib

import pandas as pd
import streamlit as st

# Streamlit keeps imported modules in sys.modules between hot-reloads and does NOT
# re-read them when only app.py changes. If the server was started before
# pawpal_system.py gained new symbols, `from pawpal_system import X` would hit the
# stale cached module and raise ImportError. Force a fresh load every script run so
# edits to pawpal_system.py always take effect without a manual server restart.
import pawpal_system
importlib.reload(pawpal_system)

from pawpal_system import (
    PRIORITY_EMOJI,
    STATUS_EMOJI,
    TASK_TYPE_EMOJI,
    VALID_TASK_TYPES,
    Owner,
    Pet,
    Scheduler,
    Task,
    load_from_json,
    save_to_json,
)

DATA_FILE = "data.json"   # defined locally — avoids module-cache import races

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Global CSS — orange/brown palette, Fredoka/Nunito, web card layout
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap');

    /* ── base typography ── */
    html, body, [class*="css"], .stMarkdown, p, span, li { font-family: 'Nunito', sans-serif !important; }
    h1, h2, h3, h4, h5 { font-family: 'Fredoka', sans-serif !important; color: #7C2D12; letter-spacing: .3px; }

    /* ── page background ── */
    .stApp { background: #FFF7ED; }

    /* ── sidebar ── */
    [data-testid="stSidebar"] { background: #FFEDD5 !important; border-right: 2px solid #FED7AA; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #9A3412 !important; }

    /* ── tab bar ── */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #FED7AA; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Fredoka', sans-serif !important;
        font-size: 1.05rem;
        color: #9A3412;
        border-radius: 12px 12px 0 0;
        padding: 8px 20px;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #F97316 !important;
        color: #FFFFFF !important;
    }

    /* ── buttons ── */
    .stButton > button {
        font-family: 'Fredoka', sans-serif !important;
        border-radius: 14px;
        border: 2px solid #FDBA74;
        background: #FFFFFF;
        color: #9A3412;
        font-weight: 600;
        font-size: .97rem;
        padding: 8px 20px;
        transition: all 180ms ease;
        cursor: pointer;
    }
    .stButton > button:hover { background: #FB923C; color: #FFFFFF; border-color: #F97316; }
    .stButton > button[kind="primary"] { background: #F97316; color: #FFFFFF; border-color: #EA580C; }
    .stButton > button[kind="primary"]:hover { background: #7C2D12; border-color: #7C2D12; }

    /* ── form inputs ── */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 10px !important;
        border: 1.5px solid #FED7AA !important;
        background: #FFFBF7 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #F97316 !important;
        box-shadow: 0 0 0 3px rgba(249,115,22,.15) !important;
    }

    /* ── divider ── */
    hr { border-color: #FED7AA !important; }

    /* ── dataframe ── */
    [data-testid="stDataFrame"] { border: 1.5px solid #FED7AA; border-radius: 12px; overflow: hidden; }

    /* ─────────── CARD COMPONENTS ─────────── */

    /* Hero banner */
    .pawpal-hero {
        background: linear-gradient(135deg, #EA580C 0%, #F97316 50%, #FB923C 100%);
        border-radius: 24px;
        padding: 28px 32px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 12px 32px rgba(234,88,12,.25);
        display: flex;
        align-items: center;
        gap: 18px;
    }
    .pawpal-hero h1 { color: #FFFFFF !important; margin: 0; font-size: 2.3rem; line-height: 1.2; }
    .pawpal-hero p  { margin: 6px 0 0 0; opacity: .95; font-size: 1.05rem; }
    .pawpal-hero .hero-icon { font-size: 3.5rem; }

    /* Section header with accent bar */
    .section-header {
        display: flex; align-items: center; gap: 12px;
        margin: 8px 0 20px 0;
    }
    .section-header .accent-bar {
        width: 5px; height: 32px; background: #F97316;
        border-radius: 3px; flex-shrink: 0;
    }
    .section-header h2 { margin: 0; font-size: 1.55rem; }

    /* Pet card */
    .pet-card {
        background: #FFFFFF;
        border: 1.5px solid #FED7AA;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(124,45,18,.07);
        transition: transform 180ms ease, box-shadow 180ms ease;
        height: 100%;
    }
    .pet-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(124,45,18,.13); }
    .pet-card .pet-icon { font-size: 3rem; margin-bottom: 8px; }
    .pet-card .pet-name { font-family: 'Fredoka', sans-serif; font-size: 1.35rem; color: #7C2D12; font-weight: 600; margin: 0; }
    .pet-card .pet-meta { color: #92400E; font-size: .9rem; margin-top: 4px; }
    .pet-card .pet-badge {
        display: inline-block;
        margin-top: 10px;
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        border-radius: 999px;
        padding: 3px 12px;
        font-size: .82rem;
        color: #9A3412;
        font-weight: 700;
    }

    /* Task card (Kanban) */
    .task-card {
        background: #FFFFFF;
        border: 1.5px solid #FED7AA;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(124,45,18,.06);
    }
    .task-card .task-title { font-weight: 700; color: #7C2D12; font-size: .97rem; }
    .task-card .task-meta { color: #92400E; font-size: .82rem; margin-top: 3px; }

    /* Kanban column */
    .kanban-col {
        background: #FFECE0;
        border: 2px dashed #FDBA74;
        border-radius: 18px;
        padding: 14px;
        min-height: 180px;
    }
    .kanban-col-head {
        font-family: 'Fredoka', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #9A3412;
        text-align: center;
        padding-bottom: 10px;
        border-bottom: 1.5px solid #FED7AA;
        margin-bottom: 12px;
    }

    /* Priority / status pills */
    .pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: .78rem;
        font-weight: 700;
        margin-right: 4px;
        vertical-align: middle;
    }
    .pill-high   { background: #FEE2E2; color: #991B1B; }
    .pill-medium { background: #FEF3C7; color: #92400E; }
    .pill-low    { background: #DCFCE7; color: #166534; }
    .pill-todo   { background: #F3F4F6; color: #374151; }
    .pill-in_progress { background: #DBEAFE; color: #1E40AF; }
    .pill-done   { background: #D1FAE5; color: #065F46; }

    /* Metric card overrides */
    [data-testid="stMetricValue"] { color: #9A3412 !important; font-family: 'Fredoka', sans-serif !important; }
    [data-testid="stMetricLabel"] { color: #92400E !important; }

    /* Schedule slot row highlight */
    .slot-row {
        display: flex;
        align-items: center;
        gap: 14px;
        background: #FFFFFF;
        border: 1px solid #FED7AA;
        border-radius: 14px;
        padding: 11px 16px;
        margin-bottom: 8px;
    }
    .slot-time { font-family: 'Fredoka', sans-serif; font-size: 1.1rem; color: #EA580C; font-weight: 600; min-width: 52px; }
    .slot-title { font-weight: 700; color: #7C2D12; }
    .slot-meta  { font-size: .82rem; color: #92400E; }

    /* Info / warning override */
    [data-testid="stAlert"] { border-radius: 14px !important; }

    /* Conflict warning */
    .conflict-item {
        background: #FEF3C7;
        border: 1.5px solid #FDE68A;
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: .9rem;
        color: #78350F;
    }

    /* ── Slot finder card ── */
    .slot-finder-card {
        background: #FFFFFF;
        border: 1.5px solid #FED7AA;
        border-radius: 18px;
        padding: 18px 20px;
    }

    /* Sidebar owner summary card */
    .owner-card {
        background: #FFFFFF;
        border: 1.5px solid #FDBA74;
        border-radius: 16px;
        padding: 14px 16px;
        margin-top: 12px;
    }
    .owner-card .owner-name { font-family: 'Fredoka', sans-serif; font-size: 1.15rem; color: #7C2D12; font-weight: 600; }
    .owner-card .owner-meta { font-size: .87rem; color: #92400E; margin-top: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SPECIES_ICON = {"dog": "🐶", "cat": "🐱", "other": "🐾"}


def pill(text: str, css_class: str) -> str:
    return f'<span class="pill {css_class}">{text}</span>'


def task_pill(t: Task) -> str:
    return (
        f'{t.type_emoji()} {t.title} &nbsp;'
        f'{pill(t.priority, f"pill-{t.priority}")}'
        f'<span style="font-size:.8rem;color:#92400E;"> {t.duration_minutes} min</span>'
    )


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state["owner"] = None

# ---------------------------------------------------------------------------
# Sidebar — Owner setup + persistence
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<h2 style="margin-bottom:2px;">🐾 PawPal+</h2>'
        '<p style="color:#92400E;font-size:.9rem;margin-top:0;">Your pet care planner</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    with st.expander("⚙️ Owner settings", expanded=st.session_state["owner"] is None):
        with st.form("owner_form"):
            owner_name  = st.text_input("Your name", value="Jordan")
            col_s, col_e = st.columns(2)
            with col_s:
                day_start = st.text_input("Day start", value="07:00")
            with col_e:
                day_end = st.text_input("Day end", value="19:00")
            owner_email = st.text_input("Email (optional)", value="")
            submitted   = st.form_submit_button("Save owner", type="primary", use_container_width=True)

        if submitted:
            st.session_state["owner"] = Owner(
                name=owner_name.strip(),
                email=owner_email.strip(),
                day_start=day_start.strip(),
                day_end=day_end.strip(),
            )
            st.success(f"Saved {owner_name}!")

    st.divider()

    # Persistence
    st.markdown("**💾 Save / Load data**")
    st.caption(f"File: `{DATA_FILE}`")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save", use_container_width=True):
            if st.session_state["owner"]:
                save_to_json(st.session_state["owner"], DATA_FILE)
                st.success("Saved!")
            else:
                st.error("No owner yet.")
    with c2:
        if st.button("📂 Load", use_container_width=True):
            loaded = load_from_json(DATA_FILE)
            if loaded:
                st.session_state["owner"] = loaded
                st.success(f"Loaded {loaded.name}!")
            else:
                st.warning(f"No `{DATA_FILE}` found.")

    # Owner summary
    if st.session_state["owner"]:
        o = st.session_state["owner"]
        st.markdown(
            f"""
            <div class="owner-card">
                <div class="owner-name">👤 {o.name}</div>
                <div class="owner-meta">
                    ⏰ {o.day_start} – {o.day_end} &nbsp;·&nbsp;
                    {o.available_minutes()} min/day<br>
                    🐾 {len(o.get_pets())} pet(s) registered
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="pawpal-hero">
        <div class="hero-icon">🐾</div>
        <div>
            <h1>Welcome to PawPal+</h1>
            <p>Take care of your pets — walks, meals, meds, and more. All planned, all on time.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------

if not st.session_state["owner"]:
    st.info("Open **Owner settings** in the sidebar, fill in your name and schedule window, then click **Save owner** — or use **Load** to restore a saved session.")
    st.stop()

owner: Owner = st.session_state["owner"]

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_pets, tab_tasks, tab_kanban, tab_schedule = st.tabs(
    ["🐶 Pets", "📋 Tasks", "🗂️ Kanban", "📅 Schedule"]
)

# ===========================================================================
# TAB 1 — Pets
# ===========================================================================

with tab_pets:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Your Pets</h2></div>',
        unsafe_allow_html=True,
    )

    # Add pet form inside expander so it doesn't dominate the page
    with st.expander("➕ Add a new pet", expanded=len(owner.get_pets()) == 0):
        with st.form("add_pet_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                pet_name = st.text_input("Pet name", placeholder="e.g. Biscuit")
            with c2:
                species  = st.selectbox("Species", ["dog", "cat", "other"],
                                         format_func=lambda s: f"{SPECIES_ICON.get(s, '🐾')} {s}")
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
                st.success(f"Added **{pet_name.strip()}** the {species}!")

    # Pet card grid — 3 per row
    pets = owner.get_pets()
    if pets:
        st.markdown(f"**{len(pets)} pet(s) registered**")
        cols_per_row = 3
        for row_start in range(0, len(pets), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, pet in zip(cols, pets[row_start:row_start + cols_per_row]):
                incomplete = len(pet.filter_tasks(completed=False))
                done       = len(pet.filter_tasks(completed=True))
                with col:
                    st.markdown(
                        f"""
                        <div class="pet-card">
                            <div class="pet-icon">{SPECIES_ICON.get(pet.species, '🐾')}</div>
                            <p class="pet-name">{pet.name}</p>
                            <p class="pet-meta">
                                {pet.species}{', ' + pet.breed if pet.breed else ''}<br>
                                🎂 {pet.age_years} yr
                                {' &nbsp;·&nbsp; ⚖️ ' + str(pet.weight_kg) + ' kg' if pet.weight_kg else ''}
                            </p>
                            <div class="pet-badge">📋 {incomplete} pending &nbsp; ✅ {done} done</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    else:
        st.info("No pets yet — add one above to get started.")

# ===========================================================================
# TAB 2 — Tasks
# ===========================================================================

with tab_tasks:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Pet Tasks</h2></div>',
        unsafe_allow_html=True,
    )

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet in the **Pets** tab first.")
    else:
        selected_name = st.selectbox(
            "Viewing tasks for:", [p.name for p in pets], key="task_pet_select",
            format_func=lambda n: f"{SPECIES_ICON.get(next((p.species for p in pets if p.name==n), ''), '🐾')} {n}",
        )
        selected_pet: Pet = next(p for p in pets if p.name == selected_name)

        left_col, right_col = st.columns([5, 3], gap="large")

        with right_col:
            # Add task panel
            st.markdown("#### ➕ Add task")
            with st.form("add_task_form"):
                task_title = st.text_input("Title", placeholder="e.g. Morning walk")
                task_type  = st.selectbox("Type", sorted(VALID_TASK_TYPES),
                                           format_func=lambda t: f"{TASK_TYPE_EMOJI.get(t, '🐾')} {t}")
                c1, c2 = st.columns(2)
                with c1:
                    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
                    priority = st.selectbox("Priority", ["high", "medium", "low"],
                                             format_func=lambda p: f"{PRIORITY_EMOJI.get(p, '')} {p}")
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
                    st.success(f"Added **{task_title.strip()}**!")

            # Mark complete
            incomplete = selected_pet.filter_tasks(completed=False)
            if incomplete:
                st.markdown("#### ✅ Mark complete")
                with st.form("mark_complete_form"):
                    choice = st.selectbox(
                        "Task",
                        [t.title for t in incomplete],
                        format_func=lambda ti: f"{TASK_TYPE_EMOJI.get(next((t.task_type for t in incomplete if t.title==ti), ''), '🐾')} {ti}",
                    )
                    mark_btn = st.form_submit_button("Mark & reschedule", use_container_width=True)
                if mark_btn:
                    target = next(t for t in incomplete if t.title == choice)
                    target.mark_complete()
                    next_t = target.next_occurrence()
                    if next_t:
                        selected_pet.add_task(next_t)
                        st.success(f"Done! Next **{target.title}** due **{next_t.due_date}**.")
                    else:
                        st.success(f"**{target.title}** marked complete.")

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
                    status_icon = "✅" if t.completed else "🔲"
                    st.markdown(
                        f"""
                        <div class="task-card">
                            <div class="task-title">{status_icon} {t.type_emoji()} {t.title}</div>
                            <div class="task-meta">
                                {PRIORITY_EMOJI.get(t.priority,'')} {t.priority} &nbsp;·&nbsp;
                                ⏱ {t.duration_minutes} min &nbsp;·&nbsp;
                                🕐 {t.preferred_time} &nbsp;·&nbsp;
                                🔁 {t.recurrence}
                                {' &nbsp;·&nbsp; 📅 due ' + t.due_date if t.due_date else ''}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# ===========================================================================
# TAB 3 — Kanban
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
        kb_name = st.selectbox(
            "Pet:", [p.name for p in pets], key="kanban_pet_select",
            format_func=lambda n: f"{SPECIES_ICON.get(next((p.species for p in pets if p.name==n),''), '🐾')} {n}",
        )
        kb_pet: Pet = next(p for p in pets if p.name == kb_name)

        tasks_all = kb_pet.get_tasks()
        if not tasks_all:
            st.info(f"{kb_pet.name} has no tasks yet. Add some in the Tasks tab.")
        else:
            st.caption("Use the buttons to move tasks between columns.")
            col_todo, col_inprog, col_done = st.columns(3, gap="medium")
            COLUMNS = [
                (col_todo,   "todo",        f"{STATUS_EMOJI['todo']} To Do"),
                (col_inprog, "in_progress", f"{STATUS_EMOJI['in_progress']} In Progress"),
                (col_done,   "done",        f"{STATUS_EMOJI['done']} Done"),
            ]
            ORDER = ["todo", "in_progress", "done"]

            for col_widget, status_key, label in COLUMNS:
                col_tasks = kb_pet.tasks_by_status(status_key)
                with col_widget:
                    st.markdown(
                        f'<div class="kanban-col-head">{label} ({len(col_tasks)})</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown('<div class="kanban-col">', unsafe_allow_html=True)
                    if not col_tasks:
                        st.caption("Nothing here yet.")
                    for t in col_tasks:
                        cur_idx = ORDER.index(status_key)
                        st.markdown(
                            f"""
                            <div class="task-card" style="margin-bottom:4px;">
                                <div class="task-title">{t.type_emoji()} {t.title}</div>
                                <div class="task-meta">
                                    {pill(t.priority, f'pill-{t.priority}')}
                                    &nbsp;⏱ {t.duration_minutes} min
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        b1, b2 = st.columns(2)
                        with b1:
                            if cur_idx > 0 and st.button("◀", key=f"kb_back_{t.task_id}", use_container_width=True):
                                t.set_status(ORDER[cur_idx - 1])
                                st.rerun()
                        with b2:
                            if cur_idx < 2 and st.button("▶", key=f"kb_next_{t.task_id}", use_container_width=True):
                                t.set_status(ORDER[cur_idx + 1])
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
# TAB 4 — Schedule
# ===========================================================================

with tab_schedule:
    st.markdown(
        '<div class="section-header"><div class="accent-bar"></div><h2>Daily Schedule</h2></div>',
        unsafe_allow_html=True,
    )

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet in the **Pets** tab first.")
    else:
        # Controls row
        ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 3])
        with ctrl1:
            sched_name = st.selectbox(
                "Pet:", [p.name for p in pets], key="sched_pet_select",
                format_func=lambda n: f"{SPECIES_ICON.get(next((p.species for p in pets if p.name==n),''), '🐾')} {n}",
            )
        with ctrl2:
            day = st.selectbox("Day:", ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"])
        with ctrl3:
            sort_mode_label = st.radio(
                "Sort by:",
                ["🔴 Priority (high → low)", "🕐 Time of day (morning → evening)"],
                horizontal=True, key="sort_mode",
            )
        sort_key = "time" if "Time" in sort_mode_label else "priority"

        sched_pet: Pet = next(p for p in pets if p.name == sched_name)

        generate_col, _ = st.columns([2, 5])
        with generate_col:
            gen_btn = st.button("📅 Generate schedule", type="primary", use_container_width=True)

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
                        f"**{sched_pet.name}** — {day.title()} &nbsp;·&nbsp; "
                        f"{len(schedule)} tasks &nbsp;·&nbsp; {total_used}/{budget} min"
                    )

                    # Metrics strip
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Tasks scheduled", len(schedule))
                    m2.metric("Time used",       f"{total_used} min")
                    m3.metric("Available",        f"{budget} min")
                    m4.metric("Skipped",          skipped)

                    st.divider()

                    # Schedule as styled slot cards (left) + plan text (right)
                    sched_col, explain_col = st.columns([3, 2], gap="large")

                    with sched_col:
                        st.markdown("#### Schedule")
                        for slot in schedule:
                            t = slot["task"]
                            st.markdown(
                                f"""
                                <div class="slot-row">
                                    <div class="slot-time">{slot['start_time']}</div>
                                    <div>
                                        <div class="slot-title">{t.type_emoji()} {t.title}</div>
                                        <div class="slot-meta">
                                            ⏱ {t.duration_minutes} min &nbsp;
                                            {PRIORITY_EMOJI.get(t.priority,'')} {t.priority} &nbsp;
                                            {STATUS_EMOJI.get(t.status,'')} {t.status}
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    with explain_col:
                        st.markdown("#### Plan explanation")
                        st.code(scheduler.explain_plan(), language=None)

                    # Cross-pet conflict detection
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
                            st.markdown(
                                f"#### ⚠️ {len(conflicts)} scheduling conflict(s) on {day.title()}"
                            )
                            st.caption(f"{owner.name} cannot attend two pets simultaneously.")
                            for c in conflicts:
                                msg = c.replace("CONFLICT: ", "")
                                st.markdown(
                                    f'<div class="conflict-item">⚠️ {msg}</div>',
                                    unsafe_allow_html=True,
                                )
                            st.info("**Tip:** Set one pet's tasks to a later preferred time to reduce overlap.")
                        else:
                            st.success(f"No schedule conflicts between {sched_pet.name} and other pets on {day.title()}.")

        # Next available slot finder
        st.divider()
        st.markdown("#### 🔍 Find next available slot")
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
                        st.success(f"Earliest **{int(slot_dur)}-min** opening: **{slot_result}**")
                    else:
                        st.error("No opening fits before the day ends.")
            st.markdown("</div>", unsafe_allow_html=True)
