import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  StatusBar,
} from "react-native";
import { useRouter } from "expo-router"; // Import useRouter

export default function Index() {
  const router = useRouter(); // Get the router instance

  const handleGetStarted = () => {
    //router.push('/home');
    router.navigate("/home");
    console.log("Get Started Pressed! Navigating...");
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-900">
      <StatusBar barStyle="light-content" />
      <View className="flex-1 justify-center items-center p-6">
        {/* App Name / Logo Placeholder */}
        <Text className="text-4xl font-bold text-white mb-4">Zendrive</Text>

        {/* Welcome Message */}
        <Text className="text-xl text-gray-300 text-center mb-2">
          Welcome, Driver!
        </Text>

        {/* Basic Info */}
        <Text className="text-lg text-gray-400 text-center mb-12 px-4">
          Helping you stay safe and alert on every journey. Let's prevent
          fatigue together.
        </Text>

        {/* Get Started Button */}
        <TouchableOpacity
          className="bg-blue-600 w-full py-4 rounded-lg shadow-md"
          onPress={handleGetStarted}
          activeOpacity={0.7}
        >
          <Text className="text-white text-center text-lg font-semibold">
            Get Started
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}
