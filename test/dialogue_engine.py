from nlu_unit import task_classification, text_classification
from nlg_unit import generate_sentences, load_nlg_example
from load_json import load_fsm, load_task_list
from user_profile_setup import UserProfile
import secrets

user_amount = 0

def initialization():
    # events, event_examples = load_fsm(type = "events")
    # text_classification_learning(events, event_examples)
    sample_sentence = load_nlg_example()
    print(generate_sentences(sample_sentence, "opening", "greeting"))
    return sample_sentence

def run(user, user_input, sample_sentence, current_task, current_task_input):
    user.handle_user_input(user_input)
    ### temporary for goal claification
    if user.get_current_state() == "goal clarification":
        if user.get_current_substate() == "task identification":
            current_task = secrets.choice(user.get_goal_setting_choices())
        elif user.get_current_substate() == "correct task":
            user.add_to_goal_setting_trajectory(current_task)
            user.select_next_goal_setting_task(current_task)
        elif user.get_current_substate() == "incorrect task identification":
            user.remove_goal_setting_task(current_task)
            current_task = secrets.choice(user.get_goal_setting_choices())
    ###
    ### temporary for task identification
    if user.get_current_state() == "task identification":
        if current_task_input == None:
            current_task_input = user_input
            current_task = task_classification(current_task_input, user.get_current_all_tasks())
        if user.get_current_substate() == "task identification":
            user.add_to_task_trajectory(current_task)
        elif user.get_current_substate() == "incorrect task identification":
            user.remove_task_from_current_all_tasks(current_task)
            print(user.get_current_all_tasks())
            current_task = task_classification(current_task_input, user.get_current_all_tasks())
    ###
    print(generate_sentences(sample_sentence, user.get_current_state() , user.get_current_substate(), current_task))
    return current_task, current_task_input

def client():
    global user_amount
    sample_sentence = initialization()
    user = UserProfile(user_id = user_amount)
    user_amount += 1
    current_task = None
    current_task_input = None

    while True:
        user_input = input()
        if user_input == "exit":
            exit()
        current_task, current_task_input = run(user, user_input, sample_sentence, current_task, current_task_input)

if __name__ == "__main__":
    client()