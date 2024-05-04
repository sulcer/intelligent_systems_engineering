import pandas as pd


class BikeStationService:
    def __init__(self):
        pass

    @staticmethod
    def get_bike_station_data(station_number: int):
        url = (f"https://dagshub.com/sulcer/intelligent_systems_engineering_dagshub"
               f"/raw/main/data/processed/station_{station_number}.csv")

        df = pd.read_csv(url)

        return df
