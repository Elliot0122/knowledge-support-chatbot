import json

class Task:
    def __init__(self, description, elements):
        self.description = description
        self.element_check_list = list(elements.keys())
        self.elements = {}

    def get_elements(self):
        return self.elements

    def set_element_value(self, key, value):
        if key in self.element_check_list:
            self.elements[key] = value
        else:
            raise ValueError(f"{key} is not a valid element for this task.")

    def reset_element(self):
        self.elements = {}

class all_tasks:
    def __init__(self, task_data):
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

    def get_task(self, task_name):
        if task_name in self.task_list:
            return self.tasks[task_name]
        else:
            raise ValueError(f"Task {task_name} not found.")
        
    def set_task_element(self, task_name, element_name, value):
        if task_name in self.task_list:
            self.tasks[task_name].set_element_value(element_name, value)
        else:
            raise ValueError(f"Task {task_name} not found.")
    
    def reset_task_state(self, task_name):
        if task_name in self.task_list:
            self.tasks[task_name].reset_element()

def load_task_from_json(file_path = 'module/task_list.json'):
    with open(file_path, 'r') as file:
        task_data = json.load(file)
        tasks = all_tasks(task_data)
    return tasks

if __name__ == "__main__":
    tasks = load_task_from_json('module/task_list.json')
    get_direction_task = tasks.get_task("get direction")

    # Setting element values dynamically
    tasks.set_task_element("get direction", "starting point", "Home")
    tasks.set_task_element("get direction", "destination", "Office")

    # Accessing updated task elements
    print(get_direction_task.get_elements())  # Updated elements
    tasks.reset_task_state("get direction")
    print(get_direction_task.get_elements())  # Empty elements