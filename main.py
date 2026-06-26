"""main.py — CLI demo for PawPal+. Run: python main.py

Demonstrates the full backend: scheduling, priority sorting, next-available-slot,
Kanban board, JSON persistence, and cross-pet conflict detection. Output is
formatted with the tabulate-based helpers in cli_format.py.
"""

import sys

# Render emoji correctly in the Windows terminal (default code page can't encode them).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    save_to_json,
    load_from_json,
)
from cli_format import format_schedule_table, format_kanban, format_task_list


def banner(text: str) -> None:
    """Print a section banner."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def build_owner() -> Owner:
    """Construct the demo owner with two pets and their tasks."""
    jordan = Owner(name="Jordan", email="jordan@example.com",
                   day_start="07:00", day_end="19:00")

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age_years=3.0)
    mochi = Pet(name="Mochi", species="cat", breed="Domestic Shorthair", age_years=5.0)
    jordan.add_pet(biscuit)
    jordan.add_pet(mochi)

    # --- Biscuit (dog) ---
    biscuit.add_task(Task("Morning walk", "walk", 30, priority="high", preferred_time="morning"))
    biscuit.add_task(Task("Breakfast feeding", "feeding", 10, priority="high", preferred_time="morning"))
    biscuit.add_task(Task("Heartworm medication", "medication", 5, priority="high",
                          preferred_time="morning", recurrence="weekly", recurrence_days=["monday"]))
    biscuit.add_task(Task("Afternoon walk", "walk", 45, priority="medium", preferred_time="afternoon"))
    biscuit.add_task(Task("Evening feeding", "feeding", 10, priority="high", preferred_time="evening"))
    biscuit.add_task(Task("Grooming brush", "grooming", 20, priority="low", preferred_time="evening",
                          recurrence="weekly", recurrence_days=["wednesday", "saturday"]))
    biscuit.add_task(Task("Fetch / enrichment play", "enrichment", 30, priority="medium",
                          preferred_time="afternoon"))

    # --- Mochi (cat) ---
    mochi.add_task(Task("Breakfast feeding", "feeding", 10, priority="high", preferred_time="morning"))
    mochi.add_task(Task("Thyroid medication", "medication", 5, priority="high", preferred_time="morning"))
    mochi.add_task(Task("Interactive toy session", "enrichment", 20, priority="medium", preferred_time="afternoon"))
    mochi.add_task(Task("Evening feeding", "feeding", 10, priority="high", preferred_time="evening"))
    mochi.add_task(Task("Litter box cleaning", "grooming", 10, priority="medium", preferred_time="any"))

    return jordan


def main():
    jordan = build_owner()
    biscuit, mochi = jordan.get_pets()
    day = "monday"

    banner(f"PawPal+ — Today's Schedule ({day.title()})")
    print(f"Owner: {jordan.name}  |  Window: {jordan.day_start}–{jordan.day_end}\n")

    biscuit_sched = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)
    biscuit_sched.generate_schedule()
    print(format_schedule_table(biscuit_sched))
    print()

    mochi_sched = Scheduler(owner=jordan, pet=mochi, day_of_week=day)
    mochi_sched.generate_schedule()
    print(format_schedule_table(mochi_sched))

    # ----------------------------------------------------------------------
    # Challenge 3 — Priority-based scheduling (priority first, then time)
    # ----------------------------------------------------------------------
    banner("Challenge 3 — Priority Scheduling (priority first, then time)")
    print("Same tasks, two sort modes:\n")
    by_priority = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)
    by_priority.generate_schedule(sort_mode="priority")
    print("Sort = PRIORITY:")
    print(format_schedule_table(by_priority))
    print()
    by_time = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)
    by_time.generate_schedule(sort_mode="time")
    print("Sort = TIME OF DAY:")
    print(format_schedule_table(by_time))

    # ----------------------------------------------------------------------
    # Challenge 3 — Kanban board
    # ----------------------------------------------------------------------
    banner("Challenge 3 — Kanban Board")
    tasks = biscuit.get_tasks()
    tasks[0].set_status("done")            # Morning walk -> done
    tasks[1].set_status("in_progress")     # Breakfast feeding -> in progress
    tasks[3].set_status("in_progress")     # Afternoon walk -> in progress
    print(format_kanban(biscuit))

    # ----------------------------------------------------------------------
    # Challenge 1 — Next available slot
    # ----------------------------------------------------------------------
    banner("Challenge 1 — Next Available Slot")
    fresh = Scheduler(owner=jordan, pet=mochi, day_of_week=day)
    fresh.generate_schedule()
    for dur in (15, 30, 90):
        slot = fresh.find_next_available_slot(dur)
        print(f"  Earliest opening for a {dur}-min task: {slot}")
    after = fresh.find_next_available_slot(20, after_time="12:00")
    print(f"  Earliest 20-min opening after 12:00: {after}")

    # ----------------------------------------------------------------------
    # Challenge 2 — JSON persistence round-trip
    # ----------------------------------------------------------------------
    banner("Challenge 2 — Data Persistence (data.json)")
    save_to_json(jordan, "data.json")
    print("  Saved owner + 2 pets + 12 tasks -> data.json")
    reloaded = load_from_json("data.json")
    print(f"  Reloaded owner: {reloaded.name}")
    print(f"  Pets restored:  {[p.name for p in reloaded.get_pets()]}")
    r_biscuit = reloaded.get_pets()[0]
    print(f"  {r_biscuit.name}'s tasks restored: {len(r_biscuit.get_tasks())}")
    print(f"  Kanban status survived round-trip: "
          f"'{r_biscuit.get_tasks()[0].title}' -> {r_biscuit.get_tasks()[0].status}")
    print(format_task_list(r_biscuit.get_tasks()[:3], title="  First 3 reloaded tasks"))

    # ----------------------------------------------------------------------
    # Conflict detection (cross-pet)
    # ----------------------------------------------------------------------
    banner("Cross-Pet Conflict Detection")
    b2 = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)
    m2 = Scheduler(owner=jordan, pet=mochi, day_of_week=day)
    b2.generate_schedule()
    m2.generate_schedule()
    conflicts = b2.detect_conflicts(other_schedules=[m2])
    if conflicts:
        print(f"  {len(conflicts)} conflict(s) — Jordan cannot attend two pets at once:\n")
        for c in conflicts:
            print(f"  ⚠️  {c}")
    else:
        print("  No cross-pet conflicts detected.")


if __name__ == "__main__":
    main()
