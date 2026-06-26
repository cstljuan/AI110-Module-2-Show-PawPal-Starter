"""Tests for PawPal+ core logic."""

import pytest
from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    save_to_json,
    load_from_json,
)


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


# ---------------------------------------------------------------------------
# sort_by_time tests
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """sort_by_time returns morning before afternoon before evening."""
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)

    tasks = [
        make_task(title="Evening task",   preferred_time="evening"),
        make_task(title="Morning task",   preferred_time="morning"),
        make_task(title="Afternoon task", preferred_time="afternoon"),
    ]
    result = scheduler.sort_by_time(tasks)
    times = [t.preferred_time for t in result]
    assert times == ["morning", "afternoon", "evening"]


def test_sort_by_time_priority_breaks_ties():
    """When two tasks share the same preferred_time, high priority comes before low."""
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)

    tasks = [
        make_task(title="Low morning",  preferred_time="morning", priority="low"),
        make_task(title="High morning", preferred_time="morning", priority="high"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert result[0].priority == "high"
    assert result[1].priority == "low"


# ---------------------------------------------------------------------------
# next_occurrence / handle_completion tests
# ---------------------------------------------------------------------------

def test_next_occurrence_daily_advances_one_day():
    """Daily task next_occurrence sets due_date to base + 1 day."""
    task = make_task(recurrence="daily", due_date="2026-01-10")
    next_t = task.next_occurrence()
    assert next_t is not None
    assert next_t.due_date == "2026-01-11"
    assert next_t.completed is False


def test_next_occurrence_weekly_advances_seven_days():
    """Weekly task next_occurrence sets due_date to base + 7 days."""
    task = make_task(recurrence="weekly", due_date="2026-01-10")
    next_t = task.next_occurrence()
    assert next_t is not None
    assert next_t.due_date == "2026-01-17"


def test_next_occurrence_none_returns_none():
    """Task with recurrence='none' returns None from next_occurrence."""
    task = make_task(recurrence="none")
    assert task.next_occurrence() is None


def test_handle_completion_marks_task_done_and_returns_next():
    """handle_completion marks the original complete and returns a fresh next occurrence."""
    owner = make_owner()
    pet = make_pet()
    scheduler = Scheduler(owner=owner, pet=pet)

    task = make_task(recurrence="daily", due_date="2026-03-01")
    next_t = scheduler.handle_completion(task)

    assert task.completed is True
    assert next_t is not None
    assert next_t.completed is False
    assert next_t.due_date == "2026-03-02"


# ---------------------------------------------------------------------------
# filter_tasks tests
# ---------------------------------------------------------------------------

def test_filter_tasks_completed_returns_only_done():
    """filter_tasks(completed=True) returns only tasks where completed is True."""
    pet = make_pet()
    done = make_task(title="Done")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task(title="Pending"))

    result = pet.filter_tasks(completed=True)
    assert len(result) == 1
    assert result[0].title == "Done"


def test_filter_tasks_incomplete_returns_only_pending():
    """filter_tasks(completed=False) returns only tasks not yet completed."""
    pet = make_pet()
    done = make_task(title="Done")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task(title="Pending"))

    result = pet.filter_tasks(completed=False)
    assert len(result) == 1
    assert result[0].title == "Pending"


def test_filter_tasks_none_returns_all():
    """filter_tasks() with no argument returns all tasks regardless of status."""
    pet = make_pet()
    done = make_task(title="Done")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(make_task(title="Pending"))

    assert len(pet.filter_tasks()) == 2


# ---------------------------------------------------------------------------
# detect_conflicts tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_finds_cross_pet_overlap():
    """Two pets with overlapping schedules from the same owner start produce conflicts."""
    owner = make_owner(day_start="08:00", day_end="20:00")

    pet_a = make_pet(name="Biscuit")
    pet_b = make_pet(name="Mochi")
    pet_a.add_task(make_task(title="Walk",     duration_minutes=30))
    pet_b.add_task(make_task(title="Feeding",  duration_minutes=10))

    sched_a = Scheduler(owner=owner, pet=pet_a)
    sched_b = Scheduler(owner=owner, pet=pet_b)
    sched_a.generate_schedule()
    sched_b.generate_schedule()

    conflicts = sched_a.detect_conflicts(other_schedules=[sched_b])
    # Both start at 08:00 — Walk (08:00–08:30) overlaps Feeding (08:00–08:10)
    assert len(conflicts) > 0
    assert "CONFLICT" in conflicts[0]


def test_detect_conflicts_no_warning_when_other_schedule_empty():
    """No conflicts when the other pet has no tasks scheduled for that day."""
    owner = make_owner()

    pet_a = make_pet(name="Biscuit")
    pet_b = make_pet(name="Mochi")
    pet_a.add_task(make_task(title="Walk", duration_minutes=30))
    pet_b.add_task(make_task(title="Skipped", recurrence="none"))  # never active

    sched_a = Scheduler(owner=owner, pet=pet_a)
    sched_b = Scheduler(owner=owner, pet=pet_b)
    sched_a.generate_schedule()
    sched_b.generate_schedule()

    conflicts = sched_a.detect_conflicts(other_schedules=[sched_b])
    assert conflicts == []


