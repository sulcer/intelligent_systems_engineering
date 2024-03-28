import os
import joblib
import pandas as pd
from keras.models import load_model
from src.models.utils.utils import create_test_train_split, create_time_series, write_evaluation_metrics_to_file, \
    evaluate_model, information_gain_feature_selection


def predict_model(station_number: int) -> None:
    data = pd.read_csv(f"../../data/processed/station_{station_number}.csv")

    model = load_model(f"../../models/station_{station_number}/model.h5")
    scaler = joblib.load(f"../../models/station_{station_number}/scaler.gz")

    train_data, test_data = create_test_train_split(data)
    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)

    window_size = 2

    X_train, y_train = create_time_series(train_data, window_size)
    X_test, y_test = create_time_series(test_data, window_size)

    predicted_train = model.predict(X_train)
    predicted_test = model.predict(X_test)

    mse_train, mae_train, evs_train = evaluate_model(y_train, predicted_train, train_data, scaler)
    mse_test, mae_test, evs_test = evaluate_model(y_test, predicted_test, test_data, scaler)

    if not os.path.exists(f"../../reports/station_{station_number}"):
        os.makedirs(f"../../reports/station_{station_number}")

    write_evaluation_metrics_to_file(model.name, mse_train, mae_train, evs_train,
                                     f"../../reports/station_{station_number}/train_metrics.txt")
    write_evaluation_metrics_to_file(model.name, mse_test, mae_test, evs_test,
                                     f"../../reports/station_{station_number}/metrics.txt")

    print(f"Model for station {station_number} predicted")


if __name__ == "__main__":
    dir_path = "../../data/processed/"
    for file in os.listdir(dir_path):
        if file.startswith("station_") and file.endswith(".csv"):
            station_number = file.split("_")[1].split(".")[0]
            print(f"Predicting model for station {station_number}")
            predict_model(int(station_number))
