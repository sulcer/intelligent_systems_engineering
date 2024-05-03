from datetime import datetime, timedelta, timezone
from typing import List
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from keras.models import load_model
from pydantic import BaseModel
from sklearn.preprocessing import MinMaxScaler
from src.config import settings
from src.data.fetch_data import Fetcher
from src.serve.app.services.logging_service import LoggingService
from src.serve.app.utils.helpers import use_model_prediction, create_time_series
import onnxruntime as ort

router = APIRouter(
    prefix="/mbajk",
    tags=["Prediction"],
    responses={404: {"description": "Not found"}},
)


class PredictionInput(BaseModel):
    available_bike_stands: int
    surface_pressure: float
    temperature: float
    apparent_temperature: float
    relative_humidity: float
    precipitation: float


window_size = settings.window_size


@router.post("/predict_basic/{station_number}")
def predict_one(station_number: int, data: List[PredictionInput]):
    model = load_model(f"models/station_{station_number}/model.h5")
    scaler = joblib.load(f"models/station_{station_number}/scaler.gz")

    if len(data) != window_size:
        raise HTTPException(status_code=400, detail=f"Data must contain {window_size} items")

    data = [[data_slice.available_bike_stands, data_slice.surface_pressure, data_slice.temperature,
             data_slice.apparent_temperature, data_slice.relative_humidity, data_slice.precipitation]
            for data_slice in data]

    scaled_data = scaler.transform(data)
    feature_cols = list(range(len(data[0])))

    X = create_time_series(scaled_data, window_size, feature_cols)

    prediction = use_model_prediction(X, model, scaler, window_size, feature_cols)

    return {"prediction": prediction}


@router.get("/predict/{station_number}/{n_time_units}")
def predict(station_number: int, n_time_units: int):
    fetcher = Fetcher()
    forcast = fetcher.fetch_weather_forcast()

    model = ort.InferenceSession(f"models/station_{station_number}/model_production.onnx")
    scaler: MinMaxScaler = joblib.load(f"models/station_{station_number}/scaler_production.gz")

    dataset = pd.read_csv(f"data/processed/station_{station_number}.csv")

    predictions = []
    last_rows = dataset.tail(window_size).values.tolist()
    feature_cols = list(range(len(last_rows[0])))

    for n in range(n_time_units):
        scaled_data = scaler.transform(last_rows)

        X = create_time_series(scaled_data, window_size, feature_cols)
        prediction = use_model_prediction(X, model, scaler, window_size, feature_cols)
        predictions.append(prediction)

        forcast_index = n + 1
        new_row = [prediction,
                   forcast["surface_pressure"][forcast_index],
                   forcast["temperature_2m"][forcast_index],
                   forcast["apparent_temperature"][forcast_index],
                   forcast["relative_humidity_2m"][forcast_index],
                   forcast["precipitation"][forcast_index]]

        last_rows.pop(0)
        last_rows.append(new_row)

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    logged_predictions = []
    for i, p in enumerate(predictions):
        prediction_time = now + timedelta(hours=i + 1)

        logged_predictions.append({
            "prediction": p,
            "date": prediction_time
        })

    LoggingService.save_log(station_number, n_time_units, logged_predictions)

    return predictions
