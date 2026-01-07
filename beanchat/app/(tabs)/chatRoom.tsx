import { Alert, TouchableOpacity, View, Text } from "react-native";
import React, { useEffect, useRef, useState } from "react";
import { StatusBar } from "expo-status-bar";
import MessageList from "../../components/MessageList";
import { MessageInterface } from "../../types/types";
import {
  widthPercentageToDP as wp,
  heightPercentageToDP as hp,
} from "react-native-responsive-screen";
import {
  GestureHandlerRootView,
  TextInput,
} from "react-native-gesture-handler";
import { Feather } from "@expo/vector-icons";
import { callChatBotAPI } from "../../services/chatBot";
import PageHeader from "../../components/PageHeader";
import { useCart } from "../../components/CartContext";

const ChatRoom = () => {
  const { addToCart, emptyCart } = useCart();

  const [messages, setMessages] = useState<MessageInterface[]>([]);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const textRef = useRef("");
  const inputRef = useRef<TextInput>(null);

  useEffect(() => {
    console.log("💬 Messages updated:", messages.length);
  }, [messages]);

  const handleSendMessage = async () => {
    let message = textRef.current.trim();
    if (!message) return;

    try {
      console.log("📝 User message:", message);

      // Create user message object
      const userMessage: MessageInterface = {
        content: message,
        role: "user",
      };

      // Add the user message to the list of messages
      let InputMessages = [...messages, userMessage];

      setMessages(InputMessages);
      textRef.current = "";
      if (inputRef) inputRef?.current?.clear();
      setIsTyping(true);

      console.log("🔄 Calling API with messages:", InputMessages);

      let responseMessage = await callChatBotAPI(InputMessages);

      console.log("✅ Got response:", responseMessage);

      setIsTyping(false);
      setMessages((prevMessages) => [...prevMessages, responseMessage]);

      if (responseMessage) {
        if (responseMessage.memory) {
          console.log("🧠 Memory found:", responseMessage.memory);
          if (responseMessage.memory.order) {
            console.log(
              "🛒 Order found, updating cart:",
              responseMessage.memory.order
            );
            emptyCart();
            responseMessage.memory.order.forEach((item: any) => {
              addToCart(item.item, item.quantity);
            });
          }
        }
      }
    } catch (err: any) {
      setIsTyping(false);
      console.error("❌ Error in handleSendMessage:", err);
      Alert.alert("Error", err.message || "Failed to send message");
    }
  };

  return (
    <GestureHandlerRootView>
      <StatusBar style="dark" />

      <View className="flex-1 bg-white">
        <PageHeader title="Chat Bot" showHeaderRight={false} bgColor="white" />

        <View className="h-3 border-b border-neutral-300" />

        <View className="flex-1 justify-between bg-neutral-100 overflow-visibile">
          <View className="flex-1">
            <MessageList messages={messages} isTyping={isTyping} />
          </View>

          <View style={{ marginBottom: hp(2.7) }} className="pt-2">
            <View className="flex-row mx-3 justify-between border p-2 bg-white border-neutral-300 rounded-full pl-5">
              <TextInput
                ref={inputRef}
                onChangeText={(value) => (textRef.current = value)}
                placeholder="Type message..."
                style={{ fontSize: hp(2) }}
                className="flex-1 mr2"
              />
              <TouchableOpacity
                onPress={handleSendMessage}
                className="bg-neutral-200 p-2 mr-[1px] rounded-full"
              >
                <Feather name="send" size={hp(2.7)} color="#737373" />
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </View>
    </GestureHandlerRootView>
  );
};

export default ChatRoom;
