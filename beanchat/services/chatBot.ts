import axios from "axios";
import { MessageInterface } from "../types/types";
import { API_KEY, API_URL } from "../config/runpodConfigs";

async function callChatBotAPI(
  messages: MessageInterface[]
): Promise<MessageInterface> {
  try {
    console.log("📤 Sending to API:", JSON.stringify({ messages }, null, 2));

    const response = await axios.post(
      API_URL,
      {
        input: {
          messages: messages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        },
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${API_KEY}`,
        },
      }
    );

    console.log("📥 API Response:", JSON.stringify(response.data, null, 2));

    let output = response.data;
    let outputMessage: MessageInterface = output["output"];

    return outputMessage;
  } catch (error: any) {
    console.error("❌ Error calling the API:", error);
    if (error.response) {
      console.error("Response data:", error.response.data);
      console.error("Response status:", error.response.status);
    }
    throw error;
  }
}

export { callChatBotAPI };
