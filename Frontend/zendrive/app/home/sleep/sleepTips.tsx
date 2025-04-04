import React from "react";
import { View, Text, ScrollView, SafeAreaView } from "react-native";

const SleepTips = () => {
  return (
    <SafeAreaView className="bg-slate-900 h-full">
      <ScrollView className="p-5 bg-slate-900">
        <Text className="text-5xl font-bold mb-1 text-white">
          For a better sleep
        </Text>
        <Text className="text-3xl font-semibold mb-5 ml-1 text-white">
          For a better tommorrow
        </Text>
        <Text className="text-base mb-2 leading-6 text-white">
          1. Stick to a sleep schedule, even on weekends.
        </Text>
        <Text className="text-base mb-2 leading-6 text-white">
          2. Practice a relaxing bedtime ritual.
        </Text>
        <Text className="text-base mb-2 leading-6 text-white">
          3. Avoid naps, especially in the afternoon.
        </Text>
        <Text className="text-base mb-2 leading-6 text-white">
          4. Exercise daily, but not too close to bedtime.
        </Text>
        <Text className="text-base mb-2 leading-6 text-white">
          5. Make your bedroom comfortable and free of distractions.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
};

export default SleepTips;
