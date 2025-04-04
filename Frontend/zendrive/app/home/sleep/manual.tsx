import React, { useState } from "react";
import {
  View, // Use standard View
  Text, // Use standard Text
  TextInput, // Use standard TextInput
  TouchableOpacity, // Use standard TouchableOpacity
  ScrollView, // Use standard ScrollView
  Platform,
  ActivityIndicator,
  Alert,
  Keyboard,
  SafeAreaView, // Use standard SafeAreaView
} from "react-native";
// No need to import from react-native-safe-area-context unless specifically preferred
import DateTimePicker, {
  DateTimePickerEvent,
} from "@react-native-community/datetimepicker";

// --- Placeholder for your API functions ---
// Replace with your actual API call logic
const API_URL = "YOUR_BACKEND_API_URL"; // e.g., http://192.168.1.100:3001

async function saveSleepDataApi(userId: string, sleepData: any) {
  console.log(`Sending to ${API_URL}/api/users/${userId}/sleep`, sleepData);
  try {
    const response = await fetch(`${API_URL}/api/users/${userId}/sleep`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sleepData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.message || `HTTP error! status: ${response.status}`
      );
    }
    const result = await response.json();
    console.log("API Success:", result);
    return result;
  } catch (error) {
    console.error("API Error saving sleep data:", error);
    throw error;
  }
}
// ----------------------------------------

// --- Mock User ID (Replace with actual logic) ---
const MOCK_USER_ID = "REPLACE_WITH_ACTUAL_USER_ID";
// ----------------------------------------

