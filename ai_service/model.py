import numpy as np
from sklearn.linear_model import LinearRegression


class LinearRegressionModel:
    def __init__(self):
        self.model = LinearRegression()
        self._train_model()

    def _train_model(self):
        x_train = np.array([[1], [2], [3], [4], [5]])
        y_train = np.array([2, 4, 6, 8, 10])
        self.model.fit(x_train, y_train)

    def predict(self, x):
        x_input = np.array([[x]])
        return self.model.predict(x_input)[0]


model = LinearRegressionModel()
