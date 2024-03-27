import os.path
import pandas as pd
from sklearn.feature_selection import mutual_info_regression


def main():
    df_stations = pd.read_csv("../../data/raw/mbajk_stations.csv")
    df_weather = pd.read_csv("../../data/raw/weather.csv")

    merged_df = merge_data(df_stations, df_weather)

    target_feature = "available_bike_stands"
    input_cols = merged_df.columns.tolist()

    for i in ["number", "name", "address", "bike_stands", "available_bikes", "lon", "lat"]:
        input_cols.remove(i)

    top_features = get_top_features(merged_df[input_cols], target_feature, 5)

    map_data_to_station(merged_df, target_feature, top_features)


def merge_data(df_stations, df_weather):
    df_weather.drop(columns=["date"], inplace=True)

    merged_df = pd.concat([df_stations, df_weather], axis=1)
    merged_df.drop(columns=["date"], inplace=True)

    merged_df.to_csv("../../data/processed/merged_data.csv", index=False)
    return merged_df


def get_top_features(df, target_feature, num_features):
    input_cols = df.columns.tolist()
    input_cols.remove(target_feature)
    information_gain = mutual_info_regression(df[input_cols], df[target_feature])

    feature_importance = pd.Series(information_gain, index=input_cols)
    feature_importance.sort_values(ascending=False, inplace=True)

    return feature_importance.head(num_features).index.tolist()


def map_data_to_station(df, target_feature, top_features):
    for index, row in df.iterrows():
        if not os.path.exists(f"../../data/raw/{row['name']}.csv"):
            new_station = pd.DataFrame(
                columns=[[target_feature] + top_features]
            )
            new_station.to_csv(f"../../data/processed/station_{row['number']}.csv", index=False)

        new_station_entry = pd.DataFrame([{
            target_feature: row[target_feature],
            top_features[0]: row[top_features[0]],
            top_features[1]: row[top_features[1]],
            top_features[2]: row[top_features[2]],
            top_features[3]: row[top_features[3]],
            top_features[4]: row[top_features[4]]
        }])

        new_station_entry.to_csv(f"../../data/processed/station_{row['number']}.csv",
                                 mode="a", header=False, index=False)


if __name__ == '__main__':
    main()
