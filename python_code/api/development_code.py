from agents import (GuardAgent,
                    ClassificationAgent,
                    DetailsAgent,
                    AgentProtocol)

from typing import Dict
import os

def main():
    pass

if __name__ == "__main__":
    guard_agent = GuardAgent()
    classification_agent = ClassificationAgent()

    # Updated agent_dict to match the classification agent's output
    agent_dict: Dict[str, AgentProtocol] = {
        "details_agent": DetailsAgent(),
        "order_taking_agent": DetailsAgent(),  # Replace with OrderTakingAgent() when available
        "recommendation_agent": DetailsAgent()  # Replace with RecommendationAgent() when available
    }

    messages = []
    while True:
        # os.system('cls' if os.name == 'nt' else 'clear')

        print("\n\n Print Messages ......")
        for message in messages:
            print(f"{message['role']}:{message['content']}")

        # Get user input
        prompt = input("User: ")
        messages.append({"role": "user", "content": prompt})

        # Get GuardAgent's response
        guard_agent_response = guard_agent.get_response(messages)
        if guard_agent_response["memory"]["guard_decision"] == "not allowed":
            messages.append(guard_agent_response)
            continue
        
        # Get ClassificationAgent's response
        classification_agent_response = classification_agent.get_response(messages)
        chosen_agent = classification_agent_response["memory"]["classification_decision"]
        print("Chosen Agent: ", chosen_agent)

        # Get the chosen agent's response
        agent = agent_dict[chosen_agent]
        response = agent.get_response(messages)
        
        messages.append(response)