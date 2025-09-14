from test01 import Task

def create_default_task():
    return Task("Default Title", "Default Description", "medium")

def mark_and_print(task: Task):
    task.mark_done()
    print(task.to_dict())
