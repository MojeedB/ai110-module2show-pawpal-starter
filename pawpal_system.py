from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    title: str
    category: str  # e.g. "walk", "feeding", "meds", "enrichment", "grooming"
    duration_minutes: int
    priority: int = 2  # 1 = low, 2 = medium, 3 = high
    preferred_time: str = ""  # e.g. "morning"
    recurrence: str | None = None  # "daily", "weekly" or None
    is_complete: bool = False

    def mark_complete(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def is_due(self, on_date: date) -> bool:
        pass

    def edit(self, **fields) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass

    def get_tasks_by_category(self, category: str) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_name: str) -> None:
        pass

    def get_pet(self, name: str) -> Pet | None:
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
