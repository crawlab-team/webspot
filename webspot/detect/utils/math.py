import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def log_positive(x) -> float:
    return float(np.log(x + 1))