def test_detect_conflicts_same_pet_slots_never_flagged():
    """Sequential slots within a single pet's schedule are never reported as conflicts."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(make_task(title="Task 1", duration_minutes=10))
    pet.add_task(make_task(title="Task 2", duration_minutes=10))

    sched = Scheduler(owner=owner, pet=pet)
    sched.generate_schedule()

    # No other schedules — only self; same-pet skipped by design
    conflicts = sched.detect_conflicts()
    assert conflicts == []


# ---------------------------------------------------------------------------
# find_next_available_slot tests (Challenge 1)
# ---------------------------------------------------------------------------

def test_next_slot_empty_schedule_returns_day_start():
    """With nothing booked, the next slot is the start of the owner's day."""
    owner = make_owner(day_start="08:00", day_end="20:00")
    pet = make_pet()
    sched = Scheduler(owner=owner, pet=pet)
    sched.generate_schedule()  # no tasks -> empty schedule
    assert sched.find_next_available_slot(30) == "08:00"


def test_next_slot_after_back_to_back_bookings():
    """Back-to-back tasks push the next opening to the end of the last booking."""
    owner = make_owner(day_start="08:00", day_end="20:00")
    pet = make_pet()
    pet.add_task(make_task(title="A", duration_minutes=30, priority="high"))
    pet.add_task(make_task(title="B", duration_minutes=20, priority="high"))
    sched = Scheduler(owner=owner, pet=pet)
    sched.generate_schedule()
    # 08:00-08:30 then 08:30-08:50 -> first free slot at 08:50
    assert sched.find_next_available_slot(15) == "08:50"


def test_next_slot_honors_after_time_floor():
    """after_time pushes the search start forward even if earlier gaps exist."""
    owner = make_owner(day_start="08:00", day_end="20:00")
    pet = make_pet()
    sched = Scheduler(owner=owner, pet=pet)
    sched.generate_schedule()
    assert sched.find_next_available_slot(30, after_time="14:00") == "14:00"


def test_next_slot_returns_none_when_no_room():
    """Returns None when the requested duration cannot fit before day_end."""
    owner = make_owner(day_start="08:00", day_end="08:30")  # only 30 min
    pet = make_pet()
    sched = Scheduler(owner=owner, pet=pet)
    sched.generate_schedule()
    assert sched.find_next_available_slot(60) is None


# ---------------------------------------------------------------------------
# Kanban status tests (Challenge 3)
# ---------------------------------------------------------------------------

def test_task_default_status_is_todo():
    """New tasks start in the 'todo' Kanban column."""
    assert make_task().status == "todo"


def test_set_status_moves_task_and_syncs_completed():
    """set_status('done') moves the task and flips completed to True."""
    task = make_task()
    task.set_status("in_progress")
    assert task.status == "in_progress"
    assert task.completed is False
    task.set_status("done")
    assert task.status == "done"
    assert task.completed is True


def test_mark_complete_also_sets_done_status():
    """mark_complete() keeps the Kanban status in sync."""
    task = make_task()
    task.mark_complete()
    assert task.status == "done"


def test_set_status_rejects_invalid_value():
    """An unknown status raises ValueError."""
    task = make_task()
    with pytest.raises(ValueError):
        task.set_status("archived")


def test_tasks_by_status_groups_correctly():
    """tasks_by_status returns only tasks in the requested column."""
    pet = make_pet()
    t1 = make_task(title="A")
    t2 = make_task(title="B")
    t2.set_status("in_progress")
    pet.add_task(t1)
    pet.add_task(t2)
    assert len(pet.tasks_by_status("todo")) == 1
    assert len(pet.tasks_by_status("in_progress")) == 1
    assert pet.tasks_by_status("done") == []


# ---------------------------------------------------------------------------
# Persistence tests (Challenge 2)
# ---------------------------------------------------------------------------

def test_task_dict_round_trip_preserves_fields():
    """Task.from_dict(task.to_dict()) reproduces all fields."""
    task = make_task(title="Walk", priority="high", preferred_time="morning",
                     recurrence="weekly", recurrence_days=["monday"])
    task.set_status("in_progress")
    clone = Task.from_dict(task.to_dict())
    assert clone.title == task.title
    assert clone.priority == task.priority
    assert clone.recurrence_days == task.recurrence_days
    assert clone.status == task.status
    assert clone.task_id == task.task_id


def test_owner_dict_round_trip_preserves_nested_pets_and_tasks():
    """Owner.from_dict(owner.to_dict()) restores the full object graph."""
    owner = make_owner()
    pet = make_pet(name="Biscuit")
    pet.add_task(make_task(title="Walk"))
    pet.add_task(make_task(title="Feed", task_type="feeding"))
    owner.add_pet(pet)

    clone = Owner.from_dict(owner.to_dict())
    assert clone.name == owner.name
    assert len(clone.get_pets()) == 1
    assert clone.get_pets()[0].name == "Biscuit"
    assert len(clone.get_pets()[0].get_tasks()) == 2


def test_save_and_load_json_round_trip(tmp_path):
    """save_to_json then load_from_json restores an equivalent Owner from disk."""
    owner = make_owner(name="Jordan")
    pet = make_pet(name="Mochi", species="cat")
    pet.add_task(make_task(title="Feed", task_type="feeding"))
    owner.add_pet(pet)

    path = tmp_path / "data.json"
    save_to_json(owner, str(path))
    loaded = load_from_json(str(path))

    assert loaded is not None
    assert loaded.name == "Jordan"
    assert loaded.get_pets()[0].name == "Mochi"
    assert loaded.get_pets()[0].get_tasks()[0].title == "Feed"


def test_load_json_missing_file_returns_none(tmp_path):
    """load_from_json returns None when the file does not exist."""
    missing = tmp_path / "nope.json"
    assert load_from_json(str(missing)) is None
