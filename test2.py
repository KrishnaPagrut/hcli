# main.py
from tasks import TaskManager, Task

def main():
    manager = TaskManager()

    # Create a new task
    learn_ai = manager.add_task("Learn AI", "Complete tutorials on machine learning")

    # Add subtasks
    learn_ai.add_subtask(Task("Read textbook", "Chapter 1 - Introduction"))
    learn_ai.add_subtask(Task("Watch video", "Neural networks basics"))
    learn_ai.add_subtask(Task("Code project", "Build a simple regression model"))

    # Mark one as done
    manager.mark_done("Read textbook")

    # Print hierarchy
    print(manager)

    # Export to JSON
    manager.export_to_json("learn_ai.json")
    print("✅ Tasks exported to learn_ai.json")

if __name__ == "__main__":
    main()
