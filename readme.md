# Beanchat – AI Coffee Shop Ordering Assistant ☕🤖

Beanchat is a cross-platform mobile application designed to modernize the coffee shop experience. By leveraging **Large Language Models (LLMs)** and a specialized **Multi-Agent Backend**, it allows customers to place orders, ask for menu details, and receive personalized recommendations through a seamless chat interface.

The system is powered by a **Serverless AI Infrastructure** on **RunPod**, ensuring high performance and scalability by offloading heavy AI computations to dedicated cloud GPUs.

---

## 🧠 System Architecture

Beanchat uses a modular **Agent-Based System**. Every user message is routed through specialized modules to ensure accuracy and relevance:

| Agent                    | Role                   | Technical Implementation                                                                                          |
| :----------------------- | :--------------------- | :---------------------------------------------------------------------------------------------------------------- |
| **Guard Agent**          | Safety & Relevance     | Filters out-of-scope or harmful prompts (e.g., math problems or off-topic questions).                             |
| **Classification Agent** | Intent Routing         | Analyzes the query to route it to Ordering, Info, or Recommendation agents based on detected keywords.            |
| **Order Taking Agent**   | Transaction Logic      | Manages the cart state and guides users through coffee customization (size, milk, etc.).                          |
| **Details Agent (RAG)**  | Knowledge Retrieval    | Answers menu-specific questions using **Vector Search (Pinecone)** and **Embeddings**.                            |
| **Recommendation Agent** | Personalized Upselling | Uses a **Market Basket Analysis (Apriori Algorithm)** to suggest complementary pairings like muffins with lattes. |

---

## 🛠 Tech Stack

- **Frontend:** React Native (Expo SDK 51), NativeWind (Tailwind CSS), Expo Router.
- **Backend Orchestration:** Python (Agent logic), Docker.
- **AI Infrastructure:** - **RunPod Serverless vLLM:** Hosting the Llama LLM for text generation.
  - **RunPod Infinity:** Hosting the `BAAI/bge-small-en-v1.5` model for RAG embeddings.
- **Databases:** - **Firebase Realtime DB:** Stores menu items and handles order synchronization.
  - **Pinecone:** Vector database for semantic search and menu knowledge.

---

## 🚀 Execution Guide

### 1. Frontend Setup

The frontend is built with **React Native** and is optimized for Android using **Expo SDK 51**.

1.  **Environment Variables:** Place the `.env` files provided in your project root into the `/beanchat` folder.
2.  **Install Dependencies:**
    ```bash
    cd beanchat
    npm install
    ```
3.  **Run the App:**
    ```bash
    npx expo start --tunnel -c
    ```
4.  **Mobile Access:** - Install **Expo Go** on your Android device.
    - Due to specific dependency versions, you **must** use **SDK 51** via this link: [https://expo.dev/go?sdkVersion=51&platform=android&device=true](https://expo.dev/go?sdkVersion=51&platform=android&device=true).
    - Scan the QR code generated in your terminal to open the app.

### 2. Backend Execution

The backend is a **Serverless Python API** already deployed and ready for use.

- **Deployment Status:** The backend is containerized via Docker and deployed as a serverless endpoint on **RunPod**.
- **How it functions:** - The `main.py` script utilizes the `runpod.serverless` handler to process incoming requests.
  - It orchestrates calls between the **LLM Endpoint** and **Embedding Endpoint** using secure API tokens.
- **Data Flow:** When a user interacts with the app, the frontend sends the message to the RunPod endpoint. The agents process the intent, query the necessary databases (Firebase/Pinecone), and return a structured response to the mobile client.

---

## 🏁 How the Data Flows

1. **User Interaction:** User types "I want a Latte" in the app.
2. **Classification:** The message hits the **RunPod Backend**, where the **Classification Agent** identifies it as an "Order" intent.
3. **Intelligence:** The **Details Agent** retrieves current pricing from **Pinecone**, while the **Recommendation Agent** suggests a pairing based on the Apriori model.
4. **Real-time Sync:** The order is updated in the **Firebase Realtime Database** , and the item appears instantly in the app's Cart.
