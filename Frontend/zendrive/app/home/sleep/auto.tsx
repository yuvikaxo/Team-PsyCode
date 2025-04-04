import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Animated,
  StyleSheet,
  Platform,
  AppState,
  Dimensions,
  SafeAreaView,
  Button,
} from "react-native";
import { Audio, InterruptionModeIOS, InterruptionModeAndroid } from "expo-av";
import OverlayPanel from "../../components/OverlayPanel"; // Adjust the import path as needed

// --- Configuration ---
const AUDIO_UPDATE_INTERVAL_MS = 100; // How often to check audio level (milliseconds)
const BASE_SCALE = 1.0; // Scale when silent
const MAX_SCALE = 2.0; // Max scale for loud sound
const MIN_DBFS = -60.0; // Assumed minimum dBFS for silence (adjust based on testing)
const MAX_DBFS = 0.0; // Maximum possible dBFS

const { width } = Dimensions.get("window");

const AutoScreen: React.FC = () => {
  // --- Refs ---
  const recordingRef = useRef<Audio.Recording | undefined>(undefined); // Use Ref for the recording object
  const scaleAnim = useRef(new Animated.Value(BASE_SCALE)).current; // Ref for animation value
  const meterInterval = useRef<NodeJS.Timeout | null>(null); // Ref for the interval ID

  // --- State (for UI updates) ---
  const [permissionResponse, requestPermission] = Audio.usePermissions();
  const [isRecording, setIsRecording] = useState(false); // Does affect button appearance/text
  const [recordingUri, setRecordingUri] = useState<string | null>(null); // Does affect displayed text
  const [statusMessage, setStatusMessage] = useState<string>(
    "Press circle to record"
  ); // Does affect displayed text

  const [isPanelVisible, setIsPanelVisible] = useState(false); // State for overlay panel visibility

  // --- Animation/Audio Level Update Function ---
  const updateAudioScale = async () => {
    const currentRecording = recordingRef.current; // Get current value from ref

    if (!currentRecording) {
      // If interval is still running but ref is cleared, stop the interval
      if (meterInterval.current) {
        clearInterval(meterInterval.current);
        meterInterval.current = null;
        // Animate back to base if unexpectedly stopped
        Animated.timing(scaleAnim, {
          toValue: BASE_SCALE,
          duration: 300,
          useNativeDriver: true,
        }).start();
      }
      return;
    }

    try {
      const status = await currentRecording.getStatusAsync();

      if (status.isRecording && status.metering !== undefined) {
        // Map dBFS to scale
        const dbfs = status.metering;
        const clampedDbfs = Math.max(MIN_DBFS, Math.min(MAX_DBFS, dbfs));
        const normalizedLevel =
          (clampedDbfs - MIN_DBFS) / (MAX_DBFS - MIN_DBFS);
        const targetScale =
          BASE_SCALE + normalizedLevel * (MAX_SCALE - BASE_SCALE);
        const clampedScale = Math.max(
          BASE_SCALE,
          Math.min(MAX_SCALE, targetScale)
        );

        // Animate scale
        Animated.spring(scaleAnim, {
          toValue: clampedScale,
          useNativeDriver: true,
        }).start();
      } else if (!status.isRecording && isRecording) {
        // Status says not recording, but UI thinks it is. Force stop.
        console.warn(
          "Recording status mismatch detected in updateAudioScale. Stopping."
        );
        await stopRecording(); // Ensure stopRecording cleans up ref and interval
      }
    } catch (error) {
      console.error("Error getting recording status:", error);
      // Stop interval and reset state on error getting status
      if (meterInterval.current) {
        clearInterval(meterInterval.current);
        meterInterval.current = null;
      }
      Animated.timing(scaleAnim, {
        toValue: BASE_SCALE,
        duration: 300,
        useNativeDriver: true,
      }).start();
      setIsRecording(false);
      setStatusMessage("Error during recording update");
      recordingRef.current = undefined; // Clear the ref
    }
  };

  // --- useEffect for Initial Setup and Cleanup ---
  useEffect(() => {
    // Configure audio session settings
    const configureAudio = async () => {
      try {
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: true,
          playsInSilentModeIOS: true,
          interruptionModeIOS: InterruptionModeIOS.DoNotMix,
          shouldDuckAndroid: true,
          interruptionModeAndroid: InterruptionModeAndroid.DoNotMix,
          playThroughEarpieceAndroid: false,
        });
        console.log("Audio mode configured.");
      } catch (error) {
        console.error("Error setting audio mode", error);
      }
      // Request permission if needed
      if (!permissionResponse || permissionResponse.status === "undetermined") {
        console.log("Requesting microphone permission...");
        requestPermission();
      }
    };
    configureAudio();

    // Handle app going to background/inactive
    const handleAppStateChange = async (nextAppState: string) => {
      if (nextAppState.match(/inactive|background/) && recordingRef.current) {
        console.log(
          "App state changed to inactive/background, stopping recording..."
        );
        await stopRecording(); // Use the function that handles ref and interval cleanup
      }
    };
    const subscription = AppState.addEventListener(
      "change",
      handleAppStateChange
    );

    // Cleanup function when component unmounts
    return () => {
      console.log("Component unmounting...");
      subscription.remove(); // Remove listener

      // Stop and unload any active recording
      if (recordingRef.current) {
        console.log("Unloading recording on unmount...");
        // Use fire-and-forget, as component is disappearing
        recordingRef.current
          .stopAndUnloadAsync()
          .catch((e) => console.error("Error unloading on unmount:", e));
        recordingRef.current = undefined;
      }
      // Clear any active interval
      if (meterInterval.current) {
        console.log("Clearing meter interval on unmount.");
        clearInterval(meterInterval.current);
        meterInterval.current = null;
      }
    };
  }, [permissionResponse, requestPermission]); // Depend only on permission hook values

  // --- Recording Start Function ---
  async function startRecording() {
    try {
      // Check/Request Permissions
      const currentPermissions = await Audio.getPermissionsAsync();
      if (!currentPermissions.granted) {
        const permission = await Audio.requestPermissionsAsync();
        if (!permission.granted) {
          setStatusMessage("Microphone permission is required!");
          return; // Exit if permission denied
        }
      }

      // --- Prepare for Recording ---
      setStatusMessage("Recording...");
      setRecordingUri(null); // Clear previous URI
      setIsRecording(true); // Update UI state
      scaleAnim.setValue(BASE_SCALE); // Reset animation scale

      // Set audio mode specifically for recording
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log("Starting recording preparation...");
      // Create the recording object
      const { recording: newRecording } = await Audio.Recording.createAsync({
        ...Audio.RecordingOptionsPresets.HIGH_QUALITY,
        isMeteringEnabled: true, // Enable audio level measurement
      });

      // --- Store Recording Object and Start Metering ---
      recordingRef.current = newRecording; // Store in the ref
      console.log("Recording started and ref set.");

      // Clear any old interval before starting a new one
      if (meterInterval.current) clearInterval(meterInterval.current);
      // Start polling audio levels
      meterInterval.current = setInterval(
        updateAudioScale,
        AUDIO_UPDATE_INTERVAL_MS
      );
      console.log("Audio level metering started.");
    } catch (err) {
      console.error("Failed to start recording", err);
      setStatusMessage("Failed to start recording");
      setIsRecording(false); // Reset UI
      // Ensure interval is cleared on error
      if (meterInterval.current) {
        clearInterval(meterInterval.current);
        meterInterval.current = null;
      }
      // Reset animation scale on error
      Animated.timing(scaleAnim, {
        toValue: BASE_SCALE,
        duration: 300,
        useNativeDriver: true,
      }).start();
      recordingRef.current = undefined; // Clear ref on error
    }
  }

  // --- Recording Stop Function ---
  async function stopRecording() {
    console.log("Stop recording requested...");

    // --- Stop Metering Interval FIRST ---
    if (meterInterval.current) {
      clearInterval(meterInterval.current);
      meterInterval.current = null;
      console.log("Audio level metering stopped.");
    }

    // --- Get current recording object from ref ---
    const currentRecording = recordingRef.current;

    // --- Reset UI State and Animation ---
    setIsRecording(false);
    Animated.timing(scaleAnim, {
      toValue: BASE_SCALE,
      duration: 300, // Quick reset animation
      useNativeDriver: true,
    }).start();

    // Check if we actually have a recording object to stop
    if (!currentRecording) {
      console.log("Stop called, but no active recording reference found.");
      // Ensure status message is reasonable if called unexpectedly
      if (statusMessage === "Recording...")
        setStatusMessage("Press circle to record");
      return;
    }

    setStatusMessage("Processing recording...");

    // --- Clear the ref BEFORE async operations ---
    // This prevents potential race conditions or using a stale object if stop/unload fails
    recordingRef.current = undefined;
    console.log("Recording ref cleared.");

    try {
      // --- Stop and Unload the Recording ---
      console.log("Awaiting stop and unload...");
      await currentRecording.stopAndUnloadAsync();

      // --- Optionally reset audio mode ---
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false }); // Disallow recording after stopping

      // --- Get and Store URI ---
      const uri = currentRecording.getURI();
      setRecordingUri(uri); // Update UI state with URI
      console.log("Recording stopped and stored at", uri);
      setStatusMessage(`Recording saved!`);
    } catch (error) {
      console.error("Failed to stop or unload recording", error);
      setStatusMessage("Failed to save recording");
      setRecordingUri(null); // Clear URI display on error
      // recordingRef is already cleared
    }

    setIsPanelVisible(true);
  }

  // --- Button Handler ---
  const onPressHandler = isRecording ? stopRecording : startRecording;

  // --- Render Logic ---
  // Handle permission denied state
  if (
    permissionResponse &&
    !permissionResponse.granted &&
    permissionResponse.status !== "undetermined"
  ) {
    return (
      <View style={styles.container}>
        <Text style={styles.permissionText}>
          Microphone permission is required. Please enable it in your device
          settings.
        </Text>
      </View>
    );
  }

  // Main recorder UI
  return (
    <View className="flex-1 bg-slate-500">
      <SafeAreaView className="flex-1 justify-center items-center bg-slate-900">
        <Text className="text-white mb-5 text-5xl font-thin text-center">
          Sleep Recorder
        </Text>
        <Text className="text-white mt-4 text-2xl font-mono tracki">
          {statusMessage}
        </Text>

        <View className="w-[160px] h-[160px] justify-center items-center mt-3">
          {/* Outer animated circle */}
          <Animated.View
            className="absolute rounded-full border-2 border-blue-400 opacity-50"
            style={[
              styles.outerCircleBase,
              { transform: [{ scale: scaleAnim }] }, // Apply scale animation
            ]}
          />
          {/* Inner button circle */}
          <TouchableOpacity
            className="absolute rounded-full justify-center items-center"
            style={[
              styles.innerCircleButton,
              isRecording
                ? styles.innerCircleRecording
                : styles.innerCircleIdle, // Change color
              !permissionResponse?.granted && styles.buttonDisabled, // Dim if no permission
            ]}
            onPress={onPressHandler}
            disabled={!permissionResponse?.granted} // Disable if no permission
          >
            <Text className="text-white">
              {isRecording ? "Stop" : "Record"}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Display saved recording URI */}
        {recordingUri && (
          <Text selectable={true} className="text-white mt-20 px-2 opacity-80">
            Saved to: {recordingUri}
          </Text>
        )}
      </SafeAreaView>
      <OverlayPanel
        isVisible={isPanelVisible}
        onClose={() => {
          setIsPanelVisible(false);
        }}
        title="Sleep Stats"
      >
        <View className="flex gap-2 mt-10">
          <View className="justify-between flex flex-row">
            <Text className="text-xl">Age : </Text>
            <Text className="text-xl">25</Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl">Total Duration (hr): </Text>
            <Text className="text-xl">8</Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl">Sleep Efficiency %: </Text>
            <Text className="text-xl">85</Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl">Deep Sleep %: </Text>
            <Text className="text-xl">10</Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl">REM Sleep %: </Text>
            <Text className="text-xl">30</Text>
          </View>{" "}
          <View className="justify-between flex flex-row">
            <Text className="text-xl">Light Sleep %: </Text>
            <Text className="text-xl">60</Text>
          </View>
        </View>
      </OverlayPanel>
    </View>
  );
};

// --- StyleSheet --- (Same as before)
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a", // slate-900
    justifyContent: "center",
    alignItems: "center",
  },
  safeArea: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    width: "100%",
  },
  statusText: {
    color: "white",
    fontSize: 20,
    marginBottom: 40,
    paddingHorizontal: 16,
    textAlign: "center",
  },
  circleContainer: {
    width: 160,
    height: 160,
    justifyContent: "center",
    alignItems: "center",
  },
  outerCircleBase: {
    position: "absolute",
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: "#60a5fa", // blue-400
    opacity: 0.5,
  },
  innerCircleButton: {
    width: 96,
    height: 96,
    borderRadius: 48,
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  innerCircleIdle: {
    backgroundColor: "#ef4444", // red-500
  },
  innerCircleRecording: {
    backgroundColor: "#dc2626", // red-600
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 18,
  },
  uriText: {
    color: "#9ca3af", // gray-400
    marginTop: 40,
    paddingHorizontal: 16,
    textAlign: "center",
    fontSize: 12,
  },
  permissionText: {
    color: "white",
    textAlign: "center",
    fontSize: 18,
    padding: 20,
  },
});

export default AutoScreen;
