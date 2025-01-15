import random
from load_json import load_task_list, load_fsm

class FSM:
    def __init__(self, fsm_data):
        self.current_state = fsm_data["initial_state"]
        self.initial_state = fsm_data["initial_state"]
        self.transitions = {}
        self.states = set(fsm_data["states"])
        self.events = fsm_data["events"]
        self.event_examples = fsm_data["event_examples"]
        
        # Initialize transitions with multiple start states
        for transition in fsm_data["transitions"]:
            for start_state in transition["start_state"]:
                if start_state not in self.transitions:
                    self.transitions[start_state] = {}
                self.transitions[start_state][transition["event"]] = transition["end_state"]
    
    def _state_transition(self, event):
        """Transition to the next state based on the event and current state."""
        if event in self.transitions.get(self.current_state, {}):
            self.current_state = self.transitions[self.current_state][event]

    def _get_possible_events(self):
        events = list(self.transitions.get(self.current_state, {}).keys())
        examples = {}
        for event in events:
            if event not in self.event_examples:
                events.remove(event)
                continue
            examples[event] = self.event_examples[event]
        return events, examples
    
    def _get_current_state(self):
        return self.current_state

class SubFSM(FSM):
    def __init__(self, fsm_data):
        super().__init__(fsm_data)
        self.done = False

    def _initialize_state(self):
        self.current_state = self.initial_state
        self.done = False
    
    def _subfsm_handle_event(self, event):
        if event == "other":
            print("I'm sorry, I didn't understand that. Please try again.")
        # print(f'SubFSM(state:{self.current_state} event:{event})')
        self._state_transition(event)
        # print(f'SubFSM(state:{self.current_state})')
        if self._get_current_state() == "done":
            self.done = True

    def _is_done(self):
        return self.done
    
class ParentFSM(FSM):
    def __init__(self, fsm_data):
        super().__init__(fsm_data)
        self.sub_fsms = {}
        for state in self.states:
            sub_fsm_data = load_fsm(file_path=f'module/submodule/{state}.json', type='fsm')
            self.sub_fsms[state] = SubFSM(sub_fsm_data)

    def _parent_fsm_handle_event(self, event):
        if event == "other":
            print("I'm sorry, I didn't understand that. Please try again.")
        # print(f'ParentFSM(state:{self.current_state} event:{event})')
        self._state_transition(event)
        self.sub_fsms[self.current_state]._initialize_state()
        # print(f'ParentFSM(state:{self.current_state})')

class Primitive:
    def __init__(self, name, detail):
        self.name = name
        self.detail = detail
        self.complete = False
        '''
        ranging from 1 to 5, from lay person to expert
        if proficiency is greater or equal to 4, the user is considered an expert
        the system provides guidance base help to the user
        else the user is considered a lay person
        the system provides more detailed help to the user
        '''
        self.proficiency = 3

    def get_proficiency(self):
        return self.proficiency
    
    def add_one_to_proficiency(self):
        self.proficiency += 1

    def subtract_one_from_proficiency(self):
        self.proficiency -= 1

    def get_name(self):
        return self.name
    
    def get_detail(self):
        return self.detail

class Task:
    def __init__(self, name, description, primitive_workflow):
        self.name = name
        self.description = description
        self.primitive_workflow = primitive_workflow
        self.current_pimitive = primitive_workflow
        self.next_primitive_selection = None

    def get_name(self):
        return self.name
    
    def get_current_primitive_options(self):
        return list(self.current_pimitive.keys())
    
    def set_next_primitive_selection(self, primitive_name):
        self.next_primitive_selection = primitive_name
    
    def get_next_primitive_selection(self):
        return self.next_primitive_selection
    
    def remove_primitive(self, primitive_name):
        del self.current_pimitive[primitive_name]

    def select_next_primitive(self):
        self.current_pimitive = self.current_pimitive[self.next_primitive_selection]

    def is_done(self):
        return self.current_pimitive == {}

class Workflow:
    def __init__(self, workflow):
        self.workflow = workflow
        self.current_task = workflow
        self.trajectory_index = 0
        self.trajectory = []
        self.task_input = None
        self.all_task_options = self._find_all_task_options(workflow, [])
        self.current_all_task_options = self.all_task_options

    def _find_all_task_options(self, workflow, all_task_options):
        for key, value in workflow.items():
            if key not in all_task_options:
                all_task_options.append(key)
            if isinstance(value, dict):
                self._find_all_task_options(value, all_task_options)

        return all_task_options
    
    def _get_trajectory_index(self):
        return self.trajectory_index
    
    def _add_one_to_trajectory_index(self):
        self.trajectory_index += 1
    
    def _add_to_trajectory(self, task_name):
        self.trajectory.append(task_name)
    
    def _get_trajectory(self):
        return self.trajectory

    def _task_input_is_None(self):
        return self.task_input is None
    
    def _set_task_input(self, task_input):
        self.task_input = task_input

    def _get_task_input(self):
        return self.task_input
    
    def _get_current_all_task_options(self):
        return self.current_all_task_options
    
    def _set_current_task(self, task_name):
        self.trajectory = []
        self.trajectory = self._find_task_trajectory(task_name, self.workflow)

    def  _find_task_trajectory(self, task_name, current_workflow):
        if task_name in current_workflow:
            return [task_name]
        else:
            for key in current_workflow:
                result = self._find_task_trajectory(task_name, current_workflow[key])
                if result:
                    return [key] + result
        return None

    def _get_current_task(self):
        return self.trajectory[-1]
    
    def _remove_task(self, task):
        self.current_all_task_options.remove(task)

