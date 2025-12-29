from dotenv import load_dotenv
import os
import json
from copy import deepcopy
from .utils import get_chatbot_response
import re
load_dotenv()

class ClassificationAgent():
    def __init__(self):
        pass
    
    def get_response(self, messages):
        messages = deepcopy(messages)

        system_prompt = """
You are a helpful AI assistant for a coffee shop application.
Your task is to determine what agent should handle the user input. You have 3 agents to choose from:
1. details_agent: This agent is responsible for answering questions about the coffee shop, like location, delivery places, working hours, details about menu items. Or listing items in the menu items. Or by asking what we have.
2. order_taking_agent: This agent is responsible for taking orders from the user. It's responsible to have a conversation with the user about the order until it's complete.
3. recommendation_agent: This agent is responsible for giving recommendations to the user about what to buy. If the user asks for a recommendation, this agent should be used.

CRITICAL: Respond with ONLY ONE JSON object. Do not include multiple JSON objects or any extra text.

Your output should be in a structured json format like so:
{
"chain_of_thought": "go over each of the agents above and write your thoughts about what agent this input is relevant to",
"decision": "details_agent or order_taking_agent or recommendation_agent - pick one",
"message": ""
}
"""
        
        input_messages = [
            {"role": "system", "content": system_prompt},
        ]

        input_messages += messages[-3:]

        # Fixed: get_chatbot_response only takes messages parameter
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
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output)
        if json_match:
            output = json_match.group(0)
        
        try:
            parsed_output = json.loads(output)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error in ClassificationAgent: {e}")
            print(f"Raw output: {output[:500]}")
            # Fallback - default to details_agent for safety
            parsed_output = {
                "chain_of_thought": "Invalid response format, defaulting to details_agent",
                "decision": "details_agent",
                "message": ""
            }
        
        # Validate decision
        valid_agents = ["details_agent", "order_taking_agent", "recommendation_agent"]
        decision = parsed_output.get('decision', 'details_agent')
        
        if decision not in valid_agents:
            print(f"Invalid agent decision: {decision}, defaulting to details_agent")
            decision = "details_agent"

        dict_output = {
            "role": "assistant",
            "content": parsed_output.get('message', ''),
            "memory": {
                "agent": "classification_agent",
                "classification_decision": decision
            }
        }
        return dict_output