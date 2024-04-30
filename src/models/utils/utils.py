from typing import Tuple
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import GRU, Dropout, Dense, Input
from keras.optimizers import Adam
from sklearn.feature_selection import mutual_info_regression
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score
from sklearn.pipeline import Pipeline


def create_test_train_split(dataset: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    test_data_size = round(0.2 * len(dataset))
    train_data = dataset[:-test_data_size]
    test_data = dataset[-test_data_size:]

    return train_data, test_data


def create_time_series(data, n_past):
    X, y = [], []
    for i in range(n_past, len(data)):
        X.append(data[i - n_past:i, 0:data.shape[1]])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


def create_model(input_shape):
    model = Sequential(name='GRU')

    model.add(Input(shape=(input_shape.shape[1], input_shape.shape[2])))
    model.add(GRU(128, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(GRU(64, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(GRU(32))
    model.add(Dense(units=32, activation="relu"))
    model.add(Dense(1))

    optimizer = Adam(learning_rate=0.01)
    model.compile(optimizer, loss="mean_squared_error")
    return model


def write_evaluation_metrics_to_file(model_name, mse, mae, evs, file_path: str):
    with open(file_path, "w") as file:
        file.write(f"Model: {model_name}\n")
        file.write(f"Train MSE: {mse}\n")
        file.write(f"Train MAE: {mae}\n")
        file.write(f"Train EVS: {evs}\n")


def information_gain_feature_selection(data: pd.DataFrame, target_variable: str) -> pd.DataFrame:
    input_data = data.columns.tolist()
    input_data.remove(target_variable)
    ig_scores = mutual_info_regression(data[input_data], data[target_variable])

    feature_scores = pd.DataFrame({'Feature': data[input_data].columns, 'Information_Gain': ig_scores})
    feature_scores = feature_scores.sort_values(by='Information_Gain', ascending=False)

    return feature_scores


def evaluate_model(y_actual, predicted, dataset, scaler):
    predicted_copy = np.repeat(predicted, dataset.shape[1], axis=-1)
    pred = scaler.inverse_transform(np.reshape(predicted_copy, (len(predicted), dataset.shape[1])))[:, 0]

    actual_copy = np.repeat(y_actual, dataset.shape[1], axis=-1)
    actual = scaler.inverse_transform(np.reshape(actual_copy, (len(y_actual), dataset.shape[1])))[:, 0]

    mse = mean_squared_error(actual, pred)
    mae = mean_absolute_error(actual, pred)
    evs = explained_variance_score(actual, pred)

    return mse, mae, evs


def run_sklearn_pipeline(data):
    if data.isnull().values.any():
        print("[WARN]: Missing data in row")

        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
        ])

        pipeline = Pipeline(steps=[
            ('preprocessor', numerical_transformer),
        ])

        pipeline.fit_transform(data)
