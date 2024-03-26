import os
from datetime import datetime
import pandas as pd
import requests
from src.data.fetched_entites import Station


class Fetcher:
    def __init__(self, contract="maribor", api_key="5e150537116dbc1786ce5bec6975a8603286526b"):
        self.contract = contract
        self.api_key = api_key
        self.url = f"https://api.jcdecaux.com/vls/v1/stations?contract={contract}&apiKey={api_key}"
        self.weather_url = "https://api.open-meteo.com/v1/forecast?"

    def fetch_data(self):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        response = requests.get(self.url)
        response.raise_for_status()
        data = response.json()

        csv_file = f"../../data/raw/mbajk_stations.csv"
        if not os.path.exists(csv_file):
            df = pd.DataFrame(
                columns=["date",
                         "name",
                         "address",
                         "bike_stands",
                         "available_bike_stands",
                         "available_bikes",
                         "lat",
                         "lon"])
            df.to_csv(csv_file, index=False)

        for station_data in data:
            station = Station(**station_data)

            new_station_entry = pd.DataFrame([{
                "date": date,
                "name": station.name,
                "address": station.address,
                "bike_stands": station.bike_stands,
                "available_bike_stands": station.available_bike_stands,
                "available_bikes": station.available_bikes,
                "lat": station.position["lat"],
                "lon": station.position["lng"]
            }])

            self.fetch_weather_data(date, station.position["lat"], station.position["lng"])
            new_station_entry.to_csv(csv_file, mode="a", header=False, index=False)

    def fetch_weather_data(self, date, lat, lon):
        weather_for_station_url = (f"{self.weather_url}latitude={lat}&longitude={lon}&current=temperature_2m,"
                                   f"relative_humidity_2m,apparent_temperature,precipitation,rain,"
                                   f"surface_pressure&timezone=Europe%2FBerlin")

        response = requests.get(weather_for_station_url)
        response.raise_for_status()
        data = response.json()["current"]

        csv_file = f"../../data/raw/weather.csv"
        if not os.path.exists(csv_file):
            df = pd.DataFrame(
                columns=["date",
                         "temperature",
                         "relative_humidity",
                         "apparent_temperature",
                         "precipitation",
                         "rain",
                         "surface_pressure"
                         ])
            df.to_csv(csv_file, index=False)

        new_weather_entry = pd.DataFrame([{
            "date": date,
            "temperature": data["temperature_2m"],
            "relative_humidity": data["relative_humidity_2m"],
            "apparent_temperature": data["apparent_temperature"],
            "precipitation": data["precipitation"],
            "rain": data["rain"],
            "surface_pressure": data["surface_pressure"]
        }])

        new_weather_entry.to_csv(csv_file, mode="a", header=False, index=False)


def main():
    fetcher = Fetcher()
    fetcher.fetch_data()


if __name__ == "__main__":
    main()
