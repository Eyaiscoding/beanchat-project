from dotenv import load_dotenv
import os
import json
import re
from copy import deepcopy
from .utils import get_chatbot_response, double_check_json_output

load_dotenv()

class GuardAgent():
    def __init__(self):
        # Keywords that indicate coffee shop related queries (ALLOWED)
        self.allowed_keywords = [
            # Ordering
            "order", "want", "get", "buy", "purchase", "take", "have",
            # Pricing
            "price", "cost", "how much", "expensive", "cheap", "dollar",
            # Recommendations
            "recommend", "suggest", "best", "good", "popular", "favorite",
            # Menu items
            "latte", "cappuccino", "coffee", "espresso", "mocha",
            "croissant", "scone", "biscotti", "syrup", "chocolate",
            "pastry", "drink", "menu",
            # Info
            "location", "hours", "open", "close", "where", "when",
            "ingredients", "contain", "allergy",
            # Conversation
            "yes", "no", "thanks", "thank", "please", "hello", "hi",
            "good", "great", "ok", "okay", "sure", "also", "add",
            "nope", "yep", "yeah",
            # General coffee shop
            "merry", "shop", "cafe", "coffee shop"
        ]

    def get_response(self, messages):
        messages = deepcopy(messages)
        
        # Get the last user message
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "").lower()
                break
        
        # Quick keyword check - if any allowed keyword is present, skip LLM call
        if any(keyword in last_message for keyword in self.allowed_keywords):
            print("[GuardAgent] Quick pass - allowed keyword detected")
            return {
                "role": "assistant",
                "content": "",
                "memory": {
                    "agent": "guard_agent",
                    "guard_decision": "allowed"
                }
            }
        
        # Check for obvious math problems
        math_indicators = ["what's", "what is", "whats"]
        has_math_operator = any(op in last_message for op in ["+", "-", "*", "/", "×", "÷", "plus", "minus", "times", "divided"])
        
        if any(indicator in last_message for indicator in math_indicators) and has_math_operator:
            print("[GuardAgent] Math problem detected - blocking")
            return {
                "role": "assistant",
                "content": "Sorry, I can't help with that. Can I help you with your order?",
                "memory": {
                    "agent": "guard_agent",
                    "guard_decision": "not allowed"
                }
            }
        
        # If very short message (1-5 words), likely conversational - allow it
        word_count = len(last_message.split())
        if word_count <= 5 and not has_math_operator:
            print("[GuardAgent] Short conversational message - allowing")
            return {
                "role": "assistant",
                "content": "",
                "memory": {
                    "agent": "guard_agent",
                    "guard_decision": "allowed"
                }
            }
        
        # Fall back to LLM for ambiguous cases
        system_prompt = """You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.

Your task is to determine whether the user is asking something relevant to the coffee shop or not.

The user is ALLOWED to:
1. Ask questions about the coffee shop, like location, working hours, menu items and coffee shop related questions.
2. Ask questions about menu items - ingredients, details, PRICES, COSTS, descriptions.
3. Make an order or say they want to order something.
4. Ask for recommendations on what to buy, order, or try (e.g., "what do you recommend?", "what should I get?", "any suggestions?").
5. Have general friendly conversation about the coffee shop and ordering.
6. Respond to questions about their order - saying "yes", "no", "that's all", "nothing else", "thanks", etc.

IMPORTANT EXAMPLES OF ALLOWED:
- "what's the price of a latte?" → ALLOWED
- "how much does a cappuccino cost?" → ALLOWED
- "what do you recommend?" → ALLOWED
- "I want to order a latte" → ALLOWED
- "yes" / "no" / "that's all" / "thanks" → ALLOWED

The user is NOT ALLOWED to:
1. Ask questions about anything completely unrelated to our coffee shop (e.g., math problems like "what's 1+2?", science, history, other topics).
2. Ask questions about the staff, employees, or how to make/prepare menu items.

CRITICAL: Respond with ONLY ONE JSON object in this format:

{"decision": "allowed", "message": ""}

OR

{"decision": "not allowed", "message": "Sorry, I can't help with that. Can I help you with your order?"}

Rules:
- If decision is "allowed", message MUST be empty string ""
- If decision is "not allowed", message MUST be the exact text shown above
- Do NOT add any other fields
- Do NOT add markdown or explanations
"""

        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
        
        try:
            chatbot_output = get_chatbot_response(input_messages, timeout=30)
            output = self.postprocess(chatbot_output)
            return output
        except Exception as e:
            print(f"[GuardAgent] Error calling LLM: {e}")
            # Default to allowed on error (better UX)
            print("[GuardAgent] Defaulting to allowed due to error")
            return {
                "role": "assistant",
                "content": "",
                "memory": {
                    "agent": "guard_agent",
                    "guard_decision": "allowed"
                }
            }

    def postprocess(self, output):
        # Clean the output
        output = output.strip()
        
        # Remove markdown code blocks
        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]
        
        if output.endswith("```"):
            output = output[:-3]
        
        output = output.strip()
        
        # Extract first JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output)
        if json_match:
            output = json_match.group(0)
        
        # Try to parse JSON
        try:
            parsed_output = json.loads(output)
        except json.JSONDecodeError as e:
            print(f"[GuardAgent] JSON Decode Error: {e}")
            print(f"[GuardAgent] Raw output: {output[:200]}")
            
            # Try double_check as fallback
            try:
                output = double_check_json_output(output)
                parsed_output = json.loads(output)
            except Exception as e2:
                print(f"[GuardAgent] Double check failed: {e2}")
                # Default to ALLOWED on error
                parsed_output = {
                    "decision": "allowed",
                    "message": ""
                }
        
        # Ensure decision is in correct format
        decision = parsed_output.get('decision', 'allowed').lower().strip()
        
        # Normalize decision
        if decision not in ["allowed", "not allowed"]:
            print(f"[GuardAgent] Invalid decision '{decision}', defaulting to allowed")
            decision = "allowed"
        
        # Get message
        message = parsed_output.get('message', '').strip()
        
        # Ensure message is consistent with decision
        if decision == "allowed":
            message = ""
        elif decision == "not allowed" and not message:
            message = "Sorry, I can't help with that. Can I help you with your order?"
        
        print(f"[GuardAgent] Decision: {decision}")
        
        dict_output = {
            "role": "assistant",
            "content": message,
            "memory": {
                "agent": "guard_agent",
                "guard_decision": decision
            }
        }
        
        return dict_output