from flask import Flask, request, jsonify
from flask_cors import CORS
from controller import message_processing
from dialogue_engine import start_dialogue_engine

app = Flask(__name__)
CORS(app)
messages = []

@app.route('/api/client_input', methods=['POST'])
def client_input():
    user_message = request.json.get('message')
    print(user_message)
    messages.append({"role": "user", "content": user_message})
    message = message_processing(messages)
    messages.append(message)
    return jsonify({'response': message["content"]})


if __name__ == '__main__':
    start_dialogue_engine()
    app.run(debug=True)
