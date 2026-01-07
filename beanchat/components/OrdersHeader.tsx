import { Text, View, TouchableOpacity } from "react-native";
import React from "react";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";
import { router } from "expo-router";

const OrdersHeader = () => {
  return (
    <View>
      {/* Order then Pick Up Button */}
      <View className="mx-7 mt-6">
        <TouchableOpacity className="bg-[#C67C4E] rounded-2xl py-4 items-center">
          <Text className="text-white text-base font-[Sora-SemiBold]">
            Order then Pick Up
          </Text>
        </TouchableOpacity>
      </View>

      {/* Validate your order section */}
      <View className="mx-7 mt-6">
        <Text className="text-[#242424] text-base font-[Sora-SemiBold]">
          Validate your order
        </Text>
        <Text className="text-[#A2A2A2] text-xs font-[Sora-Regular] mt-2">
          Please check your order carefully before validatig it.
        </Text>

        {/* Chat button */}
        <TouchableOpacity
          className="flex-row items-center border border-[#DEDEDE] rounded-2xl py-3 px-4 mt-3"
          onPress={() => {
            router.push("/(tabs)/chatRoom");
          }}
        >
          <MaterialCommunityIcons
            name="message-processing-outline"
            size={20}
            color="#242424"
          />
          <Text className="text-[#242424] text-sm font-[Sora-Regular] ml-2">
            Talk to ChatBot for more info
          </Text>
        </TouchableOpacity>
      </View>

      <View className="mx-7 border-b border-[#EAEAEA] mt-6 mb-4" />
    </View>
  );
};

export default OrdersHeader;
