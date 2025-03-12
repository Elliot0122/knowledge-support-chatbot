from src.utils.nlu_unit import text_classification
from src.models.user_profile_setup import UserProfile
from src.utils.RAG import ResponseGenerator
from src.fsm.goal_clarification import check_goal_is_exhausted, goal_clarification_task_manipulation
from src.fsm.task_identification import task_identification_task_manipulation
from src.fsm.task_execution import task_execution_get_instruction
import secrets

def initialization():
    user = UserProfile()
    nlg = ResponseGenerator('data/nlg/nlg_example.json')
    response = nlg.generate_response(
        parent_fsm="opening",
        subfsm="start"
    )
    return user, nlg, response

def run(user, nlg, user_input):
    ## nlu for sub fsm
    # restart conversation with specific key word that should be told to the user
    if user_input == "restart conversation":
        return initialization()

    events, examples = user.get_subfsm_possible_events()
    event, message = text_classification(user_input, events, examples)
    if event not in events:
        for i in events:
            if event in i:
                event = i
                break
    print(user.get_subfsm_state())
    print(f"event: {event}")
    current_task_name = None
    ## handle events
    ### check if goal is exhausted
    event = check_goal_is_exhausted(user, event)
    ### 
    user.subfsm_handle_event(event)

    ## nlu for parent fsm if needed
    if user.subfsm_is_done():
        if user.get_parent_fsm_state() == "opening":
            parent_event = event
        else:
            parent_event, examples = user.get_parent_fsm_possible_events()
            parent_event, message = text_classification(user_input, parent_event, examples)
        print(f"parent_event: {parent_event}")
        ## handle events
        user.parent_fsm_handle_event(parent_event)
        user.subfsm_handle_event(parent_event)
    ### manipulate the task information in goal clarification
    if user.get_parent_fsm_state() == "goal clarification":
        current_task_name = goal_clarification_task_manipulation(user, user_input)
    ### 
    ### manipulate the task information in task identification
    elif user.get_parent_fsm_state() == "task identification":
        task_identification_task_manipulation(user, user_input)
    ### 
    ### providing instruction or detail during task execution
    elif user.get_parent_fsm_state() == "task execution":
        return task_execution_get_instruction(user)

    ## nlg
    response = nlg.generate_response(
        parent_fsm = user.get_parent_fsm_state(),
        subfsm = user.get_subfsm_state(),
        task = current_task_name,
        name_entity = user.get_location()
    )
    return response