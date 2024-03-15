from typing import List
import joblib
import numpy as np
from fastapi import APIRouter, HTTPException
from keras.models import load_model
from pydantic import BaseModel
from src.serve.app.utils.helpers import use_model_prediction

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


model = load_model("models/mbajk_GRU.h5")
scaler = joblib.load("models/min_max_scaler.gz")


def create_time_series(data, window_size, feature_cols):
    sequences = []
    n_samples = len(data)

    for i in range(window_size, n_samples + 1):
        sequence = data[i - window_size:i, feature_cols]
        sequences.append(sequence)

    return np.array(sequences)


@router.post("/predict")
def predict(data: List[PredictionInput]):
    window_size = 48
    if len(data) != window_size:
        raise HTTPException(status_code=400, detail=f"Data must contain {window_size} items")

    data = [[data_slice.available_bike_stands, data_slice.surface_pressure, data_slice.temperature,
             data_slice.apparent_temperature] for data_slice in data]

    scaled_data = scaler.transform(data)
    feature_cols = list(range(len(data[0])))

    X = create_time_series(scaled_data, window_size, feature_cols)

    prediction = use_model_prediction(X, model, scaler, window_size, feature_cols)

    return {"prediction": prediction}
