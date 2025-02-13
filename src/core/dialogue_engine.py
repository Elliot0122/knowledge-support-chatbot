from src.utils.nlu_unit import task_classification, text_classification, name_entity_recognition
from src.models.user_profile_setup import UserProfile
from src.utils.RAG import ResponseGenerator
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
    ### temporary for goal claification
    if user.get_parent_fsm_state() == "goal clarification":
        choices = user.get_goal_setting_current_task_choices()
        if (len(choices) == 1 and event == "negate") or len(choices) == 0:
            event = "done"
    ### temporary for goal claification
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
    ### temporary for goal claification
    if user.get_parent_fsm_state() == "goal clarification":
        if user.get_subfsm_state() == "task identification":
            user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
            current_task_name = user.get_goal_setting_next_task_selection()
            if user.get_location() == None:
                if current_task_name == "share location" or current_task_name == "save location" or current_task_name == "get directions":
                    user.set_location(name_entity_recognition(user_input))
        elif user.get_subfsm_state() == "correct task":
            current_task_name = user.get_goal_setting_next_task_selection()
            print(f"current_task_name: {current_task_name}")
            user.add_to_workflow_trajectory(current_task_name)
            user.select_goal_setting_next_task(current_task_name)             
        elif user.get_subfsm_state() == "incorrect task identification":
            user.remove_goal_setting_task(user.get_goal_setting_next_task_selection())
            user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
            current_task_name = user.get_goal_setting_next_task_selection()
    ### temporary for goal claification
    ### temporary for task identification
    elif user.get_parent_fsm_state() == "task identification":
        if user.workflow_task_input_is_None():
            user.set_workflow_task_input(user_input)
        if user.get_subfsm_state() == "task identification":
            current_task_name = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
            user.set_workflow_current_task(current_task_name)
            if user.get_location() == None:
                if current_task_name == "locate destination" or current_task_name == "get directions" or current_task_name == "share location" or current_task_name == "save location":
                    user.set_location(name_entity_recognition(user_input))
        elif user.get_subfsm_state() == "incorrect task identification":
            user.remove_task_from_workflow_current_all_task_options(user.get_workflow_current_task())
            current_task_name = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
            user.set_workflow_current_task(current_task_name)
            current_task_name = user.get_workflow_current_task()
            if user.get_location() == None:
                if current_task_name == "locate destination" or current_task_name == "get directions" or current_task_name == "share location" or current_task_name == "save location":
                    user.set_location(name_entity_recognition(user_input))
    ### temporary for task identification
    ### temporary for task execution
    elif user.get_parent_fsm_state() == "task execution":
        if user.get_workflow_trajectory() == []:
            return 
        
        current_task = user.get_task(user.get_workflow_trajectory()[user.get_workflow_trajectory_index()])

        if user.get_subfsm_state() == "provide detail":
            current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
            current_primitive.subtract_one_from_proficiency()
            return current_primitive.get_detail()

        elif user.get_subfsm_state() == "provide other instruction":
            current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
            current_primitive.subtract_one_from_proficiency()
            current_task.remove_primitive(current_task.get_next_primitive_selection())

        elif user.get_subfsm_state() == "provide instruction" and current_task.get_next_primitive_selection():
            current_task.select_next_primitive()
            if current_task.is_done():
                user.add_one_to_workflow_trajectory_index()
                current_task = user.get_task(user.get_workflow_trajectory()[user.get_workflow_trajectory_index()])

        current_task.set_next_primitive_selection(secrets.choice(current_task.get_current_primitive_options()))
        current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
        current_primitive.add_one_to_proficiency()
        if current_primitive.get_proficiency() > 3:
            return f'Now, you should {current_primitive.get_name()}.'
        else: 
            return current_primitive.get_detail()

    ## nlg
    response = nlg.generate_response(
        parent_fsm = user.get_parent_fsm_state(),
        subfsm = user.get_subfsm_state(),
        task = current_task_name,
        name_entity = user.get_location()
    )
    return response