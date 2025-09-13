import json
from typing import List, Dict, Optional


class Task:
    def __init__(self, title: str, description: str = "", done: bool = False):
        self.title = title
        self.description = description
        self.done = done
        self.subtasks: List["Task"] = []

    def add_subtask(self, subtask: "Task") -> None:
        self.subtasks.append(subtask)

    def mark_done(self) -> None:
        self.done = True
        for sub in self.subtasks:
            sub.mark_done()

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "done": self.done,
            "subtasks": [sub.to_dict() for sub in self.subtasks],
        }

    def __str__(self, level: int = 0) -> str:
        indent = "  " * level
        status = "[x]" if self.done else "[ ]"
        result = f"{indent}{status} {self.title} - {self.description}\n"
        for sub in self.subtasks:
            result += sub.__str__(level + 1)
        return result


class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(title, description)
        self.tasks.append(task)
        return task

    def find_task(self, title: str) -> Optional[Task]:
        def _find(task_list: List[Task]) -> Optional[Task]:
            for t in task_list:
                if t.title == title:
                    return t
                result = _find(t.subtasks)
                if result:
                    return result
            return None

        return _find(self.tasks)

    def mark_done(self, title: str) -> bool:
        task = self.find_task(title)
        if task:
            task.mark_done()
            return True
        return False

    def export_to_json(self, file_name: str) -> None:
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def __str__(self) -> str:
        result = ""
        for task in self.tasks:
            result += task.__str__()
        return result


if __name__ == "__main__":
    manager = TaskManager()

    # Add main tasks
    study = manager.add_task("Study", "Prepare for exams")
    workout = manager.add_task("Workout", "Stay healthy")

    # Add subtasks under study
    math = Task("Math", "Review calculus notes")
    study.add_subtask(math)
    math.add_subtask(Task("Practice Problems", "Solve 20 questions"))
    math.add_subtask(Task("Flashcards", "Revise formulas"))

    cs = Task("CS Project", "Build scheduler app")
    study.add_subtask(cs)
    cs.add_subtask(Task("Frontend", "React components"))
    cs.add_subtask(Task("Backend", "Flask API"))
    cs.add_subtask(Task("Testing", "Unit tests"))

    # Add subtasks under workout
    workout.add_subtask(Task("Cardio", "Run 5 km"))
    workout.add_subtask(Task("Strength", "Push-ups and squats"))

    # Mark one task done
    manager.mark_done("Frontend")

    # Print the task hierarchy
    print(manager)

    # Export to JSON
    manager.export_to_json("tasks.json")
    print("Tasks exported to tasks.json ✅")