const ManualSleepEntryScreen: React.FC = () => {
  // --- State Variables (same as before) ---
  const [remSleep, setRemSleep] = useState("");
  const [deepSleep, setDeepSleep] = useState("");
  const [lightSleep, setLightSleep] = useState("");
  const [totalDuration, setTotalDuration] = useState("");
  const [sleepTime, setSleepTime] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // --- DateTimePicker Handler (same as before) ---
  const onDateChange = (event: DateTimePickerEvent, selectedDate?: Date) => {
    const currentDate = selectedDate || sleepTime;
    // Hiding picker is usually handled differently per platform by the picker itself
    // For simplicity, we'll hide it manually on selection, may need adjustment
    setShowDatePicker(false); // Hide after selection/dismiss
    setSleepTime(currentDate);
    console.log("Date selected:", currentDate);
  };

  // --- Form Submission Handler (same as before) ---
  const handleSubmit = async () => {
    Keyboard.dismiss();
    setErrorMessage(null);

    // Validation
    if (
      !remSleep ||
      !deepSleep ||
      !lightSleep ||
      !totalDuration ||
      !sleepTime
    ) {
      setErrorMessage("Please fill in all fields.");
      return;
    }
    const remNum = parseFloat(remSleep);
    const deepNum = parseFloat(deepSleep);
    const lightNum = parseFloat(lightSleep);
    const durationNum = parseFloat(totalDuration);
    if (
      isNaN(remNum) ||
      isNaN(deepNum) ||
      isNaN(lightNum) ||
      isNaN(durationNum)
    ) {
      setErrorMessage("Sleep percentages and duration must be numbers.");
      return;
    }

    const sleepDataPayload = {
      remSleepPercentage: remNum,
      deepSleepPercentage: deepNum,
      lightSleep: lightNum,
      totalSleepDuration: durationNum,
      timeOfSleep: sleepTime.toISOString(),
    };

    // API Call
    setIsLoading(true);
    try {
      await saveSleepDataApi(MOCK_USER_ID, sleepDataPayload);
      setIsLoading(false);
      Alert.alert("Success", "Sleep data saved!");
      setRemSleep("");
      setDeepSleep("");
      setLightSleep("");
      setTotalDuration("");
      setSleepTime(new Date());
      // navigation.goBack();
    } catch (error: any) {
      setIsLoading(false);
      setErrorMessage(error.message || "An unexpected error occurred.");
      Alert.alert("Error", error.message || "Failed to save sleep data.");
    }
  };

  return (
    // Use standard View with className
    <View className="flex-1 bg-slate-900">
      <SafeAreaView className="flex-1">
        {/* Use standard ScrollView with className */}
        <ScrollView
          className="flex-1 px-5 pt-5"
          keyboardShouldPersistTaps="handled"
        >
          {/* Heading */}
          <Text className="text-white text-3xl font-bold mb-8 text-center">
            Log Sleep Manually
          </Text>

          {/* --- Form Fields --- */}

          {/* REM Sleep */}
          <View className="mb-4">
            <Text className="text-gray-300 text-sm font-medium mb-1">
              REM Sleep (%)
            </Text>
            <TextInput // Standard TextInput
              className="bg-slate-700 border border-slate-600 text-white text-base rounded-lg p-3 w-full"
              placeholder="e.g., 20"
              placeholderTextColor="#9ca3af"
              keyboardType="numeric"
              value={remSleep}
              onChangeText={setRemSleep}
            />
          </View>

          {/* Deep Sleep */}
          <View className="mb-4">
            <Text className="text-gray-300 text-sm font-medium mb-1">
              Deep Sleep (%)
            </Text>
            <TextInput // Standard TextInput
              className="bg-slate-700 border border-slate-600 text-white text-base rounded-lg p-3 w-full"
              placeholder="e.g., 25"
              placeholderTextColor="#9ca3af"
              keyboardType="numeric"
              value={deepSleep}
              onChangeText={setDeepSleep}
            />
          </View>

          {/* Light Sleep */}
          <View className="mb-4">
            <Text className="text-gray-300 text-sm font-medium mb-1">
              Light Sleep (%)
            </Text>
            <TextInput // Standard TextInput
              className="bg-slate-700 border border-slate-600 text-white text-base rounded-lg p-3 w-full"
              placeholder="e.g., 55"
              placeholderTextColor="#9ca3af"
              keyboardType="numeric"
              value={lightSleep}
              onChangeText={setLightSleep}
            />
          </View>

          {/* Total Duration */}
          <View className="mb-4">
            <Text className="text-gray-300 text-sm font-medium mb-1">
              Total Sleep Duration (Hours)
            </Text>
            <TextInput // Standard TextInput
              className="bg-slate-700 border border-slate-600 text-white text-base rounded-lg p-3 w-full"
              placeholder="e.g., 7.5"
              placeholderTextColor="#9ca3af"
              keyboardType="numeric"
              value={totalDuration}
              onChangeText={setTotalDuration}
            />
          </View>

          {/* Time of Sleep */}
          <View className="mb-6">
            <Text className="text-gray-300 text-sm font-medium mb-1">
              Time Sleep Started
            </Text>
            <TouchableOpacity // Standard TouchableOpacity
              className="bg-slate-700 border border-slate-600 rounded-lg p-3 w-full flex-row justify-between items-center"
              onPress={() => setShowDatePicker(true)}
            >
              <Text className="text-white text-base">
                {sleepTime.toLocaleString()}
              </Text>
              <Text className="text-blue-400 text-base">Change</Text>
            </TouchableOpacity>
            {/* DateTimePicker remains the same - it's not a standard RN component */}
            {showDatePicker && (
              <DateTimePicker
                testID="dateTimePicker"
                value={sleepTime}
                mode={"datetime"}
                display="default"
                onChange={onDateChange}
              />
            )}
          </View>

          {/* Error Message Display */}
          {errorMessage && (
            <Text className="text-red-500 text-center mb-4">
              {errorMessage}
            </Text>
          )}

          {/* Submit Button */}
          <TouchableOpacity // Standard TouchableOpacity
            className={`bg-blue-600 rounded-lg py-3 px-5 mb-10 ${
              isLoading ? "opacity-50" : ""
            }`}
            onPress={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text className="text-white text-lg font-semibold text-center">
                Save Sleep Data
              </Text>
            )}
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
};

export default ManualSleepEntryScreen;
