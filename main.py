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


if __name__ == "__main__":
    main()
