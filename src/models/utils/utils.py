from typing import Tuple
import numpy as np
import pandas as pd
from keras import Sequential, Input
from keras.src.layers import GRU, Dropout, Dense
from keras.src.optimizers import Adam


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
    model.compile(optimizer=optimizer, loss="mean_squared_error")
    return model


def write_evaluation_metrics_to_file(model_name, mse, mae, evs, file_path: str):
    with open(file_path, "w") as file:
        file.write(f"Model: {model_name}\n")
        file.write(f"Train MSE: {mse}\n")
        file.write(f"Train MAE: {mae}\n")
        file.write(f"Train EVS: {evs}\n")
