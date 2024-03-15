import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.models.utils.utils import create_test_train_split, create_time_series, create_model, \
    information_gain_feature_selection

if __name__ == "__main__":
    data = pd.read_csv("../../data/processed/mbajk_dataset.csv")
    data.drop(columns=["date"], inplace=True)

    target_variable = "available_bike_stands"

    features_to_keep = information_gain_feature_selection(data, target_variable)['Feature'][:3].tolist()

    features = [target_variable] + features_to_keep
    data = data[features]
    train_data, test_data = create_test_train_split(data)

    scaler = MinMaxScaler()
    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)

    window_size = 50

    X_train, y_train = create_time_series(train_data, window_size)
    X_test, y_test = create_time_series(test_data, window_size)

    model = create_model(X_train)

    model.fit(X_train, y_train, epochs=10, batch_size=64, validation_data=(X_test, y_test), verbose=1)

    joblib.dump(scaler, "../../models/min_max_scaler.gz")
    model.save(f"../../models/mbajk_{model.name}.h5")
