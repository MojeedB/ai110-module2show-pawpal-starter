from datetime import date, time, timedelta

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


# ---------- helpers ----------

def make_scheduler():
    owner = Owner(name="Jordan", available_minutes=240)
    rex = Pet(name="Rex", species="dog")
    mia = Pet(name="Mia", species="cat")
    owner.add_pet(rex)
    owner.add_pet(mia)
    return Scheduler(owner), rex, mia


def timed_task(title, hour, minute=0, duration=30, due=None, **kwargs):
    return Task(
        title=title,
        category="walk",
        duration_minutes=duration,
        start_time=time(hour, minute),
        due_date=due,
        **kwargs,
    )


# ---------- sorting ----------

def test_sort_by_time_returns_chronological_order():
    tasks = [timed_task("C", 18), timed_task("A", 7, 30), timed_task("B", 12)]

    result = Scheduler.sort_by_time(tasks)

    assert [t.title for t in result] == ["A", "B", "C"]


def test_sort_by_time_puts_tasks_without_start_time_last():
    flexible = Task(title="Flexible", category="grooming", duration_minutes=10)
    early = timed_task("Early", 6)
    late = timed_task("Late", 22)

    result = Scheduler.sort_by_time([flexible, late, early])

    assert [t.title for t in result] == ["Early", "Late", "Flexible"]


def test_sort_by_time_handles_midnight_and_empty_list():
    midnight = timed_task("Midnight", 0, 0)
    noon = timed_task("Noon", 12)

    assert Scheduler.sort_by_time([noon, midnight])[0] is midnight
    assert Scheduler.sort_by_time([]) == []


def test_daily_plan_lists_timed_tasks_in_clock_order():
    scheduler, rex, mia = make_scheduler()
    today = date.today()
    rex.add_task(timed_task("Evening walk", 18, due=today))
    mia.add_task(timed_task("Morning feed", 8, due=today))
    rex.add_task(timed_task("Lunch", 12, due=today))

    plan = scheduler.generate_daily_plan(today)

    assert [t.title for t, _ in plan] == ["Morning feed", "Lunch", "Evening walk"]


# ---------- recurrence ----------

def test_daily_task_next_occurrence_is_one_day_later():
    due = date(2026, 1, 10)
    task = Task(title="Feed", category="feeding", duration_minutes=5,
                recurrence="daily", due_date=due)

    nxt = task.next_occurrence()

    assert nxt.due_date == due + timedelta(days=1)
    assert nxt.is_complete is False
    assert nxt.id != task.id


def test_weekly_task_next_occurrence_is_seven_days_later():
    due = date(2026, 1, 10)
    task = Task(title="Bath", category="grooming", duration_minutes=20,
                recurrence="weekly", due_date=due)

    assert task.next_occurrence().due_date == due + timedelta(days=7)


def test_non_recurring_task_has_no_next_occurrence():
    task = Task(title="Vet visit", category="meds", duration_minutes=60)

    assert task.next_occurrence() is None
    assert task.mark_complete() is None


def test_recurring_task_without_due_date_counts_from_today():
    task = Task(title="Feed", category="feeding", duration_minutes=5, recurrence="daily")

    assert task.next_occurrence().due_date == date.today() + timedelta(days=1)


def test_next_occurrence_crosses_month_boundary():
    task = Task(title="Feed", category="feeding", duration_minutes=5,
                recurrence="daily", due_date=date(2026, 1, 31))

    assert task.next_occurrence().due_date == date(2026, 2, 1)


def test_mark_complete_twice_does_not_create_duplicate_occurrence():
    task = Task(title="Feed", category="feeding", duration_minutes=5,
                recurrence="daily", due_date=date(2026, 1, 10))

    assert task.mark_complete() is not None
    assert task.mark_complete() is None


def test_complete_task_adds_next_occurrence_to_same_pet():
    pet = Pet(name="Rex", species="dog")
    task = Task(title="Walk", category="walk", duration_minutes=30,
                recurrence="daily", due_date=date(2026, 1, 10))
    pet.add_task(task)

    new_task = pet.complete_task(task.id)

    assert task.is_complete is True
    assert new_task is not None
    assert new_task.pet_id == pet.id
    assert pet.task_count() == 2
    assert new_task in pet.get_pending_tasks()


