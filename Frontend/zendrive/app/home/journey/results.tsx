import React from "react";
import { View, Text, StyleSheet, SafeAreaView, ScrollView } from "react-native";
import PanelSection from "../../components/PanelSection";
import SubHeadingText from "../../components/SubHeadingText";

const colorMap: Record<string, string> = {
  "lime-300": "#D9F99D",
  "amber-300": "#FDE68A",
  "rose-300": "#FCA5A5",
  "sky-300": "#7DD3FC",
  "emerald-300": "#6EE7B7",
  "violet-300": "#C4B5FD",
};

const SearchEntry: React.FC<{
  location: string;
  score: number;
  color: string;
}> = ({ location, score, color }) => {
  return (
    <PanelSection
      style={{ backgroundColor: colorMap[color] }}
      className={`w-full`}
    >
      <Text className="text-2xl font-semibold">{location}</Text>
      <Text className="text-xl text-center mt-3">Sleep Score: {score}</Text>
    </PanelSection>
  );
};

const colorRotation = [
  "lime-300",
  "amber-300",
  "rose-300",
  "sky-300",
  "emerald-300",
  "violet-300",
];

const SearchHistoryData = [
  { location: "Kolkata, West Bengal", score: 85 },
  { location: "Chandni Chawk, Delhi", score: 90 },
  { location: "India Gate, Delhi", score: 75 },
  { location: "Hyderabad, Telangana", score: 80 },
  { location: "Hyderabad, Telangana", score: 80 },
  { location: "Hyderabad, Telangana", score: 80 },
];

const ResultsScreen = () => {
  return (
    <SafeAreaView className="bg-slate-900">
      <SubHeadingText>Search History</SubHeadingText>
      <View className="mx-4"></View>

      <ScrollView>
        <View className="flex-row flex-wrap justify-between mx-4 mt-2 mb-10">
          {SearchHistoryData.map((entry, index) => (
            <SearchEntry
              key={index}
              location={entry.location}
              score={entry.score}
              color={colorRotation[index % colorRotation.length]}
            />
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

export default ResultsScreen;
