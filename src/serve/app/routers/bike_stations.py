import requests
from fastapi import APIRouter

router = APIRouter(
    prefix="/mbajk/stations",
    tags=["Bike Stations"],
    responses={404: {"description": "Not found"}},
)


@router.get("")
def get_bike_stations():
    response = requests.get('https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey'
                            '=5e150537116dbc1786ce5bec6975a8603286526b')
    response.raise_for_status()
    data = response.json()

    return data


@router.get("/{station_number}")
def get_bike_station(station_number: int):
    response = requests.get(f'https://api.jcdecaux.com/vls/v1/stations/{station_number}?contract=maribor&apiKey'
                            '=5e150537116dbc1786ce5bec6975a8603286526b')
    response.raise_for_status()
    data = response.json()

    if data:
        return data
    else:
        return {"message": "Station not found"}
