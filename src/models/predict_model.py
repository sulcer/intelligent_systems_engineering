import joblib
import numpy as np
import pandas as pd
from keras.src.saving import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score
from src.models.utils.utils import create_test_train_split, create_time_series, write_evaluation_metrics_to_file


def evaluate_model(y_actual, predicted, dataset, scaler):
    predicted_copy = np.repeat(predicted, dataset.shape[1], axis=-1)
    pred = scaler.inverse_transform(np.reshape(predicted_copy, (len(predicted), dataset.shape[1])))[:, 0]

    actual_copy = np.repeat(y_actual, dataset.shape[1], axis=-1)
    actual = scaler.inverse_transform(np.reshape(actual_copy, (len(y_test), dataset.shape[1])))[:, 0]

    mse = mean_squared_error(actual, pred)
    mae = mean_absolute_error(actual, pred)
    evs = explained_variance_score(actual, pred)

    return mse, mae, evs


if __name__ == "__main__":
    data = pd.read_csv("../../data/processed/mbajk_dataset.csv")
    data.drop(columns=["date"], inplace=True)

    model = load_model("../models/mbajk_GRU.keras")
    scaler = joblib.load("../models/min_max_scaler.gz")

    target_variable = "available_bike_stands"
    features = [target_variable] + [col for col in data.columns if col != target_variable]
    data = data[features]

    train_data, test_data = create_test_train_split(data)

    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)

    window_size = 50

    X_train, y_train = create_time_series(train_data, window_size)
    X_test, y_test = create_time_series(test_data, window_size)

    predicted_train = model.predict(X_train)
    predicted_test = model.predict(X_test)

    mse_train, mae_train, evs_train = evaluate_model(y_train, predicted_train, train_data, scaler)
    mse_test, mae_test, evs_test = evaluate_model(y_test, predicted_test, test_data, scaler)

    write_evaluation_metrics_to_file(model.name, mse_train, mae_train, evs_train, "reports/train_metrics.txt")
    write_evaluation_metrics_to_file(model.name, mse_test, mae_test, evs_test, "reports/metrics.txt")
