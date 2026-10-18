from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from uuid import uuid4

VALID_CATEGORIES = {"walk", "feeding", "meds", "enrichment", "grooming"}
VALID_PRIORITIES = (1, 2, 3)  # 1 = low, 2 = medium, 3 = high
VALID_RECURRENCES = {None, "daily", "weekly"}
EDITABLE_TASK_FIELDS = {
    "title",
    "category",
    "duration_minutes",
    "priority",
    "preferred_time",
    "start_time",
    "due_date",
    "recurrence",
}


def new_id() -> str:
    return uuid4().hex


def format_time(value: time) -> str:
    return value.strftime("%I:%M %p").lstrip("0")


@dataclass
class Task:
    title: str
    category: str  # must be in VALID_CATEGORIES
    duration_minutes: int  # must be > 0
    priority: int = 2  # must be in VALID_PRIORITIES
    preferred_time: str = ""  # e.g. "morning"
    start_time: time | None = None  # fixed clock time, e.g. time(8, 0); None = flexible
    due_date: date | None = None  # date the task should be done by
    recurrence: str | None = None  # must be in VALID_RECURRENCES
    is_complete: bool = False
    id: str = field(default_factory=new_id)
    pet_id: str = ""  # set by Pet.add_task; links the task back to its pet

    def __post_init__(self) -> None:
        """Validate title, category, duration_minutes, priority and recurrence."""
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if self.category not in VALID_CATEGORIES:
            raise ValueError(
                f"Unknown category {self.category!r}; expected one of {sorted(VALID_CATEGORIES)}"
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
        if self.recurrence not in VALID_RECURRENCES:
            raise ValueError("recurrence must be 'daily', 'weekly' or None")

    def mark_complete(self) -> "Task | None":
        """Mark this task as done.

        Returns a fresh copy for the next occurrence if the task recurs, else None.
        The copy is not attached to a pet; use Pet.complete_task to add it automatically.
        """
        already_done = self.is_complete
        self.is_complete = True
        return None if already_done else self.next_occurrence()

    def next_occurrence(self) -> "Task | None":
        """Return an incomplete copy due one day (daily) or seven days (weekly) later.

        The new due date counts from this task's due_date, or from today if it has none.
        Returns None if the task does not recur.
        """
        if self.recurrence is None:
            return None
        step = timedelta(days=1 if self.recurrence == "daily" else 7)
        return replace(
            self,
            due_date=(self.due_date or date.today()) + step,
            is_complete=False,
            id=new_id(),
        )

    def reset(self) -> None:
        """Mark this task as not done again."""
        self.is_complete = False

    def is_due(self, on_date: date) -> str:
        """Compare on_date with due_date and is_complete.

        Returns a status string: "complete", "past due", "due today" or "upcoming".
        If due_date is None, the task is treated as due today.
        """
        if self.is_complete:
            return "complete"
        if self.due_date is None or self.due_date == on_date:
            return "due today"
        if self.due_date < on_date:
            return "past due"
        return "upcoming"

    def edit(self, **changes) -> None:
        """Update only keys in EDITABLE_TASK_FIELDS, validating the new values."""
        unknown = set(changes) - EDITABLE_TASK_FIELDS
        if unknown:
            raise ValueError(
                f"Cannot edit {sorted(unknown)}; allowed: {sorted(EDITABLE_TASK_FIELDS)}"
            )
        # replace() re-runs __post_init__, so invalid values raise before self changes.
        replace(self, **changes)
        for key, value in changes.items():
            setattr(self, key, value)


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    id: str = field(default_factory=new_id)

    def __post_init__(self) -> None:
        """Validate name is non-empty and age is not negative."""
        if not self.name.strip():
            raise ValueError("Pet name cannot be empty")
        if self.age < 0:
            raise ValueError("Pet age cannot be negative")

    def add_task(self, task: Task) -> None:
        """Attach a task and set task.pet_id to this pet's id."""
        task.pet_id = self.id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id, if this pet has it."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def complete_task(self, task_id: str) -> Task | None:
        """Mark the task with the given id complete and add its next occurrence, if any.

        Returns the new task, or None if the task doesn't recur, was already
        complete, or this pet doesn't have it.
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None:
            return None
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def task_count(self) -> int:
        """Return the total number of tasks attached to this pet."""
        return len(self.tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that are not yet complete."""
        return [task for task in self.tasks if not task.is_complete]

    def get_tasks_by_category(self, category: str) -> list[Task]:
        """Return the tasks that belong to the given category."""
        return [task for task in self.tasks if task.category == category]


@dataclass
class Owner:
    name: str
    available_minutes: int  # must be >= 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)
    id: str = field(default_factory=new_id)

    def __post_init__(self) -> None:
        """Validate name is non-empty and available_minutes is not negative."""
        if not self.name.strip():
            raise ValueError("Owner name cannot be empty")
        if self.available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")

    def add_pet(self, pet: Pet) -> None:  # we should restrict to unique pet names on the front end
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given id, along with its tasks."""
        self.pets = [pet for pet in self.pets if pet.id != pet_id]

    def get_pet(self, pet_id: str) -> Pet | None:
        """Return the pet with the given id, or None if there isn't one."""
        return next((pet for pet in self.pets if pet.id == pet_id), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet as one flat list."""
        return [task for pet in self.pets for task in pet.tasks]

    def total_task_count(self) -> int:
        """Return the number of tasks across all of this owner's pets."""
        return sum(pet.task_count() for pet in self.pets)

    def set_preference(self, key: str, value) -> None:
        """Set one owner preference, replacing any existing value for that key."""
        self.preferences[key] = value


class Scheduler:
    def __init__(self, owner: Owner):
        """Create a scheduler that plans tasks for the given owner."""
        self.owner = owner
        # (task, reason) pairs left out of the most recent plan
        self.last_skipped: list[tuple[Task, str]] = []

    def generate_daily_plan(self, on_date: date) -> list[tuple[Task, str]]:
        """Return an ordered list of (task, reason) that fits the owner's time."""
        due = self._collect_due_tasks(on_date)
        ranked = self._rank_tasks(due)
        scheduled, skipped = self._fit_to_available_time(ranked)
        self.last_skipped = skipped
        # Timed tasks in clock order first; flexible tasks keep their ranked order after.
        order = {task.id: i for i, task in enumerate(self.sort_by_time([t for t, _ in scheduled]))}
        scheduled.sort(key=lambda item: order[item[0].id])
        return scheduled

    def explain_plan(self, plan: list[tuple[Task, str]]) -> str:
        """Format a plan as text grouped by pet, with each task's reason."""
        if not plan:
            return "No tasks were scheduled."
        # Group by pet in the owner's pet order; plan order is kept within each pet.
        groups: dict[str, list[tuple[Task, str]]] = {}
        for pet in self.owner.pets:
            groups[pet.id] = [item for item in plan if item[0].pet_id == pet.id]
        known = set(groups)
        groups[""] = [item for item in plan if item[0].pet_id not in known]

        lines = []
        total = 0
        for pet_id, items in groups.items():
            if not items:
                continue
            pet = self.owner.get_pet(pet_id)
            lines.append(f"{pet.name} ({pet.species})" if pet else "Other tasks")
            for task, reason in items:
                at = format_time(task.start_time) if task.start_time else "Anytime"
                lines.append(
                    f"  {at:<8} {task.title} ({task.duration_minutes} min) - {reason}"
                )
                total += task.duration_minutes
            lines.append("")
        lines.append(
            f"Total: {total} of {self.owner.available_minutes} available minutes."
        )
        return "\n".join(lines)

    def _collect_due_tasks(self, on_date: date) -> list[Task]:
        """Return the owner's tasks that are due today or past due on the given date."""
        return [
            task
            for task in self.owner.get_all_tasks()
            if task.is_due(on_date) in ("due today", "past due")
        ]

    def _rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority, highest first."""
        # Among equal priorities, shorter tasks come first so more of them fit.
        return sorted(tasks, key=lambda task: (-task.priority, task.duration_minutes))

    def _fit_to_available_time(
        self, ranked: list[Task]
    ) -> tuple[list[tuple[Task, str]], list[tuple[Task, str]]]:
        """Return (scheduled, skipped), each as a list of (task, reason)."""
        priority_names = {1: "Low", 2: "Medium", 3: "High"}
        remaining = self.owner.available_minutes
        scheduled: list[tuple[Task, str]] = []
        skipped: list[tuple[Task, str]] = []
        timed: list[Task] = []  # scheduled tasks that have a fixed start_time
        for task in ranked:
            clash = self._find_clash(task, timed)
            if task.duration_minutes > self.owner.available_minutes:
                skipped.append(
                    (task, f"Needs {task.duration_minutes} min, longer than the "
                           f"{self.owner.available_minutes} min available in total")
                )
            elif task.duration_minutes > remaining:
                skipped.append(
                    (task, f"Needs {task.duration_minutes} min but only {remaining} min left")
                )
            elif clash:
                skipped.append(
                    (task, f"At {format_time(task.start_time)} it overlaps "
                           f"{clash.title} at {format_time(clash.start_time)}")
                )
            else:
                remaining -= task.duration_minutes
                when = f", set for {format_time(task.start_time)}" if task.start_time else ""
                scheduled.append(
                    (task, f"{priority_names[task.priority]} priority{when}, fits "
                           f"({remaining} min left after it)")
                )
                if task.start_time:
                    timed.append(task)
        return scheduled, skipped

    def check_conflict(self, task: Task) -> str | None:
        """Return a warning if task's time overlaps an existing pending task, else None.

        Checks tasks across all of the owner's pets. Tasks only conflict when their
        due dates match; a task with no due_date is treated as due on any date.
        """
        if task.start_time is None:
            return None
        others = [
            other
            for other in self.owner.get_all_tasks()
            if other is not task
            and not other.is_complete
            and (other.due_date == task.due_date or None in (other.due_date, task.due_date))
        ]
        clash = self._find_clash(task, [other for other in others if other.start_time])
        if clash is None:
            return None
        pet = self.owner.get_pet(clash.pet_id)
        whose = f" ({pet.name})" if pet else ""
        return (
            f"Warning: {task.title} at {format_time(task.start_time)} for "
            f"{task.duration_minutes} min overlaps {clash.title}{whose} at "
            f"{format_time(clash.start_time)} for {clash.duration_minutes} min"
        )

    def add_task(self, pet: Pet, task: Task) -> str | None:
        """Add task to pet and return a conflict warning, or None if there is none.

        A conflict never blocks the add or raises; the task is always added.
        """
        warning = self.check_conflict(task)
        pet.add_task(task)
        return warning

    def filter_tasks(
        self, is_complete: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return the owner's tasks matching the given completion status and/or pet name.

        A filter left as None is not applied. Pet names are matched case-insensitively.
        """
        tasks = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.strip().lower() != pet_name.strip().lower():
                continue
            tasks.extend(pet.tasks)
        if is_complete is not None:
            tasks = [task for task in tasks if task.is_complete == is_complete]
        return tasks

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return tasks in clock order by start_time; tasks with no start_time go last."""
        return sorted(tasks, key=lambda task: (task.start_time is None, task.start_time or time.min))

    @staticmethod
    def _find_clash(task: Task, timed: list[Task]) -> Task | None:
        """Return an already-scheduled timed task whose time overlaps this one, if any."""
        if task.start_time is None:
            return None
        start = task.start_time.hour * 60 + task.start_time.minute
        end = start + task.duration_minutes
        for other in timed:
            other_start = other.start_time.hour * 60 + other.start_time.minute
            if start < other_start + other.duration_minutes and other_start < end:
                return other
        return None
