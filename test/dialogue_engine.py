from nlu_unit import task_classification, text_classification
from nlg_unit import generate_sentences, load_nlg_example
from user_profile_setup import UserProfile
import secrets

user_amount = 0

def initialization():
    # events, event_examples = load_fsm(type = "events")
    # text_classification_learning(events, event_examples)
    sample_sentence = load_nlg_example()
    print(generate_sentences(sample_sentence, "opening", "start"))
    return sample_sentence

def run(user, user_input, sample_sentence):
    ## nlu for sub fsm
    events, examples = user.get_subfsm_possible_events()
    event, message = text_classification(user_input, events, examples)
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
        parent_event, examples = user.get_parent_fsm_possible_events()
        parent_event, message = text_classification(user_input, parent_event, examples)
        ## handle events
        user.parent_fsm_handle_event(parent_event)
        user.subfsm_handle_event(parent_event)

    ### temporary for goal claification
    if user.get_parent_fsm_state() == "goal clarification":
        if user.get_subfsm_state() == "task identification":
            user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
            current_task_name = user.get_goal_setting_next_task_selection()
        elif user.get_subfsm_state() == "correct task":
            current_task_name = user.get_goal_setting_next_task_selection()
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
        elif user.get_subfsm_state() == "incorrect task identification":
            user.remove_task_from_workflow_current_all_task_options(user.get_workflow_current_task())
            current_task_name = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
            user.set_workflow_current_task(current_task_name)
            current_task_name = user.get_workflow_current_task()
    ### temporary for task identification
    ### temporary for task execution
    elif user.get_parent_fsm_state() == "task execution":
        if user.get_workflow_trajectory() == []:
            print("Trajectory is empty")
            return
        
        current_task = user.get_task(user.get_workflow_trajectory()[user.get_workflow_trajectory_index()])

        if user.get_subfsm_state() == "confirm task execution":
            print(f'I will now guide you through the task "{current_task.get_name()}".')
            return

        if user.get_subfsm_state() == "provide detail":
            current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
            current_primitive.subtract_one_from_proficiency()
            print(current_primitive.get_detail())
            return

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
            print(f'Now, you should {current_primitive.get_name()}.')
        else: 
            print(current_primitive.get_detail())
        
        return
    ### temporary for task execution

    ## nlg
    print(generate_sentences(sample_sentence, user.get_parent_fsm_state() , user.get_subfsm_state(), current_task_name))

def client():
    global user_amount
    sample_sentence = initialization()
    user = UserProfile(user_id = user_amount)
    user_amount += 1

    while True:
        user_input = input()
        if user_input == "exit":
            exit()
        run(user, user_input, sample_sentence)

if __name__ == "__main__":
    client()