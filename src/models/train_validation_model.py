import os
import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.config import settings
from src.models.utils.utils import create_test_train_split, create_time_series, create_model


def train_validation_model() -> None:
    validation_data = pd.read_csv("data/processed/train.csv")
    scaler = MinMaxScaler()

    train_validation_data, test_validation_data = create_test_train_split(validation_data)

    train_data = scaler.fit_transform(train_validation_data)
    test_data = scaler.transform(test_validation_data)

    # window_size = settings.window_size
    window_size = 2

    X_train, y_train = create_time_series(train_data, window_size)
    X_test, y_test = create_time_series(test_data, window_size)

    model = create_model(X_train)

    model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test), verbose=1)

    if not os.path.exists("models/mbajk_validation"):
        os.makedirs("models/mbajk_validation")

    joblib.dump(scaler, "models/mbajk_validation/scaler.gz")
    model.save("models/mbajk_validation/model.h5")

    print("Model for validation data trained")


if __name__ == "__main__":
    train_validation_model()
