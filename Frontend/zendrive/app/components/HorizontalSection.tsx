import React from "react";
import { TouchableOpacity, View, Text } from "react-native";

interface HorizontalSectionProps {
  name: string;
  className?: string;
  children?: React.ReactNode;
}

const HorizontalSection: React.FC<HorizontalSectionProps> = ({
  name,
  className,
  children,
}) => {
  return (
    <TouchableOpacity className="flex flex-row justify-between items-center mb-4 px-8 py-3 rounded-full bg-slate-200">
      <Text className="text-slate-900 text-lg font-semibold">{name}</Text>
      <View>
        <Text className="text-xl">{"-->"}</Text>
      </View>
    </TouchableOpacity>
  );
};

export default HorizontalSection;
