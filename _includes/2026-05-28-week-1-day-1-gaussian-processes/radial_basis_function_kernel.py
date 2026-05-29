import numpy as np

def radial_basis_function_kernel(x_0: np.ndarray, x_1: np.ndarray, sigma_squared: float) -> np.ndarray:
    return np.exp(- np.sum((x_0 - x_1)**2) / (2 * sigma_squared))

def create_points(number_of_points: int, lower_limit, upper_limit) -> np.ndarray:
    return np.linspace(lower_limit, upper_limit, num=number_of_points, endpoint=True)

def covariance_matrix() -> np.ndarray:
    cov = np.zeros((50, 50))
    points = create_points(50, -3, 3)
    for idx in range(50):
        for idy in range(50):
            cov[idx, idy] = radial_basis_function_kernel(points[idx], points[idy], 1.0)
    return cov

def sample_over_the_prior_functions(mean, sigma, size):
    return np.random.multivariate_normal(mean, sigma, size)