import numpy as np
from sklearn.linear_model import LinearRegression
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

x_train = np.array([[1], [2], [3], [4], [5]])
y_train = np.array([2, 4, 6, 8, 10])

model = LinearRegression()
model.fit(x_train, y_train)


class InputData(BaseModel):
    x: float


@app.post("/predict")
def predict(data: InputData):
    x_input = np.array([[data.x]])
    prediction = model.predict(x_input)
    return {"prediction": prediction[0]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
