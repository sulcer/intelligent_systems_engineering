from fastapi import FastAPI
from keras.src.saving import load_model

app = FastAPI()

model = load_model("../../../models/mbajk_GRU.h5")


@app.get("/")
def health_check():
    return {"status": "api is up and running"}


@app.post("/mbajk/predict")
def predict():
    return {"prediction": 12}
