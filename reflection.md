# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    The initail thought here would be to have a class call owner that has a pet, and a pet class that is assign to an owner.
    we alse need to be able to track the task each owner must complete each day

- What classes did you include, and what responsibilities did you assign to each?
    Two main clases for an app like thise would be a user/owner class and a pet class
    User/Owner - Has a pet, name, can add, create and edit tasks, user can have many pets
    Pet - Has a name
    Task class keeps track of tasks to do for pets, priorities and completion

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
    We identify issues with validation and unique values in the attributes of the classes so 
    unique ID was added to the classes. This should allow for duplicate names of users and pets while 
    keeping the object unique and remove ambiguity and potential errors.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    Time and Priority
- How did you decide which constraints mattered most?
    Preference was added but was not considered as much as Time and priority. certain task need to be completed at specific times like feeding each pet at breakfast or lunch.
    Priority matters as well considering things like medication, these can't be left up to the owners preferred time schedule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
    Initialy, there was a pet.add_task which seemed resonable for adding task to the pet. This was substituted in favor of a schduler.add_task as an encapsulating method for conflict detection across all pets and tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    Cluade was used to design and brainstorm the unl design and implementation. It was also used to explain concepts
    and syntax that was unfamiliar like the Python Dataclass
- What kinds of prompts or questions were most helpful?
    Code review prompts were very helpful, for example i had to check if i was keeping track of the number of tasks
    each pet had and claude was able to review pawpal_system.py and give me a definitive answer.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    The initial implementations of the code did not include a dedicated time for the tasks so this was rejected and i added time specific tasks.
- How did you evaluate or verify what the AI suggested?
    i reviewed the logic of the code and tested the results without completeing relying on what claude had written.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    Scheduling 
    Task status
    Priority
    conflict check
    next occurence
- Why were these tests important?
    These make up a good portion of the app's logic, we want to make sure that tasks can be added in the correct order and completed without throwing errors, we also want to make sure there are no cases where the app crashes as a result of invalid edge cases.
    
**b. Confidence**

- How confident are you that your scheduler works correctly?
    Confidence level is about a 3.5, i would like to review more of the code to make sure this work as expected.
- What edge cases would you test next if you had more time?
    I'm not certain the recurrence method handels completeing of tasks that are over due.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    Generating the scheduling was satisfactory, the logic is fine as is but can always be improved

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    I would rebuild most of the logic and redesign the filtering and sorying logic. 
    Improve more quality of life features

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    Not to let the AI run away with the code, it implemented some nice things but was trying to get ahead of itself in other places.
