import json

class FSM:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.transitions = {}
        self.states = set()
        self.event_stack = []
    
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

def load_fsm_from_json(file_path = "module/states.json"):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    initial_state = data["initial_state"]
    fsm = FSM(initial_state)
    
    for transition in data["transitions"]:
        fsm.add_transition(transition["start_state"], transition["end_state"], transition["event"])
    
    return fsm, data["events"], data["event_examples"]

# Example usage
if __name__ == "__main__":
    fsm = load_fsm_from_json('module/states.json')