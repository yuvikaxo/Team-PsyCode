from fastapi import FastAPI
import numpy as np
import uvicorn
import openrouteservice
from pydantic import BaseModel
import pickle

app = FastAPI()

sample_data = [25, 85, 0.1, 0.20, 0.60, 1, 8]

def get_tdo ( sample = sample_data ):
    with open('tdo_model.pkl', 'rb') as file:
        model = pickle.load(file)
        
    features = np.array(sample[:-1]).reshape(1, -1)
    duration = sample[-1]
    base_tdo = model.predict(features)
    final_tdo = base_tdo[0] * (duration / 7.0) * np.power(duration / 7.0, 0.5)
    return final_tdo

def get_tdo_loc(route, duration_route, final_tdo, client):
    # --- Locate position after TDO hours ---
    tdo_seconds = final_tdo * 3600
    line = route['features'][0]['geometry']['coordinates']
    step = tdo_seconds / (duration_route * 3600)  # ratio of time passed
    index = int(step * len(line))

    if index < len(line):
        future_position = line[index]
        place = get_place_name_from_coords(future_position, client)
        return place
    else:
        return None

def get_coordinates(place_name, client):
        result = client.pelias_search(text=place_name)
        coords = result['features'][0]['geometry']['coordinates']
        return tuple(coords)

def get_place_name_from_coords(coords, client):
        res = client.pelias_reverse(point=coords, size=1)
        return res['features'][0]['properties']['label']


def get_route_data(start_place, end_place):
    client = openrouteservice.Client(key='5b3ce3597851110001cf6248f0228e3b0fb646b28c92af9d8cbb4562')

    # start_place = input("Enter starting location: ")
    # end_place = input("Enter destination location: ")

    start = get_coordinates(start_place, client)
    end = get_coordinates(end_place, client) 

    route = client.directions(coordinates=[start, end], profile='driving-car', format='geojson')
    distance = route['features'][0]['properties']['segments'][0]['distance'] / 1000
    duration_route = route['features'][0]['properties']['segments'][0]['duration'] / 3600

    coordinates = route['features'][0]['geometry']['coordinates']
    converted_coords = [
          
        {'latitude': coord[1], 'longitude': coord[0]} for coord in coordinates
    ]
    tdo = get_tdo()
    tdo_loc = get_tdo_loc(route, duration_route, tdo, client=client)

    return {
        "start_place": start_place,
        "end_place": end_place,
        "start_coord": {
            "latitude": start[1],
            "longitude": start[0]
        },
        "end_coord": {
            "latitude": end[1],
            "longitude": end[0]
        },
        "distance": distance,
        "duration": duration_route,
        "routeCoordinates": converted_coords,
        "tdo": tdo,
        "tdo_loc": tdo_loc
    }


class RouteRequest(BaseModel):
        start_place: str
        end_place: str

@app.post("/getRoute")
def getRoute(request: RouteRequest):
    route_data = get_route_data(request.start_place, request.end_place)
    return route_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)