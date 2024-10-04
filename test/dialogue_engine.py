from nlu_unit import text_classification_learning, task_classification_learning, task_classification, text_classification, send_to_llm
from nlg_unit import generate_sentences, load_nlg_example
from load_json import load_fsm, load_task_list
from user_profile_setup import user_profile

user_amount = 0

def confirmation(fsm, event):
    user_input = input(f'Perfect! If you want to proceed to {fsm.transitions[fsm.get_current_state()][event]}, please type "yes". If not, please type "no".\n')
    while True:
        if user_input == "yes" or user_input == "Yes" or user_input == "YES":
            return True
        elif user_input == "no" or user_input == "No" or user_input == "NO":
            return False
        else:
            user_input = input("Invalid input. Please type 'yes' or 'no'.\n")
            continue

def initialization(all_messages):
    events, event_examples = load_fsm(type = "events")
    text_classification_learning(events, event_examples, all_messages)
    task_list = load_task_list(type = "task_list")
    task_classification_learning(task_list, all_messages)

    sample_sentence = load_nlg_example()
    print(generate_sentences(sample_sentence, "opening", "opening"))
    return sample_sentence

def main(user, user_input, all_messages):
    event, message = text_classification(user_input, all_messages)
    all_messages.append(message)

    if user.fsm.state_changable(event):
        if confirmation(user.fsm, event):
            user.fsm.state_change(event)
            # need further modification so that's not hard coded 
            if user.fsm.get_current_state() == "method clarification":
                task_name = task_classification(user_input, all_messages)
                user.set_current_task(task_name)       
    else:
        pass

    return event, user

def client():
    all_messages = []
    user = user_profile(user_id = user_amount)
    user_amount += 1
    sample_sentence = initialization(all_messages)

    while True:
        user_input = input()
        if user_input == "exit":
            exit()

        event, user = main(user, user_input, all_messages)

        print(generate_sentences(sample_sentence, user.fsm.get_current_state(), event))

if __name__ == "__main__":
    client()