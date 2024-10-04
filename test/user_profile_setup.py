from typing import Any
from load_json import load_task_list, load_fsm

class FSM:
    def __init__(self, fsm_data):
        self.current_state = fsm_data["initial_state"]
        self.transitions = {}
        self.states = set()
        self.event_stack = []
        for transition in fsm_data["transitions"]:
            self.add_transition(transition["start_state"], transition["end_state"], transition["event"])
    
    def add_transition(self, start_state, end_state, event):
        if start_state not in self.transitions:
            self.transitions[start_state] = {}
        self.transitions[start_state][event] = end_state
        self.states.add(start_state)
        self.states.add(end_state)
    
    def state_changable(self, event):
        if self.current_state in self.transitions and event in self.transitions[self.current_state]:
            return True
        else:
            return False

    def state_change(self, event):
        self.current_state = self.transitions[self.current_state][event]

    def get_current_state(self):
        return self.current_state

class Primitive:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.complete = False
        # ranging from 1 to 5, from lay person to expert
        self.proficiency = 1

    def _get_name(self):
        return self.name

    def _get_description(self):
        return self.description
    
    def _get_completion(self):
        return self.complete
    
    def _set_completion(self):
        self.complete = True

    def _reset_completion(self):
        self.complete = False

    def _get_proficiency(self):
        return self.proficiency

    def _add_proficiency(self):
        self.proficiency = min(5, self.proficiency + 1)

    def _sub_proficiency(self):
        self.proficiency = max(1, self.proficiency - 1)

    def _set_proficiency(self, proficiency):
        if proficiency < 1 or proficiency > 5:
            raise ValueError(f"Proficiency level {proficiency} is out of range.")
        self.proficiency = proficiency

    def __repr__(self):
        return f"Token(name={self.name}, description={self.description}, proficiency={self.proficiency})"

class Task:
    def __init__(self, name, description, primitive_workflow):
        self.name = name
        self.description = description
        self.primitive_workflow = primitive_workflow
        self.current_pimitive = primitive_workflow
        self.complete = False
        self.trajectory = []

    def _get_name(self):
        return self.name

    def _get_description(self):
        return self.description
    
    def _get_current_primitive(self):
        if self.trajectory != []:
            return self.trajectory[-1]
        else:
            return None
    
    def _get_next_step_choices(self):
        choices = list(self.current_pimitive.keys())
        if choices == []:
            self.complete = True
        return choices
    
    def _select_next_step(self, primitive_name):
        if primitive_name in self.current_pimitive:
            self.trajectory.append(primitive_name)
            self.current_pimitive = self.current_pimitive[primitive_name]

    def _get_completion(self):
        return self.complete
    
    def _reset_task(self):
        self.current_pimitive = self.primitive_workflow
        self.trajectory = []
        self.complete = False

class Workflow:
    def __init__(self, workflow):
        self.workflow = workflow
        self.current_task = workflow
        self.trajectory = []
    
    def _get_current_task(self):
        if self.trajectory != []:
            return self.trajectory[-1]
        else:
            return None

    def _get_next_task_choices(self):
        choices = list(self.current_task.keys())
        if choices == []:
            return None
        return choices
    
    def _select_next_task(self, task_name):
        if task_name in self.current_task:
            self.trajectory.append(task_name)
            self.current_task = self.current_task[task_name]

    def reset_workflow(self):
        self.current_task = self.workflow
        self.trajectory = []

class UserProfile:
    def __init__(self, user_id = None):
        fsm_data = load_fsm(type = "fsm")
        task_data = load_task_list(type = "all")

        self.user_id = user_id
        self.fsm = FSM(fsm_data)
        self.workflow = Workflow(task_data['workflow'])
        self.tasks = self._create_task(task_data['tasks'])
        self.primitives = self._create_primitive(task_data['primitives'])

    def _create_task(self, task_data):
        # Dynamically create tasks from the provided task_data dictionary
        tasks = {}
        for task_name, task_info in task_data.items():
            tasks[task_name] = Task(
                name = task_name,
                description=task_info["description"],
                primitive_workflow=task_info["primitive_workflow"]
            )
        return tasks
    
    def _create_primitive(self, primitive_data):
        # Dynamically create primitives from the provided primitive_data dictionary
        primitives = {}
        for primitive_name, primitive_info in primitive_data.items():
            primitives[primitive_name] = Primitive(
                name = primitive_name,
                description = primitive_info["description"]
            )
        return primitives
    
    def get_user_id(self):
        return self.user_id
    
    def get_current_task(self):
        current_task = self.workflow._get_current_task()
        if current_task == None:
            return None
        else:
            return self.tasks[current_task]
    
    def get_next_task_choices(self):
        return self.workflow._get_next_task_choices()
    
    def select_next_task(self, task_name):
        self.workflow._select_next_task(task_name)
    
    def get_current_step(self):
        current_task = self.workflow._get_current_task()
        if current_task == None:
            return None
        else:
            current_primitive = self.tasks[current_task]._get_current_primitive()
            if current_primitive == None:
                return None
            else:
                return self.primitives[current_primitive]
    
    def set_current_step_complete(self):
        currtent_step = self.get_current_step()
        if currtent_step != None:
            currtent_step._set_completion()
    
    def get_next_step_choices(self):
        current_task = self.workflow._get_current_task()
        if current_task == None:
            return []
        else:
            return self.tasks[current_task]._get_next_step_choices()
        
    def select_next_step(self, primitive_name):
        current_task = self.get_current_task()
        if current_task != None:
            self.primitives[primitive_name].reset_completion()
            self.tasks[current_task]._select_next_step(primitive_name)

    def get_proficiency(self):
        current_step = self.get_current_step()
        if current_step != None:
            return current_step._get_proficiency()
        else:
            return None

    def add_proficiency(self):
        current_step = self.get_current_step()
        if current_step != None:
            current_step._add_proficiency()
         

    def sub_proficiency(self):
        current_step = self.get_current_step()
        if current_step != None:
            current_step._sub_proficiency()

    def set_proficiency(self, proficiency):
        current_step = self.get_current_step()
        if current_step != None:
            current_step._set_proficiency(proficiency)

    def check_task_completion(self):
        return self.get_current_task()._get_completion() and self.get_current_step().check_completion()
    
    def reset_task(self):
        self.get_current_task()._reset_task()