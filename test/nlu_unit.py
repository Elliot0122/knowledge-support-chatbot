import json
import requests
from load_json import load_fsm, load_task_list

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"  # TODO: update this for whatever model you wish to use

def send_to_llm(messages):
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True
    )
    r.raise_for_status()
    output = ""

    for line in r.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content
        if body.get("done", False):
            message["content"] = output
            return message

def task_classification_learning(task_list, all_messages):
    user_input = f'remember a function called "task classification" as description: Your task is to perform classification with an input. The classes are'
    for task in task_list:
        user_input += f' {task},'
    user_input = user_input[:-1]
    user_input += ('I want to identify which task in the list the user input is related to.\nTo trigger this function call, the user input is in between the bracket of “task classification()”. Please reply the answer if I prompt the function call. Don’t reply anything else. Only reply the answer.')
    all_messages.append({"role": "user", "content": user_input})
    _message = send_to_llm(all_messages)

def task_classification(user_input, all_messages):
    user_input = f'task classification({user_input})'
    all_messages.append({"role": "user", "content": user_input})
    message = send_to_llm(all_messages)
    return message["content"]

def text_classification_learning(events, examples, all_messages):

    user_input = f'remember a function called "text classification" as description: Your task is to perform text classification with an input. The classes are'
    for event in events:
        user_input += f' {event},'
    user_input = user_input[:-1]
    user_input += f'. Here are some examples for each classs: '
    
    for event in events:
        if event == "other": continue
        user_input += f'{event}: '
        for example in examples[event]:
            user_input += f'"{example}", '
        user_input = user_input[:-2]
        user_input += '. '
    
    user_input += ('\nTo trigger this function call, the user input is in between the bracket of “text classification()”, such as “text classification(Hi. How are you). Please reply the answer if I prompt the function call. Don’t reply anything else. Only reply the answer.')
                #    '\nAdditionally, identify and extract any relevant metadata from the input. Return the result in the following JSON format: '
                #    '{"label": "label_name", "metadata": {"intent": "identified_intent", "object": "identified_object", "action": "identified_action"}}'
                #    '\nClassify the following input text and extract metadata:')
    all_messages.append({"role": "user", "content": user_input})
    _message = send_to_llm(all_messages)
    # print(_message)
    
    # Assuming LLM response will be in JSON format for easier processi   ng.
    # response_json = json.loads(_message['content'])
    # return 

def text_classification(user_input, all_messages):
    user_input = f'text classification({user_input})'
    all_messages.append({"role": "user", "content": user_input})
    message = send_to_llm(all_messages)
    event  = message["content"]
    return event, message

def profiency_eval_learning():
    user_input = f'remember a function called "proficiency evaluation" as description: Your task is to perform proficiency evaluation with an input and a relevant task. You need to decide if the user is able to follow the instruction or do it by themselves. if they are good at it reply True, if not, reply False.'
    user_input += ('\nTo trigger this function call, the task and the user input is in between the bracket of “proficiency evaluation()”, such as “proficiency evaluation("get direction", How can I get to Davis). Please reply the answer if I prompt the function call. Don’t reply anything else. Only reply the answer.')
    all_messages.append({"role": "user", "content": user_input})
    _message = send_to_llm(all_messages)

def profiency_eval(current_task, user_input, all_messages):
    user_input = f'proficiency evaluation("{current_task}",{user_input})'
    all_messages.append({"role": "user", "content": user_input})
    message = send_to_llm(all_messages)
    return message["content"]

if __name__ == "__main__":
    all_messages = []
    events, event_examples = load_fsm(type = "events")
    text_classification_learning(events, event_examples, all_messages)
    task_list = load_task_list(type = "task_list")
    task_classification_learning(task_list, all_messages)
    profiency_eval_learning()
    print("How can I help you today?")
    while True:
        user_input = input()
        if user_input == "exit":
            exit()
        all_messages.append({"role": "user", "content": user_input})
        message = send_to_llm(all_messages)
        all_messages.append(message)
        print(message["content"])