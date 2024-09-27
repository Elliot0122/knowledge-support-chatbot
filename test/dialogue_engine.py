from nlu_unit import text_classification_learning, task_classification_learning, task_classification, text_classification, send_to_llm
from nlg_unit import generate_sentences, load_nlg_example
from task_import import load_task_from_json
from FSM import load_fsm_from_json

all_messages = []

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

def main():

    fsm, events, event_examples = load_fsm_from_json('module/states.json')
    text_classification_learning(events, event_examples, all_messages)
    task_list, tasks = load_task_from_json('module/task_list.json')
    task_classification_learning(task_list, tasks, all_messages)
    sample_sentence = load_nlg_example()
    print(generate_sentences(sample_sentence, "opening", "opening"))

    while True:
        user_input = input()
        if user_input == "exit":
            exit()

        event, message = text_classification(user_input, all_messages)
        all_messages.append(message)

        if fsm.state_changable(event):
            if confirmation(fsm, event):
                fsm.state_change(event)
            # else:
            #     event = "negate"

        # print(fsm.get_current_state())
        print(generate_sentences(sample_sentence, fsm.get_current_state(), event))

if __name__ == "__main__":
    main()