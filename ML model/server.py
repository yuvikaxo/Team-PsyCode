from fastapi import FastAPI
import uvicorn
import openrouteservice
from pydantic import BaseModel

app = FastAPI()

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
        "routeCoordinates": converted_coords
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