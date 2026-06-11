import numpy as np
from typing import Callable


def radial_basis_function_kernel(x_0: np.ndarray, x_1: np.ndarray, length_scale: float = 1.0, variance: float = 1.0) -> float:
    return variance * np.exp(-np.sum((x_0 - x_1) ** 2) / (2 * length_scale ** 2))


def inhomogeneous_linear_kernel(x_0: np.ndarray, x_1: np.ndarray, bias_variance: float = 1.0, slope_variance: float = 1.0) -> float:
    return bias_variance + slope_variance * np.dot(x_0, x_1)


def exponential_sin_squared_kernel(x_0: np.ndarray, x_1: np.ndarray, length_scale: float = 1.0, variance: float = 1.0, period: float = 1.0) -> float:
    return variance * np.exp(-2 * np.sin(np.pi * np.linalg.norm(x_0 - x_1) / period) ** 2 / length_scale ** 2)


def generate_covariance_matrix(func: Callable, n_points: int = 50, x_range: tuple = (-3, 3), **kwargs) -> np.ndarray:
    points = np.linspace(x_range[0], x_range[1], n_points)
    return generate_covariance_matrix_from_points(points, points, func, **kwargs)


def generate_covariance_matrix_from_points(points_x: np.ndarray, points_y: np.ndarray, func: Callable, **kwargs) -> np.ndarray:
    i_range, j_range = points_x.shape[0], points_y.shape[0]
    cov = np.zeros((i_range, j_range))
    for i in range(i_range):
        for j in range(j_range):
            cov[i, j] = func(points_x[i], points_y[j], **kwargs)
    return cov
