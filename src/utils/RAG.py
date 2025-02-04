import json
from nlu_unit import send_to_llm
from typing import Optional, List

class ResponseGenerator:
    def __init__(self, nlg_file_path: str):
        """Initialize with NLG examples file"""
        with open(nlg_file_path, 'r') as f:
            self.nlg_data = json.load(f)
            
    def generate_response(self, 
                         parent_fsm: str,
                         subfsm: str,
                         task: Optional[str] = None,
                         name_entity: Optional[str] = None) -> str:
        """
        Generate appropriate response based on current state and task, using examples as reference
        
        Args:
            parent_fsm (str): Parent finite state machine name
            subfsm (str): Sub finite state machine name
            task (Optional[str]): Current task identifier
            name_entity (Optional[str]): Entity name to be included in response
        """
        # Get state data
        flow_data = self.nlg_data.get(parent_fsm, {})
        state_data = flow_data.get(subfsm, {})
        
        if not state_data:
            return "I'm not sure how to respond in this state."
            
        # Get prompt and examples
        prompt = state_data.get("prompt", "")
        
        # Get relevant examples based on task
        examples = []
        if "tasks" in state_data:
            if task and task in state_data["tasks"]:
                examples = state_data["tasks"][task]["examples"]
            elif "None" in state_data["tasks"]:
                examples = state_data["tasks"]["None"]["examples"]
        else:
            examples = state_data.get("examples", [])
            
        # Pass state_data to _generate_rag_response
        return self._generate_rag_response(prompt, examples, state_data, task, name_entity)
        
    def _generate_rag_response(self, 
                             prompt: str,
                             examples: List[str],
                             state_data: dict,
                             task: Optional[str] = None,
                             name_entity: Optional[str] = None) -> str:
        """
        Generate response using RAG with examples as reference
        
        Args:
            prompt (str): Context prompt for response generation
            examples (List[str]): Reference examples for style and tone
            state_data (dict): Current state data containing purpose and other info
            task (Optional[str]): Current task identifier
            name_entity (Optional[str]): Entity name to be included in response
        """
        # Get the purpose from state_data if available
        purpose = ""
        if task and task in state_data.get("tasks", {}):
            purpose = state_data["tasks"][task].get("purpose", "")
        elif "purpose" in state_data:
            purpose = state_data["purpose"]

        # Format examples with entity if available
        formatted_examples = []
        if name_entity and task in ["locate destination", "get directions"]:
            for example in examples:
                try:
                    formatted_example = example.format(destination=name_entity)
                    formatted_examples.append(formatted_example)
                except KeyError:
                    formatted_examples.append(example)
        else:
            formatted_examples = examples

        # Construct messages for the LLM
        messages = [
            {
                "role": "system",
                "content": f"""You are a Maps assistant. Generate a concise and natural response.
                Context: {prompt}
                Task: {task if task else 'None'}
                {'Destination: ' + name_entity if name_entity and task in ["locate destination", "get directions"] else ''}
                
                Reference examples for style and tone:
                {chr(10).join(f'- {example}' for example in formatted_examples)}
                
                generate a response according to the examples. Don't ask extra questions for information.
                Only ask one question at a time. keep the conversation concise and natural. keep the response short and to the point.
                Generate a new response that incorporate the destination naturally into the response if provided. 
                Don't mention about destination if destination is not provided. 
                Only Identify yourself when the example also identifies themselves."""
            },
            {
                "role": "user",
                "content": "Generate an appropriate response for the user."
            }
        ]
        
        try:
            # Send request to LLM
            response = send_to_llm(messages)
            return response.get("content", "I'm not sure how to respond right now.")
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
        
# Example usage:
if __name__ == "__main__":
    # Initialize
    generator = ResponseGenerator('module/nlg_example.json')

    # Test with examples as reference
    response = generator.generate_response(
        parent_fsm="opening",
        subfsm="start"
    )
    print("Opening response:", response)

    # Test with task and entities
    response = generator.generate_response(
        parent_fsm="goal clarification",
        subfsm="task identification",
        task="locate destination",
        name_entity= "Memorial Union" 
    )
    print("Task response:", response)

    # Test error handling
    response = generator.generate_response(
        parent_fsm="invalid_flow",
        subfsm="invalid_state"
    )
    print("Error response:", response)