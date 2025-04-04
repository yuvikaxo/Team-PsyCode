import React from "react";
import {
  TouchableOpacity,
  View,
  Text,
  StyleProp,
  ViewStyle,
} from "react-native";

interface PanelSectionProps {
  className?: string;
  children?: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}

const PanelSection: React.FC<PanelSectionProps> = ({
  className,
  children,
  style,
}) => {
  return (
    <TouchableOpacity
      className={`flex rounded-[10%] mb-4 py-4 px-8 ${className}`}
      style={style}
    >
      <View className="flex-grow">{children}</View>
      <View className="flex-row justify-end">
        <Text className="text-slate-900 text-2xl font-semibold">{"-->"}</Text>
      </View>
    </TouchableOpacity>
  );
};

export default PanelSection;