class GoalSettingWorkflow(Workflow):
    def __init__(self, workflow):
        super().__init__(workflow)
        self.next_task_selection = None

    def _get_current_task_choices(self):
        return list(self.current_task.keys())
    
    def _set_next_task_selection(self, task_name):
        self.next_task_selection = task_name

    def _get_next_task_selection(self):
        return self.next_task_selection
    
    def _select_next_task(self, task_name):
        self.current_task = self.current_task[task_name]

    def _remove_task(self, task_name):
        del self.current_task[task_name]

class UserProfile:
    def __init__(self, user_id = None):
        fsm_data = load_fsm(type = "fsm")
        task_data = load_task_list(type = "all")

        self.user_id = user_id
        self.location = None
        self.dialogue_fsm = ParentFSM(fsm_data)
        self.workflow = Workflow(task_data['workflow'])
        self.goal_setting_workflow = GoalSettingWorkflow(task_data['workflow'])
        self.tasks = self._create_task(task_data['tasks'])
        self.primitives = self._create_primitive(task_data['primitives'])

    def _create_task(self, task_data):
        # Dynamically create tasks from the provided task_data dictionary
        tasks = {}
        for task_name, task_info in task_data.items():
            tasks[task_name] = Task(
                name = task_name,
                description=task_info["description"],
                primitive_workflow=task_info["primitive workflow"]
            )
        return tasks
    
    def _create_primitive(self, primitive_data):
        # Dynamically create primitives from the provided primitive_data dictionary
        primitives = {}
        for primitive_name, primitive_detail in primitive_data.items():
            primitives[primitive_name] = Primitive(
                name = primitive_name,
                detail = primitive_detail
            )
        return primitives
    
    def get_location(self):
        return self.location

    def set_location(self, location):
        self.location = location
    
    def get_subfsm_possible_events(self):
        return self.dialogue_fsm.sub_fsms[self.dialogue_fsm._get_current_state()]._get_possible_events()
    
    def subfsm_handle_event(self, event):
        self.dialogue_fsm.sub_fsms[self.dialogue_fsm._get_current_state()]._subfsm_handle_event(event)

    def subfsm_is_done(self):
        return self.dialogue_fsm.sub_fsms[self.dialogue_fsm._get_current_state()]._is_done()
    
    def get_parent_fsm_possible_events(self):
        return self.dialogue_fsm._get_possible_events()

    def parent_fsm_handle_event(self, event):
        self.dialogue_fsm._parent_fsm_handle_event(event)
    
    def get_parent_fsm_state(self):
        return self.dialogue_fsm._get_current_state()
    
    def get_subfsm_state(self):
        return self.dialogue_fsm.sub_fsms[self.dialogue_fsm._get_current_state()]._get_current_state()
    
    def get_goal_setting_current_task_choices(self):
        return self.goal_setting_workflow._get_current_task_choices()

    def set_goal_setting_next_task_selection(self, task):
        self.goal_setting_workflow._set_next_task_selection(task)

    def get_goal_setting_next_task_selection(self):
        return self.goal_setting_workflow._get_next_task_selection()
    
    def select_goal_setting_next_task(self, task):
        self.goal_setting_workflow._select_next_task(task)

    def remove_goal_setting_task(self, task_name):
        self.goal_setting_workflow._remove_task(task_name)

    def get_workflow_trajectory_index(self):
        return self.workflow._get_trajectory_index()
    
    def add_one_to_workflow_trajectory_index(self):
        self.workflow._add_one_to_trajectory_index()
    
    def add_to_workflow_trajectory(self, task_name):
        self.workflow._add_to_trajectory(task_name)

    def get_workflow_trajectory(self):
        return self.workflow._get_trajectory()

    def workflow_task_input_is_None(self):
        return self.workflow._task_input_is_None()
    
    def set_workflow_task_input(self, task_input):
        self.workflow._set_task_input(task_input)

    def get_workflow_task_input(self):
        return self.workflow._get_task_input()
    
    def get_current_all_task_options(self):
        return self.workflow._get_current_all_task_options()
    
    def set_workflow_current_task(self, task_name):
        self.workflow._set_current_task(task_name)

    def get_workflow_current_task(self):
        return self.workflow._get_current_task()
    
    def remove_task_from_workflow_current_all_task_options(self, task):
        self.workflow._remove_task(task)

    def get_task(self, task_name):
        return self.tasks[task_name]
    
    def get_primitive(self, primitive_name):
        return self.primitives[primitive_name]