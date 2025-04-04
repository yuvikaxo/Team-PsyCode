import { MapPin, RefreshCcw, Search, X } from "lucide-react-native";
import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  View,
  Alert,
  Text,
  TouchableOpacity,
  TextInput,
  Modal,
  useColorScheme,
} from "react-native";
import MapView, { Polyline, Marker, UrlTile } from "react-native-maps";

const ORIGIN = { latitude: 28.855393, longitude: 78.771284 };
const DESTINATION = { latitude: 28.853282, longitude: 78.773299 };
const GRAPH_HOPPER_API_KEY = "b43ba286-2b19-46c3-8066-4bf24159527f";

const darkMapStyle = [
  {
    elementType: "geometry",
    stylers: [{ color: "#212121" }],
  },
  {
    elementType: "labels.text.fill",
    stylers: [{ color: "#ffffff" }],
  },
  {
    elementType: "labels.text.stroke",
    stylers: [{ color: "#212121" }],
  },
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#373737" }],
  },
];

const MapComponent = ({ children }) => {
  const [currentLocation, setCurrentLocation] = useState(ORIGIN);
  const [destination, setDestination] = useState(DESTINATION);
  const [routeCoords, setRouteCoords] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    if (destination) {
      getRoute(currentLocation, destination);
    }
  }, [destination]);

  const getRoute = async (origin, dest) => {
    // try {
    //   const url = `http://172.16.1.116:3000/maps/route?originLat=${origin.latitude}&originLon=${origin.longitude}&endpointLat=${dest.latitude}&endpointLon=${dest.longitude}`;
    //   const response = await fetch(url);
    //   const data = await response.json();
    //   if (data.route.length > 0) {
    //     setRouteCoords(data.route);
    //   } else {
    //     console.warn("No route found!");
    //   }
    // } catch (error) {
    //   console.error("Error fetching route:", error);
    // }
  };

  const geocodeSearch = async () => {
    // const encodedQuery = encodeURIComponent(searchQuery);
    // const url = `https://graphhopper.com/api/1/geocode?q=${encodedQuery}&key=${GRAPH_HOPPER_API_KEY}`;
    // try {
    //   const response = await fetch(url);
    //   const data = await response.json();
    //   if (data.hits && data.hits.length > 0) {
    //     const { lat, lng } = data.hits[0].point;
    //     setDestination({ latitude: lat, longitude: lng });
    //   } else {
    //     Alert.alert("Location not found");
    //   }
    // } catch (error) {
    //   console.error("Error in geocoding:", error);
    // }
  };

  return (
    <View className="flex-1 relative">
      {/* Search Bar */}
      <View className="px-4 pb-3">
        <View className="flex-row items-center bg-gray-200 rounded-full px-4 py-2">
          <TextInput
            className="flex-1 mr-2"
            placeholder="Search for a place"
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={geocodeSearch}
          />
          <Search color="#999999" size={20} />
        </View>
      </View>

      {/* Map View */}
      <MapView
        style={{ flex: 1 }}
        initialRegion={{
          latitude: ORIGIN.latitude,
          longitude: ORIGIN.longitude,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
        customMapStyle={darkMapStyle}
      >
        <UrlTile
          urlTemplate="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maximumZ={19}
        />
        <Marker coordinate={ORIGIN} title="Start" />
        <Marker coordinate={destination} title="End" />
        {routeCoords.length > 0 && (
          <Polyline
            coordinates={routeCoords}
            strokeColor="#000"
            strokeWidth={6}
          />
        )}

        {children}
      </MapView>

      {/* Popup Modal */}
      <Modal transparent={true} visible={modalVisible} animationType="slide">
        <View className="flex-1 justify-center items-center bg-black/50">
          <View className="bg-white p-6 rounded-lg w-80">
            <Text className="text-lg font-semibold mb-2">Location Details</Text>

            <View className="flex-row justify-between mt-4">
              <TouchableOpacity
                className="bg-blue-500 px-4 py-2 rounded-lg"
                onPress={() => setModalVisible(false)}
              >
                <Text className="text-white">Close</Text>
              </TouchableOpacity>
              <TouchableOpacity
                className="bg-green-500 px-4 py-2 rounded-lg"
                onPress={() => {
                  setModalVisible(false);
                  getRoute(currentLocation, destination);
                }}
              >
                <Text className="text-white">Go To</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

export default MapComponent;
