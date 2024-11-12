import random
from load_json import load_task_list, load_fsm
from nlu_unit import text_classification

class FSM:
    def __init__(self, fsm_data):
        self.current_state = fsm_data["initial_state"]
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

    def state_transition(self, event):
        """Transition to the next state based on the event and current state."""
        if event in self.transitions.get(self.current_state, {}):
            self.current_state = self.transitions[self.current_state][event]

    def get_possible_events(self):
        events = list(self.transitions.get(self.current_state, {}).keys())
        examples = {}
        for event in events:
            if event not in self.event_examples:
                events.remove(event)
                continue
            examples[event] = self.event_examples[event]
        return events, examples

    def get_current_state(self):
        return self.current_state

class SubFSM(FSM):
    def __init__(self, fsm_data):
        super().__init__(fsm_data)
        self.initial_state = fsm_data["initial_state"]
        self.done = False
        self.current_event = None

    def _initialize_state(self):
        self.current_state = self.initial_state
    
    def _handle_event(self, user_input, choices = True):
        events, examples = self.get_possible_events()
        event, message = text_classification(user_input, events, examples)
        print(f"CHOICES in Sub: {choices}")
        if not choices:
            event += " done"
        self.current_event = event
        
        if event == "other":
            print("I'm sorry, I didn't understand that. Please try again.")
        
        print(f'SubFSM(state:{self.current_state} event:{event})')
        self.state_transition(event)
        print(f'SubFSM(state:{self.current_state})')
        if self.get_current_state() == "done":
            self.done = True
            

    def _is_done(self):
        return self.done

class ParentFSM(FSM):
    def __init__(self, fsm_data):
        super().__init__(fsm_data)
        self.initial_state = fsm_data["initial_state"]
        self.sub_fsm_active = True
        self.sub_fsms = {}

        for state in self.states:
            sub_fsm_data = load_fsm(file_path=f'module/submodule/{state}.json', type='fsm')
            self.sub_fsms[state] = SubFSM(sub_fsm_data)

    def _handle_event(self, user_input, choices = True):

        if self.sub_fsm_active:
            self.sub_fsms[self.current_state]._handle_event(user_input, choices)
            if self.sub_fsms[self.current_state]._is_done():
                self.sub_fsm_active = False

        events, examples = self.get_possible_events()
        event, message = text_classification(user_input, events, examples)

        if not self.sub_fsm_active:
            print(f'ParentFSM(state:{self.current_state} event:{event})')
            self.state_transition(event)
            print(f'ParentFSM(state:{self.current_state})')
            self.sub_fsm_active = True
            self.sub_fsms[self.current_state]._initialize_state()
            self.sub_fsms[self.current_state]._handle_event(user_input, choices)

class Primitive:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.complete = False
        '''
        ranging from 1 to 10, from lay person to expert
        low proficiency tend to triggers menu based guidance
        high proficiency tend to confirm the user's capability
        dialogue engine would use random sampling to determine which help to provide
        if the random number is greater than the proficiency level, then dialogue engine would confirm the user's capability first
        if the  user is incapable of completing the task or the random number is less than or equal to the proficiency level,
        dialogue engine would provide menu based guidance to the user.

        deterministic is fine. 
        '''
        self.proficiency = 4

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

    def _is_expert(self):
        rand = random.randint(1, 10)
        return rand <= self.proficiency

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
        self.goal_setting_workflow = workflow
        self.goal_setting_workflow_selection = None
        self.current_task = workflow
        self.trajectory = []
        self.all_task_options = self._find_all_task_options(workflow)
        self.current_all_task_options = self.all_task_options

    def _get_current_all_task_options(self):
        return self.get_current_all_task_options
    
    def _remove_task_from_current_all_task_options(self, task):
        self.current_all_task_options.remove(task)
    
    def _find_all_task_options(self, workflow, all_task_options=None):
        if all_task_options is None:
            all_task_options = []
        
        for key, value in workflow.items():
            if key not in all_task_options:
                all_task_options.append(key)
            if isinstance(value, dict):
                self._find_all_task_options(value, all_task_options)

        return all_task_options
    
    def _find_task_trajectory(self, task_name, current_workflow):
        if task_name in current_workflow:
            return [task_name]
        else:
            for key in current_workflow:
                result = self._find_task_trajectory(task_name, current_workflow[key])
                if result:
                    return [key] + result
        return None
    
    def _get_current_task(self):
        if self.trajectory != []:
            return self.trajectory[-1]
        else:
            return None
        
    def _set_current_task(self, task_name):
        self.current_task = task_name
        
    def _reset_current_task(self):
        self.current_task = self.workflow

    def _get_next_task_choices(self):
        choices = list(self.current_task.keys())
        if choices == []:
            return None
        return choices
    
    def _select_next_task(self, task_name):
        if task_name in self.current_task:
            self.current_task = self.current_task[task_name]
    
    def _get_workflow(self):
        return self.workflow

    def _reset_workflow(self):
        self.current_task = self.workflow
        self.trajectory = []

    def _get_goal_setting_workflow(self):
        return self.goal_setting_workflow
    
    def _get_goal_setting_choices(self):
        choices = list(self.goal_setting_workflow.keys())
        return choices
    
    def _add_to_trajectory(self, task_name):
        self.trajectory.append(task_name)

    def _get_goal_setting_workflow_selection(self):
        return self.goal_setting_workflow_selection

    def _set_goal_setting_workflow_selection(self, task_name):
        self.goal_setting_workflow_selection = task_name

    def _select_next_goal_setting_task(self, task_name):
        if task_name in self.goal_setting_workflow:
            self.goal_setting_workflow = self.goal_setting_workflow[task_name]

    def _reset_goal_setting_workflow(self):
        self.goal_setting_workflow = self.workflow

    def _remove_goal_setting_task(self, task_name):
        if task_name in self.goal_setting_workflow:
            del self.goal_setting_workflow[task_name]

