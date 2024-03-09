from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "api is up and running"}


@app.post("/mbajk/predict")
def predict():
    return {"prediction": 12}
