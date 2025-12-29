from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response
import re
load_dotenv()

class GuardAgent():
    def __init__(self):
        pass
    
    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = """
You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.
Your task is to determine whether the user is asking something relevant to the coffee shop or not.

The user is allowed to:
1. Ask questions about the coffee shop, like location, working hours, menu items and coffee shop related questions.
2. Ask questions about menu items, they can ask for ingredients in an item and more details about the item.
3. Make an order.
4. Ask about recommendations of what to buy.

The user is NOT allowed to:
1. Ask questions about anything else other than our coffee shop.
2. Ask questions about the staff or how to make a certain menu item.

CRITICAL: Respond with ONLY ONE JSON object. Do not include multiple JSON objects. Do not include any text before or after the JSON.

Output format (exactly like this):
{
"chain_of_thought": "your analysis here",
"decision": "allowed",
"message": ""
}

OR

{
"chain_of_thought": "your analysis here",
"decision": "not allowed",
"message": "Sorry, I can't help with that. Can I help you with your order?"
}
"""
        
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
        
        # Get response from chatbot
        chatbot_output = get_chatbot_response(input_messages)
        
        output = self.postprocess(chatbot_output)
        
        return output

    def postprocess(self, output):
        # Clean the output
        output = output.strip()
        
        # Remove markdown code block markers
        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]
        
        if output.endswith("```"):
            output = output[:-3]
        
        output = output.strip()
        
        # Extract first JSON object if multiple exist
        # Find the first complete JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output)
        if json_match:
            output = json_match.group(0)
        
        try:
            parsed_output = json.loads(output)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw output: {output[:500]}")  # Limit output length
            # Fallback if JSON is invalid
            parsed_output = {
                "chain_of_thought": "Invalid response format",
                "decision": "not allowed",
                "message": "Sorry, I can't help with that. Can I help you with your order?"
            }
        
        # Ensure decision is in correct format
        decision = parsed_output.get('decision', 'not allowed').lower().strip()
        if decision not in ["allowed", "not allowed"]:
            decision = "not allowed"
        
        # Only include message in content if decision is "not allowed"
        content = parsed_output.get('message', '') if decision == "not allowed" else ''
        
        dict_output = {
            "role": "assistant",
            "content": content,
            "memory": {
                "agent": "guard_agent",
                "guard_decision": decision
            }
        }
        return dict_output