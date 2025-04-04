import { Stack } from "expo-router";

const Layout = () => {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{
          title: "Sleep Center",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="auto"
        options={{
          title: "AutoRecord",
          headerShown: false,
        }}
      />
      <Stack.Screen name="manual" options={{ headerShown: false }} />
      <Stack.Screen
        name="sleepTips"
        options={{
          title: "Sleep Tips",
          headerShown: true,
        }}
      />
    </Stack>
  );
};

export default Layout;
