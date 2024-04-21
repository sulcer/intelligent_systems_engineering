import pathlib
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    window_size: int = 24
    lat: float = 46.5547
    lon: float = 15.6467
    api_key: str = "5e150537116dbc1786ce5bec6975a8603286526b"
    target_feature: str = "available_bike_stands"
    # the following order of columns is important!
    raw_station_columns: List[str] = ["date",
                                      "number",
                                      "name",
                                      "address",
                                      "bike_stands",
                                      "available_bike_stands",
                                      "available_bikes",
                                      "lat",
                                      "lon"]
    raw_weather_columns: List[str] = ["date",
                                      "temperature",
                                      "relative_humidity",
                                      "apparent_temperature",
                                      "precipitation",
                                      "rain",
                                      "surface_pressure"]
    features: List[str] = ["surface_pressure",
                           "temperature",
                           "apparent_temperature",
                           "relative_humidity",
                           "precipitation"]
    columns_to_remove: List[str] = ["number",
                                    "name",
                                    "address",
                                    "bike_stands",
                                    "available_bikes",
                                    "lon",
                                    "lat"]
    # dagshub configuration
    mlflow_tracking_username: str
    mlflow_tracking_uri: str
    mlflow_tracking_password: str
    dagshub_user_token: str
    dagshub_repo_name: str

    __project_root = pathlib.Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(env_file=f"{__project_root}/.env")


settings = Settings()
