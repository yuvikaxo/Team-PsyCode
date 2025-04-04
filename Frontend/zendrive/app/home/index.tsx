import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  StatusBar,
  Image,
} from "react-native";
import PanelSection from "../components/PanelSection";
import HorizontalSection from "../components/HorizontalSection";
import HeadingText from "../components/HeadingText";

const HomeScreen = () => {
  return (
    <SafeAreaView className="bg-slate-900 h-screen flex">
      {/* Name Section */}
      <View className=" py-8">
        <HeadingText>Hi, Tomas</HeadingText>
      </View>

      {/* Grid View */}
      <View className="h-[72%] flex flex-col px-2 my-2">
        {/* Notification */}
        <HorizontalSection className="bg-slate-100" name="Notifications" />

        {/* Top Panal */}
        <PanelSection className="w-full h-[40%] bg-orange-300">
          <Text className="text-slate-900 text-2xl font-semibold">
            Heart Rate Monitor
          </Text>
          <View className="flex-grow bg-slate-50 my-2" />
        </PanelSection>

        <View className="flex-grow flex flex-row  gap-2">
          <PanelSection className="flex-grow  bg-cyan-300 max-w-[50%]">
            <Text className="text-slate-900 text-2xl font-semibold">
              Plan Your Journey
            </Text>
          </PanelSection>
          <PanelSection className="flex-grow  bg-teal-300 ">
            <Text className="text-slate-900 text-2xl font-semibold">
              Sleep History
            </Text>
          </PanelSection>
        </View>
      </View>

      {/* Alert Testing */}
      <HorizontalSection className="bg-slate-100" name="Alert Testing" />
    </SafeAreaView>
  );
};

export default HomeScreen;
