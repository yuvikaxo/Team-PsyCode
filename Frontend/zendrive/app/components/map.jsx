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
import PanelSection from "./PanelSection";
import OverlayPanel from "./OverlayPanel";

const StartCoord = { latitude: 28.855393, longitude: 78.771284 };

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
  const [currentLocation, setCurrentLocation] = useState(StartCoord);
  const [destinationCoord, setDestinationCoord] = useState();
  const [routeCoords, setRouteCoords] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [modalVisible, setModalVisible] = useState(false);
  const [routeDetails, setRouteDetails] = useState({
    distance: 10,
    duration: 20,
    start_place: "Sector 125 Noida, Uttar Pradesh",
    end_place: "Palwal, Haryana",
    tdo: 10,
    tdo_loc: null,
  });

  useEffect(() => {
    // if (destinationCoord) {
    //   getRoute(currentLocation, destinationCoord);
    // }
  }, []);

  const getRoute = async (start_place, end_place) => {
    try {
      const url = `http://192.168.228.212:8000/getRoute`;
      const reqBody = {
        start_place,
        end_place,
      };
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(reqBody),
      });

      const data = await response.json();

      if (data.routeCoordinates.length > 0) {
        setRouteDetails({
          start_place: data.start_place,
          end_place: data.end_place,
          start_coord: data.start_coord,
          end_coord: data.end_coord,
          distance: data.distance,
          duration: data.duration,
          tdo: data.tdo,
          tdo_loc: data.tdo_loc,
        });

        setRouteCoords(data.routeCoordinates);
      } else {
        console.warn("No route found!");
      }
    } catch (error) {
      console.error("Error fetching route:", error);
    }
  };

  const handleSearchSubmit = async () => {
    if (searchQuery.trim() === "") {
      Alert.alert("Please enter a location to search.");
      return;
    }

    try {
      await getRoute(routeDetails.start_place, searchQuery); // Call the getRoute function with the search query as destination
      setModalVisible(true);
      setSearchQuery("");
    } catch (e) {
      console.error("Error in fetching route:", e);
    }
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
            onSubmitEditing={handleSearchSubmit}
          />
          <Search color="#999999" size={20} />
        </View>
      </View>

      {/* Map View */}
      <MapView
        style={{ flex: 1 }}
        initialRegion={{
          latitude: StartCoord.latitude,
          longitude: StartCoord.longitude,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
        customMapStyle={darkMapStyle}
      >
        <UrlTile
          urlTemplate="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maximumZ={19}
        />
        {/* <Marker coordinate={ORIGIN} title="Start" />
        <Marker coordinate={destination} title="End" /> */}
        {routeCoords.length > 0 && (
          <Polyline
            coordinates={routeCoords}
            strokeColor="#000"
            strokeWidth={6}
          />
        )}

        {children}
      </MapView>

      {/* PopUp */}
      <OverlayPanel
        title="Destination Details"
        isVisible={modalVisible}
        onClose={() => {
          setModalVisible(false);
        }}
      >
        {/* 
          - Details to show here:
          - Name
          - Distance
          - Duration to go there
          - Set Destination button
        */}
        <View className="flex gap-3 mt-10">
          <View className="">
            <Text className="text-xl font-semibold">Target Location : </Text>
            <Text className="text-xl text-center">
              {routeDetails.end_place}
            </Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl font-semibold">Distance : </Text>
            <Text className="text-xl">{routeDetails.distance}</Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl font-semibold">Duration : </Text>
            <Text className="text-xl">{routeDetails.duration}</Text>
          </View>
          <View className="justify-between flex flex-row">
            <Text className="text-xl font-semibold">
              Sleepy after (hours) :{" "}
            </Text>
            <Text className="text-xl">{routeDetails.tdo}</Text>
          </View>
          {routeDetails.tdo_loc ? (
            <View className="">
              <Text className="text-xl font-semibold">
                You will feel drowsy around :{" "}
              </Text>
              <Text className="text-xl text-center">
                {routeDetails.tdo_loc}
              </Text>
            </View>
          ) : (
            <View className="justify-between flex flex-row">
              <Text className="text-xl font-semibold text-lime-900">
                You are good to go on this journey
              </Text>
            </View>
          )}
        </View>
      </OverlayPanel>
    </View>
  );
};

export default MapComponent;
