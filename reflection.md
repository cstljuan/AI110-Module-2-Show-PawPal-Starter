# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    - Four-class design: 
        - `Owner` holds user identity and schedule window preferences.
        - `Pet` stores animal profile and owns a list of tasks.
        - `Task` models a single care action with type, duration, priority, and recurrence
        - `Scheduler` takes an owner + pet and produces an ordered daily plan from their task list.

- What classes did you include, and what responsibilities did you assign to each?
    - **Owner**: stores name, preferred day window (start/end time), and available hours per day. Single source of truth for scheduling constraints.
    - **Pet**: stores species, breed, age, weight. Owns the task list and knows how to add/remove tasks.
    - **Task**: models actions (walk, feeding, medication, grooming, enrichment). Carries title, type, duration in minutes, priority (low/medium/high), recurrence (daily/weekly/none), preferred time-of-day, and completion flag.
    - **Scheduler**: references Owner and Pet; runs `generate_schedule()` which sorts tasks by priority, assigns time slots from the owner's window, skips tasks that overflow available time, and returns an ordered plan with start times and reasoning notes.

**b. Design changes**

- Did your design change during implementation?
    - Yes. Originally `tasks` lived on `Scheduler` directly, but moved them to `Pet` because a pet's care needs exist independently of any scheduling run. Scheduler reads from `Pet.tasks`; it does not own them.
- If yes, describe at least one change and why you made it.
    - Added `preferred_time` field to `Task` (morning/afternoon/evening/any). Initial design only had priority. Realized medication tasks often have a required window, so time-of-day preference became a soft constraint that the scheduler honors before falling back to pure priority order.
    - Added `recurrence_days: list` to `Task` during implementation. Without it, `recurrence = "weekly"` had no way to specify *which* days — the scheduler would have no data to compare against `day_of_week`. This was a logic gap invisible in the UML but obvious once writing `_is_active_today()`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    - **Hard constraint:** total available minutes in the owner's day window. Tasks that push past the end time are dropped.
    - **Soft constraint 1 — priority:** high-priority tasks (medications, feedings) are always scheduled first regardless of duration.
    - **Soft constraint 2 — preferred time-of-day:** if a task requests "morning", the scheduler places it in the first third of the window when possible.
    - **Soft constraint 3 — recurrence:** daily tasks are always included; weekly tasks are included only on the designated day.
- How did you decide which constraints mattered most?
    - Hard time limit is non-negotiable. A schedule that overflows the day is useless. Priority rank follows because a missed medication is worse than a missed enrichment session. Time-of-day preference is honored only after priority is satisfied, since it's a comfort concern, not a health concern.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - Scheduler uses a greedy, priority-first insertion: it fills time slots from highest to lowest priority until the window is exhausted, then drops remaining tasks.
- Why is that tradeoff reasonable for this scenario?
    - For a single pet in a single day, greedy insertion is fast, predictable, and easy to explain to the owner. Optimal bin-packing would maximize total tasks scheduled but the explanation ("why is walk before feeding?") would be opaque. Owners care more about understanding the plan than fitting in one extra low-priority task.

- Describe a second tradeoff from Phase 3 (conflict detection).
    - `detect_conflicts()` checks whether two tasks' time windows overlap using the interval formula `a_start < b_end and b_start < a_end`. It does not check exact start-time equality — it checks whether any part of the duration overlaps.
- Why does this matter and what does it miss?
    - An exact-match check (`a_start == b_start`) would miss cases like Biscuit's 30-min walk (07:00–07:30) overlapping Mochi's 5-min medication (07:10–07:15). Overlap-duration detection catches those. The tradeoff is that the method only detects conflicts *after* both schedules are generated — it warns but does not re-plan. A smarter resolver would stagger pet schedules automatically; this version returns warnings and trusts the owner to adjust.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - Used AI for initial class design brainstorming (what attributes each class needs), for scaffolding method stubs with correct signatures, and for explaining algorithm tradeoffs (greedy vs. optimal scheduling; exact-match vs. overlap-interval conflict detection). In Phase 3, used AI to generate the `detect_conflicts()` implementation and the full pytest suite, then reviewed each test manually to confirm it actually tests the right behavior.
