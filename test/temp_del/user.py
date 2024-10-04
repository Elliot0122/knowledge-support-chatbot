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
        # ranging from 1 to 5, from lay person to expert
        self.proficiency = 1

    def _get_name(self):
        return self.name

    def _get_description(self):
        return self.description

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
        self.trajectory = []

    def _get_name(self):
        return self.name

    def _get_description(self):
        return self.description

    def _get_next_steps(self):
        return list(self.current_pimitive.keys())
    
    def _get_trajectory(self):
        return self.trajectory
    
    def _select_primitive(self, primitive_name):
        self.trajectory.append(primitive_name)
        self.current_pimitive = self.current_pimitive[primitive_name]

    def _reset_task(self):
        self.current_pimitive = self.primitive_workflow
        self.trajectory = []

class Workflow:
    def __init__(self, task_data):
        workflow = task_data['workflow']
        tasks = task_data['tasks']
        primitives = task_data['primitives']
        
        self.tasks = self._create_task(tasks)
        self.primitives = self._create_primitive(primitives)
        self.workflow = workflow
        self.current_task = workflow

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
    
    def _get_current_task(self):
        return self.tasks[self.trajectory[-1]]
    
    def _get_next_task_selection(self):
        return list(self.current_task.keys())
    
    def _get_trajectory(self):
        return self.trajectory
    
    def _select_task(self, task_name):
        self.current_task = self._check_task_exist(task_name)
        self.trajectory.append(task_name)

    def _check_task_exist(self, task_name):
        if task_name in self.task_list:
            return task_name
        else:
            raise ValueError(f"Task {task_name} not found.")
    
    def _reset_workflow(self):
        self.current_task = self.workflow
        self.trajectory = []

class UserProfile:
    def __init__(self, user_id = None):
        self.user_id = user_id

        fsm_data = load_fsm(type = "fsm")
        self.fsm = FSM(fsm_data)
        
        task_data = load_task_list(type = "all")
        self.workflow = Workflow(task_data)

        def get_user_id(self):
            return self.user_id

        def get_current_task(self):
            return self.workflow._get_current_task()
        
        def get_task_description(self):
            return self.get_current_task()._get_description()
        
        def get_next_steps(self):
            return self.get_current_task()._get_next_steps()
        
        def select_next_step(self, step_name):
            self.get_current_task()._select_primitive(step_name)

        def get_next_task_selection(self):
            return self.workflow._get_next_task_selection()
        
        def select_next_task(self, task_name):
            self.workflow._select_task(task_name)

        def get_proficiency(self, primitive_name = None):
            if primitive_name:
                return self.workflow.primitives[primitive_name]._get_proficiency()
            else:
                raise ValueError("No primitive name is unprovided or incorrect.")

        def add_proficiency(self, primitive_name = None):
            if primitive_name:
                self.workflow.primitives[primitive_name]._add_proficiency()
            else:
                raise ValueError("No primitive name is unprovided or incorrect.")

        def sub_proficiency(self, primitive_name = None):
            if primitive_name:
                self.workflow.primitives[primitive_name]._sub_proficiency()
            else:
                raise ValueError("No primitive name is unprovided or incorrect.")
            
        def reset_current_task(self):
            self.current_task._reset_task()

if __name__ == "__main__":
    user = UserProfile(user_id = 0)
