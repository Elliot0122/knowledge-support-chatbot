from nlu_unit import task_classification_learning, task_classification, text_classification
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
    task_list = load_task_list(type = "task_list")
    task_classification_learning(task_list)
    return sample_sentence

def run(user, user_input, sample_sentence, current_task):
    event = user.handle_user_input(user_input)
    ### temporary
    if user.get_current_state() == "goal clarification":
        if user.get_current_substate() == "task identification":
            current_task = secrets.choice(user.get_goal_setting_choices())
    ###
    print(generate_sentences(sample_sentence, user.get_current_state() , user.get_current_substate(), current_task))
    return current_task

def client():
    global user_amount
    sample_sentence = initialization()
    user = UserProfile(user_id = user_amount)
    user_amount += 1
    current_task = None

    while True:
        user_input = input()
        if user_input == "exit":
            exit()
        current_task = run(user, user_input, sample_sentence, current_task)

if __name__ == "__main__":
    client()