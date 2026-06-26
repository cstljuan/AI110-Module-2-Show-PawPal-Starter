"""Tests for PawPal+ core logic."""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(**kwargs) -> Task:
    defaults = dict(title="Test task", task_type="walk", duration_minutes=20)
    defaults.update(kwargs)
    return Task(**defaults)


def make_pet(**kwargs) -> Pet:
    defaults = dict(name="Rex", species="dog")
    defaults.update(kwargs)
    return Pet(**defaults)


def make_owner(**kwargs) -> Owner:
    defaults = dict(name="Jordan", day_start="08:00", day_end="20:00")
    defaults.update(kwargs)
    return Owner(**defaults)


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_sets_completed_true():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_is_idempotent():
    task = make_task()
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    pet = make_pet()
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


def test_add_multiple_tasks_increases_count():
    pet = make_pet()
    pet.add_task(make_task(title="Walk"))
    pet.add_task(make_task(title="Feed", task_type="feeding"))
    assert len(pet.get_tasks()) == 2


def test_remove_task_decreases_count():
    pet = make_pet()
    task = make_task()
    pet.add_task(task)
    pet.remove_task(task.task_id)
    assert len(pet.get_tasks()) == 0


def test_remove_nonexistent_task_does_not_crash():
    pet = make_pet()
    pet.remove_task("does-not-exist")   # should not raise
    assert len(pet.get_tasks()) == 0


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

def test_available_minutes_correct():
    owner = make_owner(day_start="08:00", day_end="20:00")
    assert owner.available_minutes() == 720  # 12 hours


def test_set_schedule_window_updates_times():
    owner = make_owner()
    owner.set_schedule_window("09:00", "17:00")
    assert owner.day_start == "09:00"
    assert owner.day_end == "17:00"
    assert owner.available_minutes() == 480  # 8 hours


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

def test_generate_schedule_priority_order():
    """High-priority tasks appear before medium/low in the plan."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task(title="Low task", priority="low", duration_minutes=10))
    pet.add_task(make_task(title="High task", priority="high", duration_minutes=10))
    pet.add_task(make_task(title="Med task", priority="medium", duration_minutes=10))

    scheduler = Scheduler(owner=owner, pet=pet)
    schedule = scheduler.generate_schedule()

    priorities = [slot["task"].priority for slot in schedule]
    assert priorities == ["high", "medium", "low"]


def test_generate_schedule_drops_overflow_tasks():
    """Tasks that exceed available time are dropped, not truncated."""
    owner = make_owner(day_start="08:00", day_end="08:30")  # 30 min window
    pet = make_pet()
    pet.add_task(make_task(title="Short", priority="high", duration_minutes=20))
    pet.add_task(make_task(title="Too long", priority="medium", duration_minutes=20))

    scheduler = Scheduler(owner=owner, pet=pet)
    schedule = scheduler.generate_schedule()

    assert len(schedule) == 1
    assert schedule[0]["task"].title == "Short"


def test_generate_schedule_empty_task_list():
    """Scheduler returns empty list when pet has no tasks."""
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.generate_schedule() == []


def test_weekly_task_excluded_on_wrong_day():
    """Weekly task set to Monday is excluded when scheduler runs on Wednesday."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(
        title="Monday med",
        task_type="medication",
        duration_minutes=5,
        recurrence="weekly",
        recurrence_days=["monday"],
    ))

    scheduler = Scheduler(owner=owner, pet=pet, day_of_week="wednesday")
    schedule = scheduler.generate_schedule()
    assert len(schedule) == 0


def test_weekly_task_included_on_correct_day():
    """Weekly task set to Monday is included when scheduler runs on Monday."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(
        title="Monday med",
        task_type="medication",
        duration_minutes=5,
        recurrence="weekly",
        recurrence_days=["monday"],
    ))

    scheduler = Scheduler(owner=owner, pet=pet, day_of_week="monday")
    schedule = scheduler.generate_schedule()
    assert len(schedule) == 1


def test_task_with_recurrence_none_excluded():
    """Tasks with recurrence='none' are never scheduled."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task(recurrence="none"))

    scheduler = Scheduler(owner=owner, pet=pet)
    assert scheduler.generate_schedule() == []
