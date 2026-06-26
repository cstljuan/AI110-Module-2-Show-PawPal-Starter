# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

| Feature | Where | How it works |
|---------|-------|--------------|
| **Owner setup** | Sidebar | Name, email, and daily window (HH:MM) stored in `st.session_state` |
| **Multi-pet support** | Pets tab | Register unlimited pets; each owns its own task list |
| **Task management** | Tasks tab | Add tasks with type, duration, priority, preferred time, and recurrence |
| **Completion filter** | Tasks tab | Toggle All / Incomplete / Completed via `Pet.filter_tasks()` |
| **Mark complete + auto-reschedule** | Tasks tab | Mark a task done; `Task.next_occurrence()` creates the next instance with an updated due date |
| **Priority-first scheduling** | Schedule tab | `Scheduler.sort_by_priority()` — high → medium → low, morning preferred when priority ties |
| **Time-of-day scheduling** | Schedule tab | `Scheduler.sort_by_time()` — morning → afternoon → evening toggle via UI radio button |
| **Time-budget enforcement** | Schedule tab | `Scheduler.filter_by_time()` greedy drop: tasks that exceed available minutes are skipped entirely |
| **Daily recurrence** | Schedule tab | `recurrence="daily"` tasks appear every day via `Scheduler._is_active_today()` |
| **Weekly recurrence** | Schedule tab | `recurrence="weekly"` tasks appear only on selected days in `Task.recurrence_days` |
| **Conflict detection** | Schedule tab | `Scheduler.detect_conflicts()` checks for overlapping time windows across pets (interval formula) |
| **Plan explanation** | Schedule tab | `Scheduler.explain_plan()` prints a human-readable text summary of each slot and its reasoning |
| **Next available slot** 🆕 | Schedule tab | `Scheduler.find_next_available_slot()` finds the earliest free gap that fits a given duration |
| **Kanban board** 🆕 | Kanban tab | Drag tasks across To Do → In Progress → Done via `Task.set_status()` / `Pet.tasks_by_status()` |
| **JSON persistence** 🆕 | Sidebar Save/Load | `save_to_json()` / `load_from_json()` remember pets and tasks between runs in `data.json` |
| **Professional formatting** 🆕 | CLI + UI | `tabulate` grid tables, emoji indicators, warm orange/brown theme (Fredoka/Nunito fonts) |
| **39 automated tests** | `tests/` | Full pytest suite covering all behaviors above |

## 🌟 Module 2 Extensions (Stretch Challenges)

These four challenges build on the core app. Files touched are listed per challenge.

### Challenge 1 — Advanced algorithm: next available slot

`Scheduler.find_next_available_slot(duration_minutes, after_time=None)` scans the
already-generated schedule for free gaps and returns the earliest `HH:MM` that fits
the requested duration (or `None` if the day is full). An optional `after_time`
floor lets a caller ask "what's the next opening *after* 12:00?". Back-to-back
bookings push the answer to the end of the last task; a full day returns `None`.

- **Files modified:** `pawpal_system.py` (method), `main.py` (demo), `app.py` (UI widget), `tests/test_pawpal.py` (4 tests)

### Challenge 2 — Data persistence (`data.json`)

PawPal+ remembers pets and tasks between runs using **custom dictionary conversion**
rather than a third-party serializer:

- `Task.to_dict()` / `Task.from_dict()`, `Pet.to_dict()` / `Pet.from_dict()`, `Owner.to_dict()` / `Owner.from_dict()` round-trip the whole object graph (Owner → Pets → Tasks).
- Module-level `save_to_json(owner, path="data.json")` and `load_from_json(path="data.json")` write/read the file; `load_from_json` returns `None` if the file is missing.

**Why custom dicts instead of marshmallow?** The object graph is small and fully
owned by us, and every field is JSON-native (str/int/float/bool/list). A hand-written
round-trip is dependency-free, easy to debug, and keeps the schema in one place.
`marshmallow` earns its keep when you need declarative schema validation, partial
loads, or polymorphic nesting — none of which this app needs. (If validation were
required, marshmallow `Schema` classes per model with `@post_load` hooks to rebuild
objects would be the path; the trade-off is an extra dependency and more ceremony.)

**Persistence workflow:**
1. Build pets/tasks in the UI (or run `python main.py`).
2. Click **💾 Save** in the sidebar (or `save_to_json(owner)` in code) → writes `data.json`.
3. On a later run, click **📂 Load** (or `load_from_json()`) → the Owner, pets, tasks, **and Kanban status** are restored exactly.

