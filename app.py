from datetime import time

import streamlit as st

from pawpal_system import VALID_CATEGORIES, Owner, Pet, Task, Scheduler, format_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Original starter code, replaced by the Owner/Pet wiring below:
# st.subheader("Quick Demo Inputs (UI only)")
# owner_name = st.text_input("Owner name", value="Jordan")
# pet_name = st.text_input("Pet name", value="Mochi")
# species = st.selectbox("Species", ["dog", "cat", "other"])

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Minutes available per day", min_value=0, max_value=1440, value=120
)

# Streamlit reruns this script on every interaction, so the Owner lives in
# session_state and is only created once.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
owner = st.session_state.owner
if owner_name.strip():
    owner.name = owner_name
owner.available_minutes = int(available_minutes)

st.subheader("Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    existing_names = {pet.name.strip().casefold() for pet in owner.pets}
    if pet_name.strip().casefold() in existing_names:
        st.error(f"{owner.name} already has a pet called {pet_name.strip()!r}.")
    else:
        try:
            owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
            st.success(f"Added {pet_name} to {owner.name}'s pets.")
        except ValueError as error:
            st.error(str(error))

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"Name": pet.name, "Species": pet.species, "Age": pet.age, "Tasks": pet.task_count()}
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

# Original starter code, replaced by the Task wiring below:
# st.markdown("### Tasks")
# st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")
#
# if "tasks" not in st.session_state:
#     st.session_state.tasks = []
#
# col1, col2, col3 = st.columns(3)
# with col1:
#     task_title = st.text_input("Task title", value="Morning walk")
# with col2:
#     duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
# with col3:
#     priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
#
# if st.button("Add task"):
#     st.session_state.tasks.append(
#         {"title": task_title, "duration_minutes": int(duration), "priority": priority}
#     )
#
# if st.session_state.tasks:
#     st.write("Current tasks:")
#     st.table(st.session_state.tasks)
# else:
#     st.info("No tasks yet. Add one above.")

st.markdown("### Tasks")

PRIORITY_VALUES = {"low": 1, "medium": 2, "high": 3}
PRIORITY_NAMES = {value: name for name, value in PRIORITY_VALUES.items()}

if not owner.pets:
    st.info("Add a pet above before adding tasks.")
else:
    pet_id = st.selectbox(
        "Pet", [pet.id for pet in owner.pets], format_func=lambda pid: owner.get_pet(pid).name
    )

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox("Category", sorted(VALID_CATEGORIES))
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", list(PRIORITY_VALUES), index=2)

    set_time = st.checkbox("Set a fixed time")
    start_time = st.time_input("Start time", value=time(8, 0)) if set_time else None

    if st.button("Add task"):
        try:
            owner.get_pet(pet_id).add_task(
                Task(
                    title=task_title,
                    category=category,
                    duration_minutes=int(duration),
                    priority=PRIORITY_VALUES[priority],
                    start_time=start_time,
                )
            )
            st.success(f"Added {task_title} to {owner.get_pet(pet_id).name}.")
        except ValueError as error:
            st.error(str(error))

if owner.total_task_count():
    st.write(f"Current tasks ({owner.total_task_count()} total):")
    st.table(
        [
            {
                "Pet": pet.name,
                "Task": task.title,
                "Category": task.category,
                "Minutes": task.duration_minutes,
                "Priority": PRIORITY_NAMES[task.priority],
                "Time": format_time(task.start_time) if task.start_time else "Anytime",
            }
            for pet in owner.pets
            for task in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
