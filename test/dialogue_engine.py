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
    current_task = None
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
        events, examples = user.get_parent_fsm_possible_events()
        parent_event, message = text_classification(user_input, events, examples)
        ## handle events
        user.parent_fsm_handle_event(parent_event)
        user.subfsm_handle_event(parent_event)

    ### temporary for goal claification
    if user.get_parent_fsm_state() == "goal clarification":
        if user.get_subfsm_state() == "task identification":
            user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
            current_task = user.get_goal_setting_next_task_selection()
        elif user.get_subfsm_state() == "correct task":
            current_task = user.get_goal_setting_next_task_selection()
            user.add_to_workflow_trajectory(current_task)
            user.select_goal_setting_next_task(current_task)             
        elif user.get_subfsm_state() == "incorrect task identification":
            user.remove_goal_setting_task(user.get_goal_setting_next_task_selection())
            user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
            current_task = user.get_goal_setting_next_task_selection()
    ### temporary for goal claification
    ### temporary for task identification
    elif user.get_parent_fsm_state() == "task identification":
        if user.workflow_task_input_is_None():
            user.set_workflow_task_input(user_input)
        if user.get_subfsm_state() == "task identification":
            current_task = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
            user.set_workflow_current_task(current_task)
        elif user.get_subfsm_state() == "incorrect task identification":
            user.remove_task_from_workflow_current_all_task_options(user.get_workflow_current_task())
            current_task = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
            user.set_workflow_current_task(current_task)
            current_task = user.get_workflow_current_task()
    ### temporary for task identification

    ## nlg
    print(generate_sentences(sample_sentence, user.get_parent_fsm_state() , user.get_subfsm_state(), current_task))

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