# Beanchat – AI Coffee Shop Ordering Assistant ☕🤖

Beanchat is a mobile application designed to reduce long queues in coffee shops by allowing users to place their orders directly through an AI-powered chatbot. Using Large Language Models, Natural Language Processing, and RunPod’s scalable infrastructure, Beanchat provides fast, accurate, and personalized ordering experiences.

The system uses a modular **agent-based architecture**, where each agent handles a specific task such as classification, recommendations, or information retrieval.

---

## 🚀 Project Goals

Beanchat aims to:

- Allow customers to place coffee orders through a conversational chatbot.
- Reduce pressure on staff and improve order throughput.
- Provide detailed menu information (ingredients, allergens, etc.) using RAG.
- Offer relevant product recommendations using market basket analysis.
- Maintain safe and relevant conversations through guardrails.

---

# 🧠 System Overview

## Core Agents

| Agent                    | Role                                                     |
| ------------------------ | -------------------------------------------------------- |
| **Guard Agent**          | Filters harmful or irrelevant messages before processing |
| **Classification Agent** | Determines user intent and routes queries                |
| **Order Taking Agent**   | Guides users through structured order placement          |
| **Details Agent (RAG)**  | Answers menu and allergen questions using vector DB      |
| **Recommendation Agent** | Suggests complementary products based on order context   |

---

# 📱 Mobile Application

Built with **React Native**, the app includes:

- Landing Page
- Home Page
- Item Details Page
- Cart Page
- Integrated Chatbot interface

The application allows customers to interact directly with the AI assistant and browse menu items.

---

# ⚙️ Tech Stack

### Frontend

- React Native

### AI Backend

- RunPod serverless deployment
- LLM-powered multi-agent architecture
- Retrieval-Augmented Generation (RAG)
- Vector database for knowledge storage

---

# 🏁 How It Works

1. User sends a message in the app.
2. Guard Agent checks for safety.
3. Classification Agent determines the user’s intent.
4. The message is forwarded to the relevant agent:
   - Order Taking Agent for placing orders
   - Details Agent for menu questions
   - Recommendation Agent for upselling
5. The selected agent processes the message and returns a structured response.
