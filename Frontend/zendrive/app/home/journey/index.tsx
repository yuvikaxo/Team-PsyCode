import React from "react";
import MapView from "react-native-maps";
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
} from "react-native";
import MapComponent from "../../components/map";
import { RefreshCcw, History } from "lucide-react-native";
import { useNavigation } from "expo-router";

const JourneyScreen = () => {
  const navigation = useNavigation();
  const handlePress = () => {
    navigation.navigate("results"); // Navigate to the results screen
  };
  return (
    <View className="flex-1 bg-slate-900">
      <SafeAreaView className="flex-1">
        <MapComponent>
          <View className="justify-end h-full">
            <View className="flex-row justify-end gap-5 mb-5 mr-5">
              <TouchableOpacity className="bg-lime-300 rounded-full w-[13%] py-3 flex justify-center items-center shadow-md shadow-black/50">
                <RefreshCcw size={25} color="black" />
              </TouchableOpacity>
              <TouchableOpacity
                className="bg-orange-300 rounded-full w-[13%] py-3 flex justify-center items-center shadow-md shadow-black/50"
                onPress={handlePress}
              >
                <History size={25} color="black" />
              </TouchableOpacity>
            </View>
          </View>
        </MapComponent>
      </SafeAreaView>
    </View>
  );
};

export default JourneyScreen;
