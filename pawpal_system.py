from dataclasses import dataclass, field
from datetime import date
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
    "recurrence",
}


def new_id() -> str:
    return uuid4().hex


@dataclass
class Task:
    title: str
    category: str  # must be in VALID_CATEGORIES
    duration_minutes: int  # must be > 0
    priority: int = 2  # must be in VALID_PRIORITIES
    preferred_time: str = ""  # e.g. "morning"
    recurrence: str | None = None  # must be in VALID_RECURRENCES
    is_complete: bool = False
    id: str = field(default_factory=new_id)
    pet_id: str = ""  # set by Pet.add_task; links the task back to its pet

    def __post_init__(self) -> None:
        """Validate title, category, duration_minutes, priority and recurrence."""
        pass

    def mark_complete(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def is_due(self, on_date: date) -> bool:
        pass

    def edit(self, **changes) -> None:
        """Update only keys in EDITABLE_TASK_FIELDS, validating the new values."""
        pass


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
        pass

    def add_task(self, task: Task) -> None:
        """Attach a task and set task.pet_id to this pet's id."""
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass

    def get_tasks_by_category(self, category: str) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int  # must be >= 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)
    id: str = field(default_factory=new_id)

    def __post_init__(self) -> None:
        """Validate name is non-empty and available_minutes is not negative."""
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass

    def get_pet(self, pet_id: str) -> Pet | None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass

    def set_preference(self, key: str, value) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_daily_plan(self, on_date: date) -> list[tuple[Task, str]]:
        """Return an ordered list of (task, reason) that fits the owner's time."""
        pass

    def explain_plan(self, plan: list[tuple[Task, str]]) -> str:
        pass

    def _collect_due_tasks(self, on_date: date) -> list[Task]:
        pass

    def _rank_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fit_to_available_time(
        self, ranked: list[Task]
    ) -> tuple[list[tuple[Task, str]], list[tuple[Task, str]]]:
        """Return (scheduled, skipped), each as a list of (task, reason)."""
        pass
