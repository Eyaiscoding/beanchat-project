from agents import (
    GuardAgent,
    ClassificationAgent,
    DetailsAgent,
    OrderTakingAgent,
    RecommendationAgent,
    AgentProtocol
)

class AgentController():
    def __init__(self):
        self.guard_agent = GuardAgent()
        self.classification_agent = ClassificationAgent()

        self.recommendation_agent = RecommendationAgent(
            'recommendation_objects/apriori_recommendations.json',
            'recommendation_objects/popularity_recommendation.csv'
        )

        self.agent_dict: dict[str, AgentProtocol] = {
            "details_agent": DetailsAgent(),
            # ✅ FIX: do NOT pass recommendation_agent
            "order_taking_agent": OrderTakingAgent(),
            "recommendation_agent": self.recommendation_agent
        }

    def get_response(self, input):
        job_input = input["input"]
        messages = job_input["messages"]

        # Guard agent
        guard_agent_response = self.guard_agent.get_response(messages)
        if guard_agent_response["memory"]["guard_decision"] == "not allowed":
            return guard_agent_response

        # Classification agent
        classification_agent_response = self.classification_agent.get_response(messages)
        chosen_agent = classification_agent_response["memory"]["classification_decision"]

        # Route to chosen agent
        agent = self.agent_dict[chosen_agent]
        response = agent.get_response(messages)

        return response
