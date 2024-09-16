from nlu_unit import few_shot_learning_for_text_classification, send_to_llm
from nlg_unit import generate_sentences, load_nlg_example
from FSM import load_fsm_from_json

all_messages = []

def start_dialogue_engine():

    fsm, events, event_examples = load_fsm_from_json('state.json')
    few_shot_learning_for_text_classification(events, event_examples, all_messages)
    sample_sentence = load_nlg_example()


    # few_shot_learning_for_text_classification(events, event_examples)
    user_input = "Your task is text classification for all the following inputs. The labels are Greeting, Request Tutorial, Request Goal Setting, Request Help, Request Information, Provide Information. Classify the following input text according to the labels and reply with just the label."
    all_messages.append({"role": "user", "content": user_input})
    message = send_to_llm(all_messages)
    print(generate_sentences(sample_sentence, "opening", "opening"))

    while True:
        user_input = input()
        if user_input == "exit":
            exit()
        all_messages.append({"role": "user", "content": user_input})
        message = send_to_llm(all_messages)
        event = message["content"]
        all_messages.append(message)
        if fsm.state_changable(event):
            user_input = input(f'Perfect! If you want to proceed to {fsm.transitions[fsm.get_current_state()][event]}, please type "yes". If not, please type "no".\n')
            while True:
                if user_input == "yes" or user_input == "Yes" or user_input == "YES":
                    fsm.state_change(event)
                elif user_input == "no" or user_input == "No" or user_input == "NO":
                    event = "Negate" 
                    break
                else:
                    user_input = input("Invalid input. Please type 'yes' or 'no'.\n")
                    continue
                break
        # print(fsm.get_current_state())
        print(generate_sentences(sample_sentence, fsm.get_current_state(), event))

if __name__ == "__main__":
    main()