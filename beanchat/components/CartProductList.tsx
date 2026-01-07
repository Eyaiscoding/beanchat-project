import React from "react";
import { View, Text, Image, TouchableOpacity, FlatList } from "react-native";
import { Product } from "../types/types";
import OrdersHeader from "./OrdersHeader";
import OrdersFooter from "./OrdersFooter";

// Props for ProductList
interface ProductListProps {
  products: Product[];
  quantities: { [key: string]: number };
  setQuantities: (itemKey: string, delta: number) => void;
  totalPrice: number;
}

const ProductList: React.FC<ProductListProps> = ({
  products,
  quantities,
  setQuantities,
  totalPrice,
}) => {
  console.log("📦 Products:", products.length);
  console.log("🛒 Quantities:", quantities);

  // Check if we're using IDs or names in quantities
  const quantityKeys = Object.keys(quantities);
  console.log("🔑 Quantity keys:", quantityKeys);

  // Filter products - try both ID and name to be safe
  const filteredProducts = products.filter((product) => {
    const hasById = (quantities[product.id] || 0) > 0;
    const hasByName = (quantities[product.name] || 0) > 0;
    return hasById || hasByName;
  });

  console.log("✅ Filtered products:", filteredProducts.length);

  const renderItem = ({ item }: { item: Product }) => {
    // Get quantity - check both ID and name
    const quantityById = quantities[item.id] || 0;
    const quantityByName = quantities[item.name] || 0;
    const quantity = quantityById > 0 ? quantityById : quantityByName;

    // Determine which key to use for updates
    const keyToUse = quantityById > 0 ? item.id : item.name;

    return (
      <View className="flex-row items-center justify-between mx-7 mb-4">
        <Image
          source={{ uri: item.image_url }}
          className="w-[54px] h-[54px] rounded-2xl"
        />
        <View className="flex-1 ml-3">
          <Text className="text-base font-[Sora-SemiBold] text-[#242424]">
            {item.name}
          </Text>
          <Text className="font-[Sora-Regular] text-xs text-[#A2A2A2] mt-1">
            {item.category}
          </Text>
        </View>

        <View className="flex-row items-center border border-[#EAEAEA] rounded-full px-2 py-1">
          <TouchableOpacity
            onPress={() => setQuantities(keyToUse, -1)}
            className="px-2"
          >
            <Text className="text-base font-[Sora-SemiBold] text-[#242424]">
              −
            </Text>
          </TouchableOpacity>
          <Text className="mx-3 text-base font-[Sora-SemiBold] text-[#242424]">
            {quantity}
          </Text>
          <TouchableOpacity
            onPress={() => setQuantities(keyToUse, 1)}
            className="px-2"
          >
            <Text className="text-base font-[Sora-SemiBold] text-[#242424]">
              +
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  return (
    <View>
      {filteredProducts.length > 0 ? (
        <FlatList
          ListHeaderComponent={<OrdersHeader />}
          ListFooterComponent={
            <OrdersFooter
              totalPrice={totalPrice}
              products={products}
              quantities={quantities}
            />
          }
          data={filteredProducts}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          showsVerticalScrollIndicator={false}
        />
      ) : (
        <View className="mx-7 items-center mt-10">
          <Text className="text-2xl font-[Sora-SemiBold] text-gray-500 mb-4 text-center">
            No items in your cart yet
          </Text>
          <Text className="text-xl font-[Sora-SemiBold] text-gray-500 text-center">
            Let's Go Get some Delicious Goodies
          </Text>
        </View>
      )}
    </View>
  );
};

export default ProductList;
