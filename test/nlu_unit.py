import json
import requests

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"  # TODO: update this for whatever model you wish to use

def few_shot_learning_for_text_classification(events, examples):

    user_input = f'Your task is to do text classification for all the following inputs. The labels are'
    for event in events:
        user_input += f' {event},'
    user_input = user_input[:-1]
    user_input += f'. Hear are some examples for each label: '
    for event in events:
        if event == "Other": continue
        user_input += f'{event}: '
        for example in examples[event]:
            user_input += f'"{example}", '
        user_input = user_input[:-2]
        user_input += '. '
    user_input += f'. Classify the following input text according to the labels and reply with just the label."'
    print(user_input)
    all_messages.append({"role": "user", "content": user_input})
    _message = send_to_llm(all_messages)

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

if __name__ == "__main__":
    all_messages = []
    with open('state.json', 'r') as file:
        data = json.load(file)
    few_shot_learning_for_text_classification(data["events"], data["event_examples"])
    while True:
        user_input = input()
        if user_input == "exit":
            exit()
        all_messages.append({"role": "user", "content": user_input})
        message = send_to_llm(all_messages)
        all_messages.append(message)
        print(message["content"])