def test_complete_task_unknown_id_returns_none():
    pet = Pet(name="Rex", species="dog")

    assert pet.complete_task("missing") is None


def test_next_occurrence_preserves_task_details():
    task = Task(title="Meds", category="meds", duration_minutes=5, priority=3,
                start_time=time(9, 0), recurrence="weekly", due_date=date(2026, 1, 10))

    nxt = task.next_occurrence()

    assert (nxt.title, nxt.category, nxt.priority, nxt.start_time, nxt.recurrence) == (
        "Meds", "meds", 3, time(9, 0), "weekly"
    )


# ---------- conflict detection ----------

def test_check_conflict_flags_overlapping_tasks_for_same_pet():
    scheduler, rex, _ = make_scheduler()
    today = date.today()
    scheduler.add_task(rex, timed_task("Walk", 8, 0, 30, due=today))

    warning = scheduler.check_conflict(timed_task("Feed", 8, 15, 10, due=today))

    assert warning is not None
    assert "Walk" in warning and "Feed" in warning


def test_check_conflict_flags_overlap_across_different_pets():
    scheduler, rex, mia = make_scheduler()
    today = date.today()
    scheduler.add_task(rex, timed_task("Walk Rex", 8, 0, 30, due=today))

    warning = scheduler.add_task(mia, timed_task("Groom Mia", 8, 0, 30, due=today))

    assert warning is not None
    assert "Rex" in warning


def test_check_conflict_back_to_back_tasks_do_not_conflict():
    scheduler, rex, _ = make_scheduler()
    today = date.today()
    scheduler.add_task(rex, timed_task("Walk", 8, 0, 30, due=today))

    assert scheduler.check_conflict(timed_task("Feed", 8, 30, 10, due=today)) is None


def test_check_conflict_ignores_different_due_dates():
    scheduler, rex, _ = make_scheduler()
    today = date.today()
    scheduler.add_task(rex, timed_task("Walk", 8, 0, 30, due=today))

    tomorrow = today + timedelta(days=1)
    assert scheduler.check_conflict(timed_task("Feed", 8, 0, 30, due=tomorrow)) is None


def test_check_conflict_task_without_due_date_matches_any_date():
    scheduler, rex, _ = make_scheduler()
    scheduler.add_task(rex, timed_task("Walk", 8, 0, 30, due=date.today()))

    assert scheduler.check_conflict(timed_task("Feed", 8, 0, 30, due=None)) is not None


def test_check_conflict_ignores_completed_tasks():
    scheduler, rex, _ = make_scheduler()
    today = date.today()
    done = timed_task("Walk", 8, 0, 30, due=today)
    scheduler.add_task(rex, done)
    done.mark_complete()

    assert scheduler.check_conflict(timed_task("Feed", 8, 0, 30, due=today)) is None


def test_check_conflict_ignores_flexible_tasks():
    scheduler, rex, _ = make_scheduler()
    flexible = Task(title="Play", category="enrichment", duration_minutes=30)

    assert scheduler.check_conflict(flexible) is None


def test_check_conflict_does_not_conflict_with_itself():
    scheduler, rex, _ = make_scheduler()
    task = timed_task("Walk", 8, 0, 30, due=date.today())
    scheduler.add_task(rex, task)

    assert scheduler.check_conflict(task) is None


def test_add_task_with_conflict_warns_but_still_adds():
    scheduler, rex, _ = make_scheduler()
    today = date.today()
    scheduler.add_task(rex, timed_task("Walk", 8, 0, 30, due=today))
    clashing = timed_task("Feed", 8, 10, 10, due=today)

    warning = scheduler.add_task(rex, clashing)

    assert warning is not None
    assert clashing in rex.tasks


def test_daily_plan_skips_lower_priority_clashing_task():
    scheduler, rex, _ = make_scheduler()
    today = date.today()
    high = timed_task("Meds", 8, 0, 30, due=today, priority=3)
    low = timed_task("Play", 8, 15, 30, due=today, priority=1)
    rex.add_task(high)
    rex.add_task(low)

    plan = scheduler.generate_daily_plan(today)

    assert [t for t, _ in plan] == [high]
    assert scheduler.last_skipped[0][0] is low
    assert "overlaps" in scheduler.last_skipped[0][1]
