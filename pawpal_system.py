"""PawPal+ backend — Owner, Pet, Task, Scheduler."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
VALID_TASK_TYPES = {"walk", "feeding", "medication", "grooming", "enrichment"}
VALID_PRIORITIES = {"low", "medium", "high"}
VALID_RECURRENCES = {"daily", "weekly", "none"}
VALID_PREFERRED_TIMES = {"morning", "afternoon", "evening", "any"}


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    task_type: str                          # walk | feeding | medication | grooming | enrichment
    duration_minutes: int
    priority: str = "medium"               # low | medium | high
    preferred_time: str = "any"            # morning | afternoon | evening | any
    recurrence: str = "daily"              # daily | weekly | none
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    completed: bool = False

    def priority_value(self) -> int:
        """Lower number = higher priority. Used for sort key."""
        return PRIORITY_RANK.get(self.priority, 1)

    def mark_complete(self) -> None:
        self.completed = True

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "task_type": self.task_type,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "preferred_time": self.preferred_time,
            "recurrence": self.recurrence,
            "completed": self.completed,
        }


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str                            # dog | cat | other
    breed: str = ""
    age_years: float = 0.0
    weight_kg: float = 0.0
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_tasks(self) -> list:
        pass


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str = ""
    day_start: str = "08:00"               # "HH:MM" 24-hour format
    day_end: str = "20:00"
    pets: list = field(default_factory=list)

    def available_minutes(self) -> int:
        """Total schedulable minutes in the owner's day window."""
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> list:
        pass

    def set_schedule_window(self, start: str, end: str) -> None:
        pass


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Reads tasks from a Pet and produces an ordered daily plan."""

    def __init__(self, owner: Owner, pet: Pet, day_of_week: str = "monday"):
        self.owner = owner
        self.pet = pet
        self.day_of_week = day_of_week.lower()
        self.schedule: list = []

    def generate_schedule(self) -> list:
        """
        Main entry point. Returns a list of scheduled slot dicts:
          {"start_time": "08:00", "task": Task, "reason": str}
        """
        pass

    def sort_by_priority(self, tasks: list) -> list:
        """Return tasks sorted high → low priority, then by preferred_time preference."""
        pass

    def filter_by_time(self, tasks: list, available_minutes: int) -> list:
        """Drop tasks that would overflow the day window (greedy, in priority order)."""
        pass

    def assign_time_slots(self, tasks: list) -> list:
        """Assign HH:MM start times to each task starting from owner.day_start."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable string summarising the generated schedule."""
        pass
