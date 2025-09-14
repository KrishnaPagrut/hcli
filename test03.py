from test01 import Task

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, title, description):
        task = Task(title, description)
        self.tasks.append(task)
        return task

    def list_tasks(self):
        return [t.to_dict() for t in self.tasks]
