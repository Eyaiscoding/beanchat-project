/// <reference types="nativewind/types" />
import {
  GestureHandlerRootView,
  TouchableOpacity,
} from "react-native-gesture-handler";
import { Text, View, SafeAreaView, ImageBackground } from "react-native";
import { router } from "expo-router";

export default function Index() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaView style={{ flex: 1, backgroundColor: "#000" }}>
        <ImageBackground
          className="w-full h-full items-center justify-end pb-10"
          source={require("../assets/images/index_bg_image.png")}
          resizeMode="cover"
        >
          <View className="w-[80%] px-4">
            <Text className="text-white text-3xl text-center font-[Sora-SemiBold]">
              Fall in Love with Coffee in Bens Coffee Shop !
            </Text>

            <Text className="pt-3 text-[#A2A2A2] text-center font-[Sora-Regular]">
              Welcome to our cozy coffee corner, where every cup is a delight
              for you.
            </Text>

            <TouchableOpacity
              className="bg-[#C57C3E] mt-10 p-4 rounded-2xl items-center"
              onPress={() => router.push("/(tabs)/home")}
            >
              <Text className="text-xl text-white font-[Sora-SemiBold]">
                Get Started
              </Text>
            </TouchableOpacity>
          </View>
        </ImageBackground>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
}
