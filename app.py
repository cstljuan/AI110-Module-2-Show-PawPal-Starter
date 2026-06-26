"""app.py — PawPal+ Streamlit UI, wired to pawpal_system.py."""

import pandas as pd
import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, VALID_TASK_TYPES

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Session state — initialise once per browser session
# ---------------------------------------------------------------------------
# st.session_state acts as a persistent dictionary across re-renders.
# We check "owner" before creating so a page refresh doesn't wipe data.

if "owner" not in st.session_state:
    st.session_state["owner"] = None          # set by the sidebar form below

# ---------------------------------------------------------------------------
# Sidebar — Owner setup
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🐾 PawPal+")
    st.subheader("Owner setup")

    with st.form("owner_form"):
        owner_name  = st.text_input("Your name", value="Jordan")
        day_start   = st.text_input("Day starts (HH:MM)", value="07:00")
        day_end     = st.text_input("Day ends (HH:MM)",   value="19:00")
        owner_email = st.text_input("Email (optional)", value="")
        submitted   = st.form_submit_button("Save owner")

    if submitted:
        # Creates or replaces the Owner object stored in session state.
        # Pets added previously are lost on re-save — expected behaviour.
        st.session_state["owner"] = Owner(
            name=owner_name.strip(),
            email=owner_email.strip(),
            day_start=day_start.strip(),
            day_end=day_end.strip(),
        )
        st.success(f"Saved {owner_name}!")

    # Show a summary when owner exists
    if st.session_state["owner"]:
        o = st.session_state["owner"]
        st.divider()
        st.markdown(f"**Owner:** {o.name}")
        st.markdown(f"**Window:** {o.day_start} to {o.day_end}")
        st.markdown(f"**Budget:** {o.available_minutes()} min/day")
        st.markdown(f"**Pets registered:** {len(o.get_pets())}")

# ---------------------------------------------------------------------------
# Guard — nothing renders until owner is set
# ---------------------------------------------------------------------------

if not st.session_state["owner"]:
    st.info("Fill in your name and schedule window in the sidebar, then click **Save owner**.")
    st.stop()

owner: Owner = st.session_state["owner"]

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_pets, tab_tasks, tab_schedule = st.tabs(["🐾 Pets", "📋 Tasks", "📅 Schedule"])

# ===========================================================================
# Tab 1 — Pets
# ===========================================================================

with tab_pets:
    st.header("Your Pets")

    with st.form("add_pet_form"):
        st.subheader("Add a pet")
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name")
            species  = st.selectbox("Species", ["dog", "cat", "other"])
        with col2:
            breed = st.text_input("Breed (optional)")
            age   = st.number_input("Age (years)", min_value=0.0, max_value=30.0, step=0.5, value=1.0)

        add_pet_btn = st.form_submit_button("Add pet")

    if add_pet_btn:
        if not pet_name.strip():
            st.error("Pet needs a name.")
        else:
            # --- BRIDGE: UI form data → Pet object → Owner.add_pet() ---
            new_pet = Pet(
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age_years=float(age),
            )
            owner.add_pet(new_pet)
            st.success(f"Added **{new_pet.name}** ({new_pet.species})!")

    # Display current pets
    pets = owner.get_pets()
    if pets:
        st.subheader(f"{len(pets)} pet(s) registered")
        for pet in pets:
            st.markdown(
                f"- **{pet.name}** — {pet.species}"
                + (f", {pet.breed}" if pet.breed else "")
                + f" | {pet.age_years} yr"
                + f" | **{len(pet.get_tasks())} task(s)**"
            )
    else:
        st.info("No pets yet. Add one above.")

# ===========================================================================
# Tab 2 — Tasks
# ===========================================================================

with tab_tasks:
    st.header("Pet Tasks")

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet in the Pets tab first.")
    else:
        selected_name = st.selectbox(
            "Select pet", [p.name for p in pets], key="task_pet_select"
        )
        # Find the actual Pet object from owner's list
        selected_pet: Pet = next(p for p in pets if p.name == selected_name)

        st.divider()

        # --- Add task form ---------------------------------------------------
        with st.form("add_task_form"):
            st.subheader(f"Add task for {selected_pet.name}")

            col1, col2, col3 = st.columns(3)
            with col1:
                task_title  = st.text_input("Task title", value="Morning walk")
                task_type   = st.selectbox("Type", sorted(VALID_TASK_TYPES))
            with col2:
                duration      = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
                priority      = st.selectbox("Priority", ["high", "medium", "low"])
            with col3:
                preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "any"])
                recurrence     = st.selectbox("Recurrence", ["daily", "weekly", "none"])

            # Always render multiselect; values only matter when recurrence == "weekly"
            recurrence_days = st.multiselect(
                "Days (only used when recurrence = weekly)",
                ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            )

            add_task_btn = st.form_submit_button("Add task")

        if add_task_btn:
            if not task_title.strip():
                st.error("Task needs a title.")
            else:
                # --- BRIDGE: form data → Task object → Pet.add_task() ---
                new_task = Task(
                    title=task_title.strip(),
                    task_type=task_type,
                    duration_minutes=int(duration),
                    priority=priority,
                    preferred_time=preferred_time,
                    recurrence=recurrence,
                    recurrence_days=recurrence_days if recurrence == "weekly" else [],
                )
                selected_pet.add_task(new_task)
                st.success(f"Added **{new_task.title}** to {selected_pet.name}!")

        # --- Task table with filter -------------------------------------------
        tasks = selected_pet.get_tasks()
        if tasks:
            st.divider()
            col_hdr, col_filt = st.columns([2, 2])
            with col_hdr:
                st.subheader(f"{selected_pet.name}'s tasks ({len(tasks)} total)")
            with col_filt:
                filter_opt = st.radio(
                    "Show:",
                    ["All", "Incomplete", "Completed"],
                    horizontal=True,
                    key="task_filter",
                )

            completed_map = {"All": None, "Incomplete": False, "Completed": True}
            filtered = selected_pet.filter_tasks(completed=completed_map[filter_opt])

            if filtered:
                rows = [
                    {
                        "Title":          t.title,
                        "Type":           t.task_type,
                        "Duration (min)": t.duration_minutes,
                        "Priority":       t.priority,
                        "Preferred time": t.preferred_time,
                        "Recurrence":     t.recurrence,
                        "Done":           "✓" if t.completed else "",
                    }
                    for t in filtered
                ]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info(f"No {filter_opt.lower()} tasks for {selected_pet.name}.")

            # --- Mark complete + auto-generate next occurrence ---------------
            st.divider()
            st.subheader("Mark task complete")
            incomplete = selected_pet.filter_tasks(completed=False)
            if not incomplete:
                st.info("All tasks are already marked complete.")
            else:
                with st.form("mark_complete_form"):
                    task_choice = st.selectbox(
                        "Task to complete",
                        [t.title for t in incomplete],
                        key="mark_complete_select",
                    )
                    mark_btn = st.form_submit_button("Mark complete & schedule next")

                if mark_btn:
                    target = next(t for t in incomplete if t.title == task_choice)
                    target.mark_complete()
                    next_t = target.next_occurrence()
                    if next_t:
                        selected_pet.add_task(next_t)
                        st.success(
                            f"**'{target.title}'** marked complete. "
                            f"Next occurrence ({target.recurrence}) added — due **{next_t.due_date}**."
                        )
                    else:
                        st.success(
                            f"**'{target.title}'** marked complete. "
                            f"Recurrence is 'none' — no follow-up task created."
                        )
        else:
            st.info(f"No tasks for {selected_pet.name} yet.")

