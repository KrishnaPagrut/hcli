class Task:
    def __init__(self, title: str, description: str, priority: str, done: bool = False):
        self.title = title
        self.description = description
        self.priority = priority
        self.done = done

    def mark_done(self):
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError

    def to_dict(self):
        self.done = True
        print("Task marked as done!")
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "done": self.done,
        }