- **Files modified:** `pawpal_system.py` (to_dict/from_dict + save/load), `app.py` (Save/Load buttons), `main.py` (round-trip demo), `tests/test_pawpal.py` (4 tests), `.gitignore` (`data.json` is runtime data)

### Challenge 3 — Priority scheduling + Kanban board

- **Priority scheduling:** `Task.priority` (`low`/`medium`/`high`) drives `Scheduler.sort_by_priority()` — high first, then preferred time-of-day as the tie-break. The UI radio toggles between *priority* and *time-of-day* sort modes (`generate_schedule(sort_mode=...)`). See the CLI examples below for both orderings on the same task list.
- **Kanban board:** a new `Task.status` field (`todo` / `in_progress` / `done`) with `set_status()` (kept in sync with the `completed` flag) and `Pet.tasks_by_status()`. The **🗂️ Kanban** tab renders three columns with ◀ Back / Next ▶ buttons to move tasks; the CLI renders the same board with `cli_format.format_kanban()`.

- **Files modified:** `pawpal_system.py` (`status`, `set_status`, `tasks_by_status`), `app.py` (Kanban tab), `cli_format.py` (`format_kanban`), `main.py` (demo), `tests/test_pawpal.py` (5 tests)

### Challenge 4 — Professional UI & output formatting (UI/UX Pro Max skill)

Design direction generated with the **UI/UX Pro Max** skill
(`python .claude/skills/ui-ux-pro-max/scripts/search.py "pet care mobile app ..." --design-system`):

| Token | Value | Use |
|-------|-------|-----|
| Primary | `#F97316` (orange-500) | buttons, accents |
| Secondary | `#FB923C` / `#FDBA74` | hovers, gradients |
| Brown | `#7C2D12` / `#9A3412` | text, primary-button hover |
| Background | `#FFF7ED` (orange-50) | warm cream app background |
| Fonts | **Fredoka** (headings) + **Nunito** (body) | playful, friendly |
| Style | Vibrant & playful, rounded cards, 200ms hovers | matches a pet app |

- **CLI formatting** (`cli_format.py`): `tabulate` (`rounded_grid`) tables for schedules, task lists, and the Kanban board; emoji indicators for task type (🦮🍖💊🛁🧸), priority (🔴🟡🟢), and status (📋🔄✅). `main.py` reconfigures stdout to UTF-8 so emoji render in the Windows terminal.
- **Streamlit theme** (`.streamlit/config.toml` + injected CSS in `app.py`): orange/brown palette, Google Fonts import, rounded `.pawpal-card` components, gradient hero header, pill badges, and styled Kanban columns.

- **Files modified:** `cli_format.py` (new), `.streamlit/config.toml` (new), `app.py` (theme CSS + emoji labels), `pawpal_system.py` (emoji constant maps + `Task.type_emoji()`), `requirements.txt` (`tabulate`)

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt   # streamlit, pytest, tabulate
```

### Run it

```bash
streamlit run app.py     # launch the web UI
python main.py           # run the CLI demo (formatted tables + all features)
python -m pytest         # run the 39-test suite
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Generated by running `python main.py`. Owner Jordan has two pets (Biscuit the dog and Mochi the cat), window 07:00–19:00 on a Monday. Output is formatted with `tabulate` + emoji indicators (`cli_format.py`).

```
============================================================
  PawPal+ — Today's Schedule (Monday)
============================================================
Owner: Jordan  |  Window: 07:00–19:00

📅  Biscuit (dog) — Monday   [130/720 min used]
╭─────────┬──────────────┬─────────────────────────┬────────────┬────────────┬──────────╮
│ Start   │ Type         │ Task                    │ Duration   │ Priority   │ Status   │
├─────────┼──────────────┼─────────────────────────┼────────────┼────────────┼──────────┤
│ 07:00   │ 🦮 walk       │ Morning walk            │ 30 min     │ 🔴 high     │ 📋 todo   │
│ 07:30   │ 🍖 feeding    │ Breakfast feeding       │ 10 min     │ 🔴 high     │ 📋 todo   │
│ 07:40   │ 💊 medication │ Heartworm medication    │ 5 min      │ 🔴 high     │ 📋 todo   │
│ 07:45   │ 🍖 feeding    │ Evening feeding         │ 10 min     │ 🔴 high     │ 📋 todo   │
│ 07:55   │ 🦮 walk       │ Afternoon walk          │ 45 min     │ 🟡 medium   │ 📋 todo   │
│ 08:40   │ 🧸 enrichment │ Fetch / enrichment play │ 30 min     │ 🟡 medium   │ 📋 todo   │
╰─────────┴──────────────┴─────────────────────────┴────────────┴────────────┴──────────╯
```

