import os.path
import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from src.config import settings


def main():
    df_stations = pd.read_csv("data/raw/mbajk_stations.csv")
    df_weather = pd.read_csv("data/raw/weather.csv")

    merged_df = merge_data(df_stations, df_weather)

    target_feature = settings.target_feature
    features = settings.features

    map_data_to_station(merged_df, target_feature, features)


def merge_data(df_stations, df_weather):
    df_weather.drop(columns=["date"], inplace=True)
    num_of_stations = df_stations["number"].nunique()
    print(f"[INFO] Number of stations: {num_of_stations}")

    # validation for data consistency and integrity
    validate_merge(num_of_stations, df_stations, df_weather)

    merged_df = pd.concat([df_stations.tail(num_of_stations), df_weather.tail(num_of_stations)], axis=1)
    merged_df.drop(columns=["date"], inplace=True)

    target_feature = settings.target_feature
    features = settings.features
    selected_features = [target_feature] + features
    print(f"[INFO] Selected features: {selected_features}")

    output_file = "data/processed/current_data.csv"
    if os.path.exists(output_file):
        merged_df[selected_features].to_csv(output_file, mode='a', header=False, index=False)
    else:
        merged_df[selected_features].to_csv(output_file, index=False)

    return merged_df


def get_top_features(df, target_feature, num_features):
    input_cols = df.columns.tolist()
    input_cols.remove(target_feature)
    information_gain = mutual_info_regression(df[input_cols], df[target_feature])

    feature_importance = pd.Series(information_gain, index=input_cols)
    feature_importance.sort_values(ascending=False, inplace=True)

    return feature_importance.head(num_features).index.tolist()


def validate_merge(num_of_stations, df_stations, df_weather):
    if df_weather.shape[0] != df_stations.shape[0]:
        raise ValueError("Number of rows in weather and station dataframes must be the same")

    check_station_path = f"data/processed/station_{df_stations['number'].iloc[0]}.csv"
    if os.path.exists(check_station_path):
        check_station = pd.read_csv(f"data/processed/station_{df_stations['number'].iloc[0]}.csv")
    else:
        check_station = []

    data_length = len(df_stations)
    num_of_fetches = data_length / num_of_stations
    number_of_rows = len(check_station)

    print("[INFO] Number of fetches", num_of_fetches)
    print("[INFO] Number of rows in test station", number_of_rows)

    if len(check_station) >= num_of_fetches:
        raise ValueError("Number of rows must be less than number of fetches when merging")


def map_data_to_station(df, target_feature, features):
    for _, row in df.iterrows():
        station_csv_path = f"data/processed/station_{row['number']}.csv"

        if not os.path.exists(station_csv_path):
            new_station = pd.DataFrame(columns=[target_feature] + features)
            new_station.to_csv(station_csv_path, index=False)

        new_station_entry = pd.DataFrame({
            target_feature: [row[target_feature]],
            **{feature: [row[feature]] for feature in features}
        })

        new_station_entry.to_csv(station_csv_path, mode="a", header=False, index=False)


if __name__ == '__main__':
    main()
