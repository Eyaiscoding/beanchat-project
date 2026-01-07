# Beanchat – AI Coffee Shop Ordering Assistant ☕🤖

Beanchat is a cross-platform mobile application designed to modernize the coffee shop experience. By leveraging **Large Language Models (LLMs)** and a specialized **Multi-Agent Backend**, it allows customers to place orders, ask for menu details, and receive personalized recommendations through a seamless chat interface.

The system is powered by a **Serverless AI Infrastructure** on **RunPod**, ensuring high performance and scalability by offloading heavy AI computations to dedicated cloud GPUs.

---

## 🧠 System Architecture

Beanchat uses a modular **Agent-Based System**. Every user message is routed through specialized modules to ensure accuracy and relevance:

| Agent | Role | Technical Implementation |
| :--- | :--- | :--- |
| **Guard Agent** | Safety & Relevance | [cite_start]Filters out-of-scope or harmful prompts (e.g., math problems or off-topic questions)[cite: 83, 91]. |
| **Classification Agent** | Intent Routing | [cite_start]Analyzes the query to route it to Ordering, Info, or Recommendation agents based on detected keywords[cite: 716, 735]. |
| **Order Taking Agent** | Transaction Logic | [cite_start]Manages the cart state and guides users through coffee customization (size, milk, etc.)[cite: 653]. |
| **Details Agent (RAG)** | Knowledge Retrieval | [cite_start]Answers menu-specific questions using **Vector Search (Pinecone)** and **Embeddings**[cite: 771, 820]. |
| **Recommendation Agent** | Personalized Upselling | [cite_start]Uses a **Market Basket Analysis (Apriori Algorithm)** to suggest complementary pairings like muffins with lattes[cite: 652]. |

---

## 🛠 Tech Stack

- [cite_start]**Frontend:** React Native (Expo SDK 51), NativeWind (Tailwind CSS), Expo Router[cite: 235, 243].
- **Backend Orchestration:** Python (Agent logic), Docker.
- [cite_start]**AI Infrastructure:** - **RunPod Serverless vLLM:** Hosting the Llama LLM for text generation[cite: 144].
  - [cite_start]**RunPod Infinity:** Hosting the `BAAI/bge-small-en-v1.5` model for RAG embeddings[cite: 780].
- [cite_start]**Databases:** - **Firebase Realtime DB:** Stores menu items and handles order synchronization[cite: 217, 628].
  - [cite_start]**Pinecone:** Vector database for semantic search and menu knowledge[cite: 782, 784].

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
    - [cite_start]It orchestrates calls between the **LLM Endpoint** and **Embedding Endpoint** using secure API tokens[cite: 144, 777].
- **Data Flow:** When a user interacts with the app, the frontend sends the message to the RunPod endpoint. [cite_start]The agents process the intent, query the necessary databases (Firebase/Pinecone), and return a structured response to the mobile client[cite: 756, 764].

---

## 🏁 How the Data Flows
1. [cite_start]**User Interaction:** User types "I want a Latte" in the app[cite: 345].
2. [cite_start]**Classification:** The message hits the **RunPod Backend**, where the **Classification Agent** identifies it as an "Order" intent[cite: 735].
3. [cite_start]**Intelligence:** The **Details Agent** retrieves current pricing from **Pinecone**[cite: 820], while the **Recommendation Agent** suggests a pairing based on the Apriori model.
4. [cite_start]**Real-time Sync:** The order is updated in the **Firebase Realtime Database** [cite: 631][cite_start], and the item appears instantly in the app's Cart[cite: 288].
