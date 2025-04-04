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
import { useNavigation } from "expo-router";

const HomeScreen = () => {
  const navigation = useNavigation();
  return (
    <SafeAreaView className="bg-slate-900 h-screen flex">
      {/* Name Section */}
      <View className=" py-8">
        <HeadingText>Hey there, Deliah</HeadingText>
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
          {/* <View className="flex-grow bg-slate-50 my-2" /> */}
          <Image
            source={require("../../assets/images/PanelSymbols/heartbeat.png")}
            className="w-[90%] h-[80%] text-center justify-center items-center mx-auto"
          />
        </PanelSection>

        <View className="flex-grow flex flex-row  gap-2">
          <PanelSection
            className="flex-grow  bg-cyan-300 max-w-[50%]"
            onPressEvent={() => {
              navigation.navigate("journey");
            }}
          >
            <Text className="text-slate-900 text-2xl font-semibold">
              Plan Your Journey
            </Text>
            <View className="flex-grow">
              <Image
                source={require("../../assets/images/PanelSymbols/car.png")}
                resizeMode="contain"
                className="flex-1 w-full"
              />
            </View>
          </PanelSection>
          <PanelSection
            className="flex-grow  bg-teal-300 "
            onPressEvent={() => {
              console.log("Hello");
              navigation.navigate("sleep");
            }}
          >
            <Text className="text-slate-900 text-2xl font-semibold">
              Sleep History
            </Text>
            <View className="flex-grow">
              <Image
                source={require("../../assets/images/PanelSymbols/sleep.png")}
                resizeMode="contain"
                className="flex-1 w-full"
              />
            </View>
          </PanelSection>
        </View>
      </View>

      {/* Alert Testing */}
      <HorizontalSection className="bg-slate-100" name="Alert Testing" />
    </SafeAreaView>
  );
};

export default HomeScreen;
