import os
import json
import re
from .utils import get_chatbot_response, double_check_json_output
from copy import deepcopy
from dotenv import load_dotenv

load_dotenv()

class OrderTakingAgent():
    def __init__(self):
        self.menu = {
            "Cappuccino": 4.50,
            "Latte": 4.75,
            "Espresso shot": 2.00,
            "Dark chocolate (Drinking Chocolate)": 5.00,
            "Chocolate Croissant": 3.75,
            "Croissant": 3.25,
            "Almond Croissant": 4.00,
            "Jumbo Savory Scone": 3.25,
            "Cranberry Scone": 3.50,
            "Oatmeal Scone": 3.25,
            "Ginger Scone": 3.50,
            "Chocolate Chip Biscotti": 2.50,
            "Hazelnut Biscotti": 2.75,
            "Ginger Biscotti": 2.50,
            "Chocolate syrup": 1.50,
            "Hazelnut syrup": 1.50,
            "Caramel syrup": 1.50,
            "Sugar Free Vanilla syrup": 1.50,
            "Dark chocolate (Packaged Chocolate)": 3.00
        }
        
        # Patterns for summary and confirmation
        self.summary_patterns = [
            r'\b(no|nope|nah|nothing|none)\b',
            r'\bthat\'?s?\s+(all|it|everything)\b',
            r'\b(done|finish|finished|complete)\b',
            r'\bgood\s+for\s+(today|now)\b',
            r'\bjust\s+that\b',
            r'\bnothing\s+else\b',
        ]
        
        self.confirmation_patterns = [
            r'^(yes|yeah|yep|yup|sure|ok|okay|correct|right|confirm)$',
            r'^(yes|yeah|yep|yup)\s*(please|thanks|thank you)?$',
        ]

    def detect_intent(self, user_text):
        """
        Detect user intent from their message.
        Returns: 'add_item', 'show_summary', 'confirm_order', or None
        """
        user_text_lower = user_text.lower().strip()
        
        # Check for confirmation (after seeing summary)
        for pattern in self.confirmation_patterns:
            if re.search(pattern, user_text_lower, re.IGNORECASE):
                return "confirm_order"
        
        # Check for summary request (done ordering)
        for pattern in self.summary_patterns:
            if re.search(pattern, user_text_lower, re.IGNORECASE):
                return "show_summary"
        
        # Check if they're mentioning a menu item
        detected_item = self.fuzzy_match_item(user_text)
        if detected_item:
            return "add_item"
        
        return None

    def fuzzy_match_item(self, user_text):
        """Match user input to menu items with fuzzy matching"""
        user_text_lower = user_text.lower()
        
        # Direct keyword mapping for common issues
        keyword_map = {
            "chocolate croissant": "Chocolate Croissant",
            "almond croissant": "Almond Croissant",
            "latte": "Latte",
            "cappuccino": "Cappuccino",
            "espresso": "Espresso shot",
            "dark chocolate": "Dark chocolate (Drinking Chocolate)",
            "drinking chocolate": "Dark chocolate (Drinking Chocolate)",
            "jumbo savory scone": "Jumbo Savory Scone",
            "jumbo scone": "Jumbo Savory Scone",
            "savory scone": "Jumbo Savory Scone",
            "cranberry scone": "Cranberry Scone",
            "oatmeal scone": "Oatmeal Scone",
            "ginger scone": "Ginger Scone",
            "chocolate chip biscotti": "Chocolate Chip Biscotti",
            "hazelnut biscotti": "Hazelnut Biscotti",
            "ginger biscotti": "Ginger Biscotti",
            "chocolate syrup": "Chocolate syrup",
            "hazelnut syrup": "Hazelnut syrup",
            "caramel syrup": "Caramel syrup",
            "vanilla syrup": "Sugar Free Vanilla syrup",
            "sugar free vanilla": "Sugar Free Vanilla syrup",
        }
        
        # Check keyword map first
        for keyword, menu_item in keyword_map.items():
            if keyword in user_text_lower:
                return menu_item
        
        # Check for "croissant" alone (should be plain Croissant)
        if "croissant" in user_text_lower and "chocolate" not in user_text_lower and "almond" not in user_text_lower:
            return "Croissant"
        
        # Fallback: check if any menu item name appears in text
        for menu_item in self.menu.keys():
            if menu_item.lower() in user_text_lower:
                return menu_item
        
        return None

    def get_response(self, messages):
        messages = deepcopy(messages)
        user_message = messages[-1]['content']
        
        # Get current order state
        current_order = []
        last_action = None
        
        for message_index in range(len(messages)-1, -1, -1):
            message = messages[message_index]
            agent_name = message.get("memory", {}).get("agent", "")
            
            if message["role"] == "assistant" and agent_name == "order_taking_agent":
                current_order = message["memory"].get("order", [])
                last_action = message["memory"].get("last_action", None)
                break
        
        # Pre-detect intent using pattern matching
        detected_intent = self.detect_intent(user_message)
        detected_item = self.fuzzy_match_item(user_message)
        
        print(f"[OrderTakingAgent] User message: '{user_message}'")
        print(f"[OrderTakingAgent] Detected intent: {detected_intent}")
        print(f"[OrderTakingAgent] Detected item: {detected_item}")
        print(f"[OrderTakingAgent] Current order: {current_order}")
        
        # If we can handle it with pattern matching, do it directly
        if detected_intent == "confirm_order" and current_order:
            print("[OrderTakingAgent] Confirming order via pattern match")
            return {
                "role": "assistant",
                "content": "Thank you for your order!",
                "memory": {
                    "agent": "order_taking_agent",
                    "last_action": "confirm_order",
                    "order": current_order
                }
            }
        
        if detected_intent == "show_summary" and current_order:
            print("[OrderTakingAgent] Showing summary via pattern match")
            summary = self._generate_summary(current_order)
            return {
                "role": "assistant",
                "content": summary,
                "memory": {
                    "agent": "order_taking_agent",
                    "last_action": "show_summary",
                    "order": current_order
                }
            }
        
        if detected_intent == "add_item" and detected_item:
            print(f"[OrderTakingAgent] Adding item via pattern match: {detected_item}")
            new_order = deepcopy(current_order)
            new_order.append({
                "item": detected_item,
                "quantity": 1,
                "price": self.menu[detected_item]
            })
            return {
                "role": "assistant",
                "content": f"Great choice! You've ordered a {detected_item}. Would you like anything else?",
                "memory": {
                    "agent": "order_taking_agent",
                    "last_action": "add_item",
                    "order": new_order
                }
            }
        
        # If pattern matching didn't work, fall back to LLM
        print("[OrderTakingAgent] Falling back to LLM")
        return self._get_llm_response(messages, current_order, user_message, detected_intent, detected_item)
    
    def _get_llm_response(self, messages, current_order, user_message, detected_intent, detected_item):
        """Fallback to LLM when pattern matching doesn't work"""
        
        system_prompt = """You are an order-taking assistant for "Merry's Way" coffee shop.

MENU:
Cappuccino - $4.50
Latte - $4.75
Espresso shot - $2.00
Dark chocolate (Drinking Chocolate) - $5.00
Chocolate Croissant - $3.75
Croissant - $3.25
Almond Croissant - $4.00
Jumbo Savory Scone - $3.25
Cranberry Scone - $3.50
Oatmeal Scone - $3.25
Ginger Scone - $3.50
Chocolate Chip Biscotti - $2.50
Hazelnut Biscotti - $2.75
Ginger Biscotti - $2.50
Chocolate syrup - $1.50
Hazelnut syrup - $1.50
Caramel syrup - $1.50
Sugar Free Vanilla syrup - $1.50
Dark chocolate (Packaged Chocolate) - $3.00

YOUR TASK: Analyze the customer's message and determine the action.

JSON FORMAT (respond ONLY with this):
{
  "action": "add_item" | "show_summary" | "confirm_order",
  "items_to_add": [{"item": "Menu Item", "quantity": 1, "price": 0.00}],
  "response": "Your response text"
}

RESPONSE RULES:
- action "add_item": Customer mentions a menu item → add it and ask if they want more
- action "show_summary": Customer says done/no/that's all → show order summary
- action "confirm_order": Customer confirms → thank them"""

        # Build context
        context = ""
        if current_order:
            context += f"CURRENT ORDER:\n{json.dumps(current_order, indent=2)}\n\n"
        
        if detected_intent:
            context += f"DETECTED INTENT: {detected_intent}\n"
        
        if detected_item:
            context += f"DETECTED ITEM: {detected_item}\nYou MUST include this in items_to_add.\n\n"
        
        context += f"CUSTOMER MESSAGE: {user_message}"
        
        messages[-1]['content'] = context
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-8:]
        
        try:
            chatbot_output = get_chatbot_response(input_messages, timeout=60)
            output = self._postprocess_llm(chatbot_output, current_order, user_message, detected_item)
        except Exception as e:
            print(f"[OrderTakingAgent] LLM error: {e}")
            # Ultimate fallback
            if detected_item:
                new_order = deepcopy(current_order)
                new_order.append({"item": detected_item, "quantity": 1, "price": self.menu[detected_item]})
                output = {
                    "role": "assistant",
                    "content": f"Great choice! You've ordered a {detected_item}. Would you like anything else?",
                    "memory": {
                        "agent": "order_taking_agent",
                        "last_action": "add_item",
                        "order": new_order
                    }
                }
            else:
                output = {
                    "role": "assistant",
                    "content": "I apologize, I had trouble understanding. Could you please repeat?",
                    "memory": {
                        "agent": "order_taking_agent",
                        "last_action": "error",
                        "order": current_order
                    }
                }
        
        return output

    def _postprocess_llm(self, output, current_order, user_message, detected_item):
        """Process LLM output"""
        output = output.strip()
        
        # Remove markdown
        output = re.sub(r'^```(?:json)?\s*', '', output)
        output = re.sub(r'\s*```$', '', output)
        output = output.strip()
        
        # Extract JSON
        json_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', output, re.DOTALL)
        if json_match:
            output = json_match.group(0)
        
        # Parse JSON
        try:
            parsed_output = json.loads(output)
            print(f"[OrderTakingAgent] LLM parsed JSON: {parsed_output}")
        except json.JSONDecodeError as e:
            print(f"[OrderTakingAgent] JSON error: {e}")
            
            # Try double check
            try:
                output = double_check_json_output(output)
                parsed_output = json.loads(output)
            except:
                # Manual fallback
                if detected_item:
                    parsed_output = {
                        "action": "add_item",
                        "items_to_add": [{"item": detected_item, "quantity": 1, "price": self.menu[detected_item]}],
                        "response": f"Great choice! You've ordered a {detected_item}. Would you like anything else?"
                    }
                else:
                    parsed_output = {
                        "action": "error",
                        "items_to_add": [],
                        "response": "I apologize, I had trouble understanding. Could you please repeat?"
                    }
        
        # Extract fields
        action = parsed_output.get("action", "add_item")
        items_to_add = parsed_output.get("items_to_add", [])
        response_text = parsed_output.get("response", "How can I help you?")
        
        # Ensure items_to_add is a list
        if not isinstance(items_to_add, list):
            items_to_add = []
        
        # If LLM failed to extract but we detected an item, add it
        if action == "add_item" and not items_to_add and detected_item:
            items_to_add = [{"item": detected_item, "quantity": 1, "price": self.menu[detected_item]}]
            response_text = f"Great choice! You've ordered a {detected_item}. Would you like anything else?"
        
        # Update order
        new_order = deepcopy(current_order)
        
        if action == "add_item" and items_to_add:
            for item in items_to_add:
                if isinstance(item, dict) and "item" in item:
                    new_order.append(item)
        
        elif action == "show_summary":
            if new_order:
                response_text = self._generate_summary(new_order)
            else:
                response_text = "Your order is empty. What would you like to order?"
        
        elif action == "confirm_order":
            response_text = "Thank you for your order!"
        
        return {
            "role": "assistant",
            "content": response_text,
            "memory": {
                "agent": "order_taking_agent",
                "last_action": action,
                "order": new_order
            }
        }
    
    def _generate_summary(self, order):
        """Generate order summary with total"""
        if not order:
            return "Your order is empty. Would you like to order something?"
        
        summary_parts = []
        total = 0.0
        
        for item in order:
            item_name = item.get("item", "Unknown item")
            quantity = item.get("quantity", 1)
            price = item.get("price", 0.0)
            item_total = quantity * price
            total += item_total
            summary_parts.append(f"{quantity} {item_name} for ${item_total:.2f}")
        
        summary = "Here's a summary of your order: " + " and ".join(summary_parts)
        summary += f". Your total is ${total:.2f}. Would you like to confirm your order?"
        
        return summary