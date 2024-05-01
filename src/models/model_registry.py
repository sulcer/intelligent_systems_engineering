import os
import joblib
import onnx
from enum import Enum, auto
from mlflow.onnx import load_model as load_onnx
from mlflow.sklearn import load_model as load_scaler
from mlflow import MlflowClient
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth
from src.config import settings


def get_latest_model(station_number: int):
    try:
        client = MlflowClient()
        model_version = client.get_latest_versions("mbajk_station_" + str(station_number), stages=["staging"])[0]
        model_url = model_version.source
        model = load_onnx(model_url)
        return model
    except IndexError:
        print(f"Model for station {station_number} not found.")
        return None


def get_latest_scaler(station_number: int):
    print("preden nalozis scaler!!!!!!!!")
    try:
        client = MlflowClient()
        model_version = (
            client.get_latest_versions("mbajk_station_" + str(station_number) + "_scaler", stages=["staging"]))[0]
        model_url = model_version.source
        scaler = load_scaler(model_url)
        return scaler
    except IndexError:
        print(f"Scaler for station {station_number} not found.")
        return None


def get_production_model(station_number: int):
    try:
        client = MlflowClient()
        model_version = client.get_latest_versions("mbajk_station_" + str(station_number), stages=["production"])[0]
        model_url = model_version.source
        model = load_onnx(model_url)
        return model
    except IndexError:
        print(f"Production model for station {station_number} not found.")
        return None


def get_production_scaler(station_number: int):
    print("preden nalozis scaler!!!!!!!!")
    try:
        client = MlflowClient()
        model_version = (
            client.get_latest_versions("mbajk_station_" + str(station_number) + "_scaler", stages=["production"]))[0]
        model_url = model_version.source
        scaler = load_scaler(model_url)
        return scaler
    except IndexError:
        print(f"Production scaler for station {station_number} not found.")
        return None


class ModelType(Enum):
    LATEST = auto()
    PRODUCTION = auto()


def download_model(station_number: int, model_type: ModelType) -> tuple:
    dh_auth.add_app_token(token=settings.dagshub_user_token)
    dagshub.init(settings.dagshub_repo_name, settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    print(f"!!!!!!{model_type.name.lower()} !!!! {station_number}")

    model_func = get_latest_model if model_type == ModelType.LATEST else get_production_model
    scaler_func = get_latest_scaler if model_type == ModelType.LATEST else get_production_scaler

    model = model_func(station_number)
    print("got model!")
    scaler = scaler_func(station_number)

    folder_name = f"models/station_{station_number}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if model is None or scaler is None:
        return None, None

    model_type_str = model_type.name.lower()
    joblib.dump(scaler, f"{folder_name}/scaler_{model_type_str}.gz")
    onnx.save_model(model, f"{folder_name}/model_{model_type_str}.onnx")

    model_path = f"{folder_name}/model_{model_type_str}.onnx"

    return model_path, scaler


def download_model_registry():
    dh_auth.add_app_token(token=settings.dagshub_user_token)
    dagshub.init(settings.dagshub_repo_name, settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    for station_number in range(1, 30):
        model_path = f"models/station_{station_number}/model_production.onnx"
        scaler_path = f"models/station_{station_number}/scaler_production.gz"

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print(f"Model and scaler for station {station_number} already exist.")
            continue

        model = get_production_model(station_number)
        scaler = get_production_scaler(station_number)

        if not os.path.exists(f"models/station_{station_number}"):
            os.makedirs(f"models/station_{station_number}")

        joblib.dump(scaler, f"models/station_{station_number}/scaler_production.gz")
        onnx.save_model(model, f"models/station_{station_number}/model_production.onnx")
        print(f"Model and scaler for station {station_number} downloaded.")


def empty_model_registry():
    dh_auth.add_app_token(token=settings.dagshub_user_token)
    dagshub.init(settings.dagshub_repo_name, settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    client = MlflowClient()
    for station_number in range(1, 30):
        try:
            client.delete_registered_model(f"mbajk_station_{station_number}")
            client.delete_registered_model(f"mbajk_station_{station_number}_scaler")
        except IndexError:
            print(f"Model and scaler for station {station_number} not found.")
            continue
