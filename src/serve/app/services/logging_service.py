import json
from datetime import timezone, datetime
from sqlalchemy.orm import sessionmaker
from src.serve.database import create_database_engine
from src.serve.models.prediction import Prediction


class LoggingService:

    @staticmethod
    def save_log(station_number: int, n_time_units: int, predictions: list):
        predictions_json = json.dumps(predictions)

        prediction_log = Prediction(
            station_number=station_number,
            n_time_units=n_time_units,
            predictions=predictions_json,
            created_at=datetime.now(timezone.utc)
        )

        Session = sessionmaker(bind=create_database_engine())
        session = Session()

        try:
            session.add(prediction_log)
            session.commit()
            return True
        except Exception as e:
            print(f"Error saving prediction log: {e}")
            session.rollback()
            return False
        finally:
            session.close()
