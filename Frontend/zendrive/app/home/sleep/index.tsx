import React from "react";
import { View, Text, StyleSheet, SafeAreaView } from "react-native";
import HorizontalSection from "../../components/HorizontalSection";
import PanelSection from "../../components/PanelSection";
import HeadingText from "../../components/HeadingText";

const SleepScreen = () => {
  return (
    <View className="bg-slate-900 h-full">
      <SafeAreaView>
        <View className="mt-5 mx-3">
          <HeadingText>Sleep Tracker</HeadingText>
        </View>

        <View className="mt-5 mx-3 h-full">
          <HorizontalSection name="Sleep Quality Today" />

          <View className="flex flex-row mt-5 w-full h-[70%] gap-3">
            {/* Long Panel */}
            <PanelSection className=" flex-grow bg-emerald-300">
              <Text className="text-slate-800 text-2xl font-bold">Sleep</Text>
            </PanelSection>

            {/* Shorter Panels */}
            <View className="w-[40%] flex justify-center">
              <PanelSection className="flex-grow bg-cyan-300">
                <Text className="text-slate-800 text-2xl font-bold">Sleep</Text>
              </PanelSection>
              <PanelSection className="h-[50%] bg-fuchsia-300">
                <Text className="text-slate-800 text-2xl font-bold">Sleep</Text>
              </PanelSection>
            </View>
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
};

export default SleepScreen;
