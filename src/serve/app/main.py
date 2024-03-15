from fastapi import FastAPI
from .routers import health, prediction

app = FastAPI()

app.include_router(health.router)
app.include_router(prediction.router)
