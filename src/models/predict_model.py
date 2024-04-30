import os
import joblib
import pandas as pd
from keras.models import load_model
from src.config import settings
from src.models.model_registry import download_model, ModelType
from src.models.utils.utils import create_test_train_split, create_time_series, write_evaluation_metrics_to_file, \
    evaluate_model
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth
from mlflow import MlflowClient
import onnxruntime as ort


def set_production_model(station_number: int) -> None:
    client = MlflowClient()

    try:
        new_model_version = (
            client.get_latest_versions("mbajk_station_" + str(station_number), stages=["staging"])[0])
        new_scaler_version = (
            client.get_latest_versions("mbajk_station_" + str(station_number) + "_scaler", stages=["staging"])[0])

        client.transition_model_version_stage("mbajk_station_" + str(station_number),
                                              new_model_version.version,
                                              "production")
        client.transition_model_version_stage("mbajk_station_" + str(station_number) + "_scaler",
                                              new_scaler_version.version,
                                              "production")

        print(f"Model and scaler for station {station_number} set to production")
    except IndexError:
        print(f"Model for station {station_number} not found.")


def predict_model(station_number: int) -> None:
    mlflow.start_run(run_name=f"mbajk_station_{station_number}", experiment_id="1", nested=True)

    production_model_path, production_scaler = download_model(station_number, ModelType.PRODUCTION)
    latest_model_path, scaler = download_model(station_number, ModelType.LATEST)

    if latest_model_path is None and scaler is None:
        return

    if production_model_path is None and production_scaler is None:
        set_production_model(station_number)
        return

    latest_model = ort.InferenceSession(latest_model_path)
    production_model = ort.InferenceSession(production_model_path)

    data = pd.read_csv(f"data/processed/station_{station_number}.csv")

    model = load_model(f"models/station_{station_number}/model.h5")
    scaler = joblib.load(f"models/station_{station_number}/scaler.gz")

    train_data, test_data = create_test_train_split(data)
    test_data = scaler.transform(test_data)

    window_size = settings.window_size

    X_test, y_test = create_time_series(test_data, window_size)

    latest_model_predictions = latest_model.run(["output"], {"input": X_test})[0]

    mse_latest, mae_latest, evs_latest = evaluate_model(y_test, latest_model_predictions, test_data, scaler)

    mlflow.log_metric("MSE_latest", mse_latest)
    mlflow.log_metric("MAE_latest", mae_latest)
    mlflow.log_metric("EVS_latest", evs_latest)

    production_model_predictions = production_model.run(["output"], {"input": X_test})[0]

    mse_production, mae_production, evs_production = evaluate_model(y_test,
                                                                    production_model_predictions,
                                                                    test_data,
                                                                    scaler)

    if mse_latest < mse_production:
        set_production_model(station_number)

    if not os.path.exists(f"reports/station_{station_number}"):
        os.makedirs(f"reports/station_{station_number}")

    write_evaluation_metrics_to_file(model.name, mse_latest, mae_latest, evs_latest,
                                     f"reports/station_{station_number}/latest_metrics.txt")

    write_evaluation_metrics_to_file(model.name, mse_production, mae_production, evs_production,
                                     f"reports/station_{station_number}/production_metrics.txt")

    print(f"[INFO]: Model for station {station_number} predicted")


if __name__ == "__main__":
    dh_auth.add_app_token(token=settings.dagshub_user_token)
    dagshub.init(settings.dagshub_repo_name, settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    if mlflow.active_run():
        mlflow.end_run()

    dir_path = "data/processed/"
    for file in os.listdir(dir_path):
        if file.startswith("station_") and file.endswith(".csv"):
            station_number = file.split("_")[1].split(".")[0]
            print(f"Predicting model for station {station_number}")
            predict_model(int(station_number))
    print("[INFO] All models predicted successfully!")
