from fastapi import APIRouter
from pydantic import BaseModel
from model import model

router = APIRouter()


class InputData(BaseModel):
    x: float


class PredictionResponse(BaseModel):
    prediction: float


@router.get("/")
def read_root():
    return {"status": "healthy", "service": "AI Service"}


@router.post("/predict", response_model=PredictionResponse)
def predict(data: InputData):
    prediction = model.predict(data.x)
    return {"prediction": prediction}
