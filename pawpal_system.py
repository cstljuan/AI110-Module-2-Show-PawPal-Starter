"""PawPal+ backend — Owner, Pet, Task, Scheduler."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import uuid


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}
VALID_TASK_TYPES = {"walk", "feeding", "medication", "grooming", "enrichment"}
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_RECURRENCES = {"daily", "weekly", "none"}
VALID_PREFERRED_TIMES = {"morning", "afternoon", "evening", "any"}
DAYS_OF_WEEK = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    task_type: str                           # walk | feeding | medication | grooming | enrichment
    duration_minutes: int
    priority: str = "medium"                # low | medium | high
    preferred_time: str = "any"             # morning | afternoon | evening | any
    recurrence: str = "daily"               # daily | weekly | none
    recurrence_days: list = field(default_factory=list)  # weekly anchor: ["monday", "friday"]
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    completed: bool = False
    due_date: str = ""                           # "YYYY-MM-DD"; set when tracking next occurrence

    def __post_init__(self):
        """Validate field values on construction."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got '{self.priority}'")
        if self.task_type not in VALID_TASK_TYPES:
            raise ValueError(f"task_type must be one of {VALID_TASK_TYPES}, got '{self.task_type}'")
        if self.recurrence not in VALID_RECURRENCES:
            raise ValueError(f"recurrence must be one of {VALID_RECURRENCES}, got '{self.recurrence}'")
        if self.preferred_time not in VALID_PREFERRED_TIMES:
            raise ValueError(f"preferred_time must be one of {VALID_PREFERRED_TIMES}, got '{self.preferred_time}'")
        if self.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be > 0, got {self.duration_minutes}")

    def priority_value(self) -> int:
        """Lower number = higher priority. Used as sort key."""
        return PRIORITY_RANK.get(self.priority, 1)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def to_dict(self) -> dict:
        """Return task fields as a plain dictionary."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "task_type": self.task_type,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "preferred_time": self.preferred_time,
            "recurrence": self.recurrence,
            "recurrence_days": self.recurrence_days,
            "completed": self.completed,
            "due_date": self.due_date,
        }

    def next_occurrence(self):
        """Return a new Task due one recurrence period later; None if recurrence='none'."""
        if self.recurrence == "none":
            return None
        base = date.fromisoformat(self.due_date) if self.due_date else date.today()
        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(days=7)
        return Task(
            title=self.title,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            recurrence=self.recurrence,
            recurrence_days=list(self.recurrence_days),
            due_date=(base + delta).isoformat(),
        )


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str                             # dog | cat | other
    breed: str = ""
    age_years: float = 0.0
    weight_kg: float = 0.0
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task matching task_id; no-op if not found."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> list:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)

    def filter_tasks(self, completed: bool = None) -> list:
        """Return tasks filtered by completion status; None returns all tasks."""
        if completed is None:
            return list(self.tasks)
        return [t for t in self.tasks if t.completed == completed]


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str = ""
    day_start: str = "08:00"                # "HH:MM" 24-hour format
    day_end: str = "20:00"
    pets: list = field(default_factory=list)

    def available_minutes(self) -> int:
        """Minutes between day_start and day_end."""
        fmt = "%H:%M"
        start = datetime.strptime(self.day_start, fmt)
        end = datetime.strptime(self.day_end, fmt)
        return max(0, int((end - start).total_seconds() // 60))

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list:
        """Return a shallow copy of the owner's pet list."""
        return list(self.pets)

    def set_schedule_window(self, start: str, end: str) -> None:
        """Update the daily scheduling window (HH:MM strings)."""
        self.day_start = start
        self.day_end = end


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds a priority-sorted daily care plan for one pet within the owner's time window."""

    def __init__(self, owner: Owner, pet: Pet, day_of_week: str = "monday"):
        """Wire owner, pet, and target weekday; call generate_schedule() to produce a plan."""
        self.owner = owner
        self.pet = pet
        self.day_of_week = day_of_week.lower()
        self.schedule: list = []

    # -- internal helpers --------------------------------------------------

    def _is_active_today(self, task: Task) -> bool:
        """Return True if task should appear in today's schedule."""
        if task.recurrence == "none":
            return False
        if task.recurrence == "daily":
            return True
        if task.recurrence == "weekly":
            if not task.recurrence_days:
                return True  # unspecified weekly → run every day
            return self.day_of_week in [d.lower() for d in task.recurrence_days]
        return False

    # -- public interface --------------------------------------------------

    def sort_by_priority(self, tasks: list) -> list:
        """Sort high → low priority; break ties with preferred_time (morning first)."""
        return sorted(
            tasks,
            key=lambda t: (t.priority_value(), TIME_ORDER.get(t.preferred_time, 3))
        )

    def sort_by_time(self, tasks: list) -> list:
        """Sort morning → afternoon → evening → any; break ties by priority."""
        return sorted(
            tasks,
            key=lambda t: (TIME_ORDER.get(t.preferred_time, 3), t.priority_value())
        )

    def filter_by_time(self, tasks: list, available_minutes: int) -> list:
        """Greedy include: keep tasks that fit remaining minutes; drop overflow tasks entirely."""
        selected, remaining = [], available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def assign_time_slots(self, tasks: list) -> list:
        """Assign sequential HH:MM start times from owner.day_start; return list of slot dicts."""
        slots = []
        fmt = "%H:%M"
        current = datetime.strptime(self.owner.day_start, fmt)
        for task in tasks:
            slots.append({
                "start_time": current.strftime(fmt),
                "task": task,
                "reason": (
                    f"Priority '{task.priority}' | type '{task.task_type}' | "
                    f"preferred '{task.preferred_time}'"
                ),
            })
            current += timedelta(minutes=task.duration_minutes)
        return slots

    def detect_conflicts(self, other_schedules: list = None) -> list:
        """Check for overlapping time slots across this schedule and any other_schedules; return warning strings."""
        named_slots = [(self.pet.name, slot) for slot in self.schedule]
        if other_schedules:
            for other in other_schedules:
                named_slots += [(other.pet.name, slot) for slot in other.schedule]

        warnings = []
        fmt = "%H:%M"
        for i in range(len(named_slots)):
            pet_a, slot_a = named_slots[i]
            for j in range(i + 1, len(named_slots)):
                pet_b, slot_b = named_slots[j]
                if pet_a == pet_b:
                    continue  # same-pet slots are assigned sequentially — never overlap
                a_start = datetime.strptime(slot_a["start_time"], fmt)
                a_end   = a_start + timedelta(minutes=slot_a["task"].duration_minutes)
                b_start = datetime.strptime(slot_b["start_time"], fmt)
                b_end   = b_start + timedelta(minutes=slot_b["task"].duration_minutes)
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"CONFLICT: [{pet_a}] '{slot_a['task'].title}' "
                        f"({slot_a['start_time']}-{a_end.strftime(fmt)}) overlaps "
                        f"[{pet_b}] '{slot_b['task'].title}' "
                        f"({slot_b['start_time']}-{b_end.strftime(fmt)})"
                    )
        return warnings

    def handle_completion(self, task) -> "Task | None":
        """Mark task complete and return the next-occurrence Task; None if recurrence='none'."""
        task.mark_complete()
        return task.next_occurrence()

    def generate_schedule(self, sort_mode: str = "priority") -> list:
        """Run full pipeline (recurrence filter -> sort -> time trim -> slot assign). sort_mode: 'priority' or 'time'."""
        all_tasks = self.pet.get_tasks()
        active = [t for t in all_tasks if self._is_active_today(t)]
        sorted_tasks = (
            self.sort_by_time(active)
            if sort_mode == "time"
            else self.sort_by_priority(active)
        )
        budget = self.owner.available_minutes()
        chosen = self.filter_by_time(sorted_tasks, budget)
        self.schedule = self.assign_time_slots(chosen)
        return self.schedule

    def explain_plan(self) -> str:
        """Human-readable schedule summary. Call generate_schedule() first."""
        if not self.schedule:
            return (
                f"No schedule for {self.pet.name}. Call generate_schedule() first."
            )
        header = (
            f"Daily plan for {self.pet.name} ({self.pet.species})"
            f" -- {self.day_of_week.title()}"
        )
        lines = [header, "-" * len(header)]
        for slot in self.schedule:
            t = slot["task"]
            lines.append(
                f"  {slot['start_time']}  {t.title}"
                f"  ({t.duration_minutes} min)  [{t.priority} priority]"
            )
        total_used = sum(s["task"].duration_minutes for s in self.schedule)
        budget = self.owner.available_minutes()
        skipped = len(self.pet.get_tasks()) - len(self.schedule)
        lines.append("-" * len(header))
        lines.append(f"  {total_used} min used / {budget} min available")
        if skipped > 0:
            lines.append(f"  {skipped} task(s) skipped (time overflow or not scheduled today)")
        return "\n".join(lines)
