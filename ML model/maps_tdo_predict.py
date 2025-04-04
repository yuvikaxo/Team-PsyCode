import openrouteservice
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# --- Sleep TDO prediction setup ---
df = pd.read_csv("Sleep_Efficiency.csv")

df = df[["Age", "Sleep duration", "Sleep efficiency", "REM sleep percentage", "Deep sleep percentage", "Light sleep percentage", "Awakenings"]]
df = df.dropna()

df["Deep/Total"] = df["Deep sleep percentage"] / 100
df["REM/Total"] = df["REM sleep percentage"] / 100
df["Light/Total"] = df["Light sleep percentage"] / 100

X = df[["Age", "Sleep efficiency", "Deep/Total", "REM/Total", "Light/Total", "Awakenings"]]
y = df["Sleep duration"] * (0.5 + df["Deep/Total"] * 0.5 + df["REM/Total"] * 0.3) * np.power(df["Sleep efficiency"] / 100, 1.5) / (0.1 + df["Awakenings"] * 0.2)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()

model.fit(X_train, y_train)

# --- Logged sleep data ---
sample = [25, 85, 0.1, 0.20, 0.60, 1, 8]  # Age, Efficiency, Deep, REM, Light, Awakenings, Duration
features = np.array(sample[:-1]).reshape(1, -1)
duration = sample[-1]
base_tdo = model.predict(features)
final_tdo = base_tdo[0] * (duration / 7.0) * np.power(duration / 7.0, 0.5)

# --- OpenRouteService API for routing ---
client = openrouteservice.Client(key='5b3ce3597851110001cf6248f0228e3b0fb646b28c92af9d8cbb4562')

def get_coordinates(place_name):
    result = client.pelias_search(text=place_name)
    coords = result['features'][0]['geometry']['coordinates']
    return tuple(coords)

def get_place_name_from_coords(coords):
    res = client.pelias_reverse(point=coords, size=1)
    return res['features'][0]['properties']['label']

start_place = input("Enter starting location: ")
end_place = input("Enter destination location: ")

start = get_coordinates(start_place)
end = get_coordinates(end_place)

route = client.directions(coordinates=[start, end], profile='driving-car', format='geojson')
distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000
duration_route = route['features'][0]['properties']['segments'][0]['duration'] / 3600
print(f"Total Route Distance: {distance:.2f} km")
print(f"Total Route Duration: {duration_route:.2f} hours")

# --- Locate position after TDO hours ---
tdo_seconds = final_tdo * 3600
line = route['features'][0]['geometry']['coordinates']
step = tdo_seconds / (duration_route * 3600)  # ratio of time passed
index = int(step * len(line))

if index < len(line):
    future_position = line[index]
    place = get_place_name_from_coords(future_position)
    print(f"You're fit to drive for {final_tdo:.2f} hours without feeling drowsy.")
    print(f"After {final_tdo:.2f} hours of driving, you will be near: {place}. Take rest here.")
else:
    print(f"You're fit to drive for {final_tdo:.2f} hours without feeling drowsy.")
    print("You've already completed the route by that time! You should already be at your destination.")