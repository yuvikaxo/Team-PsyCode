import React from "react";
import { View, Text, StyleSheet, SafeAreaView, Image } from "react-native";
import HorizontalSection from "../../components/HorizontalSection";
import PanelSection from "../../components/PanelSection";
import { useNavigation } from "expo-router";
import HeadingText from "../../components/HeadingText";

const SleepScreen = () => {
  const navigation = useNavigation();
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
            <PanelSection
              className=" flex-grow bg-emerald-300 max-w-[60%]"
              onPressEvent={() => {
                navigation.navigate("manual");
              }}
            >
              <Text className="text-slate-800 text-2xl font-bold">
                Manual Sleep Traking
              </Text>
              <View className="flex-grow">
                <Image
                  source={require("../../../assets/images/PanelSymbols/note.png")}
                  resizeMode="contain"
                  className="flex-1 w-full"
                />
              </View>
            </PanelSection>

            {/* Shorter Panels */}
            <View className="w-[40%] flex justify-center">
              <PanelSection
                className="flex-grow bg-cyan-300"
                onPressEvent={() => {
                  navigation.navigate("auto");
                }}
              >
                <Text className="text-slate-800 text-2xl font-bold">
                  Auto Tracking
                </Text>
                <View className="flex-grow">
                  <Image
                    source={require("../../../assets/images/PanelSymbols/record.png")}
                    resizeMode="contain"
                    className="flex-1 w-full"
                  />
                </View>
              </PanelSection>
              <PanelSection
                className="h-[50%] bg-fuchsia-300"
                onPressEvent={() => {
                  navigation.navigate("sleepTips");
                }}
              >
                <Text className="text-slate-800 text-2xl font-bold">
                  Sleep Tips
                </Text>
                <View className="flex-grow">
                  <Image
                    source={require("../../../assets/images/PanelSymbols/bulb.png")}
                    resizeMode="contain"
                    className="flex-1 w-full"
                  />
                </View>
              </PanelSection>
            </View>
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
};

export default SleepScreen;