class UserProfile:
    def __init__(self, user_id = None):
        fsm_data = load_fsm(type = "fsm")
        task_data = load_task_list(type = "all")

        self.user_id = user_id
        self.dialogue_fsm = ParentFSM(fsm_data)
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
                description = primitive_info
            )
        return primitives
    
    def get_current_all_task_options(self):
        return self.workflow._get_current_all_task_options()
    
    def remove_task_from_current_all_task_options(self, task):
        self.workflow._remove_task_from_current_all_task_options(task)

    def get_current_state(self):
        return self.dialogue_fsm.get_current_state()
    
    def get_current_substate(self):
        return self.dialogue_fsm.sub_fsms[self.dialogue_fsm.current_state].get_current_state()
    
    def handle_user_input(self, user_input, choices = True):
        self.dialogue_fsm._handle_event(user_input, choices)
    
    def get_user_id(self):
        return self.user_id
    
    def add_to_task_trajectory(self, task_name):
        self.workflow.trajectory.append(task_name)
    
    def get_task_trajectory(self, task_name):
        return self.workflow._find_task_trajectory(task_name, self.workflow.workflow)
    
    def get_current_task(self):
        current_task = self.workflow._get_current_task()
        if current_task == None:
            return None
        else:
            return self.tasks[current_task]
        
    def set_current_task(self, task_name):
        self.workflow._set_current_task(task_name)
        
    def get_current_task_name(self):
        current_task = self.get_current_task()
        return current_task._get_name()
        
    def reset_current_task(self):
        self.workflow._reset_current_task()
    
    def get_next_task_choices(self):
        return self.workflow._get_next_task_choices()
    
    def select_next_task(self, task_name):
        self.workflow._select_next_task(task_name)

    def get_workflow(self):
        return self.workflow._get_workflow()
    
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

    def get_expertise(self):
        current_step = self.get_current_step()
        if current_step != None:
            return current_step._is_expert()
        else:
            return None
    
    def check_task_completion(self):
        return self.get_current_task()._get_completion() and self.get_current_step().check_completion()
    
    def reset_task(self):
        self.get_current_task()._reset_task()

    def get_goal_setting_workflow(self):
        return self.workflow._get_goal_setting_workflow()
    
    def get_goal_setting_choices(self):
        return self.workflow._get_goal_setting_choices()
    
    def add_to_goal_setting_trajectory(self, task_name):
        self.workflow.trajectory.append(task_name)

    def select_next_goal_setting_task(self, task_name):
        self.workflow._select_next_goal_setting_task(task_name)
    
    def reset_goal_setting_workflow(self):
        self.workflow._reset_goal_setting_workflow()
    
    def remove_goal_setting_task(self, task_name):
        self.workflow._remove_goal_setting_task(task_name)

    def get_goal_setting_workflow_selection(self):
        return self.workflow._get_goal_setting_workflow_selection()

    def set_goal_setting_workflow_selection(self, task_name):
        self.workflow._set_goal_setting_workflow_selection(task_name)