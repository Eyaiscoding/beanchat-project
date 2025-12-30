import json
import pandas as pd
import os
from .utils import get_chatbot_response, double_check_json_output
from copy import deepcopy
from dotenv import load_dotenv
import re

load_dotenv()

class RecommendationAgent():
    def __init__(self, apriori_recommendation_path, popular_recommendation_path):
        with open(apriori_recommendation_path, 'r') as file:
            self.apriori_recommendations = json.load(file)
        
        self.popular_recommendations = pd.read_csv(popular_recommendation_path)
        self.products = self.popular_recommendations['product'].tolist()
        self.product_categories = self.popular_recommendations['product_category'].tolist()

    def get_apriori_recommendation(self, products, top_k=5):
        recommendation_list = []
        
        for product in products:
            if product in self.apriori_recommendations:
                recommendation_list += self.apriori_recommendations[product]
        
        # Sort by cofidence (typo in JSON file)
        recommendation_list = sorted(recommendation_list, key=lambda x: x.get('cofidence', 0), reverse=True)
        
        recommendations = []
        recommendations_per_category = {}
        
        for recommendation in recommendation_list:
            product_name = recommendation.get('product', '')
            product_category = recommendation.get('product_category', 'Unknown')
            
            # Skip if already recommended
            if product_name in recommendations:
                continue
            
            # Limit 2 per category
            if product_category not in recommendations_per_category:
                recommendations_per_category[product_category] = 0
            
            if recommendations_per_category[product_category] >= 2:
                continue
            
            recommendations_per_category[product_category] += 1
            recommendations.append(product_name)
            
            if len(recommendations) >= top_k:
                break
        
        return recommendations

    def get_popular_recommendation(self, product_categories=None, top_k=5):
        recommendations_df = self.popular_recommendations
        
        if type(product_categories) == str:
            product_categories = [product_categories]
        
        if product_categories is not None:
            recommendations_df = self.popular_recommendations[
                self.popular_recommendations['product_category'].isin(product_categories)
            ]
        
        recommendations_df = recommendations_df.sort_values(by='number_of_transactions', ascending=False)
        
        if recommendations_df.shape[0] == 0:
            return []
        
        recommendations = recommendations_df['product'].tolist()[:top_k]
        return recommendations

    def recommendation_classification(self, messages):
        system_prompt = """You are a helpful AI assistant for a coffee shop application which serves drinks and pastries.

We have 3 types of recommendations:

1. Apriori Recommendations: Based on the user's order history. Recommend items frequently bought together.

2. Popular Recommendations: Based on popularity. Recommend popular items among customers.

3. Popular Recommendations by Category: User asks for recommendations in a specific category (e.g., "what coffee do you recommend?"). Recommend popular items in that category.

Available items: """ + ",".join(self.products) + """

Available categories: """ + ",".join(set(self.product_categories)) + """

Your task: Determine which type of recommendation to provide.

CRITICAL: Respond with ONLY a valid JSON object. No markdown, no explanations.

Output format:
{
  "chain_of_thought": "analyze what type of recommendation",
  "recommendation_type": "popular",
  "parameters": []
}

recommendation_type must be: "apriori", "popular", or "popular by category"
parameters is a list of strings - use [] for empty list

Examples:
"what do you recommend?" → {"chain_of_thought": "general recommendation", "recommendation_type": "popular", "parameters": []}
"what coffee do you recommend?" → {"chain_of_thought": "asking for coffee category", "recommendation_type": "popular by category", "parameters": ["Coffee"]}
"""
        
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
        chatbot_output = get_chatbot_response(input_messages)
        output = self.postprocess_classification(chatbot_output)
        
        return output

    def get_response(self, messages):
        messages = deepcopy(messages)
        
        # Check if user mentioned a specific item they want to order
        last_message = messages[-1]['content'].lower()
        
        # If they said "I want to order X", extract X and give apriori recommendations
        if "i want to order" in last_message or "i'd like to order" in last_message:
            # Try to extract the item name
            for product in self.products:
                if product.lower() in last_message:
                    print(f"[RecommendationAgent] User wants to order '{product}', showing complementary items")
                    # Create a temporary order to get apriori recommendations
                    temp_order = [{"item": product, "quantity": 1, "price": 0}]
                    return self.get_recommendations_from_order(messages, temp_order)
        
        # Otherwise, proceed with normal classification
        recommendation_classification = self.recommendation_classification(messages)
        recommendation_type = recommendation_classification['recommendation_type']
        
        print(f"[RecommendationAgent] Type: {recommendation_type}")
        
        recommendations = []
        
        if recommendation_type == "apriori":
            recommendations = self.get_apriori_recommendation(recommendation_classification['parameters'])
        elif recommendation_type == "popular":
            recommendations = self.get_popular_recommendation()
        elif recommendation_type == "popular by category":
            recommendations = self.get_popular_recommendation(recommendation_classification['parameters'])
        
        if recommendations == []:
            return {
                "role": "assistant", 
                "content": "Sorry, I can't help with that. Can I help you with your order?",
                "memory": {"agent": "recommendation_agent"}
            }
        
        recommendations_str = ", ".join(recommendations)
        print(f"[RecommendationAgent] Recommendations: {recommendations_str}")
        
        system_prompt = """You are a friendly assistant for a coffee shop called Merry's Way.

Your task: Recommend the exact items I provide to you.

CRITICAL RULES:
- Use bullet points (•) for each item
- Keep descriptions brief (one sentence, max 15 words)
- Be friendly but concise
- Only recommend the items specified
- DO NOT add any notes, commentary, or extra text at the end
- DO NOT say things like "I'll provide more orders" or "you can adapt"
- STOP after listing the recommendations

Response format:
Here are some recommendations for you:
• [Item Name]: [Brief description]
• [Item Name]: [Brief description]
• [Item Name]: [Brief description]

STOP there. No additional text."""

        prompt = f"""{messages[-1]['content']}

Please recommend these items: {recommendations_str}

Remember: Only list the recommendations. No extra notes or commentary."""

        messages[-1]['content'] = prompt
        input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]
        
        chatbot_output = get_chatbot_response(input_messages)
        output = self.postprocess(chatbot_output)
        
        return output

    def postprocess_classification(self, output):
        output = output.strip()
        
        # Remove markdown
        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]
        
        if output.endswith("```"):
            output = output[:-3]
        
        output = output.strip()
        
        # Extract JSON
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output)
        if json_match:
            output = json_match.group(0)
        
        try:
            parsed_output = json.loads(output)
        except json.JSONDecodeError as e:
            print(f"[RecommendationAgent] JSON error: {e}")
            try:
                output = double_check_json_output(output)
                parsed_output = json.loads(output)
            except:
                parsed_output = {
                    "recommendation_type": "popular",
                    "parameters": []
                }
        
        return {
            "recommendation_type": parsed_output.get('recommendation_type', 'popular'),
            "parameters": parsed_output.get('parameters', []),
        }

    def get_recommendations_from_order(self, messages, order):
        """
        Get apriori recommendations based on current order.
        These are complementary items that pair well with their order.
        """
        products = []
        for product in order:
            products.append(product['item'])

        print(f"[RecommendationAgent] Getting apriori recommendations for: {products}")
        recommendations = self.get_apriori_recommendation(products, top_k=3)
        
        if not recommendations:
            print("[RecommendationAgent] No apriori recommendations found")
            return {
                "role": "assistant", 
                "content": "", 
                "memory": {"agent": "recommendation_agent"}
            }
        
        recommendations_str = ", ".join(recommendations)
        print(f"[RecommendationAgent] Apriori recommendations: {recommendations_str}")

        system_prompt = """You are a friendly assistant for a coffee shop called Merry's Way.

Your task: Suggest complementary items to go with the customer's order.

CRITICAL RULES:
- Use bullet points (•) for each item
- Keep descriptions brief (one sentence, max 15 words)
- Be friendly but concise
- Focus on items that pair well with their order
- Only recommend the items specified
- DO NOT add any notes, commentary, or extra text at the end
- DO NOT say things like "I'll provide more orders" or "you can adapt"
- STOP after listing the recommendations

Response format:
Here are some recommendations to complement your [their item]:
• [Item Name]: [Brief description]
• [Item Name]: [Brief description]
• [Item Name]: [Brief description]

STOP there. No additional text."""

        # Get the last item they ordered
        last_item = order[-1]['item'] if order else "order"
        
        prompt = f"""The customer just ordered: {last_item}

Please recommend these complementary items: {recommendations_str}

Remember: Only list the recommendations. No extra notes or commentary."""

        messages_copy = deepcopy(messages)
        messages_copy[-1]['content'] = prompt
        input_messages = [{"role": "system", "content": system_prompt}] + messages_copy[-3:]

        chatbot_output = get_chatbot_response(input_messages)
        output = self.postprocess(chatbot_output)

        return output
    
    def postprocess(self, output):
        output = output.strip()
        
        # Remove markdown
        if output.startswith("```"):
            lines = output.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            output = '\n'.join(lines).strip()
        
        # Remove common unwanted endings
        unwanted_patterns = [
            r'\(Note:.*?\)',  # Remove (Note: ...)
            r'\n\nNote:.*$',  # Remove "Note: ..." at end
            r'\n\nI\'ll.*$',  # Remove "I'll ..." at end
            r'\n\nPlease.*$',  # Remove "Please ..." at end
            r'\n\nFeel free.*$',  # Remove "Feel free ..." at end
        ]
        
        for pattern in unwanted_patterns:
            output = re.sub(pattern, '', output, flags=re.IGNORECASE | re.DOTALL)
        
        output = output.strip()
        
        return {
            "role": "assistant",
            "content": output,
            "memory": {"agent": "recommendation_agent"}
        }