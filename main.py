"""main.py — CLI demo for PawPal+. Run: python main.py"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(scheduler: Scheduler, day: str) -> None:
    scheduler.day_of_week = day
    schedule = scheduler.generate_schedule()
    print(scheduler.explain_plan())
    print()


def main():
    # --- Owner -----------------------------------------------------------
    jordan = Owner(
        name="Jordan",
        email="jordan@example.com",
        day_start="07:00",
        day_end="19:00",
    )

    # --- Pets ------------------------------------------------------------
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age_years=3.0)
    mochi = Pet(name="Mochi", species="cat", breed="Domestic Shorthair", age_years=5.0)

    jordan.add_pet(biscuit)
    jordan.add_pet(mochi)

    # --- Tasks for Biscuit (dog) -----------------------------------------
    biscuit.add_task(Task(
        title="Morning walk",
        task_type="walk",
        duration_minutes=30,
        priority="high",
        preferred_time="morning",
        recurrence="daily",
    ))
    biscuit.add_task(Task(
        title="Breakfast feeding",
        task_type="feeding",
        duration_minutes=10,
        priority="high",
        preferred_time="morning",
        recurrence="daily",
    ))
    biscuit.add_task(Task(
        title="Heartworm medication",
        task_type="medication",
        duration_minutes=5,
        priority="high",
        preferred_time="morning",
        recurrence="weekly",
        recurrence_days=["monday"],
    ))
    biscuit.add_task(Task(
        title="Afternoon walk",
        task_type="walk",
        duration_minutes=45,
        priority="medium",
        preferred_time="afternoon",
        recurrence="daily",
    ))
    biscuit.add_task(Task(
        title="Evening feeding",
        task_type="feeding",
        duration_minutes=10,
        priority="high",
        preferred_time="evening",
        recurrence="daily",
    ))
    biscuit.add_task(Task(
        title="Grooming brush",
        task_type="grooming",
        duration_minutes=20,
        priority="low",
        preferred_time="evening",
        recurrence="weekly",
        recurrence_days=["wednesday", "saturday"],
    ))
    biscuit.add_task(Task(
        title="Fetch / enrichment play",
        task_type="enrichment",
        duration_minutes=30,
        priority="medium",
        preferred_time="afternoon",
        recurrence="daily",
    ))

    # --- Tasks for Mochi (cat) -------------------------------------------
    mochi.add_task(Task(
        title="Breakfast feeding",
        task_type="feeding",
        duration_minutes=10,
        priority="high",
        preferred_time="morning",
        recurrence="daily",
    ))
    mochi.add_task(Task(
        title="Thyroid medication",
        task_type="medication",
        duration_minutes=5,
        priority="high",
        preferred_time="morning",
        recurrence="daily",
    ))
    mochi.add_task(Task(
        title="Interactive toy session",
        task_type="enrichment",
        duration_minutes=20,
        priority="medium",
        preferred_time="afternoon",
        recurrence="daily",
    ))
    mochi.add_task(Task(
        title="Evening feeding",
        task_type="feeding",
        duration_minutes=10,
        priority="high",
        preferred_time="evening",
        recurrence="daily",
    ))
    mochi.add_task(Task(
        title="Litter box cleaning",
        task_type="grooming",
        duration_minutes=10,
        priority="medium",
        preferred_time="any",
        recurrence="daily",
    ))

    # --- Run schedules ---------------------------------------------------
    day = "monday"

    print("=" * 52)
    print(f"  PawPal+ -- Today's Schedule ({day.title()})")
    print(f"  Owner: {jordan.name}  |  Window: {jordan.day_start} to {jordan.day_end}")
    print("=" * 52)
    print()

    biscuit_sched = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)
    print_schedule(biscuit_sched, day)

    mochi_sched = Scheduler(owner=jordan, pet=mochi, day_of_week=day)
    print_schedule(mochi_sched, day)

    # =========================================================================
    # Phase 3 -- Algorithm Demos
    # =========================================================================

    print("=" * 52)
    print("  Phase 3 -- Algorithm Demos")
    print("=" * 52)
    print()

    demo_sched = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)

    # --- Demo 1: sort_by_time() vs sort_by_priority() -------------------------
    print("-- sort_by_time() vs sort_by_priority() (Biscuit daily tasks) --")
    daily = [t for t in biscuit.get_tasks() if t.recurrence == "daily"]
    by_time     = demo_sched.sort_by_time(daily)
    by_priority = demo_sched.sort_by_priority(daily)
    print("  sort_by_time()    : " +
          ", ".join(f"{t.preferred_time}/{t.priority}" for t in by_time))
    print("  sort_by_priority(): " +
          ", ".join(f"{t.priority}/{t.preferred_time}" for t in by_priority))
    print()

    # --- Demo 2: filter_tasks() -----------------------------------------------
    print("-- filter_tasks(completed=...) demo (Mochi) --")
    print(f"  All tasks:  {len(mochi.filter_tasks())}")
    print(f"  Incomplete: {len(mochi.filter_tasks(completed=False))}")
    first_mochi = mochi.get_tasks()[0]
    first_mochi.mark_complete()
    print(f"  After marking '{first_mochi.title}' complete:")
    print(f"    Completed:  {len(mochi.filter_tasks(completed=True))}")
    print(f"    Incomplete: {len(mochi.filter_tasks(completed=False))}")
    print()

    # --- Demo 3: handle_completion() / next_occurrence() ----------------------
    print("-- handle_completion() recurring auto-generation (Biscuit) --")
    target = biscuit.get_tasks()[0]  # Morning walk -- daily
    print(f"  Completing: '{target.title}'  recurrence={target.recurrence}")
    next_task = demo_sched.handle_completion(target)
    if next_task:
        print(f"  Next occurrence: '{next_task.title}'  due {next_task.due_date}")
    print()

    # --- Demo 4: detect_conflicts() cross-pet ---------------------------------
    print("-- detect_conflicts() cross-pet owner-level check --")
    b2 = Scheduler(owner=jordan, pet=biscuit, day_of_week=day)
    m2 = Scheduler(owner=jordan, pet=mochi,   day_of_week=day)
    b2.generate_schedule()
    m2.generate_schedule()
    conflicts = b2.detect_conflicts(other_schedules=[m2])
    if conflicts:
        print(f"  {len(conflicts)} conflict(s) found -- owner cannot do both simultaneously:")
        for c in conflicts:
            print(f"  {c}")
    else:
        print("  No cross-pet conflicts detected.")
    print()


if __name__ == "__main__":
    main()
