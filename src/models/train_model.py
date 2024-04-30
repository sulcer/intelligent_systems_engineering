import os
import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.config import settings
from src.models.utils.utils import create_test_train_split, create_time_series, create_model, run_sklearn_pipeline
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth


def train_model(station_number: int) -> None:
    data = pd.read_csv(f"data/processed/station_{station_number}.csv")

    run_sklearn_pipeline(data)

    scaler = MinMaxScaler()

    train_data, test_data = create_test_train_split(data)

    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)

    window_size = settings.window_size

    X_train, y_train = create_time_series(train_data, window_size)
    X_test, y_test = create_time_series(test_data, window_size)

    model = create_model(X_train)

    epochs = 10
    batch_size = 64

    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test), verbose=1)

    if not os.path.exists(f"models/station_{station_number}"):
        os.makedirs(f"models/station_{station_number}")

    joblib.dump(scaler, f"models/station_{station_number}/scaler.gz")
    model.save(f"models/station_{station_number}/model.h5")

    mlflow.start_run(run_name=f"train_station_{station_number}")
    mlflow.log_param("window_size", window_size)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("epochs", epochs)

    mlflow.end_run()

    print(f"Model for station {station_number} trained")


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
            print(f"Training model for station {station_number}")
            train_model(int(station_number))
    print("[INFO] All models trained successfully!")
