import secrets
import json

# Load the JSON file
def load_nlg_example():
    with open('nlg_example.json', 'r') as file:
        sample_sentence = json.load(file)
    return sample_sentence

# Function to generate sentences
def generate_sentences(sample_sentence, state, substate, task = None):
    if task:
        return secrets.choice(sample_sentence[state][substate]["tasks"][task]["examples"])
    else:
        return secrets.choice(sample_sentence[state][substate]["examples"])
    # return secrets.choice(sample_sentence[state][substate]["examples"])

# def generate_sentences_with_task(user_input, sample_sentence, state, substate, tasks, task_choice):
#     user_input = f"You are in the {state} state and {substate} phase, and the user's possible tasks are ["
#     for task in task_choice:
#         # print(tasks["tasks"][task]["description"])
#         user_input += f' {task}: {tasks["tasks"][task]["description"]},'
#     user_input += f"]. Ask the user which of these tasks they would like to perform. Keep the response concise but allow flexibility in wording. Only present the available options and ensure the user selects one of them."
#     user_input += f" Ask in the way that the user can provide the information to the task. For example, 'I want to go to Davis' is the user answer to the question 'Do you wish to go to some place?', which the possible task is 'locate destination'."
#     # print(user_input)
#     # print()
#     message_list = [{"role": "user", "content": user_input}]
#     message = send_to_llm(message_list)
#     response  = message["content"]
#     print(response)

# if __name__ == "__main__":
#     user = UserProfile(user_id = 1)
#     sample_sentence = load_nlg_example()
#     # print(user.get_next_task_choices())
#     generate_sentences_with_task("I don't know", sample_sentence, "goal clarification", "task identification", load_task_list(type = "all"), user.get_next_task_choices())
#     user.select_next_task("locate_destination")
#     print("=============================")
#     # print(user.get_next_task_choices())
#     generate_sentences_with_task("a Japanese restaurant", sample_sentence, "goal clarification", "task identification", load_task_list(type = "all"), user.get_next_task_choices())
#     # generate_sentences_with_task