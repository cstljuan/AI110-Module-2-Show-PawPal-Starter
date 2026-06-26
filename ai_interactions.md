# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (Claude Code) to make multi-step changes autonomously.

**What task did you give the agent?**

Implement four Module 2 stretch challenges on top of the working PawPal+ app, in one pass:
1. A third scheduling algorithm beyond the basics (next available slot).
2. Data persistence to a `data.json` file.
3. Priority-based scheduling plus a Kanban board.
4. Professional UI/output formatting, using the **UI/UX Pro Max** skill and a warm orange/brown palette taken from reference pet-app mockups.

Standing instruction: after each change, keep `README.md` and `reflection.md` (and the other docs) in sync.

**What did the agent do?**

- **Ran the UI/UX Pro Max skill** (`search.py "pet care mobile app ..." --design-system`) to generate a design system: Fredoka/Nunito fonts, vibrant-playful style, orange palette.
- **`pawpal_system.py`** — added: `Task.status` (Kanban) + `set_status()` + `type_emoji()`; `Pet.tasks_by_status()`; `to_dict()`/`from_dict()` on Task/Pet/Owner; `Scheduler.find_next_available_slot()`; module-level `save_to_json()`/`load_from_json()`; emoji constant maps.
- **`cli_format.py`** (new) — `tabulate`-based `format_schedule_table()`, `format_kanban()`, `format_task_list()` with emoji indicators.
- **`app.py`** — full themed rewrite: injected CSS (orange/brown palette, fonts, cards, badges, hero), a new **Kanban** tab with move buttons, sidebar **Save/Load** persistence, and a **next-available-slot** widget.
- **`.streamlit/config.toml`** (new) — base theme colors.
- **`main.py`** — rewrote the CLI demo to showcase all four features with the formatted output.
- **`tests/test_pawpal.py`** — added 13 tests (slot finder, Kanban status, dict round-trips, JSON save/load), bringing the suite from 26 → **39 passing**.
- **Docs** — updated `README.md` (Features, a new "Module 2 Extensions" section, persistence workflow, Smarter Scheduling, Testing, Demo Walkthrough), `reflection.md` (two new tradeoffs), `diagrams/uml_final.mmd` (new methods/relationships), `requirements.txt` (`tabulate`), and `.gitignore` (`data.json`).
- Ran `py_compile`, the full `pytest` suite, `python main.py`, and a headless Streamlit boot (HTTP 200) to verify.

**What did you have to verify or fix manually?**

- **Palette override:** the skill recommended a **blue** CTA (`#2563EB`). The requested palette was orange/brown only, so the blue was swapped for brown (`#7C2D12`). *Lesson: the skill gives a strong default, but brand/owner constraints win.*
- **Windows emoji encoding:** emojis printed as `?` in the terminal until `sys.stdout.reconfigure(encoding="utf-8")` was added at the top of `main.py`.
- **Backward-compatibility of the new `status` field:** rather than replacing the existing `completed` boolean (which the scheduler, filters, and older tests depend on), `status` was added alongside it and kept in sync (`set_status("done")` ⇒ `completed=True`; `__post_init__` reconciles the two on load). This kept all 26 prior tests green while adding the Kanban capability.
- **Persistence library choice:** rejected `marshmallow` in favor of custom `to_dict`/`from_dict` — verified the decision by confirming every field is JSON-native and the graph is small (documented in `reflection.md` §2b).

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
