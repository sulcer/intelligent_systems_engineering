import os
import joblib
import pandas as pd
from mlflow.models import infer_signature
from sklearn.preprocessing import MinMaxScaler
from src.config import settings
from src.models.utils.utils import create_test_train_split, create_time_series, create_model, run_sklearn_pipeline
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth
from mlflow import MlflowClient
import tensorflow as tf
import tf2onnx
from mlflow.onnx import log_model as log_onnx_model
from mlflow.sklearn import log_model as log_sklearn_model


def train_model(station_number: int) -> None:
    client = MlflowClient()

    mlflow.start_run(run_name=f"mbajk_station_{station_number}", experiment_id="1", nested=True)

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

    model.output_names = ["output"]

    input_signature = [
        tf.TensorSpec(shape=(None, settings.window_size, (len(settings.features) + 1)), dtype=tf.double, name="input")
    ]

    onnx_model, _ = tf2onnx.convert.from_keras(model=model, input_signature=input_signature, opset=13)

    model_ = log_onnx_model(onnx_model=onnx_model,
                            artifact_path=f"models/station_{station_number}",
                            signature=infer_signature(X_test, model.predict(X_test)),
                            registered_model_name="mbajk_station_" + str(station_number))

    mv = client.create_model_version(name="mbajk_station_" + str(station_number), source=model_.model_uri,
                                     run_id=model_.run_id)

    client.transition_model_version_stage("mbajk_station_" + str(station_number), mv.version, "staging")

    scaler_meta = {"feature_range": scaler.feature_range}
    scaler = log_sklearn_model(
        sk_model=scaler,
        artifact_path=f"scalers/station_{station_number}",
        registered_model_name="mbajk_station_" + str(station_number) + "_scaler",
        metadata=scaler_meta
    )

    sv = client.create_model_version(name="mbajk_station_" + str(station_number) + "_scaler", source=scaler.model_uri,
                                     run_id=scaler.run_id)

    client.transition_model_version_stage("mbajk_station_" + str(station_number) + "_scaler", sv.version, "staging")

    if not os.path.exists(f"models/station_{station_number}"):
        os.makedirs(f"models/station_{station_number}")

    joblib.dump(scaler, f"models/station_{station_number}/scaler.gz")
    model.save(f"models/station_{station_number}/model.h5")

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
