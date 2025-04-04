// File: app/home/_layout.tsx
import React from "react";
import { Tabs } from "expo-router";
import { FontAwesome, MaterialCommunityIcons } from "@expo/vector-icons"; // Or your preferred icon set
import { Pressable, View, Text } from "react-native";

const Colors = {
  activeTint: "#000000", // Black color for active icon/text
  inactiveTint: "#FFFFFF", // White color for inactive icon/text
  // Background colors are now handled by NativeWind classes
};
// Helper function for cleaner icon rendering
function TabBarIcon(props: {
  name: React.ComponentProps<typeof MaterialCommunityIcons>["name"];
  color: string;
}) {
  return (
    <MaterialCommunityIcons size={28} style={{ marginBottom: -3 }} {...props} />
  );
}

export default function HomeTabLayout() {
  return (
    <Tabs
      screenOptions={({ route }) => ({
        headerShown: false, // Hide default header
        tabBarActiveTintColor: Colors.activeTint,
        tabBarInactiveTintColor: Colors.inactiveTint,
        tabBarStyle: {
          backgroundColor: "#121212", // Fallback if className on tabBarStyle doesn't work
          borderTopWidth: 0,
          height: 70,
          paddingLeft: 10,
          paddingRight: 10,
        },
        // Apply NativeWind classes to the label style
        tabBarLabelStyle: {
          fontWeight: "600",
          fontSize: 11,
          marginTop: -5,
          marginBottom: 5,
          // className: "font-semibold text-[11px] -mt-[5px] mb-[5px]", // Ideal NativeWind
        },
        tabBarButton: (props) => {
          const { children, onPress, accessibilityState } = props;
          const focused = accessibilityState?.selected ?? false;

          // Container Pressable - takes up full space
          return (
            <Pressable
              onPress={onPress}
              // Apply common container styles using NativeWind
              className="flex-1 justify-center items-center"
            >
              {/* Conditionally render the white background View */}
              {focused ? (
                <View
                  // Apply active "pill" styles using NativeWind
                  className="flex flex-row bg-white rounded-full px-4 py-2 justify-center items-center shadow shadow-black"
                  // Add elevation for Android if shadow isn't sufficient:
                  // style={{ elevation: 2 }} // Can mix className and style if needed
                >
                  {children}
                </View>
              ) : (
                // If not focused, render children directly within the Pressable
                children
              )}
            </Pressable>
          );
        },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: React.ComponentProps<
            typeof MaterialCommunityIcons
          >["name"];
          const iconSize = focused ? 26 : 24;

          // --- Match route.name to your file structure ---
          if (route.name === "index") {
            // Corresponds to app/home/index.tsx
            // Use home icon similar to the design's "Home" or "All Campaigns"
            iconName = focused ? "home-variant" : "home-variant-outline";
          } else if (route.name === "journey") {
            // Corresponds to app/home/journey/index.tsx
            // Use a map/route icon
            iconName = focused ? "map-marker-path" : "map-marker-path";
          } else if (route.name === "sleep/index") {
            // Corresponds to app/home/sleep/index.tsx
            // Use a moon/sleep icon
            iconName = focused
              ? "moon-waning-crescent"
              : "moon-waning-crescent";
          } else if (route.name === "account/index") {
            // Corresponds to app/home/account/index.tsx
            // Use an account/profile icon similar to the design's "Profile"
            iconName = focused ? "account-circle" : "account-circle-outline";
          } else {
            iconName = "help-circle"; // Fallback
          }

          return (
            <MaterialCommunityIcons
              name={iconName}
              size={iconSize}
              color={color}
            />
          );
        },
        // Use tabBarLabel function to apply NativeWind styling to the label Text
        tabBarLabel: ({ focused, color, children }) => {
          if (!focused) {
            return null;
          }
          return (
            <Text
              style={{ color }} // Apply active/inactive tint color
              className="font-light text-md  "
            >
              {children}
            </Text>
          );
        },
      })}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home", // Label for the tab
        }}
      />

      {/* Tab 2: Corresponds to app/home/journey/index.tsx */}
      <Tabs.Screen
        name="journey"
        options={{
          title: "Journey", // Label for the tab
        }}
      />

      {/* Tab 3: Corresponds to app/home/sleep/index.tsx */}
      <Tabs.Screen
        name="sleep/index"
        options={{
          title: "Sleep", // Label for the tab
        }}
      />

      {/* Tab 4: Corresponds to app/home/account/index.tsx */}
      <Tabs.Screen
        name="account/index"
        options={{
          title: "Account", // Label for the tab
        }}
      />
      {/* --- Home Tab --- */}
      {/* <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color }) => <TabBarIcon name="home" color={color} />,
        }}
      /> */}

      {/* Journey Tab */}
      {/* <Tabs.Screen
        name="journey/index"
        options={{
          title: "Journey",
          tabBarIcon: ({ color }) => <TabBarIcon name="map" color={color} />,
        }}
      /> */}

      {/* Sleep */}
      {/* <Tabs.Screen
        name="sleep/index"
        options={{
          title: "Sleep", // Title shown on the tab and header
          tabBarIcon: ({ color }) => <TabBarIcon name="sleep" color={color} />,
        }}
      /> */}

      {/* Account */}
      {/* <Tabs.Screen
        name="account/index"
        options={{
          title: "Account", // Title shown on the tab and header
          tabBarIcon: ({ color }) => (
            <TabBarIcon name="account" color={color} />
          ),
        }}
      /> */}
    </Tabs>
  );
}
