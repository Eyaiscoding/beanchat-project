import { useEffect, useState } from "react";
import {
  Text,
  View,
  Image,
  FlatList,
  StatusBar,
  Pressable,
} from "react-native";
import React from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  GestureHandlerRootView,
  TouchableOpacity,
} from "react-native-gesture-handler";
import { router } from "expo-router";
import AntDesign from "@expo/vector-icons/AntDesign";
import Toast from "react-native-root-toast";
import { Product, ProductCategory } from "../../types/types";
import { fetchProducts } from "../../services/productService";
import SearchArea from "../../components/SearchArea";
import Banner from "../../components/Banner";
import { useCart } from "../../components/CartContext";

const home = () => {
  const { addToCart, cartItems } = useCart();

  const [products, setProducts] = useState<Product[]>([]);
  const [shownProducts, setShownProducts] = useState<Product[]>([]);
  const [productCategories, setProductCatgories] = useState<ProductCategory[]>(
    []
  );
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const uniqueCategories = Array.from(productCategories).map((category) => ({
      id: category.id,
      selected: selectedCategory === category.id,
    }));
    setProductCatgories(uniqueCategories);

    if (selectedCategory === "All") {
      setShownProducts(products);
    } else {
      const filteredProducts = products.filter(
        (product) => product.category === selectedCategory
      );
      setShownProducts(filteredProducts);
    }
  }, [selectedCategory, products]);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const productsData = await fetchProducts();

        const categories = productsData.map((product) => product.category);
        categories.unshift("All");
        const uniqueCategories = Array.from(new Set(categories)).map(
          (category) => ({
            id: category,
            selected: selectedCategory === category,
          })
        );

        setProducts(productsData);
        setShownProducts(productsData);
        setProductCatgories(uniqueCategories);
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

  const addButton = (name: string) => {
    console.log("🔵 Add button clicked for:", name);
    addToCart(name, 1);
    Toast.show(`${name} added to cart`, {
      duration: Toast.durations.SHORT,
    });
  };

  const handleProductPress = (item: Product) => {
    router.push({
      pathname: "/details",
      params: {
        name: item.name,
        image_url: item.image_url,
        type: item.category,
        price: item.price,
        rating: item.rating,
        description: item.description,
      },
    });
  };

  const renderProduct = ({ item, index }: { item: Product; index: number }) => {
    console.log("Rendering product:", item.name, "at index:", index);

    return (
      <View className="w-[48%] mt-2 bg-white rounded-2xl p-2 flex justify-between">
        <TouchableOpacity
          onPress={() => handleProductPress(item)}
          activeOpacity={0.7}
        >
          <Image
            source={{ uri: item.image_url }}
            className="w-full h-32 rounded-2xl"
          />
          <Text className="text-[#242424] text-lg font-[Sora-SemiBold] ml-1 mt-2">
            {item.name}
          </Text>
          <Text className="text-[#A2A2A2] text-sm font-[Sora-Regular] ml-1 mt-1">
            {item.category}
          </Text>
        </TouchableOpacity>

        <View className="flex-row justify-between ml-1 mt-4 mb-2">
          <Text className="text-[#050505] text-xl font-[Sora-SemiBold]">
            DT {item.price}
          </Text>

          <Pressable onPress={() => addButton(item.name)}>
            <View className="mr-2 p-2 -mt-1 bg-app_orange_color rounded-xl">
              <AntDesign name="plus" size={20} color="white" />
            </View>
          </Pressable>
        </View>
      </View>
    );
  };

  return (
    <GestureHandlerRootView>
      <StatusBar barStyle="light-content" backgroundColor="#222222" />
      <SafeAreaView className="w-full h-full">
        <FlatList
          horizontal={false}
          columnWrapperStyle={{
            justifyContent: "space-between",
            marginLeft: 15,
            marginRight: 15,
          }}
          numColumns={2}
          keyExtractor={(item, index) => `product-${item.name}-${index}`}
          data={shownProducts}
          renderItem={renderProduct}
          removeClippedSubviews={true}
          initialNumToRender={10}
          maxToRenderPerBatch={10}
          windowSize={5}
          ListHeaderComponent={() => (
            <View className="flex">
              <SearchArea />
              <Banner />

              <View className="flex items-center">
                <FlatList
                  className="mt-6 w-[90%] mb-2"
                  data={productCategories}
                  horizontal={true}
                  keyExtractor={(item, index) => `category-${item.id}-${index}`}
                  renderItem={({ item }) => (
                    <TouchableOpacity
                      onPress={() => setSelectedCategory(item.id)}
                      activeOpacity={0.7}
                    >
                      <Text
                        className={`text-sm mr-4 font-[Sora-Regular] p-3 rounded-lg 
                        ${item.selected ? "text-white" : "text-[#313131]"}
                        ${
                          item.selected
                            ? "bg-app_orange_color "
                            : "bg-[#EDEDED] "
                        }
                        `}
                      >
                        {item.id}
                      </Text>
                    </TouchableOpacity>
                  )}
                />
              </View>
            </View>
          )}
        />
      </SafeAreaView>
    </GestureHandlerRootView>
  );
};

export default home;
