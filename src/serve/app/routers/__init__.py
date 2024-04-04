from .health import router as health_router
from .prediction import router as prediction_router
from .bike_stations import router as bike_stations_router

__all__ = ['health_router', 'prediction_router', 'bike_stations_router']
