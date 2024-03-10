import os
import pandas as pd
import requests
from src.data.fetched_entites import Station


class Fetcher:
    def __init__(self, contract="maribor", api_key="5e150537116dbc1786ce5bec6975a8603286526b"):
        self.contract = contract
        self.api_key = api_key
        self.url = f"https://api.jcdecaux.com/vls/v1/stations?contract={contract}&apiKey={api_key}"

    def fetch_data(self):
        response = requests.get(self.url)
        data = response.json()

        for station in data:
            station = Station(**station)

            csv_file = f"../../data/raw/{station.name}.csv"
            if not os.path.exists(csv_file):
                df = pd.DataFrame(
                    columns=["name", "address", "bike_stands", "available_bike_stands", "available_bikes", "date"])
                df.to_csv(csv_file, index=False)

            station_data = pd.DataFrame([{
                "name": station.name,
                "address": station.address,
                "bike_stands": station.bike_stands,
                "available_bike_stands": station.available_bike_stands,
                "available_bikes": station.available_bikes,
                "date": station.last_update
            }])

            station_data.to_csv(csv_file, mode="a", header=False, index=False)


def main():
    fetcher = Fetcher()
    fetcher.fetch_data()


if __name__ == "__main__":
    main()
