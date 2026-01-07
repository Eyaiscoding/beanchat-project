import React from "react";
import { View, Text } from "react-native";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";
import { Product } from "../types/types";

interface OrdersFooterProps {
  totalPrice: number;
  products: Product[];
  quantities: { [key: string]: number };
}

const OrdersFooter: React.FC<OrdersFooterProps> = ({
  totalPrice,
  products,
  quantities,
}) => {
  console.log("OrdersFooter - quantities:", quantities);

  // Get products that are in the cart - check both ID and name
  const cartProducts = products.filter((product) => {
    const hasById = (quantities[product.id] || 0) > 0;
    const hasByName = (quantities[product.name] || 0) > 0;
    return hasById || hasByName;
  });

  console.log("OrdersFooter - cartProducts:", cartProducts.length);

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

      {/* Payment Summary */}
      <Text className="mx-7 text-[#242424] text-base font-[Sora-SemiBold] mb-3">
        Payment Summary
      </Text>

      {/* Display each cart item with its price */}
      {cartProducts.map((product) => {
        // Get quantity - check both ID and name
        const quantityById = quantities[product.id] || 0;
        const quantityByName = quantities[product.name] || 0;
        const quantity = quantityById > 0 ? quantityById : quantityByName;
        const itemTotal = product.price * quantity;

        return (
          <View key={product.id} className="flex-row justify-between mx-7 mb-2">
            <Text className="text-sm font-[Sora-Regular] text-[#242424]">
              {product.name}
              {quantity > 1 ? ` x${quantity}` : ""}
            </Text>
            <Text className="text-sm font-[Sora-SemiBold] text-[#242424]">
              DT {itemTotal.toFixed(2)}
            </Text>
          </View>
        );
      })}

      <View className="pb-20" />
    </>
  );
};

export default OrdersFooter;
