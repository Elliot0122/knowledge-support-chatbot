import secrets
import json

# Load the JSON file
def load_nlg_example():
    with open('nlg_example.json', 'r') as file:
        sample_sentence = json.load(file)
    return sample_sentence

# Function to generate sentences
def generate_sentences(sample_sentence, subdialogue, speech_act):
    return secrets.choice(sample_sentence[subdialogue][speech_act])

# print(generate_sentences(json_data, "opening", "opening"))