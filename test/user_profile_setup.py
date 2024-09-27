import json

class Task:
    def __init__(self, description, elements):
        # ranging from 0 to 2, from lay person to expert
        self.proficiency = 0
        self.description = description
        self.element_check_list = list(elements.keys())
        self.elements = {}

    def _get_proficiency(self):
        return self.proficiency
    
    def _add_proficiency(self):
        self.proficiency = min(2, self.proficiency + 1)

    def _sub_proficiency(self):
        self.proficiency = max(0, self.proficiency - 1)

    def _get_description(self):
        return self.description

    def _get_element_list(self):
        return self.element_check_list
    
    def _get_all_elements(self):
        return self.elements
    
    def _get_element(self, key):
        return self.elements.get(key)

    def _set_element(self, key, value):
        if key in self.element_check_list:
            self.elements[key] = value
        else:
            raise ValueError(f"{key} is not a valid element for this task.")

    def _reset_all_element(self):
        self.elements = {}

class all_tasks:
    def __init__(self, file_path = 'module/task_list.json'):
        with open(file_path, 'r') as file:
            task_data = json.load(file)
        self.task_list = list(task_data.keys())
        self.tasks = self._load_tasks(task_data)

    def _load_tasks(self, task_data):
        # Dynamically create tasks from the provided task_data dictionary
        tasks = {}
        for task_name, task_info in task_data.items():
            tasks[task_name] = Task(
                description=task_info["description"],
                elements=task_info["elements"]
            )
        return tasks
    
    def _get_task_list(self):
        return self.task_list

    def _check_task_exist(self, task_name):
        if task_name in self.task_list:
            return self.tasks[task_name]
        else:
            raise ValueError(f"Task {task_name} not found.")

class user_profile:
    def __init__(self, file_path = 'module/task_list.json', user_id = None):
        self.user_id = user_id
        self.tasks = all_tasks(file_path)
        self.current_task = None
        # ranging from 0 to 2, from lay person to expert
        self.proficiency = 0

    def get_user_id(self):
        return self.user_id
    
    def get_task_list(self):
        return self.tasks._get_task_list()

    def get_current_task(self):
        return self.current_task

    def set_current_task(self, task_name):
        self.current_task = self.tasks._check_task_exist(task_name)
    
    def reset_current_task(self):
        self.current_task._reset_all_element()

    def get_task_element_list(self):
        return self.current_task._get_element_list()

    def get_task_all_elements(self):
        return self.current_task._get_all_elements()

    def set_task_element(self, element_name, value):
        self.current_task._set_element(element_name, value)

    def get_task_element(self, element_name):
        return self.current_task._get_element(element_name)

    def get_task_description(self):
        return self.current_task._get_description()
    
    def get_proficiency(self):
        return self.current_task._get_proficiency()
    
    def add_proficiency(self):
        self.current_task._add_proficiency()

    def sub_proficiency(self):
        self.current_task._sub_proficiency()