from sklearn.ensemble import IsolationForest
import numpy as np

def load_model():
    np.random.seed(42)
    data = np.random.normal(0, 1, (300, 4))
    model = IsolationForest(contamination=0.05)
    model.fit(data)
    return model