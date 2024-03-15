import joblib
import pandas as pd
from keras.models import load_model
from src.models.utils.utils import create_test_train_split, create_time_series, write_evaluation_metrics_to_file, \
    evaluate_model, information_gain_feature_selection


if __name__ == "__main__":
    data = pd.read_csv("../../data/processed/mbajk_dataset.csv")
    data.drop(columns=["date"], inplace=True)

    model = load_model("../../models/mbajk_GRU.h5")
    scaler = joblib.load("../../models/min_max_scaler.gz")

    target_variable = "available_bike_stands"

    features_to_keep = information_gain_feature_selection(data, target_variable)['Feature'][:3].tolist()

    features = [target_variable] + features_to_keep
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

    write_evaluation_metrics_to_file(model.name, mse_train, mae_train, evs_train, "../../reports/train_metrics.txt")
    write_evaluation_metrics_to_file(model.name, mse_test, mae_test, evs_test, "../../reports/metrics.txt")
