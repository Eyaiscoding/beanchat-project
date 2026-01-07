import { Text, View, StatusBar, TouchableOpacity } from "react-native";
import { useEffect, useState } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import React from "react";
import PageHeader from "../../components/PageHeader";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { Product } from "../../types/types";
import { fetchProducts } from "../../services/productService";
import ProductList from "../../components/CartProductList";
import { useCart } from "../../components/CartContext";
import Toast from "react-native-root-toast";
import { router } from "expo-router";

const Order = () => {
  const { cartItems, SetQuantityCart, emptyCart } = useCart();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPrice, setTotalPrice] = useState<number>(0);

  const calculateTotal = (
    products: Product[],
    quantities: { [key: string]: number }
  ): number => {
    return products.reduce((total, product) => {
      const quantity = quantities[product.name] || 0;
      return total + product.price * quantity;
    }, 0);
  };

  useEffect(() => {
    const total = calculateTotal(products, cartItems);
    setTotalPrice(total);
  }, [cartItems, products]);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const productsData = await fetchProducts();
        setProducts(productsData);
      } catch (err) {
        setError("Error fetching products" + err);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, []);

  if (loading) return <Text>Loading...</Text>;
  if (error) return <Text>{error}</Text>;

  const orderNow = () => {
    emptyCart();
    Toast.show("Order placed successfully!", {
      duration: Toast.durations.SHORT,
      position: Toast.positions.BOTTOM,
    });
    router.push("/thankyou");
  };

  return (
    <GestureHandlerRootView className="bg-[#F9F9F9] w-full h-full">
      <StatusBar backgroundColor="white" />
      <PageHeader title="Order" showHeaderRight={false} bgColor="#F9F9F9" />

      <View className="h-full flex-col justify-between">
        <View className="flex-1">
          <ProductList
            products={products}
            quantities={cartItems}
            setQuantities={SetQuantityCart}
            totalPrice={totalPrice}
          />
        </View>

        <View className="bg-white rounded-tl-3xl rounded-tr-3xl px-7 pt-4 pb-8 shadow-lg">
          <View className="flex-row justify-between items-center mb-4">
            <View className="flex-row items-center flex-1">
              <View className="bg-[#F9F2ED] rounded-full p-2.5">
                <MaterialIcons
                  name="account-balance-wallet"
                  size={24}
                  color="#C67C4E"
                />
              </View>
              <View className="ml-3">
                <Text className="text-[#242424] text-sm font-[Sora-SemiBold]">
                  Total to pay
                </Text>
                <Text className="text-[#C67C4E] text-sm font-[Sora-SemiBold] mt-1">
                  DT {totalPrice.toFixed(2)}
                </Text>
              </View>
            </View>
            <MaterialIcons name="keyboard-arrow-down" size={28} color="black" />
          </View>

          <TouchableOpacity
            className={`${
              totalPrice === 0 ? "bg-[#EDEDED]" : "bg-[#C67C4E]"
            } w-full rounded-2xl items-center justify-center py-4`}
            disabled={totalPrice === 0}
            onPress={orderNow}
          >
            <Text
              className={`text-base ${
                totalPrice === 0 ? "text-[#A2A2A2]" : "text-white"
              } font-[Sora-SemiBold]`}
            >
              Order
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </GestureHandlerRootView>
  );
};

export default Order;
