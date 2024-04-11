from src.data.fetch_data import Fetcher


def test_weather_api():
    fetcher = Fetcher()
    response = fetcher.ping_weather_api()
    assert len(response) > 0


def test_station_api():
    fetcher = Fetcher()
    response = fetcher.ping_station_api()
    assert len(response) > 0
