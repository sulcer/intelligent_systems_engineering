import datetime
from datetime import timezone
from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from src.serve.database import create_database_engine

Base = declarative_base()


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    station_number = Column(Integer)
    n_time_units = Column(Integer)
    predictions = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.now(timezone.utc))

    def __repr__(self):
        return (f"<Prediction(station_number={self.station_number},"
                f" n_time_units={self.n_time_units},"
                f" created_at={self.created_at})>")


Base.metadata.create_all(create_database_engine())
