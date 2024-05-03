import json
import os
import dagshub
import numpy as np
import pandas as pd
from sqlalchemy.orm import sessionmaker
from src.serve.database import create_database_engine
from src.serve.models.prediction import Prediction
# from dagshub.data_engine.datasources import mlflow
# import dagshub.auth as dh_auth
# from sqlalchemy.orm import sessionmaker
# from src.config import settings
# from src.serve.database import create_database_engine
# from src.serve.models.prediction import Prediction


def main():
    # dh_auth.add_app_token(token=settings.dagshub_user_token)
    # dagshub.init(settings.dagshub_repo_name, settings.mlflow_tracking_username, mlflow=True)
    # mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    all_predictions = session.query(Prediction).all()

    print(all_predictions[-1].predictions)

    dir_path = "data/processed/"

    station_numbers = [file.split("_")[1].split(".")[0] for file in os.listdir(dir_path) if file.startswith("station")]

    for station_number in station_numbers:
        print(f"Validating predictions for station {station_number}")
        # mlflow.start_run(run_name=f"validate_predictions_mbajk_station_{station_number}")

        station_data = pd.read_csv(f"data/processed/station_{station_number}.csv")
        station_data = bind_latest_fetch_timestamp(station_data)
        station_data = process_date(station_data)

        errors = []
        for pred in all_predictions:
            prediction_list = json.loads(pred.predictions)
            for p in prediction_list:
                prediction = p["prediction"]
                date = p["date"].replace("T", " ")

                row = station_data.loc[station_data["date"] == date]

                if row.empty:
                    print(f"Prediction for station {station_number} at date {date} not found in station data")
                    continue

                actual = row["available_bike_stands"].values[0]
                error = actual - prediction
                errors.append(error)

                print(f"Prediction: {prediction}, Actual: {actual}, Error: {error}")

        mean_error = np.mean(errors)
        print(f"Mean error for station {station_number}: {mean_error}")
        mean_squared_error = np.mean(np.square(errors))
        print(f"Mean squared error for station {station_number}: {mean_squared_error}")

        # mlflow.log_metric("mean_error", mean_error)
        # mlflow.log_metric("mean_squared_error", mean_squared_error)
        # mlflow.end_run()


def bind_latest_fetch_timestamp(station_data: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv("data/raw/mbajk_stations.csv")
    fetch_timestamps = df["date"].unique()

    station_data["date"] = fetch_timestamps
    return station_data


def process_date(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"]).dt.floor("h")
    return df


if __name__ == "__main__":
    main()