### Kanban board (`cli_format.format_kanban`)

```
🗂️  Kanban — Biscuit
╭───────────────────────────┬─────────────────────┬────────────────╮
│ 📋 TO DO (4)               │ 🔄 IN PROGRESS (2)   │ ✅ DONE (1)     │
├───────────────────────────┼─────────────────────┼────────────────┤
│ 💊 Heartworm medication    │ 🍖 Breakfast feeding │ 🦮 Morning walk │
│ 🍖 Evening feeding         │ 🦮 Afternoon walk    │                │
│ 🛁 Grooming brush          │                     │                │
│ 🧸 Fetch / enrichment play │                     │                │
╰───────────────────────────┴─────────────────────┴────────────────╯
```

### Next available slot + persistence

```
  Earliest opening for a 15-min task: 07:55
  Earliest opening for a 30-min task: 07:55
  Earliest 20-min opening after 12:00: 12:00

  Saved owner + 2 pets + 12 tasks -> data.json
  Reloaded owner: Jordan
  Pets restored:  ['Biscuit', 'Mochi']
  Kanban status survived round-trip: 'Morning walk' -> done
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with verbose output:
python -m pytest -v
```

**What the tests cover:**

| Category | Tests | What's verified |
|----------|-------|-----------------|
| Task lifecycle | `test_mark_complete_*` | `mark_complete()` sets flag; idempotent on repeat calls |
| Pet CRUD | `test_add_task_*`, `test_remove_task_*` | Task count changes correctly; removing missing ID is a no-op |
| Owner time window | `test_available_minutes_*`, `test_set_schedule_window_*` | Budget math; window update persists |
| Scheduling core | `test_generate_schedule_*` | Priority order; overflow drop; empty list |
| Recurrence | `test_weekly_task_*`, `test_task_with_recurrence_none_*` | Weekly tasks gated by day; `none` tasks never scheduled |
| Sorting | `test_sort_by_time_*` | `sort_by_time()` chronological order; priority tie-break |
| Next occurrence | `test_next_occurrence_*`, `test_handle_completion_*` | Daily +1 day, weekly +7 days, `none` returns None; `handle_completion` marks done + returns fresh task |
| Filtering | `test_filter_tasks_*` | Completed/incomplete/all filters return correct subsets |
| Conflict detection | `test_detect_conflicts_*` | Cross-pet overlap flagged; empty schedule = no conflicts; same-pet slots never flagged |
| Next available slot 🆕 | `test_next_slot_*` | Empty schedule → day start; back-to-back → end of last task; `after_time` floor; full day → `None` |
| Kanban status 🆕 | `test_set_status_*`, `test_task_default_status_*`, `test_tasks_by_status_*` | Default `todo`; status moves sync `completed`; invalid status rejected; column grouping |
| Persistence 🆕 | `test_*_round_trip_*`, `test_save_and_load_json_*`, `test_load_json_missing_*` | Task/Owner dict round-trip; JSON save+load; missing file → `None` |