- What kinds of prompts or questions were most helpful?
    - "What constraints should a pet care scheduler consider and which matter most?" — forced a ranked list rather than a flat one.
    - "What edge cases could break a greedy priority scheduler for this scenario?" — surfaced the overflow/drop problem and the same-priority tie-break issue before coding.
    - "Which AI coding assistant features were most effective here?" — the most effective feature was code generation with constraints given upfront (e.g., "generate only this method, do not change the rest of the class"). That kept changes surgical rather than wholesale rewrites that drift from intended design.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - During Phase 3, the AI initially suggested adding `detect_conflicts()` as a `@staticmethod` that takes two arbitrary slot lists as arguments, with no reference to `self`. That would have been more flexible but it disconnects the method from the Scheduler's own schedule — callers would have to reach inside the scheduler to get `scheduler.schedule` and pass it manually. Instead, it was redesigned as an instance method that uses `self.schedule` directly, and accepts `other_schedules` as a list of other Scheduler objects. This made call sites read clearly: `sched_a.detect_conflicts(other_schedules=[sched_b])`.
- How did you evaluate or verify what the AI suggested?
    - Asked: "If I run the scheduler twice in one day, should the tasks change?" No, tasks are stable pet data, not scheduler artifacts. That confirmed tasks belong on `Pet`. For conflict detection, the test `test_detect_conflicts_same_pet_slots_never_flagged` was written specifically to verify that the `if pet_a == pet_b: continue` guard works — if that guard were absent, sequential same-pet slots would generate false positives.
- How did using a structured, phase-by-phase approach help you stay organized?
    - Each phase had a clear checkpoint ("CLI output is correct," "26 tests pass," "UI shows conflict warnings"). Those checkpoints acted as acceptance criteria. Working with an AI that generates code fast makes it tempting to keep adding features; the checkpoints forced a complete stop, verification, and reflection before moving on. This prevented the codebase from drifting into unverified territory.
- What does it mean to be the "lead architect" when collaborating with a powerful AI?
    - The AI generates code quickly and confidently, but it doesn't know which design decisions are load-bearing. The architect's job is to hold the invariants — "tasks live on Pet, not Scheduler," "conflict detection warns but does not re-plan," "sort_mode is a parameter, not a subclass" — and push back when generated code violates them. AI accelerates execution; the architect is responsible for coherence.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - Priority ordering: high-priority tasks appear before medium/low in the output plan.
    - Time overflow: tasks that would exceed available minutes are dropped, not truncated.
    - Daily vs. weekly recurrence: weekly tasks only appear when the day matches.
    - Preferred time-of-day placement: "morning" tasks land in the first time slots when priority is equal.
    - Empty task list: scheduler returns an empty plan without crashing.
- Why were these tests important?
    - Priority ordering and overflow are the core scheduling guarantees. If those fail, the app produces incorrect plans. Recurrence and empty-list tests prevent silent failures that only appear in real use.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    - High confidence for the happy path (normal task list, valid owner window). Moderate confidence for edge cases like tasks with identical priority and identical preferred time (tie-break order may be arbitrary).
- What edge cases would you test next if you had more time?
    - Two tasks with same priority and same preferred time: which wins and is the tie-break deterministic?
    - Available time exactly equal to one task's duration: is it included or excluded?
    - Task duration longer than the entire available day window: is it skipped gracefully?
    - Owner window crosses midnight (e.g., 22:00–06:00 next day): does time arithmetic hold?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - The responsibility split between `Pet` (owns tasks) and `Scheduler` (reads + orders tasks) is clean. It means the scheduler is stateless between runs. You can call `generate_schedule()` multiple times and always get a fresh plan from the same task list, which makes testing straightforward.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - Add a `time_window` field to `Task` (e.g., must happen between 08:00–09:00) to handle hard time constraints like insulin shots. The current `preferred_time` is a soft zone (morning/afternoon/evening); a real medical schedule needs exact windows with conflict detection between tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - AI accelerates brainstorming but doesn't know the difference between "where does this data logically live?" and "where is it convenient to put it?" Asking "who owns this data?" as a follow-up question to every AI-generated design suggestion is the fastest way to catch misplaced responsibility before it becomes a bug.
