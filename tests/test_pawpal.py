from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status_of_scheduled_task():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Morning walk", category="walk", duration_minutes=30))

    today = date.today()
    plan = Scheduler(owner).generate_daily_plan(today)
    scheduled_task, _reason = plan[0]

    assert scheduled_task.is_complete is False
    assert scheduled_task.is_due(today) == "due today"

    scheduled_task.mark_complete()

    assert scheduled_task.is_complete is True
    assert scheduled_task.is_due(today) == "complete"


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Whiskers", species="cat")
    assert pet.task_count() == 0

    pet.add_task(Task(title="Breakfast", category="feeding", duration_minutes=5))
    assert pet.task_count() == 1

    pet.add_task(Task(title="Playtime", category="enrichment", duration_minutes=15))
    assert pet.task_count() == 2
