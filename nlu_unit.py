import json
import requests
from load_json import load_fsm, load_task_list

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"

def send_to_llm(messages):
    r = requests.post(
        "http://localhost:11434/api/chat",
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
    user_input = f'Your task is to classify the following input: "{input}". '
    user_input += f'The classes are: '
    for event in events:
        user_input += f'{event}, '
    user_input = user_input[:-2]+'. '
    user_input += f'Compare it with these examples and choose the most similar category:\n'
    
    for event in events:
        if event not in examples:
            continue
        user_input += f'"{event}":\n'
        for example in examples[event]:
            user_input += f'- {example}\n'
    
    user_input += f'\nIf the input doesn\'t match any category, reply with "error". '
    user_input += f'Only reply with the category name in lowercase, without any explanation.'

    print(user_input)
    
    message_list = [{"role": "user", "content": user_input}]
    message = send_to_llm(message_list)
    event = message["content"]
    return event, message

def name_entity_recognition(input):
    user_input = f'Your task is to perform name entity recognition on the user input: "{input}". For example, the name entity in "I want to go to MU" is "MU" and the name entity in "I want to locate a Japanese restaurant" is "Japanese restaurant". Just reply the name without quotation or any other indications. Do not reply any other thing.'
    message_list = [{"role": "user", "content": user_input}]
    message = send_to_llm(message_list)
    name  = message["content"]
    return name

