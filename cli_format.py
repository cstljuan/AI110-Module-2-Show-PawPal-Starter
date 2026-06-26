"""cli_format.py — professional terminal output for PawPal+ (Challenge 4).

Uses the `tabulate` library for structured grid tables, plus emoji indicators
for task type, priority, and Kanban status. All helpers return strings so they
are easy to test and to print.
"""

from tabulate import tabulate

from pawpal_system import (
    PRIORITY_EMOJI,
    STATUS_EMOJI,
    Pet,
    Scheduler,
)


def format_schedule_table(scheduler: Scheduler) -> str:
    """Render a Scheduler's generated plan as a tabulate grid with emoji indicators."""
    if not scheduler.schedule:
        return f"(No schedule for {scheduler.pet.name} — call generate_schedule() first.)"

    rows = []
    for slot in scheduler.schedule:
        t = slot["task"]
        rows.append([
            slot["start_time"],
            f"{t.type_emoji()} {t.task_type}",
            t.title,
            f"{t.duration_minutes} min",
            f"{PRIORITY_EMOJI.get(t.priority, '')} {t.priority}",
            f"{STATUS_EMOJI.get(t.status, '')} {t.status}",
        ])

    headers = ["Start", "Type", "Task", "Duration", "Priority", "Status"]
    table = tabulate(rows, headers=headers, tablefmt="rounded_grid")

    total_used = sum(s["task"].duration_minutes for s in scheduler.schedule)
    budget = scheduler.owner.available_minutes()
    title = (
        f"📅  {scheduler.pet.name} ({scheduler.pet.species}) — "
        f"{scheduler.day_of_week.title()}   "
        f"[{total_used}/{budget} min used]"
    )
    return f"{title}\n{table}"


def format_kanban(pet: Pet) -> str:
    """Render a pet's tasks as a 3-column Kanban board (To Do / In Progress / Done)."""
    columns = {
        "todo": pet.tasks_by_status("todo"),
        "in_progress": pet.tasks_by_status("in_progress"),
        "done": pet.tasks_by_status("done"),
    }

    def cell(tasks: list) -> str:
        if not tasks:
            return "—"
        return "\n".join(f"{t.type_emoji()} {t.title}" for t in tasks)

    headers = [
        f"{STATUS_EMOJI['todo']} TO DO ({len(columns['todo'])})",
        f"{STATUS_EMOJI['in_progress']} IN PROGRESS ({len(columns['in_progress'])})",
        f"{STATUS_EMOJI['done']} DONE ({len(columns['done'])})",
    ]
    row = [cell(columns["todo"]), cell(columns["in_progress"]), cell(columns["done"])]
    table = tabulate([row], headers=headers, tablefmt="rounded_grid")
    return f"🗂️  Kanban — {pet.name}\n{table}"


def format_task_list(tasks: list, title: str = "Tasks") -> str:
    """Render a flat task list as a tabulate grid with emoji indicators."""
    if not tasks:
        return f"{title}: (none)"
    rows = [
        [
            f"{t.type_emoji()} {t.task_type}",
            t.title,
            f"{t.duration_minutes} min",
            f"{PRIORITY_EMOJI.get(t.priority, '')} {t.priority}",
            t.preferred_time,
            t.recurrence,
            f"{STATUS_EMOJI.get(t.status, '')} {t.status}",
        ]
        for t in tasks
    ]
    headers = ["Type", "Title", "Duration", "Priority", "Preferred", "Recurrence", "Status"]
    return f"{title}\n" + tabulate(rows, headers=headers, tablefmt="rounded_grid")
