# Knowledge Support Chatbot

A flexible conversational AI assistant that provides step-by-step guidance for product usage through natural language interactions. The system uses a finite state machine (FSM) architecture to manage dialogue flow and can be adapted to support any product by modifying the knowledge base in the data folder.

## Features

- Natural language understanding for user queries
- Dynamic task identification and goal clarification
- Step-by-step guidance with adaptive detail levels
- User proficiency tracking
- Contextual response generation
- Easily adaptable to different products/domains
- Multi-step task guidance with primitive operations

## Architecture

The system uses a hierarchical FSM architecture with:
- Parent FSM for high-level conversation flow
- Sub-FSMs for specific task handling
- RAG (Retrieval-Augmented Generation) for natural responses
- Modular knowledge base structure

### Core Components

1. **Dialogue Engine**: Manages conversation flow and state transitions
2. **User Profile**: Tracks user state, proficiency, and task progress
3. **Response Generator**: Generates contextual responses using RAG
4. **NLU Unit**: Processes natural language inputs

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Elliot0122/knowledge-support-chatbot.git
cd knowledge-support-chatbot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```


3. Start the Ollama server (required for LLM functionality):

```bash
ollama serve
```


4. Run the application:

```bash
python run.py
```


## Customization

The chatbot can be adapted to support different products by modifying the data files:

### Data Structure

```
data/
├── fsm/ # Conversation flow definitions
│ ├── states.json # Main conversation states
│ └── submodule/ # Task-specific state machines
│   ├── opening.json
│   ├── goal_clarification.json
│   └── task_execution.json
├── nlg/ # Natural Language Generation
│ └── examples.json # Response templates
└── tasks/ # Product-specific tasks
  └── task_list.json # Task definitions and primitives
```


### Customization Steps

1. **Define Tasks**: Update `task_list.json` with your product's tasks and their primitive operations
2. **Update Responses**: Modify `examples.json` with product-specific response templates
3. **Adjust States**: Customize FSM states and transitions if needed

## Usage

The API server will start on `http://localhost:9000`. You can interact with it using:

```python
import requests

# Initialize conversation
response = requests.get("http://localhost:9000/init")
print(response.json()["response"])

# Send a message
response = requests.post(
"http://localhost:9000/chat",
json={"text": "I need help with this product"}
)
print(response.json()["response"])
```


## Project Structure
```
knowledge-support-chatbot/
├── src/ # Source code
│ ├── core/ # Core dialogue and business logic
│ ├── models/ # FSM and data models
│ └── utils/ # Utility functions
└── data/ # Knowledge base and configuration
```

## Key Features

1. **Adaptive Guidance**
   - Adjusts detail level based on user proficiency
   - Provides step-by-step instructions
   - Offers additional details when needed

2. **Flexible Task Management**
   - Dynamic task identification
   - Goal clarification dialogue
   - Multi-step task decomposition

3. **Natural Interaction**
   - Context-aware responses
   - Natural language understanding
   - Conversational state management

## API Endpoints

- `GET /init`: Initialize a new conversation
- `POST /chat`: Send a message to the assistant
  - Request body: `{"text": "your message here"}`
  - Response: `{"response": "assistant's response"}`

## Requirements

- Python 3.11+
- Ollama (for LLM functionality)
- FastAPI
- Uvicorn