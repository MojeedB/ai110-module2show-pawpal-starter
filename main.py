from datetime import date, time

from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Jordan", available_minutes=120)

rex = Pet(name="Rex", species="dog", age=4)
whiskers = Pet(name="Whiskers", species="cat", age=2)

owner.add_pet(rex)
owner.add_pet(whiskers)

rex.add_task(Task(title="Morning walk", category="walk", duration_minutes=30, priority=3,start_time=time(7, 30)))
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