**Confidence level: ⭐⭐⭐⭐⭐ (5/5)**
All 39 tests pass. The Phase-4 additions (slot finder, Kanban status sync, JSON round-trip) are each covered by dedicated tests, including the edge cases that motivated them: back-to-back bookings, status/`completed` consistency, and a missing data file. Remaining moderate-confidence area is identical-priority + identical-preferred-time tie-breaks (deterministic via Python's stable sort, but not asserted).

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.3, pluggy-1.6.0
collected 39 items

tests/test_pawpal.py::test_mark_complete_sets_completed_true PASSED      [  2%]
tests/test_pawpal.py::test_mark_complete_is_idempotent PASSED            [  5%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [  7%]
tests/test_pawpal.py::test_add_multiple_tasks_increases_count PASSED     [ 10%]
tests/test_pawpal.py::test_remove_task_decreases_count PASSED            [ 12%]
tests/test_pawpal.py::test_remove_nonexistent_task_does_not_crash PASSED [ 15%]
tests/test_pawpal.py::test_available_minutes_correct PASSED              [ 17%]
tests/test_pawpal.py::test_set_schedule_window_updates_times PASSED      [ 20%]
tests/test_pawpal.py::test_generate_schedule_priority_order PASSED       [ 23%]
tests/test_pawpal.py::test_generate_schedule_drops_overflow_tasks PASSED [ 25%]
tests/test_pawpal.py::test_generate_schedule_empty_task_list PASSED      [ 28%]
tests/test_pawpal.py::test_weekly_task_excluded_on_wrong_day PASSED      [ 30%]
tests/test_pawpal.py::test_weekly_task_included_on_correct_day PASSED    [ 33%]
tests/test_pawpal.py::test_task_with_recurrence_none_excluded PASSED     [ 35%]
tests/test_pawpal.py::test_sort_by_time_chronological_order PASSED       [ 38%]
tests/test_pawpal.py::test_sort_by_time_priority_breaks_ties PASSED      [ 41%]
tests/test_pawpal.py::test_next_occurrence_daily_advances_one_day PASSED [ 43%]
tests/test_pawpal.py::test_next_occurrence_weekly_advances_seven_days PASSED [ 46%]
tests/test_pawpal.py::test_next_occurrence_none_returns_none PASSED      [ 48%]
tests/test_pawpal.py::test_handle_completion_marks_task_done_and_returns_next PASSED [ 51%]
tests/test_pawpal.py::test_filter_tasks_completed_returns_only_done PASSED [ 53%]
tests/test_pawpal.py::test_filter_tasks_incomplete_returns_only_pending PASSED [ 56%]
tests/test_pawpal.py::test_filter_tasks_none_returns_all PASSED          [ 58%]
tests/test_pawpal.py::test_detect_conflicts_finds_cross_pet_overlap PASSED [ 61%]
tests/test_pawpal.py::test_detect_conflicts_no_warning_when_other_schedule_empty PASSED [ 64%]
tests/test_pawpal.py::test_detect_conflicts_same_pet_slots_never_flagged PASSED [ 66%]
tests/test_pawpal.py::test_next_slot_empty_schedule_returns_day_start PASSED [ 69%]
tests/test_pawpal.py::test_next_slot_after_back_to_back_bookings PASSED  [ 71%]
tests/test_pawpal.py::test_next_slot_honors_after_time_floor PASSED      [ 74%]
tests/test_pawpal.py::test_next_slot_returns_none_when_no_room PASSED    [ 76%]
tests/test_pawpal.py::test_task_default_status_is_todo PASSED            [ 79%]
tests/test_pawpal.py::test_set_status_moves_task_and_syncs_completed PASSED [ 82%]
tests/test_pawpal.py::test_mark_complete_also_sets_done_status PASSED    [ 84%]
tests/test_pawpal.py::test_set_status_rejects_invalid_value PASSED       [ 87%]
tests/test_pawpal.py::test_tasks_by_status_groups_correctly PASSED       [ 89%]
tests/test_pawpal.py::test_task_dict_round_trip_preserves_fields PASSED  [ 92%]
tests/test_pawpal.py::test_owner_dict_round_trip_preserves_nested_pets_and_tasks PASSED [ 94%]
tests/test_pawpal.py::test_save_and_load_json_round_trip PASSED          [ 97%]
tests/test_pawpal.py::test_load_json_missing_file_returns_none PASSED    [100%]

============================= 39 passed in 0.12s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_by_priority()` | High → medium → low; ties broken by preferred time-of-day (morning first). Used by default in `generate_schedule()`. |
| Sort by time of day | `Scheduler.sort_by_time()` | Morning → afternoon → evening → any; ties broken by priority. Alternative ordering for display or comparison. |
| Time-budget filtering | `Scheduler.filter_by_time()` | Greedy inclusion: tasks are added in priority order until available minutes run out; overflow tasks are dropped entirely, not truncated. |
| Filter by completion | `Pet.filter_tasks(completed=True/False)` | Returns completed or incomplete tasks for a pet; `None` returns all. Useful for showing what's left in the day. |
| Recurring tasks — daily | `Scheduler._is_active_today()` | Tasks with `recurrence="daily"` are always included in the schedule. |
| Recurring tasks — weekly | `Scheduler._is_active_today()` | Tasks with `recurrence="weekly"` are included only when `day_of_week` matches one of `Task.recurrence_days`. |
| Auto-generate next occurrence | `Task.next_occurrence()`, `Scheduler.handle_completion()` | Marks a task complete and creates a new Task instance with `due_date` advanced by 1 day (daily) or 7 days (weekly). |
| Conflict detection | `Scheduler.detect_conflicts(other_schedules)` | Checks for overlapping time windows across pets using the interval formula `a_start < b_end and b_start < a_end`. Returns a list of warning strings; same-pet sequential slots are skipped (they never overlap by construction). |
| Next available slot | `Scheduler.find_next_available_slot(duration, after_time)` | Scans booked intervals for the first gap that fits `duration`; honors an optional `after_time` floor; returns `None` when the day is full. |
| Kanban status | `Task.set_status()`, `Pet.tasks_by_status()` | Tracks each task across `todo` / `in_progress` / `done`; `set_status` keeps the `completed` flag in sync. |
| Persistence | `save_to_json()`, `load_from_json()`, `*.to_dict()` / `from_dict()` | Round-trips the Owner→Pet→Task graph to `data.json` via custom dict conversion (no third-party serializer). |

## 📸 Demo Walkthrough

### Example workflow: Jordan + two pets

**Step 1 — Owner setup**
Open the app (`streamlit run app.py`). In the sidebar, enter name "Jordan", window 07:00–19:00, and click **Save owner**. The sidebar immediately shows the owner's daily budget (720 min).

**Step 2 — Register pets**
Go to the **Pets** tab. Add "Biscuit" (dog, Golden Retriever, 3 yr) and "Mochi" (cat, Domestic Shorthair, 5 yr). Both appear in the registered pets list.

**Step 3 — Add tasks**
Go to the **Tasks** tab. Select Biscuit. Add a "Morning walk" (walk, 30 min, high priority, morning, daily). Add an "Afternoon walk" (walk, 45 min, medium, afternoon, daily). Toggle the **Incomplete** filter to verify both tasks show up. Use **Mark complete** to mark the morning walk done — the app creates a new copy with tomorrow's due date and confirms it in a success banner.

**Step 4 — Generate schedule**
Go to the **Schedule** tab. Select Biscuit, Monday. Choose a sort mode (**Priority** or **Time of day**). Click **Generate schedule**. The app shows metrics (tasks scheduled, minutes used, tasks skipped), an emoji-coded schedule table, and the plain-text plan explanation.

**Step 5 — Find the next free slot**
Below the schedule, enter a task length (e.g., 30 min) and click **Find slot**. The app calls `find_next_available_slot()` and reports the earliest opening (optionally after a given time).

**Step 6 — Kanban board**
Open the **🗂️ Kanban** tab, pick a pet, and use ◀ Back / Next ▶ to move tasks across **To Do → In Progress → Done**. Moving a task to *Done* also marks it completed.

**Step 7 — Conflict detection**
With both pets having tasks, generating Biscuit's schedule also builds Mochi's and runs `detect_conflicts()`. Since both start at 07:00, Jordan can't attend both at once — the app shows yellow warning banners per overlap with a tip to stagger preferred times.

**Step 8 — Save & reload**
Click **💾 Save** in the sidebar to write `data.json`. Close and reopen the app, click **📂 Load**, and all pets, tasks, and Kanban statuses come back exactly.

### CLI: priority-first vs time-of-day sort (Challenge 3)

Same Biscuit task list, two `sort_mode` values. Note **Evening feeding** (high priority, evening): it ranks **4th** under priority sort but **last** under time sort — priority overrides preferred time as the primary key.

```
Sort = PRIORITY (high → low, then time):          Sort = TIME OF DAY (morning → evening, then priority):
  07:00  🦮 Morning walk          🔴 high            07:00  🦮 Morning walk          🔴 high  (morning)
  07:30  🍖 Breakfast feeding     🔴 high            07:30  🍖 Breakfast feeding     🔴 high  (morning)
  07:40  💊 Heartworm medication  🔴 high            07:40  💊 Heartworm medication  🔴 high  (morning)
  07:45  🍖 Evening feeding       🔴 high            07:45  🦮 Afternoon walk        🟡 med   (afternoon)
  07:55  🦮 Afternoon walk        🟡 medium          08:30  🧸 Fetch / enrichment    🟡 med   (afternoon)
  08:40  🧸 Fetch / enrichment    🟡 medium          09:00  🍖 Evening feeding       🔴 high  (evening)
```

The full `python main.py` output (formatted schedule tables, Kanban board, next-slot finder, persistence round-trip, and the 7 cross-pet conflicts) is shown in the **🖥️ Sample Output** section above.

### UI design

The Streamlit UI uses the warm orange/brown palette and Fredoka/Nunito typography recommended by the UI/UX Pro Max skill, matching the friendly, rounded look of the reference pet-app mockups: a gradient hero header, rounded pet/task cards, pill badges for priority, and dashed Kanban columns.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
