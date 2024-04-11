import os
from datetime import datetime
import pandas as pd
import requests
from src.data.fetched_entites import Station
from src.config import settings


class Fetcher:
    def __init__(self, contract="maribor", api_key="5e150537116dbc1786ce5bec6975a8603286526b"):
        self.contract = contract
        self.api_key = api_key
        self.url = f"https://api.jcdecaux.com/vls/v1/stations?contract={contract}&apiKey={api_key}"
        self.weather_url = "https://api.open-meteo.com/v1/forecast?"
        self.data_path = "data"

    def fetch_data(self):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        response = requests.get(self.url)
        response.raise_for_status()
        data = response.json()

        csv_file = "data/raw/mbajk_stations.csv"
        if not os.path.exists(csv_file):
            df = pd.DataFrame(columns=settings.raw_station_columns)
            df.to_csv(csv_file, index=False)

        for station_data in data:
            station = Station(**station_data)

            new_station_entry = pd.DataFrame([{
                settings.raw_station_columns[0]: date,
                settings.raw_station_columns[1]: station.number,
                settings.raw_station_columns[2]: station.name,
                settings.raw_station_columns[3]: station.address,
                settings.raw_station_columns[4]: station.bike_stands,
                settings.raw_station_columns[5]: station.available_bike_stands,
                settings.raw_station_columns[6]: station.available_bikes,
                settings.raw_station_columns[7]: station.position["lat"],
                settings.raw_station_columns[8]: station.position["lng"]
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

        csv_file = "data/raw/weather.csv"
        if not os.path.exists(csv_file):
            df = pd.DataFrame(columns=settings.raw_weather_columns)
            df.to_csv(csv_file, index=False)

        new_weather_entry = pd.DataFrame([{
            settings.raw_weather_columns[0]: date,
            settings.raw_weather_columns[1]: data["temperature_2m"],
            settings.raw_weather_columns[2]: data["relative_humidity_2m"],
            settings.raw_weather_columns[3]: data["apparent_temperature"],
            settings.raw_weather_columns[4]: data["precipitation"],
            settings.raw_weather_columns[5]: data["rain"],
            settings.raw_weather_columns[6]: data["surface_pressure"]
        }])

        new_weather_entry.to_csv(csv_file, mode="a", header=False, index=False)

    def fetch_weather_forcast(self):
        forcast_url = (f"{self.weather_url}latitude={settings.lat}&longitude={settings.lon}&hourly=temperature_2m,"
                       f"relative_humidity_2m,apparent_temperature,precipitation,"
                       f"surface_pressure&timezone=Europe%2FBerlin&forecast_days=1&forecast_hours=12")

        response = requests.get(forcast_url)
        response.raise_for_status()
        forcast = response.json()["hourly"]

        return forcast

    def ping_weather_api(self):
        response = requests.get(f"{self.weather_url}latitude={settings.lat}&longitude={settings.lon}")
        response.raise_for_status()
        return response.json()

    def ping_station_api(self):
        response = requests.get(self.url)
        response.raise_for_status()
        return response.json()


def main():
    fetcher = Fetcher()
    fetcher.fetch_data()


if __name__ == "__main__":
    main()