# ===========================================================================
# Tab 3 — Schedule
# ===========================================================================

with tab_schedule:
    st.header("Generate Daily Schedule")

    pets = owner.get_pets()
    if not pets:
        st.info("Add a pet in the Pets tab first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            sched_pet_name = st.selectbox(
                "Select pet", [p.name for p in pets], key="sched_pet_select"
            )
        with col2:
            day = st.selectbox(
                "Day of week",
                ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            )

        sched_pet: Pet = next(p for p in pets if p.name == sched_pet_name)

        # Sort mode toggle — passes through to generate_schedule()
        sort_mode_label = st.radio(
            "Sort tasks by:",
            ["Priority (high → low)", "Time of day (morning → evening)"],
            horizontal=True,
            key="sort_mode",
        )
        sort_key = "time" if "Time" in sort_mode_label else "priority"

        if st.button("Generate schedule", type="primary"):
            if not sched_pet.get_tasks():
                st.warning(f"No tasks for {sched_pet.name}. Add some in the Tasks tab.")
            else:
                # --- BRIDGE: UI inputs → Scheduler.generate_schedule() ---
                scheduler = Scheduler(owner=owner, pet=sched_pet, day_of_week=day)
                schedule  = scheduler.generate_schedule(sort_mode=sort_key)

                if not schedule:
                    st.warning(
                        "No tasks qualify for this day. "
                        "Check recurrence settings in the Tasks tab."
                    )
                else:
                    st.success(
                        f"Schedule for **{sched_pet.name}** on **{day.title()}** — "
                        f"{len(schedule)} task(s) planned. "
                        f"Sorted by: **{sort_mode_label.split(' (')[0].lower()}**."
                    )

                    # --- Metrics row ---
                    total_used  = sum(s["task"].duration_minutes for s in schedule)
                    budget      = owner.available_minutes()
                    skipped     = len(sched_pet.get_tasks()) - len(schedule)
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Tasks scheduled", len(schedule))
                    m2.metric("Time used",        f"{total_used} min")
                    m3.metric("Time available",   f"{budget} min")
                    m4.metric("Tasks skipped",    skipped)

                    st.divider()

                    # --- Schedule table ---
                    rows = [
                        {
                            "Start":    slot["start_time"],
                            "Task":     slot["task"].title,
                            "Type":     slot["task"].task_type,
                            "Duration": f"{slot['task'].duration_minutes} min",
                            "Priority": slot["task"].priority,
                            "Reason":   slot["reason"],
                        }
                        for slot in schedule
                    ]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                    # --- Plain-text explanation ---
                    st.subheader("Plan explanation")
                    st.code(scheduler.explain_plan(), language=None)

                    # --- Cross-pet conflict detection -------------------------
                    other_pets = [p for p in owner.get_pets() if p.name != sched_pet.name]
                    if other_pets:
                        st.divider()
                        other_scheds = []
                        for op in other_pets:
                            os_sched = Scheduler(owner=owner, pet=op, day_of_week=day)
                            os_sched.generate_schedule(sort_mode=sort_key)
                            other_scheds.append(os_sched)

                        conflicts = scheduler.detect_conflicts(other_schedules=other_scheds)

                        if conflicts:
                            st.subheader("⚠️ Scheduling Conflicts")
                            st.caption(
                                f"{owner.name} cannot attend to two pets simultaneously. "
                                f"The following tasks overlap across pets on **{day.title()}**:"
                            )
                            for c in conflicts:
                                st.warning(c)
                            st.info(
                                "**Tip:** Stagger pets' schedule windows "
                                "(e.g., set one pet's tasks to 'afternoon') "
                                "to resolve conflicts."
                            )
                        else:
                            st.success(
                                f"No scheduling conflicts detected between {sched_pet.name} "
                                f"and other pets on {day.title()}."
                            )
