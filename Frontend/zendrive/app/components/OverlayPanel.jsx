import React from "react";
import { View, Text, Button, TouchableHighlight } from "react-native";

const OverlayPanel = ({ isVisible, onClose, title = "Panel", children }) => {
  if (!isVisible) {
    return null;
  }

  return (
    <View className="absolute top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <View className="absolute w-[90%] py-5 px-5 py-2 bg-slate-100 rounded-lg mx-auto">
        <Text className="text-4xl text-center mt-5 font-semibold">{title}</Text>
        <TouchableHighlight onPress={onClose}>
          <Text className="text-red-800 text-center text-lg mt-1">
            Close Panel
          </Text>
        </TouchableHighlight>
        <View className="flex-grow ">{children}</View>
      </View>
    </View>
  );
};

export default OverlayPanel;
