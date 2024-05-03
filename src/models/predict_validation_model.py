import joblib
import pandas as pd
from keras.models import load_model
from src.config import settings
from src.models.utils.utils import create_test_train_split, create_time_series, evaluate_model
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth


def predict_validation_model() -> None:
    validation_data = pd.read_csv("data/processed/test.csv")

    validation_model = load_model("models/mbajk_validation/model.h5")
    scaler = joblib.load("models/mbajk_validation/scaler.gz")

    train_validation_data, test_validation_data = create_test_train_split(validation_data)
    train_validation_data = scaler.fit_transform(train_validation_data)
    test_validation_data = scaler.transform(test_validation_data)

    # window_size = settings.window_size
    window_size = 2

    X_validation_train, y_validation_train = create_time_series(train_validation_data, window_size)
    X_validation_test, y_validation_test = create_time_series(test_validation_data, window_size)

    predicted_validation_train = validation_model.predict(X_validation_train)
    predicted_validation_test = validation_model.predict(X_validation_test)

    mse_validation_train, mae_validation_train, evs_validation_train = evaluate_model(y_validation_train,
                                                                                      predicted_validation_train,
                                                                                      train_validation_data,
                                                                                      scaler)
    mse_validation_test, mae_validation_test, evs_validation_test = evaluate_model(y_validation_test,
                                                                                   predicted_validation_test,
                                                                                   test_validation_data,
                                                                                   scaler)

    print("Validation data predicted")
    print(f"MSE train: {mse_validation_train}")
    print(f"MAE train: {mae_validation_train}")
    print(f"EVS train: {evs_validation_train}")
    print(f"MSE test: {mse_validation_test}")
    print(f"MAE test: {mae_validation_test}")
    print(f"EVS test: {evs_validation_test}")

    mlflow.start_run(run_name="validation_model")
    mlflow.log_metric("mse_validation_train", mse_validation_train)
    mlflow.log_metric("mae_validation_train", mae_validation_train)
    mlflow.log_metric("evs_validation_train", evs_validation_train)
    mlflow.log_metric("mse_validation_test", mse_validation_test)
    mlflow.log_metric("mae_validation_test", mae_validation_test)
    mlflow.log_metric("evs_validation_test", evs_validation_test)

    mlflow.end_run()


if __name__ == "__main__":
    dh_auth.add_app_token(token=settings.dagshub_user_token)
    dagshub.init(settings.dagshub_repo_name, settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    if mlflow.active_run():
        mlflow.end_run()

    predict_validation_model()
