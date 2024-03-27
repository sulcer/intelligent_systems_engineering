import os
import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.models.utils.utils import create_test_train_split, create_time_series, create_model, \
    information_gain_feature_selection


def train_model(station_number: int) -> None:
    data = pd.read_csv(f"../../data/processed/station_{station_number}.csv")
    scaler = MinMaxScaler()

    train_data, test_data = create_test_train_split(data)

    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)

    window_size = 2

    X_train, y_train = create_time_series(train_data, window_size)
    X_test, y_test = create_time_series(test_data, window_size)

    model = create_model(X_train)

    model.fit(X_train, y_train, epochs=10, batch_size=2, validation_data=(X_test, y_test), verbose=1)

    joblib.dump(scaler, f"../../models/min_max_scaler_{station_number}.gz")
    model.save(f"../../models/mbajk_{model.name}_{station_number}.h5")

    print(f"Model for station {station_number} trained")


if __name__ == "__main__":
    dir_path = "../../data/processed/"
    for file in os.listdir(dir_path):
        if file.startswith("station_") and file.endswith(".csv"):
            station_number = file.split("_")[1].split(".")[0]
            print(f"Training model for station {station_number}")
            train_model(int(station_number))
