from datetime import date, time

from pawpal_system import Owner, Pet, Task, Scheduler, format_time

owner = Owner(name="Jordan", available_minutes=120)

rex = Pet(name="Rex", species="dog", age=4)
whiskers = Pet(name="Whiskers", species="cat", age=2)

owner.add_pet(rex)
owner.add_pet(whiskers)

rex.add_task(Task(title="Morning walk", category="walk", duration_minutes=30, priority=3, start_time=time(7, 30), recurrence="daily"))
rex.add_task(Task(title="Fetch session", category="enrichment", duration_minutes=15, priority=1))
whiskers.add_task(
    Task(title="Breakfast", category="feeding", duration_minutes=5, priority=3, start_time=time(8, 0))
)

today = date.today()
scheduler = Scheduler(owner)
plan = scheduler.generate_daily_plan(today)

print(f"Today's schedule for {owner.name} ({today:%A, %B %d, %Y})")
print("-" * 100)
print(scheduler.explain_plan(plan))

if scheduler.last_skipped:
    print("\nSkipped:")
    for task, reason in scheduler.last_skipped:
        print(f"- {task.title}: {reason}")


def show(heading: str, tasks: list[Task]) -> None:
    print(f"\n{heading}")
    if not tasks:
        print("  (none)")
    for task in tasks:
        at = format_time(task.start_time) if task.start_time else "Anytime"
        status = "done" if task.is_complete else "pending"
        pet = owner.get_pet(task.pet_id)
        priority = {1: "Low", 2: "Medium", 3: "High"}[task.priority]
        print(f"  {at:<8} {task.title} - {pet.name}, {priority} priority, {status}")


# Added out of clock order on purpose, to show sort_by_time.
whiskers.add_task(Task(title="Evening meds", category="meds", duration_minutes=5, priority=1, start_time=time(18, 0)))
whiskers.add_task(Task(title="Brush fur", category="grooming", duration_minutes=10, start_time=time(9, 0)))
rex.complete_task(rex.tasks[0].id)  # recurring, so this also adds tomorrow's walk

# Overlaps Rex's 7:30 walk (30 min), so this warns but is still added.
warning = scheduler.add_task(whiskers, Task(title="Litter box", category="grooming", duration_minutes=10, start_time=time(7, 45)))
if warning:
    print(f"\n{warning}")

print("\n" + "-" * 100)
show("All tasks, in the order they were added:", owner.get_all_tasks())
show("All tasks, sorted by time:", Scheduler.sort_by_time(owner.get_all_tasks()))
show("Pending tasks:", scheduler.filter_tasks(is_complete=False))
show("Completed tasks:", scheduler.filter_tasks(is_complete=True))
show("Whiskers' tasks, sorted by time:", Scheduler.sort_by_time(scheduler.filter_tasks(pet_name="whiskers")))
show("Whiskers' pending tasks:", scheduler.filter_tasks(is_complete=False, pet_name="Whiskers"))

