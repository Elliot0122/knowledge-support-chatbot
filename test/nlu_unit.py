import json
import requests
from load_json import load_fsm, load_task_list

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"

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

def task_classification(input, task_list):
    print(task_list)
    user_input = f'Your task is to find out "{input}" implies which task. It would only be in the tasks listed in the following:'
    for task in task_list:
        user_input += f' {task},'
    user_input = user_input[:-1]
    user_input += f'Only reply the answer. Just reply without any reasoning. reply only in lower case. tasks should only be picked from the list above.'
    # user_input += ('I want to identify which task in the list the user input is related to.\n Please reply the answer if I prompt the function call. Don’t reply anything else. Only reply the answer.')
    message_list = [{"role": "user", "content": user_input}]
    message = send_to_llm(message_list)
    task  = message["content"]
    return task

def text_classification(input, events, examples):
    user_input = f'Your task is to perform text classification on "{input}". The classes are'
    for event in events:
        user_input += f' {event},'
    user_input += f' error.'
    user_input += f'Here are some examples for each classs: '
    
    for event in events:
        if event not in examples:
            continue
        for example in examples[event]:
            user_input += f'"{example}", '
        user_input = user_input[:-2]
        user_input += '. '
    
    user_input += f'Only reply the answer. Just reply without any reasoning. reply only in lower case.'
    message_list = [{"role": "user", "content": user_input}]
    message = send_to_llm(message_list)
    event  = message["content"]
    return event, message

def profiency_eval_learning():
    user_input = f'remember a function called "proficiency evaluation" as description: Your task is to perform proficiency evaluation with an input and a relevant task. You need to decide if the user is able to follow the instruction or do it by themselves. if they are good at it reply True, if not, reply False.'
    user_input += ('\nTo trigger this function call, the task and the user input is in between the bracket of “proficiency evaluation()”, such as “proficiency evaluation("get direction", How can I get to Davis). Please reply the answer if I prompt the function call. Don’t reply anything else. Only reply the answer and in lower case.')
    message_list = [{"role": "user", "content": user_input}]
    _message = send_to_llm(message_list)

def profiency_eval(current_task, user_input, message_list):
    user_input = f'proficiency evaluation("{current_task}",{user_input})'
    message_list = [{"role": "user", "content": user_input}]
    message = send_to_llm(message_list)
    return message["content"]