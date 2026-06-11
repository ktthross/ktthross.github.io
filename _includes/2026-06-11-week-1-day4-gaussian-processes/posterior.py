import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../_includes/shared"))

from kernels import radial_basis_function_kernel, generate_covariance_matrix_from_points
import numpy as np

x_train = np.array([-1.0, 0.0, 1.0])
f_train = np.array([0.3, -0.2, 0.5])
x_star = np.array([0.5])

k_train_train = generate_covariance_matrix_from_points(x_train, x_train, radial_basis_function_kernel, length_scale=1.0, variance=1.0)
k_train_star = generate_covariance_matrix_from_points(x_train, x_star, radial_basis_function_kernel, length_scale=1.0, variance=1.0)
k_star_star = generate_covariance_matrix_from_points(x_star, x_star, radial_basis_function_kernel, length_scale=1.0, variance=1.0)

posterior_mean = k_train_star.T @ np.linalg.inv(k_train_train) @ f_train
posterior_var = k_star_star - k_train_star.T @ np.linalg.inv(k_train_train) @ k_train_star

print(f"posterior mean: {posterior_mean}")
print(f"posterior variance {posterior_var}")

# Outputs
# posterior mean: [0.06626568]
# posterior variance [[0.01789237]]
