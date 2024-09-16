import json
import requests

def message_processing(messages):
    #change messages to prompt
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": "llama3", "messages": messages, "stream": True},
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