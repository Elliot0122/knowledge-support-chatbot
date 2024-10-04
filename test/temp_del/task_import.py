import json

def load_task_from_json(file_path = 'module/task_list.json'):
    with open(file_path, 'r') as file:
        task_data = json.load(file)
        task_list = list(task_data.keys())
    return task_list
