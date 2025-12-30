from agents import (GuardAgent, ClassificationAgent, DetailsAgent, 
                    OrderTakingAgent, RecommendationAgent, AgentProtocol)
import os

def main():
    guard_agent = GuardAgent()
    classification_agent = ClassificationAgent()
    recommendation_agent = RecommendationAgent(
        'recommendation_objects/apriori_recommendations.json',
        'recommendation_objects/popularity_recommendation.csv'
    )
    
    agent_dict: dict[str, AgentProtocol] = {
        "details_agent": DetailsAgent(),
        "order_taking_agent": OrderTakingAgent(),
        "recommendation_agent": recommendation_agent
    }
    
    messages = []
    
    while True:
        # Display the chat history
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*60)
        print("COFFEE SHOP CHATBOT - Conversation History")
        print("="*60 + "\n")
        
        for message in messages:
            role = message['role'].capitalize()
            content = message['content']
            
            # Show agent info if available
            agent_info = ""
            if 'memory' in message and 'agent' in message['memory']:
                agent_name = message['memory']['agent']
                agent_info = f" [{agent_name}]"
            
            print(f"{role}{agent_info}: {content}\n")
        
        print("-"*60)
        
        # Get user input
        prompt = input("User: ").strip()
        
        if not prompt:
            continue
        
        # Check for exit command
        if prompt.lower() in ['exit', 'quit', 'bye']:
            print("\nThank you for visiting Merry's Way! Goodbye!")
            break
        
        messages.append({"role": "user", "content": prompt})
        
        # Step 1: Guard Agent Check
        print("\n[DEBUG] Running Guard Agent...")
        guard_agent_response = guard_agent.get_response(messages)
        
        if guard_agent_response["memory"]["guard_decision"] == "not allowed":
            print("[DEBUG] Guard Agent blocked the request")
            messages.append(guard_agent_response)
            continue
        else:
            print("[DEBUG] Guard Agent: Request allowed")
        
        # Step 2: Classification Agent determines routing
        print("[DEBUG] Running Classification Agent...")
        classification_agent_response = classification_agent.get_response(messages)
        chosen_agent = classification_agent_response["memory"]["classification_decision"]
        print(f"[DEBUG] Chosen Agent: {chosen_agent}")
        
        # Step 3: Execute chosen agent
        agent = agent_dict[chosen_agent]
        print(f"[DEBUG] Executing {chosen_agent}...")
        response = agent.get_response(messages)
        
        # Show order status if available
        if 'memory' in response and 'order' in response['memory']:
            order = response['memory']['order']
            if order:
                print(f"[DEBUG] Current order: {order}")
        
        messages.append(response)

if __name__ == "__main__":
    main()