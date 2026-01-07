import React from "react";
import { View, Text } from "react-native";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";

interface OrdersFooterProps {
  totalPrice: number;
}

const OrdersFooter: React.FC<OrdersFooterProps> = ({ totalPrice }) => {
  return (
    <>
      {/* Discount Badge */}
      <View className="mx-7 bg-white rounded-2xl p-4 flex-row items-center mb-4 border border-[#EAEAEA]">
        <View className="bg-[#50C878] rounded-full p-2 mr-3">
          <MaterialCommunityIcons
            name="brightness-percent"
            size={20}
            color="white"
          />
        </View>
        <View className="flex-1">
          <Text className="text-sm font-[Sora-SemiBold] text-[#242424]">
            Offer applied !
          </Text>
          <Text className="text-xs font-[Sora-Regular] text-[#A2A2A2] mt-1">
            Get your free item from the counter.
          </Text>
        </View>
      </View>

      {/* Payment Summary - NO DELIVERY FEE */}
      <Text className="mx-7 text-[#242424] text-base font-[Sora-SemiBold] mb-3">
        Payment Summary
      </Text>

      <View className="flex-row justify-between mx-7 mb-3">
        <Text className="text-sm font-[Sora-Regular] text-[#242424]">
          Price
        </Text>
        <Text className="text-sm font-[Sora-SemiBold] text-[#242424]">
          DT {totalPrice.toFixed(2)}
        </Text>
      </View>

      <View className="pb-20" />
    </>
  );
};

export default OrdersFooter;
