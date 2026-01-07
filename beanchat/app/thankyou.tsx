import { Text, View, StatusBar } from "react-native";
import React, { useEffect, useState } from "react";
import {
  TouchableOpacity,
  GestureHandlerRootView,
} from "react-native-gesture-handler";
import { router } from "expo-router";

const ThankyouPage = () => {
  const [orderNumber, setOrderNumber] = useState<string>("");

  useEffect(() => {
    // Generate a random 6-digit order number
    const randomNumber = Math.floor(100000 + Math.random() * 900000);
    setOrderNumber(`N°${randomNumber}`);
  }, []);

  return (
    <GestureHandlerRootView className="flex-1">
      <StatusBar barStyle="dark-content" backgroundColor="white" />
      <View className="w-full h-full items-center justify-center px-10 bg-white">
        {/* Thank you message */}
        <Text className="text-[#C67C4E] text-3xl font-[Sora-SemiBold] text-center mb-4">
          Thank you for your order !
        </Text>

        {/* Instruction text */}
        <Text className="text-[#2F2D2C] text-lg font-[Sora-SemiBold] text-center mb-12">
          Show this Order Number to the barista:
        </Text>

        {/* Order number */}
        <Text className="text-[#F2E5D7] text-5xl font-[Sora-Bold] mb-20 tracking-wide">
          {orderNumber}
        </Text>

        {/* Return button */}
        <TouchableOpacity
          className="bg-[#C67C4E] rounded-2xl items-center justify-center py-4 px-10"
          onPress={() => router.push("/(tabs)/home")}
          activeOpacity={0.8}
        >
          <Text className="text-white text-sm font-[Sora-SemiBold]">
            Return to Home page
          </Text>
        </TouchableOpacity>
      </View>
    </GestureHandlerRootView>
  );
};

export default ThankyouPage;
