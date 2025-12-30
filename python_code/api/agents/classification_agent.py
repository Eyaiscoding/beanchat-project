from dotenv import load_dotenv
import os
import json
import re
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output

load_dotenv()

class ClassificationAgent():
    def __init__(self):
        pass

    def get_response(self, messages):
        messages = deepcopy(messages)
        
        system_prompt = """Look at the user's message and classify it into ONE of these agents:

recommendation_agent - For recommendations and initial ordering interest:
  - "what do you recommend?"
  - "what should I get?"
  - "I want to order a Latte" (showing interest, give recommendations first)
  - "I'd like to order X" (showing interest, give recommendations first)
  - "any suggestions?"

details_agent - For information questions:
  - Prices: "what's the price of a Latte?"
  - Costs: "how much does X cost?"
  - Ingredients, hours, location

order_taking_agent - For direct ordering commands:
  - "give me a Latte"
  - "I'll have a cappuccino"
  - "can I get X"
  - "I want a chocolate croissant also" (adding to existing order)
  - Continuing an order conversation
  - Order responses: "yes", "no", "that's all"

KEY DISTINCTION:
- "I want to order X" → recommendation_agent (they're expressing interest, show options)
- "give me X" / "I'll have X" → order_taking_agent (direct command, add to order)

Reply with ONLY the agent name."""

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
        
        chatbot_output = get_chatbot_response(input_messages)
        output = self.postprocess(chatbot_output, messages)
        
        return output

    def postprocess(self, output, messages):
        output = output.strip().lower()
        
        # Get the last user message
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "").lower()
                break
        
        # Check if there's an existing order in progress
        has_existing_order = False
        last_order_step = None
        for msg in reversed(messages):
            if msg.get("memory", {}).get("agent") == "order_taking_agent":
                has_existing_order = True
                last_order_step = msg.get("memory", {}).get("step number", "1")
                break
        
        print(f"[Classification] Last message: '{last_message[:50]}...'")
        print(f"[Classification] Has existing order: {has_existing_order}")
        
        # Priority 1: Price/cost questions -> details_agent
        price_keywords = ["price", "cost", "how much", "how many dollars", "what does", "what's the price"]
        if any(keyword in last_message for keyword in price_keywords):
            decision = "details_agent"
            print(f"[Classification] Price question -> details_agent")
        
        # Priority 2: If order in progress, most messages go to order_taking_agent
        elif has_existing_order:
            # Check if they're trying to ask a question (break out of order flow)
            if any(keyword in last_message for keyword in ["recommend", "suggest", "what else", "what should"]):
                decision = "recommendation_agent"
                print(f"[Classification] Asking for recommendations during order -> recommendation_agent")
            else:
                # Everything else continues the order
                decision = "order_taking_agent"
                print(f"[Classification] Order in progress -> order_taking_agent")
        
        # Priority 3: "I want to order X" WITHOUT existing order -> recommendation_agent
        elif any(phrase in last_message for phrase in ["i want to order", "i'd like to order", "i would like to order"]):
            decision = "recommendation_agent"
            print(f"[Classification] 'I want to order' (no existing order) -> recommendation_agent")
        
        # Priority 4: Direct ordering commands -> order_taking_agent
        elif any(keyword in last_message for keyword in ["give me", "i'll have", "i'll take", "can i get", 
                                                         "get me", "i want a", "i'd like a"]):
            decision = "order_taking_agent"
            print(f"[Classification] Direct order command -> order_taking_agent")
        
        # Priority 5: General recommendations -> recommendation_agent
        elif any(keyword in last_message for keyword in ["recommend", "suggest", "what should i", 
                                                         "what to order", "what to get", "any suggestions"]):
            decision = "recommendation_agent"
            print(f"[Classification] Recommendation request -> recommendation_agent")
        
        # Priority 6: Try to extract from LLM output
        else:
            valid_agents = ["details_agent", "order_taking_agent", "recommendation_agent"]
            decision = None
            for agent in valid_agents:
                if agent in output:
                    decision = agent
                    break
            
            if not decision:
                print(f"[Classification] No match, defaulting to recommendation_agent")
                decision = "recommendation_agent"
        
        dict_output = {
            "role": "assistant",
            "content": "",
            "memory": {
                "agent": "classification_agent",
                "classification_decision": decision
            }
        }
        
        return dict_output