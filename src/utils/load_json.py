import json

def load_task_list(file_path = 'data/tasks/task_list.json', type = None):
    with open(file_path, 'r') as file:
        task_data = json.load(file)
        task_list = list(task_data.keys())

    if type == "all":
        return task_data
    elif type == "task_list":
        return task_list

def load_fsm(file_path = "data/fsm/states.json", type = None):
    with open(file_path, 'r') as file:
        fsm_data = json.load(file)

    if type == "fsm":
        return fsm_data
    elif type == "events":
        return fsm_data["events"], fsm_data["event_examples"]